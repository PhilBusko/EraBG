"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
MEMBERS/MIDDLEWARE.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import threading


# adds the request object as a global variable of the current thread
# the request can then be accessed anywhere down the request-response cycle
# for example, during template binding 
class RequestMiddleware(object):

    thread_local = threading.local()

    def process_request(self, request):
        RequestMiddleware.thread_local.request = request






