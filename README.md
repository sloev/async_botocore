# async_botocore

Use gevent with botocore to call aws services in a nonblocking fashion.

by using gevent Pool and Pool.spawn() you can wrap execution of botocore in greenthreads.

a few important notes:

* always monkey.patch_all as first thing in your app (really first, like Main first, top first, just first, first, first :-)
* let each greenthread have its own connection, this worked for me. So create a function for calling aws services and inside this function; create your connection
* use pool.join(timeout=n) to check if the queue is empty
* use pool.wait_available(timeoout=n) to check if there is room in the pool for a new job
