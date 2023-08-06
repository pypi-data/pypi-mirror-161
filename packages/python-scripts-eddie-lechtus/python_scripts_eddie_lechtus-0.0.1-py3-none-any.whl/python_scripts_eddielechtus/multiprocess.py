import multiprocessing
from multiprocessing import freeze_support
from time import sleep


def worker(num):
    """thread worker function"""
    print(multiprocessing.current_process())
    print ('Worker:', num)
    sleep(100)
    return

if __name__ == '__main__':
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
        # p.join()