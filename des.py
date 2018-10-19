import sys

s0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
s1 = [[0, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]

s_box = []
s_box.append(s0)
s_box.append(s1)

def bit_list_to_int(bits):
    count = 0
    for i in range(0, len(bits)):
        if bits[i] == 1:
            count += 2**(len(bits)-i-1)

    return count

def initial_permutation(plain):
    p = [0] * 8
    p[0] = plain[1]
    p[1] = plain[5]
    p[2] = plain[2]
    p[3] = plain[0]
    p[4] = plain[3]
    p[5] = plain[7]
    p[6] = plain[4]
    p[7] = plain[6]

    return p

def inverse_permutation(bits):
    p = [0] * 8
    p[0] = bits[3]
    p[1] = bits[0]
    p[2] = bits[2]
    p[3] = bits[4]
    p[4] = bits[6]
    p[5] = bits[1]
    p[6] = bits[7]
    p[7] = bits[5]
    
    return p

def p10(key_bits):

    p = [0] * 10
    p[0] = key_bits[2]
    p[1] = key_bits[4]
    p[2] = key_bits[1]
    p[3] = key_bits[6]
    p[4] = key_bits[3]
    p[5] = key_bits[9]
    p[6] = key_bits[0]
    p[7] = key_bits[8]
    p[8] = key_bits[7]
    p[9] = key_bits[5]

    return p


def generate_keys(key_bits):
    left_bits = []
    right_bits = []

    list_of_keys = []

    permuted_key = p10(key_bits)

    for i in range(0, 5):
        left_bits.append(permuted_key[i])

    for i in range(0, 5):
        right_bits.append(permuted_key[i+5])


    for i in range(0, 2):
        left_bits.append(left_bits.pop(0))
        right_bits.append(right_bits.pop(0))
        temp_key = left_bits + right_bits


        key = [0] * 8
        key[0] = temp_key[5]
        key[1] = temp_key[2]
        key[2] = temp_key[6]
        key[3] = temp_key[3]
        key[4] = temp_key[7]
        key[5] = temp_key[4]
        key[6] = temp_key[9]
        key[7] = temp_key[8]

        list_of_keys.append(key)


    return list_of_keys


def get_s_val(n, s):
    row = 0
    if n & 8 > 0:
        row += 1
        row = row << 1

    if n & 1 > 0:
        row += 1

    col = 0
    if n & 4 > 0:
        col += 1
        col = col << 1

    if n & 2 > 0:
        col += 1

    return s_box[s][row][col]


def feistel(bits, key):
    expanded = []
    expanded = expanded + bits
    expanded.insert(0, bits[3])
    expanded.insert(4, bits[1])
    expanded.insert(5, bits[2])
    expanded.append(bits[0])

    text_val = bit_list_to_int(expanded)
    key_val = bit_list_to_int(key)

    s_box_index = text_val ^ key_val

    right_index = s_box_index & 15
    left_index = s_box_index >> 4

    s_left = get_s_val(left_index, 0)
    s_right = get_s_val(right_index, 1)

    f_val = 0
    f_val += s_left
    f_val = f_val << 2
    f_val += s_right


    return f_val





def des(plaintext_bits, key_bits, decrypt = 0): 
    permuted_bits = initial_permutation(plaintext_bits)

    left_bits = []
    right_bits = []
    for i in range(0, 4):
        left_bits.append(permuted_bits[i])


    for i in range(0, 4):
        right_bits.append(permuted_bits[i+4])


    key_list = generate_keys(key_bits)

    if decrypt != 0:
        tmp = left_bits
        left_bits = right_bits
        right_bits = tmp

    for i in range(0, 2):
        if decrypt == 0:
            next_left = right_bits
            next_right = leading_zeros(4, get_bit_array(feistel(right_bits, key_list[i]) ^ bit_list_to_int(left_bits)))


            left_bits = next_left
            right_bits = next_right
        else :
 
            next_left = right_bits
            next_right = leading_zeros(4, get_bit_array(feistel(right_bits, key_list[1-i]) ^ bit_list_to_int(left_bits)))


            left_bits = next_left
            right_bits = next_right


    if decrypt != 0:
        tmp = left_bits
        left_bits = right_bits
        right_bits = tmp


    return bit_list_to_int(inverse_permutation(left_bits + right_bits))


def leading_zeros(desired_size, bits):
    while len(bits) < desired_size:
        bits.insert(0, 0)

    return bits



def get_bit_array(num):
    bits = []
    while num > 0:

        if (num & 1) == 1:
            bits.insert(0, 1)
        else :
            bits.insert(0, 0)

        num = num >> 1

    return bits



def read_bytes_from_file(filename):
    bytelist = []
    f = open(filename, "rb")
    try:
        byte = f.read(1)
        while byte != "":
            bytelist.append(byte)
            byte = f.read(1)

    finally:
        f.close()
    
    return bytelist

def write_bytes_to_file(filename, cipher):
    f = open(filename, 'wb')

    for i in range(0, len(cipher)):
        f.write(chr(cipher[i]))

    f.close()

#-----------------------------------------------------------------
#---- MAIN -------------------------------------------------------
#----------------------------------------------------------------- 

key_val = int(sys.argv[3])

if len(sys.argv) != 5 or (key_val < 0 or key_val > 1023): 
    print "USAGE: des.py [input_file] [output_file] [key] [0 for encrypt OR 1 for decrypt]"
    print "key must be an int in range [0, 1023]"
    exit()


d = int(sys.argv[4])


plaintext = read_bytes_from_file(sys.argv[1])

key_bits = get_bit_array(key_val)
key_bits = leading_zeros(10, key_bits)

cipher = []

for i in range(0, len(plaintext)):
    cipher.append(des(leading_zeros(8, get_bit_array(ord(plaintext[i]))), key_bits, d))
write_bytes_to_file(sys.argv[2], cipher)


