"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CAMPAIGN/CONSUMERS.py    (views file for channels)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import json
import datetime
import pytz
from collections import OrderedDict
from threading import Timer

from channels import Group
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http  

import common.utility as CU
import campaign.campaign as GG


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
GAME EVENT HANDLERS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


@channel_session_user_from_http
def ws_add(message):
    # accept the connection
    message.reply_channel.send({'accept': True})
    
    # group gets messages from timer in campaign.py
    # subscribe the user to those send outs
    channel, group = message['path'].strip('/').split('/')    
    Group(group).add(message.reply_channel)     

    gameData = GG.Manager.GetGameDX(message.user)
    chanInfo = {
        'type': 'JOIN_GAME',
        'data': gameData,
    }
    message.reply_channel.send({'text': json.dumps(chanInfo)})


@channel_session_user 
def ws_message(message):

    instructions = message.content['text']


    gameData = GG.Manager.GetGameDX(message.user)
    
    chanInfo = {
        'type': 'UPDATE_GAME',
        'data': gameData,
    }    
    message.reply_channel.send({'text': json.dumps(chanInfo)})


@channel_session_user 
def ws_drop(message):
    groupName = GG.Manager.GetGroupName(message.user.username)
    Group(groupName).discard(message.reply_channel)





