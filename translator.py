import sys
import json
import struct

commands = {'STOP': (0xff, 0),
            'MV': (0x00, 2),
            'ADD': (0x10, 2),
            'INC': (0x11, 1),
            'JUMP': (0x20, 1),
            'CJUMP': (0x21, 1),
            'CMPLE': (0x30, 2),
            'INP': (0x40, 1),
            'OUT': (0x41, 1)}


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

        for line in lines:
            semicol_index = line.find(':')
            if semicol_index != -1:
                address = parse_address(line[:semicol_index])
                name, value = parse_name_value(line[semicol_index + 1:])
                name_to_address[name] = address
                code_file.write(bytearray(struct.unpack(">4b", struct.pack(">I", value))))
            else:
                tokens = line.strip().split(' ')
                tokens = [token.strip() for token in tokens if len(token.strip()) > 0]

                #print(tokens)
                #print(commands.get(tokens[0]))

                if commands.get(tokens[0]) is None:
                    sys.exit(-1)
                elif commands[tokens[0]][1] != len(tokens) - 1:
                    sys.exit(-1)

                #print(tokens)

                command_code = [commands[tokens[0]][0], 0, 0, 0]

                for i in range(1, len(tokens)):
                    if name_to_address.get(tokens[i]) is None:
                        if tokens[i].isdigit():
                            command_code[2 * i - 1] = int(tokens[i])
                        else:
                            sys.exit(-1)
                    else:
                        command_code[2 * i - 1] = name_to_address[tokens[i]]

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
