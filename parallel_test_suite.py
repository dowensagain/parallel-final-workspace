import time
import os
import multiprocessing
import math
import cupy
import numpy
import secrets
from ctypes import c_char_p

# 128 was determined to be a good chunk size
# for multiprocess pools by experimentation
globals()['CHUNK_DIVISOR'] = 128
globals()['NUM_TO_GEN'] = 1000000

def determine_messages_InputAndPlayers(num_inputs, num_players):
    a = 0.27
    b = 0.05
    num_max_ones = math.ceil(num_inputs * a)
    size_nbf = int(-(num_inputs * math.log(b))/(math.log(2)**2))
    k = math.ceil( (size_nbf / num_inputs) * math.log(2) )
    p1_bound = num_inputs * k + num_max_ones
    Not = math.ceil(p1_bound / a)
    return Not * (num_players - 1)

def pool_rand_imap(iters):
    # return os.urandom(32)
    return secrets.token_bytes(32)
    # return numpy.random.bytes(32)

def q_rand(q, num_to_gen, offset, extra):
    for i in range(num_to_gen * offset, num_to_gen + (num_to_gen * offset) + extra):
        # q.put(secrets.token_bytes(32))
        q[i] = secrets.token_bytes(32)
        # q.put(1)
        # q.get()
        # q.task_done()

def q_consume(q, arr):
    for i in range(0, len(arr)):
        arr[i] = q.get()
        q.task_done()

def serial(num_to_gen):
    start = time.time()
    nums = []
    for _ in range(num_to_gen):
        nums.append(os.urandom(32))
    return time.time() - start

def pll_cpu(num_to_gen):
    start = time.time()
    pool = multiprocessing.Pool()
    randoms = pool.imap_unordered(pool_rand_imap, range(num_to_gen), int(num_to_gen // globals()['CHUNK_DIVISOR']))
    pool.close()
    pool.join()
    return time.time() - start

def pll_cpu_2(num_to_gen):
    NUM_PROCESSES = 3
    q = multiprocessing.Array(c_char_p, num_to_gen)
    start = time.time()
    # q = multiprocessing.Queue(maxsize=0)
    a = multiprocessing.Process(target=q_rand, args=(q, num_to_gen // NUM_PROCESSES, 0, 0))
    b = multiprocessing.Process(target=q_rand, args=(q, num_to_gen // NUM_PROCESSES, 1, 0))
    c = multiprocessing.Process(target=q_rand, args=(q, num_to_gen // NUM_PROCESSES, 2, num_to_gen % NUM_PROCESSES))
    # d = multiprocessing.Process(target=q_consume, args=(q, arr))
    a.start()
    b.start()
    c.start()
    a.join()
    b.join()
    c.join()
    # d.start()
    # d.join()
    return time.time() - start


def pll_gpu(num_to_gen):
    # The highest bit integer with cupy we can generate is 32 bits.
    # To match the requirement (256 bits) we will generate 8x more messages
    start = time.time()
    for _ in range(0, 8):
        rand = cupy.random.randint(low=2**30, high=2**31, size=num_to_gen, dtype=numpy.int32)
    return time.time() - start

if __name__ == '__main__':
    multiprocessing.freeze_support()
    num_players = 3
    msgs_togen_xsmall = [
        determine_messages_InputAndPlayers(32,      num_players), # 2**5
        determine_messages_InputAndPlayers(64,      num_players), # 2**6
        determine_messages_InputAndPlayers(128,     num_players) # 2**7
        ]
    msgs_togen_small = [
        determine_messages_InputAndPlayers(256,     num_players), # 2**8
        determine_messages_InputAndPlayers(4096,    num_players), # 2**11
        determine_messages_InputAndPlayers(65536,   num_players), # 2**16
        determine_messages_InputAndPlayers(1048576, num_players) # 2**20
        ]
    msgs_togen_large = [
        determine_messages_InputAndPlayers(2097152, num_players), # 2**21
        determine_messages_InputAndPlayers(4194304, num_players), # 2**22
        determine_messages_InputAndPlayers(8388608, num_players), # 2**23
    ]

    msgs_togen_all =  msgs_togen_xsmall + msgs_togen_small + msgs_togen_large

    msgs = msgs_togen_all

    test_suite = [
        serial
        ,pll_cpu
        ,pll_gpu
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
