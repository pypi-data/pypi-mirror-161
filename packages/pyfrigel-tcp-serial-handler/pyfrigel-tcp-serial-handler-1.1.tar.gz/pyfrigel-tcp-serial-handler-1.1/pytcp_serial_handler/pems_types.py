UNKNOWN_MESSAGETYPE = 0
CMD_CMD = 1
CMD_ALARM = 2
CMD_STS = 3
CMD_ROM_W = 4
CMD_ROM_R = 5
CMD_ANIN_R = 7
CMD_ANOUT_W = 8
CMD_ANOUT_R = 9
CMD_DIGIN_R = 10
CMD_DIGOUT_R = 12
CMD_DIGOUT_W = 13
CMD_CONF = 36
CMD_INFO_PAR = 37
CMD_READ_ACCESS_ID = 38
CMD_INFO_OBJ = 44
CMD_FILE_READ = 101
CMD_FILE_WRITE = 102
CMD_TIMEOUT = 150
CMD_IGNORED = 151
CMD_ROM_R_MULTI = 205
CMD_ANIN_R_MULTI = 207
CMD_ANOUT_W_MULTI = 208
CMD_ANOUT_R_MULTI = 209
CMD_SCRALL_R = 240
CMD_NACK = 255

KNOWN_COMMANDS = [CMD_CMD,
                  CMD_ALARM,
                  CMD_STS,
                  CMD_ROM_W,
                  CMD_ROM_R,
                  CMD_ANIN_R,
                  CMD_ANOUT_W,
                  CMD_ANOUT_R,
                  CMD_DIGIN_R,
                  CMD_DIGOUT_R,
                  CMD_DIGOUT_W,
                  CMD_CONF,
                  CMD_INFO_PAR,
                  CMD_READ_ACCESS_ID,
                  CMD_INFO_OBJ,
                  CMD_FILE_READ,
                  CMD_FILE_WRITE,
                  CMD_ROM_R_MULTI,
                  CMD_ANIN_R_MULTI,
                  CMD_ANOUT_W_MULTI,
                  CMD_ANOUT_R_MULTI,
                  CMD_SCRALL_R,
                  CMD_NACK,]

EXTENDED_COMMANDS = [CMD_FILE_READ,
                     CMD_FILE_WRITE,]