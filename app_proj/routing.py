"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
PROJECT/ROUTING.py      (urls file for channels)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

from channels.routing import route

import campaign.consumers as GC

channel_routing = [
    
    route("websocket.connect",  GC.ws_add, path=r"^/campaign/"),
    route("websocket.receive",  GC.ws_message, path=r"^/campaign/"),
    route("websocket.disconnect",  GC.ws_drop, path=r"^/campaign/"),
    
]



