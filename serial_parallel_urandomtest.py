import time
import os
from random import getrandbits
import multiprocessing

def single_thread():
    nums = []
    for _ in range(num_to_gen):
        nums.append(os.urandom(128))
    return nums

def single_thread_randb():
    nums = []
    for _ in range(num_to_gen):
        nums.append(getrandbits(512))
    return nums

def pool_rand_imap(iters):
    return os.urandom(128)

def pool_rand_apply():
    return os.urandom(128)

def pool_randbits_imap(iters):
    return getrandbits(512)

def runTest(num_to_gen):
    #Time serial generation
    t_serial = time.time()
    s_nums = single_thread()
    t_serial = time.time() - t_serial

    t_p_overhead = time.time()
    # Time parallel generation
    # With no arguments, Pool() will use as many cores exist on the machine
    pool = multiprocessing.Pool()

    t_parallel_map = time.time()
    m_result = pool.imap_unordered(pool_rand_imap, range(num_to_gen), num_to_gen // os.cpu_count())
    
    pool.close()
    pool.join()
    t_parallel_map = time.time() - t_parallel_map
    t_p_overhead = time.time() - t_p_overhead
    t_p_overhead = t_p_overhead - t_parallel_map
    improvement = 0

    if t_serial == 0:
        improvement = (1 - t_parallel_map) * 100
    else:
        improvement = (1 - (t_parallel_map / t_serial)) * 100

    return (t_serial, t_parallel_map, t_p_overhead, improvement)


if __name__ == '__main__':
    targets = [1000,10000,100000,1000000,10000000,]
    iterations = 10
    t_serial = 0
    t_parallel = 0
    t_overhead = 0
    improvement = 0
    num_processes = 0
    for num_to_gen in targets:
        for run in range(iterations):
            a, b, c, d = runTest(num_to_gen)
            t_serial += a
            t_parallel += b
            t_overhead += c
            improvement += d
        t_serial = t_serial / iterations
        t_parallel = t_parallel / iterations
        t_overhead = t_overhead / iterations
        improvement = improvement / iterations

        print("Generated:\t{}".format(num_to_gen))
        print("Serial:\t\t{0:.3f}".format(t_serial))
        print("Parallel:\t{0:.3f}".format(t_parallel))
        print("Overhead:\t{0:.3f}".format(t_overhead))
        print("Improvement:\t{0:.2f}%".format(improvement))
        print("Processes:\t{}".format(os.cpu_count()))
