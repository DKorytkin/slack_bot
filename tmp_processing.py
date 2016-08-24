import requests
import concurrent.futures
import multiprocessing
import logging


def test():
    r = requests.get('http://qareport.uaprom/?component_id=10042')
    print(r.text)
    return r


# # multiprocessing
# jobs = []
# for i in range(5):
#     multiprocessing.log_to_stderr(logging.DEBUG)
#     p = multiprocessing.Process(target=test())
#     jobs.append(p)
#     p.start()


with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    result = pool.submit(test)
    result.result()
