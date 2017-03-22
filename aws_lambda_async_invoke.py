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
    return response

if __name__ == "__main__":

    logging.info("Creating a pool")
    concurrency = 10

    pool = pool.Pool(concurrency)


    logging.warning("sched")
    end = time.time() + 10
    try:
        i = 0
        while True:
            room = pool.wait_available(timeout=1)
            if time.time() > end and pool.join(timeout=1):
                logging.warning("no more jobs, no more time")
                break
            if room and time.time() < end:
                pool.spawn(invoke_test, i)
                i += 1
    except:
        logging.exception("error")

    logging.warning("waiting for jobs")


    logging.warning("exit")
