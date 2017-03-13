import sys
import json
import struct

commands = {'STOP': (0xff, 0),
            'MV': (0x00, 2),
            'ADD': (0x10, 2),
            'INC': (0x11, 1),
            'DEC': (0x12, 1),
            'JUMP': (0x20, 1),
            'CJUMP': (0x21, 1),
            'CMPLE': (0x30, 2),
            'INP': (0x40, 1),
            'OUT': (0x41, 1),
            'OUTC': (0x42, 1),
            'PUSH': (0x50, 1),
            'POP': (0x51, 0)}

block_size = 4


def init_json():
    with open('commands.json', 'w+') as command_file:
        command_file.write(json.dumps(commands))


def parse_address(address_str):
    address_str = address_str.strip()
    address_str = address_str[address_str.find('[') + 1: address_str.find(']')]
    return int(address_str)


def parse_name_value(info_string):
    info_string = info_string.strip()
    equal_index = info_string.find('=')
    name = info_string[:equal_index].strip()
    value = int(info_string[equal_index + 1:].strip())
    return name, value


def translate(lines):

    with open('code.il', 'wb+') as code_file:
        name_to_address = {}

        for line_index, line in enumerate(lines):
            print(line)
            semicol_index = line.find(':')
            if semicol_index != -1:
                address = parse_address(line[:semicol_index])
                name, value = parse_name_value(line[semicol_index + 1:])
                name_to_address[name] = address
                code_file.write(bytearray(struct.pack(">I", value)))
            else:
                tokens = line.strip().split(' ')
                tokens = [token.strip() for token in tokens if len(token.strip()) > 0]

                if commands.get(tokens[0]) is None:
                    if tokens[0] == 'MALLOC':
                        if tokens[1].isdigit():
                            empty_command = [0, 0, 0, 0]
                            for i in range(line_index * block_size, line_index * block_size + int(tokens[1])):
                                code_file.write(bytearray(empty_command))
                            return
                        else:
                            print('ERROR: wrong malloc arg')
                            sys.exit(-1)
                    else:
                        print('ERROR: unknown command name')
                        sys.exit(-1)
                elif commands[tokens[0]][1] != len(tokens) - 1:
                    print('ERROR: wrong argument number')
                    sys.exit(-1)

                command_code = [commands[tokens[0]][0], 0, 0, 0]

                for i in range(1, len(tokens)):
                    if tokens[i][0] == '*':
                        tokens[i] = tokens[i][1:]
                        command_code[2] = 1
                    if name_to_address.get(tokens[i]) is None:
                        if tokens[i].isdigit():
                            command_code[2 * i - 1] = int(tokens[i])
                        elif tokens[0] == 'OUTC':
                            print(tokens[i][1])
                            print(ord(tokens[i][1]))
                            command_code[2 * i - 1] = ord(tokens[i][1])
                        else:
                            print('ERROR: address is not a number')
                            sys.exit(-1)
                    else:
                        command_code[2 * i - 1] = name_to_address[tokens[i]]

                print(command_code)
                code_file.write(bytearray(command_code))

        print(name_to_address)

if __name__ == '__main__':

    init_json()

    if len(sys.argv) == 1:
        print('Need input file\n')
        exit()

    lines = []
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    translate(lines)
