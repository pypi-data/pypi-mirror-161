# -*- coding: utf-8 -*-
import logging
from typing import List
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from tqdm import tqdm


class Task:
    CONCURRENT_THREADS = 0
    CONCURRENT_PROCESS = 0

    def get_params(self):
        pass

    def run(self, param):
        pass

    def post_run(self, res_list: List):
        pass

    def __str__(self):
        return self.__class__.__name__


class TaskRunner:

    def __init__(self, tasks=None):
        self.tasks = tasks or []
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self):
        c = len(self.tasks)
        self.log.info('total tasks: %d', c)

        for i, task in enumerate(self.tasks):
            self.log.info('run task %d/%d : %s', i + 1, c, task)
            self.run_task(task)

    def run_task(self, task):
        result = []
        self.log.info('task start: %s', task)

        params = task.get_params()
        if not isinstance(params, (tuple, list, set)):
            params = [params]
        self.log.info('params count: %d', len(params))

        if params:
            if task.CONCURRENT_THREADS:
                with ThreadPoolExecutor(max_workers=task.CONCURRENT_THREADS) as executor:
                    iter_results = [executor.submit(task.run, param) for param in params]
                    for future in tqdm(iter_results, total=len(params), desc=str(task)):
                        result.append(future.result())

            elif task.CONCURRENT_PROCESS:
                with ProcessPoolExecutor(max_workers=task.CONCURRENT_PROCESS) as executor:
                    iter_results = [executor.submit(task.run, param) for param in params]
                    for future in tqdm(iter_results, total=len(params), desc=str(task)):
                        result.append(future.result())
            else:
                for param in tqdm(params, total=len(params), desc=str(task)):
                    res = task.run(param)
                    result.append(res)

        self.log.info('result count: %d', len(result))
        task.post_run(result)

        self.log.info('task end: %s', task)
        return result
