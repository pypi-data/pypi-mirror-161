"""
This module gives the option to run any function in parallel
"""

import time
from multiprocessing import Process


def run_parallel(count_of_process, function_target):
    start = time.perf_counter()
    process_index = 0
    process_list = []
    while process_index < count_of_process:
        temp_process = Process(target=function_target)
        process_list.insert(process_index, temp_process)
        process_index += 1

    for process in process_list:
        process.start()

    for process in process_list:
        process.join()

    finish = time.perf_counter()
    print(f'Finished in {round(finish - start, 2)} second(s)')
