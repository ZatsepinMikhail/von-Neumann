import sys
import json
import os
import mmap
import struct

block_size = 4

commands_by_number = {}


def MV(file_in_map, instruction_ptr, first_param, second_param):
    file_in_map[first_param: first_param + block_size] = file_in_map[second_param: second_param + block_size]
    file_in_map[0: block_size] = struct.pack('>I', instruction_ptr + block_size)
    return True


def ADD(file_in_map, instruction_ptr, first_param, second_param):
    first_value = struct.unpack('>I', file_in_map[first_param: first_param + block_size])[0]
    second_value = struct.unpack('>I', file_in_map[second_param: second_param + block_size])[0]
    file_in_map[first_param: first_param + block_size] = struct.pack('>I', first_value + second_value)
    file_in_map[0: block_size] = struct.pack('>I', instruction_ptr + block_size)
    return True


def INC(file_in_map, instruction_ptr, first_param, second_param):
    first_value = struct.unpack('>I', file_in_map[first_param: first_param + block_size])[0]
    file_in_map[first_param: first_param + block_size] = struct.pack('>I', first_value + 1)
    file_in_map[0: block_size] = struct.pack('>I', instruction_ptr + block_size)
    return True


def INP(file_in_map, instruction_ptr, first_param, second_param):
    file_in_map[first_param: first_param + block_size] = struct.pack('>I', int(input('Enter natural number: ')))
    file_in_map[0: block_size] = struct.pack('>I', instruction_ptr + block_size)
    return True


def OUT(file_in_map, instruction_ptr, first_param, second_param):
    print('Fib =', struct.unpack('>I', file_in_map[first_param: first_param + block_size])[0])
    file_in_map[0: block_size] = struct.pack('>I', instruction_ptr + block_size)
    return True


def STOP(file_in_map, instruction_ptr, first_param, second_param):
    return False


def JUMP(file_in_map, instruction_ptr, first_param, second_param):
    file_in_map[0: block_size] = struct.pack('>I', first_param)
    return True


def CJUMP(file_in_map, instruction_ptr, first_param, second_param):
    bool_result = struct.unpack('>I', file_in_map[block_size: block_size + block_size])[0]
    if bool_result:
        file_in_map[0: block_size] = struct.pack('>I', first_param)
    else:
        file_in_map[0: block_size] = struct.pack('>I', instruction_ptr + block_size)
    return True


# compare less or equal
def CMPLE(file_in_map, instruction_ptr, first_param, second_param):
    first_value = struct.unpack('>I', file_in_map[first_param: first_param + block_size])[0]
    second_value = struct.unpack('>I', file_in_map[second_param: second_param + block_size])[0]
    if first_value <= second_value:
        file_in_map[block_size: block_size + block_size] = struct.pack('>I', 1)
    else:
        file_in_map[block_size: block_size + block_size] = struct.pack('>I', 0)
    file_in_map[0: block_size] = struct.pack('>I', instruction_ptr + block_size)
    return True


def interprete(file_in_map):
    not_stopped = True

    while not_stopped:
        instruction_ptr = struct.unpack('>I', file_in_map[0: block_size])[0]
        function_name = commands_by_number[file_in_map[instruction_ptr]][0]
        not_stopped = globals()[function_name](file_in_map, instruction_ptr, file_in_map[instruction_ptr + 1], file_in_map[instruction_ptr + 3])


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print('Need input file\n')
        exit()

    file_size = os.path.getsize(sys.argv[1])
    file_on_disk = os.open(sys.argv[1], os.O_RDWR)
    file_in_map = mmap.mmap(file_on_disk, file_size, mmap.ACCESS_WRITE)

    with open('commands.json') as command_file:
        commands_serialized = command_file.read()

    commands = json.loads(commands_serialized)
    for command in commands.items():
        commands_by_number[command[1][0]] = (command[0], command[1][1])

    interprete(file_in_map)
    file_in_map.close()
