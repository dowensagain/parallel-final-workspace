import time
import os
import multiprocessing
import math
import cupy
import numpy

# 128 was determined to be a good chunk size
# for multiprocess pools by experimentation
globals()['CHUNK_SIZE'] = 128

def determine_messages_byInput(num_inputs):
    a = 0.27
    b = 0.05
    num_max_ones = math.ceil(num_inputs * a)
    size_nbf = int(-(num_inputs * math.log(b))/(math.log(2)**2))
    k = math.ceil( (size_nbf / num_inputs) * math.log(2) )
    p1_bound = num_inputs * k + num_max_ones
    return math.ceil(p1_bound / a)

def pool_rand_imap(iters):
    return os.urandom(32)

def serial(num_to_gen):
    start = time.time()
    nums = []
    for _ in range(num_to_gen):
        nums.append(os.urandom(32))
    return time.time() - start

def pll_cpu(num_to_gen):
    start = time.time()
    pool = multiprocessing.Pool()
    randoms = pool.imap_unordered(pool_rand_imap, range(num_to_gen), int(num_to_gen // globals()['CHUNK_SIZE']))
    pool.close()
    pool.join()
    return time.time() - start

def pll_gpu(num_to_gen):
    # The highest bit integer with cupy we can generate is 32 bits.
    # To match the requirement (256 bits) we will generate 8x more messages
    start = time.time()
    for _ in range(0, 8):
        rand = cupy.random.randint(low=2**30, high=2**31, size=num_to_gen, dtype=numpy.int32)
    return time.time() - start

if __name__ == '__main__':
    msgs_togen_xsmall = [
        determine_messages_byInput(16), # 2**4
        determine_messages_byInput(32), # 2**5
        determine_messages_byInput(64), # 2**6
        determine_messages_byInput(128) # 2**7
        ]
    msgs_togen_small = [
        determine_messages_byInput(256), # 2**8
        determine_messages_byInput(4096), # 2**11
        determine_messages_byInput(65536), # 2**16
        determine_messages_byInput(1048576) # 2**20
        ]
    msgs_togen_large = [
        determine_messages_byInput(2097152), # 2**21
        determine_messages_byInput(4194304), # 2**22
        determine_messages_byInput(8388608), # 2**23
        determine_messages_byInput(16777216) # 2**24
    ]

    msgs_togen_all =  msgs_togen_xsmall + msgs_togen_small # + msgs_togen_large

    msgs = msgs_togen_all

    test_suite = [
        serial
        , pll_cpu
        , pll_gpu
        ]
    row = []
    rows = [[""]]
    [rows[0].append(x) for x in msgs]

    # prime execution
    test_suite[0](msgs[0])
    test_suite[1](msgs[0])
    test_suite[2](msgs[0])
    
    for test in test_suite:
        row = [test.__name__]
        for msg in msgs:
            print("Running test {} with {} messages".format(test.__name__, msg))
            r = test(msg)
            row.append(r)
        rows.append(row)
    
    f = open("parallel_test_suite_results.csv", "w")
    for row in rows:
        r = ""
        for column in row:
            r += str(column) + ","
        f.write(r)
        f.write("\n")
    f.close()
