from gevent import monkey
monkey.patch_all()#socket=True, dns=True, time=True, select=True,thread=False, os=True, ssl=True, httplib=False, aggressive=True)
from gevent.pool import Pool


import botocore.session
import logging
import time

concurrency = 10

def invoke_test(i):
    start = time.time()
    session = botocore.session.get_session()

    client = session.create_client('lambda')

    logging.warning("{} calling".format(i))
    response = client.invoke(
        FunctionName='test',
        InvocationType = "RequestResponse"
    )
    took = time.time() - start
    logging.warning("{} finished, took:{}".format(i, took))
    return response[u"Payload"].read()

def process_jobs(todo, end):
    pool = Pool(concurrency)
    jobs = {}


    try:
        i = 0
        while True:
            # add jobs if within grace period
            if not pool.full() and time.time() < end:
                try:
                    for _ in range(concurrency - len(jobs.keys())):
                        func, args = todo.pop(0) # raises IndexError if no more jobs todo
                        greenthread = pool.spawn(func, *args)
                        jobs[greenthread] = args

                except IndexError:
                    logging.warning("no more jobs todo")
            # check if done
            done = pool.join(timeout=1)
            # iterate through results, delete done greenthreads
            for greenthread, args in reversed(jobs.items()):
                if greenthread.successful():
                    logging.warning("success! args:{}, result:{}".format(args, greenthread.value))
                    jobs.pop(greenthread)
                elif greenthread.ready():
                    logging.warning("fail! args:{}, result:{}".format(args, greenthread.value))
            # if no more jobs and graceperiod ended then shutdown
            if time.time() > end and done :
                logging.warning("no more jobs, no more time")
                break
    except:
        logging.exception("error")
    return jobs

if __name__ == "__main__":

    logging.info("Creating a pool")



    logging.warning("sched")
    end = time.time() + 10

    todo = [(invoke_test, (i, )) for i in range(20)]
    error_jobs = process_jobs(todo, end)



    logging.warning("exit, jobs={}".format(error_jobs))
