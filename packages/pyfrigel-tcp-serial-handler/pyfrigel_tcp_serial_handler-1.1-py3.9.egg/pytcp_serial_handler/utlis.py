from pytcp_serial_handler import pems_consts, pems_types

def uint_to_byte(value):
    return value.to_bytes(1, 'big', signed=False)


def checksum(bytes_array: bytearray):
    return uint_to_byte(sum(bytes_array)%256)


def is_message_complete(bytes_array: bytearray):
    message_length = get_message_length (bytes_array);
    return message_length > 0 and len(bytes_array) >= message_length


def get_message_length(bytes_array: bytearray):
    if len(bytes_array) >=4:
        message_type = bytes_array[pems_consts.MESSAGE_TYPE_POS]
        if message_type in pems_types.KNOWN_COMMANDS:
            
            if message_type in pems_types.EXTENDED_COMMANDS:
                return 6 + int.from_bytes(bytes_array[2:4], byteorder='big', signed=False)
            else:
                return 4 + bytes_array[2];
            
    return -1


def create_timeout_message(slave: int):
    data = []
    data.append(uint_to_byte(slave))
    data.append(uint_to_byte(pems_types.CMD_TIMEOUT))
    data.append(checksum(b''.join(data)))
    return b''.join(data)


def create_ignored_message(slave: int):
    data = []
    data.append(uint_to_byte(slave))
    data.append(uint_to_byte(pems_types.CMD_IGNORED))
    data.append(checksum(b''.join(data)))
    return b''.join(data)


def create_access_id_message(slave: int):
    data = []
    data.append(uint_to_byte(slave))
    data.append(uint_to_byte(pems_types.CMD_READ_ACCESS_ID))
    data.append(uint_to_byte(1))
    data.append(str.encode(pems_consts.ONBOARD_DEVICE_ID))
    data.append(checksum(b''.join(data)))
    return b''.join(data)


def get_pems_slave(bytes_array: bytearray):
    return bytes_array[pems_consts.MESSAGE_SLAVE_POS] if len(bytes_array) > pems_consts.MESSAGE_SLAVE_POS else -1


def get_pems_type(bytes_array: bytearray):
    return bytes_array[pems_consts.MESSAGE_TYPE_POS] if len(bytes_array) > pems_consts.MESSAGE_TYPE_POS else -1