import time
import os
from random import getrandbits
import multiprocessing
import math

def rough_messages_byInput(input_size):
    a = 0.27
    b = 0.05
    num_max_ones = math.ceil(input_size * a)
    size_nbf = int(-(input_size * math.log(b))/(math.log(2)**2))
    k = math.ceil( (size_nbf / input_size) * math.log(2) )
    p1_bound = input_size * k + num_max_ones
    return math.ceil(p1_bound / a)

def pool_rand_imap(iters):
    return os.urandom(128)

def runTest(chunk_divisor, length):

    t_p_overhead = time.time()
    # Time parallel generation
    # With no arguments, Pool() will use as many cores exist on the machine
    pool = multiprocessing.Pool()
    t_parallel_map = time.time()
    m_result = pool.imap_unordered(pool_rand_imap, range(length), int(length // chunk_divisor))
    
    pool.close()
    pool.join()
    r = list(m_result)
    t_parallel_map = time.time() - t_parallel_map
    t_p_overhead = time.time() - t_p_overhead
    t_p_total = t_p_overhead
    t_p_overhead = t_p_overhead - t_parallel_map

    return (t_p_total, t_p_overhead)


if __name__ == '__main__':
    chunks_divisors = [4,8,16,32,64,128]
    messages = [
        rough_messages_byInput(256),
        rough_messages_byInput(4096),
        rough_messages_byInput(65536),
        rough_messages_byInput(1048576)
        ]
    row = []
    rows = [[0]]
    [rows[0].append(x) for x in chunks_divisors]
    iterations = 10
    t_parallel = 0
    t_overhead = 0
    
    for length in messages:
        row = [length]
        for divisor in chunks_divisors:
            for run in range(iterations):
                a, b = runTest(divisor, length)
                t_parallel += a
                t_overhead += b
            t_parallel = t_parallel / iterations
            t_overhead = t_overhead / iterations
            row.append(t_parallel)
            print("Chunk divisor:\t{}".format(divisor))
            print("Generated:\t{}".format(length))
            print("Time:\t{0:.3f}".format(t_parallel))
            print("Overhead:\t{0:.3f}".format(t_overhead))
            print("Processes:\t{}".format(os.cpu_count()))
            # rows.append(column)
        rows.append(row)
    f = open("chunk_size_results.txt", "w")
    for row in rows:
        r = ""
        for column in row:
            r += str(column) + ","
        f.write(r)
        f.write("\n")
    f.close()
