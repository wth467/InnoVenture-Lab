import multiprocessing
from tqdm import tqdm

def parallel_process(func, tasks, n_jobs=None, **kwargs):
    """
    并行处理任务
    :param func: 处理函数
    :param tasks: 任务列表
    :param n_jobs: 并行进程数
    :return: 结果列表
    """
    if n_jobs is None:
        n_jobs = multiprocessing.cpu_count() - 1
    
    results = []
    with multiprocessing.Pool(n_jobs) as pool:
        futures = [
            pool.apply_async(func, (task,), kwargs)
            for task in tasks
        ]
        
        for future in tqdm(futures, total=len(tasks)):
            results.append(future.get())
    
    return results