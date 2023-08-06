# import random
# import threading
# import time
# from concurrent.futures import ThreadPoolExecutor
# import requests
#
#
# def do_task(i):
#     try:
#         resp = requests.get("https://baidu.com", timeout=10)
#         print(resp)
#     except:
#         pass
#     # time.sleep(3)
#     # print(i, "done", end="\n")
#     return i
#
#
# tasks = []
#
# done = False
#
# def add_task():
#     for i in range(1, 10000):
#         print("添加任务种子", i)
#         tasks.append(i)
#         time.sleep(random.random())
#
#     global done
#     done = True
#
#
# threading.Thread(target=add_task).start()
#
#
# def get_task():
#     if tasks:
#         return tasks.pop()
#
#
# thread_count = 32
#
#
# def test_ThreadPoolExecutor():
#     begin_time = time.time()
#     semaphore = threading.BoundedSemaphore(thread_count)  # 为了限制 线程池堆积的任务数，
#     with ThreadPoolExecutor(max_workers=thread_count) as t:  # 创建一个最大容纳数量为5的线程池
#         while tasks or not done:
#             task = get_task()
#             if not task:
#                 time.sleep(1)
#                 continue
#
#             print("add task ", task)
#             semaphore.acquire()
#             task = t.submit(do_task, task)
#             task.add_done_callback(lambda x: semaphore.release())
#
#     end_time = time.time()
#     print("耗时", end_time - begin_time)
#
#
# def test_thread():
#     class Test(threading.Thread):
#         def run(self) -> None:
#             while tasks or not done:
#                 task = get_task()
#                 if not task:
#                     time.sleep(1)
#                     continue
#
#                 print("add task ", task)
#                 do_task(task)
#
#     begin_time = time.time()
#
#     threads = []
#     for i in range(thread_count):
#         # print("开启线程", i)
#         thread = Test()
#         threads.append(thread)
#         thread.start()
#
#     for thread in threads:
#         thread.join()
#
#     end_time = time.time()
#     print("耗时", end_time - begin_time)
#
#
# if __name__ == "__main__":
#     # 任务充足的情况下，两者性能一样
#     # 任务不充足的情况下，线程池效果好
#
#     # test_ThreadPoolExecutor() # 11765
#     # print(1)
#     # test_thread()  #
#     thread = threading.Thread(target=test_ThreadPoolExecutor)
#     thread.start()
#     # thread.join()
#     while True:
#         print("---")
#         time.sleep(1)

from feapder import Request

request = Request("https://www.ti.com/product/DRV632", params={"b":[1,3]})
request.params
