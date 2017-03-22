from gevent import monkey, pool
monkey.patch_all()#socket=True, dns=True, time=True, select=True,thread=False, os=True, ssl=True, httplib=False, aggressive=True)


import botocore.session
import logging
import time


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

if __name__ == "__main__":

    logging.info("Creating a pool")
    concurrency = 10

    pool = pool.Pool(concurrency)


    logging.warning("sched")
    end = time.time() + 10

    todo = [(i, ) for i in range(20)]
    jobs = {}
    try:
        i = 0
        while True:
            # add jobs if within grace period
            if not pool.full() and time.time() < end:
                try:
                    for _ in range(concurrency - len(jobs.keys())):
                        args = todo.pop() # raises IndexError if no more jobs todo
                        greenthread = pool.spawn(invoke_test, *args)
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


    logging.warning("exit, jobs={}".format(jobs))
