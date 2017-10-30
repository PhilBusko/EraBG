"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
MEMBERS/MODELS/MEMBERS.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import os
import datetime
import pytz
from collections import OrderedDict

from django.conf import settings
from django.db.models import Count, F, Q     
import django.contrib.auth.models as AM
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.template.loader import render_to_string

import common.utility as CU
import kingdoms.kingdoms as KK
import members.models.tables as MT
#import members.models.postman as MP
#import postman.models as PM


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
PROFILE TABLE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Profile_Reporter(object):
    

    @staticmethod
    def GetUserModel(p_user):
        try:
            user_m = AM.User.objects.get(username=p_user)
        except AM.User.DoesNotExist:
            user_m = None
        return user_m


    @staticmethod
    def GetProfile_Mdl(p_user_m):
        prof_m = MT.Profile.objects.get(UserFK=p_user_m)
        return prof_m
    
    
    # returns user info as dict
    @staticmethod
    def GetUserData(p_user):   
        
        try:
            user_m = AM.User.objects.get(username=p_user)
        except AM.User.DoesNotExist:
            raise ObjectDoesNotExist("User not found.")
        
        try:
            prof_m = MT.Profile.objects.get(UserFK=user_m)
        except MT.Profile.DoesNotExist:
            raise ObjectDoesNotExist("Profile not found.")
        
        if prof_m.TimeZone:
            timezone = pytz.timezone(prof_m.TimeZone).localize(datetime.datetime.now()).strftime('%Z')
            country = prof_m.Country
        else:
            timezone = "Unknown"
            country = "Unknown"
        
        timeOW_dlt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc) - user_m.date_joined    # no GetCustomNow
        if timeOW_dlt.days <= 365:
            timeOW_nm = timeOW_dlt.days / 30.42
            timeOnWebsite = str(round(timeOW_nm, 1)) + " months"
        else:
            timeOW_nm = timeOW_dlt.days / 365
            timeOnWebsite = str(round(timeOW_nm, 2)) + " years"
        
        full = {}
        full['hashID'] = prof_m.HashID
        full['userName'] = user_m.username
        full['email'] = user_m.email
        full['dateJoined'] = user_m.date_joined.strftime(CU.FORMAT_DTSTR_DT)
        full['timeOnWebsite'] = timeOnWebsite
        full['timezone'] = timezone 
        full['country'] = country 
        full['slogan'] = prof_m.Slogan
        full['icon'] = '{0}/{1}'.format(prof_m.Icon[0], prof_m.Icon)   if prof_m.Icon   else None
        
        return full
    
    
    # returns a datetime in the user's timezone
    @staticmethod
    def GetUserNow(p_user_m):
        
        if p_user_m.is_authenticated():
            profile_m = Profile_Reporter.GetProfile_Mdl(p_user_m)
            profTZ = pytz.timezone(profile_m.TimeZone   if profile_m.TimeZone   else 'UTC')
            userNow = FM.TimeMachine.GetCustomNow().astimezone(profTZ).strftime(CU.FORMAT_DTSTR)
        else:   
            userNow = FM.TimeMachine.GetCustomNow().strftime(CU.FORMAT_DTSTR)
        
        return userNow
    
    
    @staticmethod
    def ViewProfileData(p_requester, p_target):
        
        # get user models
        
        try:
            target_m = AM.User.objects.get(username=p_target)
        except AM.User.DoesNotExist:
            raise ObjectDoesNotExist("Target user not found.")
        
        try:
            targetProf_m = MT.Profile.objects.get(UserFK=target_m)
        except MT.Profile.DoesNotExist:
            raise ObjectDoesNotExist("Target user profile not found.")
        
        # get any relation among users
        
        if not p_requester.id:
            relation = "None"
        else:
            relRequester = MT.Relationship.objects.filter(User1FK=p_requester, User2FK=target_m
                ).values_list('RelationValue', flat=True)
            
            relTarget = MT.Relationship.objects.filter(User1FK=target_m, User2FK=p_requester
                ).values_list('RelationValue', flat=True)
            
            if relRequester:
                if relRequester[0] == 1:
                    relation = "Your friend"
                else:
                    relation = "Ignored by you"
                    
            elif relTarget:
                relation = "Ignored by them"
                
            else:
                relation = "None"
        
        # discover target user info for display
        
        if relation == "Your friend" and targetProf_m.Pref_FriendsRealName == True and target_m.get_full_name():
            realName = target_m.get_full_name()
        elif target_m.get_full_name():   # name is set
            realName = "****** ******"
        else:
            realName = ""
        
        if relation == "Your friend" and targetProf_m.Pref_FriendsEmail == True:
            email = target_m.email
        else:
            email = "*********"
        
        if targetProf_m.TimeZone:
            timezone = pytz.timezone(targetProf_m.TimeZone).localize(datetime.datetime.now()).strftime('%Z')
            country = targetProf_m.Country
        else:
            timezone = "Unknown"
            country = "Unknown"
        
        timeOW_dlt = FM.TimeMachine.GetCustomNow() - target_m.date_joined
        if timeOW_dlt.days <= 365:
            timeOW_nm = timeOW_dlt.days / 30.42
            timeOnWebsite = str(round(timeOW_nm, 1)) + " months"
        else:
            timeOW_nm = timeOW_dlt.days / 365
            timeOnWebsite = str(round(timeOW_nm, 2)) + " years"
        
        # create return data structure
        
        full = lambda: None
        
        full.userName = target_m.username
        full.realName = realName
        full.email = email
        full.timezone = timezone 
        full.country = country
        full.icon = '{0}/{1}'.format(targetProf_m.Icon[0], targetProf_m.Icon)   if targetProf_m.Icon   else None
        
        full.relationship = relation
        full.slogan = targetProf_m.Slogan if targetProf_m.Slogan else ""
        full.lifetimeDiamonds = targetProf_m.LifetimeDiamonds
        full.timeOnWebsite = timeOnWebsite        
        full.dateJoined = target_m.date_joined.strftime(CU.FORMAT_DTSTR_DT)
        full.favClub = targetProf_m.FavClubFK.Club if targetProf_m.FavClubFK else None
        
        full.friendList = Relationship_R.GetFriendData(target_m) 
        
        return full.__dict__


class Profile_Editor(object):
    
    
    @staticmethod
    def ChangeUserName(user, newName):        
        
        prog_lg.info(newName)
        
        try:
            user_m = AM.User.objects.get(username = user)
        except AM.User.DoesNotExist:
            return "User not found."
        
        user_m.username = newName
        user_m.save()
        
        return "1"
    
    
    @staticmethod
    def SaveSlogan(user, newSlogan):
        hret = CU.HttpReturn()
        try:
            user_m = AM.User.objects.get(username = user)
        except AM.User.DoesNotExist:
            hret.results = "User not found."
            hret.status = 201
            return hret
        
        try:
            prof_m = MT.Profile.objects.get(UserFK = user_m)
        except MT.Profile.DoesNotExist:
            hret.results = "Profile not found."
            hret.status = 201
            return hret
        
        prof_m.Slogan = newSlogan
        prof_m.save()
        
        # return succesfull results
        
        hret = CU.HttpReturn()
        hret.results = newSlogan
        hret.status = 201
        return hret
    
    
    @staticmethod
    def SaveIcon(user, newIcon):
        
        # data gathering
        
        hret = CU.HttpReturn()
        try:
            user_m = AM.User.objects.get(username=user)
        except AM.User.DoesNotExist:
            hret.results = "User not found."
            hret.status = 501
            return hret
        
        try:
            profile_m = MT.Profile.objects.get(UserFK=user_m)
        except AM.User.DoesNotExist:
            hret.results = "Profile not found."
            hret.status = 501
            return hret
        
        # save parameter file from user to the server's file storage
        # new icon type: django.core.files.uploadedfile.InMemoryUploadedFile
        
        # 1. check if it's an image
        
        import magic
        filetype = magic.from_buffer(newIcon.read())
        newIcon.seek(0)     # reset file cursor
        
        if 'image' not in filetype:
            hret.results = "File is not an image."
            hret.status = 422
            return hret
        
        # 2. reduce size of image to at most 500 pixels per side
        
        
        
        
        # 3. save file at server
        
        from django.core.files.storage import FileSystemStorage
        from django.core.files.base import ContentFile
        import socket
        
        folder = profile_m.HashID[0]
        
        host = socket.gethostname()
        if host.startswith('test') or host.startswith('prod'):
            fsLoc = os.path.join(settings.BASE_DIR, 'app_proj/static/user_icons', folder )
        else:
            fsLoc = os.path.join(settings.BASE_DIR, 'members/static/user_icons', folder )
        
        fs = FileSystemStorage(location=fsLoc)      # requires the absolute path
        
        if profile_m.Icon:
            existingFullPath = os.path.join(fsLoc, profile_m.Icon)
            if os.path.isfile(existingFullPath):
                os.remove(existingFullPath)
        
        fileName = profile_m.HashID + '_icon.jpg'
        fs.save(fileName, ContentFile(newIcon.read()))
        
        profile_m.Icon = fileName
        profile_m.save()
        
        # return succesfull results
        
        records = {
            'message': "User icon saved.",
            'iconFileName': fileName,
        }
        
        hret = CU.HttpReturn()
        hret.results = records
        hret.status = 201
        return hret
    

    @staticmethod
    def DeleteUser(userName):
        try:
            user_m = AM.User.objects.get(username=userName)
        except:
            return "User not found."
        
        if user_m.is_superuser:
            return "Can't delete an admin."

        user_m.delete();
        
        return "User deleted."


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
USER DECKS TABLE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Decks_Reporter(object):

    
    @staticmethod
    def GetDecksFT(p_user_m):

        if p_user_m.is_authenticated():
            decks = MT.UserDeck.objects.values_list('KingdomFK__Name', 'PowerCards'
                                        ).filter(UserFK=p_user_m).order_by('KingdomFK__Name')
        else:
            decks = []
        
        decks_dict = []
        for deck in decks:
            newDeck = OrderedDict()
            newDeck['kingdom'] = deck[0]
            newDeck['PowerCards'] = deck[1]
            decks_dict.append(newDeck)

        ftable = {
            'data': decks_dict,
            'colFmt': [],
        }
        return ftable

    
    @staticmethod
    def GetDecksLS(p_user_m):
        if p_user_m.is_authenticated():
            decks_ls = MT.UserDeck.objects.values_list('KingdomFK__Name', flat=True
                                    ).filter(UserFK=p_user_m).order_by('KingdomFK__Name')
        else: 
            decks_ls = []
        return decks_ls


class Decks_Editor(object):

    
    @staticmethod
    def SaveDeck(p_user_m, p_kingdom):
        kingdom_m = KK.Kingdom.objects.get(Name=p_kingdom)
        prof_m, crtd = MT.UserDeck.objects.get_or_create(
            UserFK=p_user_m, KingdomFK=kingdom_m)

        return crtd


    @staticmethod
    def DeleteDecks(p_user_m):
        deck_mdl = MT.UserDeck.objects.filter(UserFK=p_user_m)
        delNum = deck_mdl.delete()
        return delNum


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
PROFILE SIGNALS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# when a user is created, also create their profile

import hashlib
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
@receiver(post_save, sender=AM.User)
def TriggerProfile(sender, instance, created, **kwargs):
    if created:
        emailEnc = instance.email.encode('utf-8')
        hashRaw = hashlib.md5(emailEnc).hexdigest()     # 32 digits
        hashID = ""
        for h in range(0, 9, 1):
            d = hashRaw[h]
            hashID += d.capitalize()
            if h in (2, 5):
                hashID += "-"
        
        prof_m, crtd = MT.Profile.objects.get_or_create(
            UserFK = instance, HashID = hashID)


# override user logged in signal

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login
from members.middleware import RequestMiddleware
from django.contrib.gis.geoip2 import GeoIP2
from timezonefinder import TimezoneFinder

user_logged_in.disconnect(update_last_login)

@receiver(user_logged_in)
def user_login_preupdate(sender, user, **kwargs):
    
    # get request data from custom middleware
    
    thread_local = RequestMiddleware.thread_local
    if hasattr(thread_local, 'request'):
        request = thread_local.request
        userIP = request.META['REMOTE_ADDR']
    else:
        CU.excp_lg.error('No http request available for:' + user.username)
        userIP = None
    
    if userIP == "127.0.0.1" and user.username == 'admin':
        userIP = "69.143.33.123"    
    
    if userIP and userIP != "127.0.0.1":
        try:
            geo = GeoIP2()
            city_dx = geo.city(userIP)
            
            lat = float(city_dx['latitude'])
            lng = float(city_dx['longitude'])
            tf = TimezoneFinder()
            timezone = tf.timezone_at(lng=lng, lat=lat)
            if timezone is None:
                timezone = tf.closest_timezone_at(lng=lng, lat=lat)
            
            if not timezone:
                CU.excp_lg.error("TimeZone not found for " + user.username)
            
            prof_m = MT.Profile.objects.get(UserFK=user)
            
            prof_m.IP = userIP
            prof_m.TimeZone = timezone
            prof_m.Region = city_dx['region']
            prof_m.Country = city_dx['country_name']
            prof_m.City = city_dx['city']
            prof_m.save()
            
        except Exception as ex:
            excp_lg.error(ex)
    
    
    # display welcome message
    
    if not user.last_login:
        first_login = True
    
    # reconnect the built-in signal
    update_last_login(sender, user, **kwargs)


# allow users to change email addresses, but limit to one email per user

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed  
@receiver(email_confirmed)
def update_user_email(sender, request, email_address, **kwargs):
    email_address.set_as_primary()
    stale_addresses = EmailAddress.objects.filter(
        user=email_address.user).exclude(primary=True).delete()


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
POSTMAN INTERFACE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# can't import central files to this file
# so define the message admin here 
MESSAGE_ADMIN = "EraPostHouse"


# class IPostman(object):
    
    
#     @staticmethod
#     def GetMessage(p_request, p_msgID):
#         profile_m = MT.Profile.objects.get(UserFK=p_request.user)
#         timezone = pytz.timezone( profile_m.TimeZone   if profile_m.TimeZone   else 'UTC' )
#         message_dx = MP.Postman.GetMessage(p_request, p_msgID, timezone)
        
#         hret = CU.HttpReturn()
#         hret.results = message_dx
#         hret.status = 201
#         return hret
    
    
#     @staticmethod
#     def GetConversation(p_request, p_msgID):
#         profile_m = MT.Profile.objects.get(UserFK=p_request.user)
#         timezone = pytz.timezone( profile_m.TimeZone   if profile_m.TimeZone   else 'UTC' )
#         message_dict = MP.Postman.GetConversation(p_request, p_msgID, timezone)
        
#         hret = CU.HttpReturn()
#         hret.results = message_dict
#         hret.status = 201
#         return hret
    
    
#     @staticmethod
#     def WriteUserMessage(p_request):
        
#         sender = p_request.user.username
#         recipient = p_request.POST.get('recipients')
        
#         # prog_lg.debug(sender)
#         # prog_lg.debug(recipient)
        
#         # exceptions
        
#         if "admin " in recipient:
#             return IPostman.WriteAdminMessage(p_request)
        
#         if sender == recipient:
#             return MP.Postman.WriteMessage(p_request)
        
#         # check for relationship status
        
#         relValue = MT.Relationship.objects.values_list('RelationValue', flat=True
#             ).filter(User1FK__username = recipient, User2FK__username = sender)
#         if relValue:
#             relValue = relValue[0]
#         else:
#             relValue = 0
        
#         hret = CU.HttpReturn()
        
#         if relValue == 0:
#             hret.results = "Message NOT sent: user is not in your friends list."
#             hret.status = 201
#             return hret
#         elif relValue == -1:
#             hret.results = "Message NOT sent: user has you in their ignore list."
#             hret.status = 201
#             return hret
        
#         # send message if friends
        
#         return MP.Postman.WriteMessage(p_request)
    
    
#     @staticmethod
#     def WriteAdminMessage(p_request):
        
#         sender = p_request.user.username
#         recipient = p_request.POST.get('recipients')
#         subject = p_request.POST.get('subject')
#         body = p_request.POST.get('body')
        
#         if "Technical" in recipient:
#             subject = "[TS] " + subject
#         elif "Suggestion" in recipient:
#             subject = "[SI] " + subject
        
#         message = MP.MessageData()
#         message.sender = sender
#         message.recipients = MESSAGE_ADMIN     
#         message.subject = subject
#         message.body = body
        
#         fReq = MP.Postman.GetFakeRequest(sender, message.__dict__)
        
#         return MP.Postman.WriteMessage(fReq)
    
    
#     @staticmethod
#     def GetUnreadCount(p_request):
#         inbox_dict = MP.Postman.GetInboxDict(p_request)
        
#         unreadCnt = 0
#         for msg in inbox_dict:
#             if not msg['read_at']:
#                 unreadCnt += 1
        
#         return unreadCnt



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
END OF FILE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""