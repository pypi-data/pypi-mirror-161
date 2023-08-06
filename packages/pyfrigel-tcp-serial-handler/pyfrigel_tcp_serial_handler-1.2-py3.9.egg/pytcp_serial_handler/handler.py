import asyncio
import logging
from time import sleep
from serial_asyncio import open_serial_connection
from .utlis import *

RETRY_TIMER = 5

class PemsRequest:
    ''' Basic class used to encapsulate a client request
    
    inputs:
        transport (asyncio.BaseTransport): Transport used to for the reply message
        data (bytearray): data to send on the serial port
    '''
    def __init__(self, transport: asyncio.BaseTransport, data: bytearray) -> None:
        self.transport = transport
        self.data = data


class Handler():
    ''' Main orchestrator that handles the request on the serial port
    
    inputs:
        loop (asyncio.AbstractEventLoop): event loop on which the handler will run
        serial_settings (dict): dict containing kwargs with the serial configuration
                                {'url': _,'baudrate': _, 'parity': _, 'stopbits': _, 'bytesize': _}
        serial_timeout (int): time after which a message is considered timedout
        port_tcp (int): TCP port on which the server will listen
        retry_connection (bool): if True, will try to reopen the server and the serial port on failure
    '''
    
    def __init__(self, loop: asyncio.AbstractEventLoop, serial_settings: dict, serial_timeout: int, port_tcp: int, retry_connection: bool=False) -> None:
        self.loop = loop
        self.serial_settings = serial_settings
        self.port_tcp = port_tcp
        self.serial_timeout = serial_timeout
        self.retry_connection = retry_connection
        self.request_queue = []
        self.request_in_progress = False
        self.last_request = None
        self.reader = None
        self.writer = None
        self.buffer = b''
        self.timeout_task = None
        self.slaves_timeout_counter = {}
        self.blacklisted_slaves_timer = {}
        
        
        while True:
            try:
                server_coro = self.loop.create_server(lambda: TCPServerProtocol(self), 
                                                      '0.0.0.0',
                                                      self.port_tcp)
                self.server = self.loop.run_until_complete(server_coro)
                logging.info('listening on {}:{}'.format('0.0.0.0', self.port_tcp))
                break
            except Exception:
                logging.exception
                if self.retry_connection:
                    logging.info('retrying to open the server in {} seconds'.format(RETRY_TIMER))
                    sleep(RETRY_TIMER)
                else:
                    quit()

        self.serial_task = self.loop.create_task(self.run_serial())
        self.unblacklister_task = self.loop.create_task(self.unblacklist_slaves())


    def send_new_request_from_queue(self):
        ''' Sends the next available request from the queue
        '''
        if self.request_in_progress:
            return
        self.last_request = None
        
        if self.request_queue:
            self.last_request = self.request_queue.pop(0)
            slave = get_pems_slave(self.last_request.data)
            
            # if the request queue is not empty, check if the request must be discarded
            if self.blacklisted_slaves_timer.get(slave, 0) >0 and self.request_queue:
                for r in self.request_queue:
                    if self.blacklisted_slaves_timer.get(get_pems_slave(r.data), 0) == 0:
                        logging.debug('ignored  request for slave {} because it\'s blacklisted for additional {} seconds'.format(slave, self.blacklisted_slaves_timer[slave]))
                        try:
                            self.last_request.transport.write(create_ignored_message(slave))
                        except Exception:
                            logging.exception()
                        self.send_new_request_from_queue()
            
            self.request_in_progress = True
            self.write_message_to_serial(self.last_request)
        
        
    def write_message_to_serial(self, p_rquest: PemsRequest):
        ''' Writes the request to the serial port
        
        inputs:
            p_rquest (PemsRequest): object containing information to send on the serial
        '''
        if self.writer:
            try:
                logging.debug('sending message to serial {}'.format(p_rquest.data))
                self.buffer = b''
                self.writer.write(p_rquest.data)
                self.writer.drain()
                self.start_timeout_timer()
            except Exception:
                logging.exception()
                quit()
        else:
            logging.debug('serial not initialized, ignoring message')
            try:
                p_rquest.transport.write(create_ignored_message(get_pems_slave(p_rquest.data)))
            except Exception:
                logging.exception()
            finally:
                self.request_in_progress = False
                self.last_request = None
                
            
    async def run_serial(self):
        ''' Used in a coroutine to open the serial port and read the data
        '''
        while not self.writer:
            try:
                self.reader, self.writer = await open_serial_connection(**self.serial_settings)
                logging.info('successfully opened serial device {}'.format(self.serial_settings['url']))
            except:
                if self.retry_connection:
                    self.reader = None
                    self.writer = None
                    logging.warning('failed to open port {}, retrying in {} seconds'.format(self.serial_settings['url'], RETRY_TIMER))
                    await asyncio.sleep(RETRY_TIMER)
                else:
                    logging.error('failed to open port {}'.format(self.serial_settings['url']))
                    quit()
                
        while True:
            try:
                data = await self.reader.read(1)
            except Exception:
                logging.exception()
                quit()
            self.buffer += data
            if is_message_complete (self.buffer):
                logging.debug('new message from serial {}'.format(self.buffer))
                self.request_in_progress = False
                self.stop_timeout_timer()
                slave = get_pems_slave(data)
                self.slaves_timeout_counter[slave] = 0
                if slave in self.blacklisted_slaves_timer:
                    self.blacklisted_slaves_timer[slave] = 0
                    logging.debug('removed slave {} from blacklist beacuse of a new message'.format(slave))
                try:
                    self.last_request.transport.write(self.buffer)
                except Exception:
                    logging.exception()
                finally:
                    self.buffer = b''
                    self.send_new_request_from_queue()
                    
        
    async def unblacklist_slaves(self):
        ''' Used in a coroutine. Decreases the timer of blacklisted slaves until 0
        '''
        while True:
            for slave, timer in self.blacklisted_slaves_timer.items():
                self.blacklisted_slaves_timer[slave] = max(timer-0.1, 0)
            await asyncio.sleep(0.1)
            
            
    def start_timeout_timer(self):
        ''' Starts timeout timer for the serial message
        '''
        if self.timeout_task:
            self.stop_timeout_timer()
        self.timeout_task = asyncio.ensure_future(self.timeout())
        
        
    def stop_timeout_timer(self):
        ''' Stops timeout timer for the serial message
        '''
        self.timeout_task.cancel()
        self.timeout_task = None
        
        
    async def timeout(self):
        ''' Handles message timeout
        '''
        await asyncio.sleep(self.serial_timeout/1000)
        
        self.timeout_task = None
        self.request_in_progress = False
        if not self.last_request:
            return
        
        slave = get_pems_slave(self.last_request.data)
        logging.debug('message timeout for slave {}'.format(slave))
        
        new_timeout_counter = min(self.slaves_timeout_counter.get(slave, 0) + 1, pems_consts.PEMS_MASTER_BLACKLIST_TIMEOUTS)
        self.slaves_timeout_counter[slave] = new_timeout_counter
        
        if new_timeout_counter >= pems_consts.PEMS_MASTER_BLACKLIST_TIMEOUTS:
            new_timeout_timer = min(pems_consts.PEMS_SCHEDULER_BLACKLIST_TIME_BASE*len(self.slaves_timeout_counter), pems_consts.PEMS_SCHEDULER_BLACKLIST_TIME_MAX)
            self.blacklisted_slaves_timer[slave] = new_timeout_timer
            logging.debug('slave {} blacklisted for {} seconds because of {} or more consecutive timeouts'.format(slave, new_timeout_timer, new_timeout_counter))
        elif new_timeout_counter >= pems_consts.PEMS_MASTER_CONGESTION_TIMEOUTS:
            new_timeout_timer = min(pems_consts.PEMS_SCHEDULER_CONGESTION_TIME_BASE*len(self.slaves_timeout_counter), pems_consts.PEMS_SCHEDULER_CONGESTION_TIME_MAX)
            self.blacklisted_slaves_timer[slave] = new_timeout_timer
            logging.debug('slave {} throttled for {} seconds because of {} or more consecutive timeouts'.format(slave, new_timeout_timer, new_timeout_counter))
        
        try:
            self.last_request.transport.write(create_timeout_message(slave))
        except Exception:
            logging.exception()
        self.last_request = None
        self.send_new_request_from_queue()
        
            
class TCPServerProtocol(asyncio.Protocol):
    ''' Created on new connection from client
    
    inputs: handler (Handler)
    '''
    
    def __init__(self, handler: Handler):
        self.handler = handler
        asyncio.Protocol.__init__(self)
        
    
    def connection_made(self, transport: asyncio.BaseTransport):
        peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(peername))
        self.transport = transport
            

    def data_received(self, data: bytearray):
        logging.debug('new request received: {}'.format(data))
        
        if get_pems_type(data) == pems_types.CMD_READ_ACCESS_ID:
            self.handle_access_id(get_pems_slave(data))
            return
        
        if self.handler.writer is None:
            self.transport.write(create_timeout_message(get_pems_slave(data)))
            return
        
        if self.handler.last_request and self.handler.last_request.transport == self.transport:
            # client already asking another request, ignore it
            return
        
        # delete previous request if present
        for index, p_request in enumerate(self.handler.request_queue):
            if p_request.transport == self.transport:
                self.handler.request_queue.remove(index)
                break
        
        self.handler.request_queue.append(PemsRequest(transport=self.transport, data=data))
        self.handler.send_new_request_from_queue()
        

    def connection_lost(self, exc: Exception):
        logging.info('connection lost with client: {}{}'.format(self.transport.get_extra_info('peername'),
                                                         ', error: {}'.format(exc) if exc else ''))
        
        
    def handle_access_id(self, slave: int):
        ''' Used to reply to onboard special message
        '''
        try:
            self.transport.write(create_access_id_message(slave))
        except Exception:
            logging.exception()