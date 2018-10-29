import mmh3
import sys

def add_one_to_each(item, queue, big_list):
    for i in range(0, len(item)):
        item[i] += 1
        queue.append(list(item))
        big_list.append(list(item))
        item[i] -= 1


def generate_variations(message, m_list, num_variations):
    split_list = message.split()

    queue = []
    big_list = []
    m_list = [1] * len(split_list)

    queue.append(m_list)
    big_list.append(m_list)

    while(len(big_list) < num_variations):
        add_one_to_each(queue.pop(0), queue, big_list)


    print "finished generating variations!"
    print "compiling messages:"
    word_list = []
    for i in range(0, len(big_list)):
        msg = ""
        if i % 500000 == 0 and i > 0:
            print "compiled", i, "messages"
        for j in range(0, len(big_list[i])):
            msg += big_list[i][j] * " "
            msg += split_list[j]

        word_list.append(msg)

    print "finished compiling", num_variations, "messages"

    return word_list



message1 = "More efficient attacks are possible by employing cryptanalysis to specific hash functions. When a collision attack is discovered and is found to be faster than a birthday attack, a hash function is often denounced as \"broken\". The NIST hash function competition was largely induced by published collision attacks against two very commonly used hash functions, MD5 and SHA-1. The collision attacks against MD5 have improved so much that, as of 2007, it takes just a few seconds on a regular computer. Hash collisions created this way are usually constant length and largely unstructured, so cannot directly be applied to attack widespread document formats or protocols."

message2 = "This is a fraudulent message. This is a fraudulent message. This is a fraudulent message."

m_list1 = []
m_list2 = []

print "MESSAGE 1 IS:", message1
print ""
print "generating variations of message 1..."
word_list_1 = generate_variations(message1, m_list1, int(sys.argv[1]))
print ""
print "MESSAGE 2 IS:", message2
print ""
print "generating variations of message 2..."
word_list_2 = generate_variations(message2, m_list2, int(sys.argv[1]))


print "\ncomparing hashes..."

hashes = {}

for i in range(0, len(word_list_1)):
    h = mmh3.hash(word_list_1[i])

    hashes[str(h)] = i

for i in range(0, len(word_list_2)):
    h = mmh3.hash(word_list_2[i])
    if str(h) in hashes:
        print "\nCOLLISION FOUND!!!\n"
        print "MESSAGE:", "\"" + word_list_1[hashes[str(h)]] + "\""
        print "HASH:", mmh3.hash(word_list_1[hashes[str(h)]])
        print ""
        print "MESSAGE:", "\"" + word_list_2[i] + "\""
        print "HASH:", mmh3.hash(word_list_2[i])

        exit()

print "NO COLLISION FOUND"
