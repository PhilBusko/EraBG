"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
PROJECT/URLS.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

from django.conf.urls import include, url
from django.contrib import admin
import allauth.account.views as AV

import common.views as BV 
import kingdoms.views as KV 
import members.views as MV 
import campaign.views as GV 
import central.views as CV 


kingdoms_url = [
    url(r'^kingdoms/$', KV.kingdoms, name='kingdoms'),
    url(r'^special_cards/$', KV.special_cards, name='special_cards'),
    url(r'^game_rules/$', KV.game_rules, name='game_rules'),
    url(r'^reference_jx/([a-zA-Z0-9_]+)/$', KV.reference_jx, name='reference_jx'),
    
    url(r'^data_load/$', KV.data_load, name='data_load'),
    url(r'^manager_jx/([a-zA-Z0-9_]+)/$', KV.manager_jx, name='manager_jx'),
]


members_url = [    
    url(r"^accounts/signup/$", AV.signup, name="account_signup"),        # must preserve allauth name field for its internal calls
    url(r"^accounts/login/$", AV.login, name="account_login"),
    url(r"^accounts/logout/$", AV.logout, name="account_logout"),

    url(r"^accounts/email/$", MV.email, name="account_email"),
    url(r"^accounts/confirm-email/(?P<key>[-:\w]+)/$", AV.confirm_email, name="account_confirm_email"),
    url(r"^accounts/confirm-email/$", AV.email_verification_sent, name="account_email_verification_sent"),    # used when email still requires confirmation
 
    url(r"^accounts/password/change/$", AV.password_change, name="account_change_password"),
   	url(r"^accounts/password/reset/$", MV.password_reset, name="account_reset_password"),
    url(r"^accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$", MV.password_reset_from_key, name="account_reset_password_from_key"),
    url(r"^accounts/inactive/$", AV.account_inactive, name="account_inactive"),         

    url(r'^auth_dialog/', MV.dialog),
    url(r'^messages/', MV.messages, name='messages'),
    url(r'^messages_jx/([a-zA-Z0-9_]+)/$', MV.messages_jx, name='messages_jx'),
    url(r'^profile/', MV.profile, name='profile'),
    url(r'^profile_jx/([a-zA-Z0-9_]+)/$', MV.profile_jx, name='profile_jx'),

    url(r'^members_admin/', MV.members_admin, name='members_admin'),
    url(r'^members_jx/([a-zA-Z0-9_]+)/$', MV.members_jx, name='members_jx')    
]


campaign_url = [
    url(r'^campaign/$', GV.campaign, name='campaign'),
    url(r'^campaign_jx/([a-zA-Z0-9_]+)/$', GV.campaign_jx, name='campaign_jx'),
]


central_url = [
    url(r'^headquarters/$', CV.headquarters, name='headquarters'),
    # url(r'^view_profile/([a-zA-Z0-9_]+)', CV.view_profile, name='view_profile'),
    # url(r'^store/$', CV.store, name='store'),
    # url(r'^central_jx/([a-zA-Z0-9_]+)/$', CV.central_jx, name='central_jx'),
    # 
    url(r'^master/', CV.master, name='master'),
    #url(r'^master_jx/([a-zA-Z0-9_]+)/$', CV.master_jx, name='master_jx'),
]


urlpatterns = [
    url(r'^$', CV.landing_page, name='landing_page'),

    url(r'^members/', include(members_url)),   # do not use a namespace, breaks allauth reverse urls 
    url(r'^messages/', include('postman.urls', namespace='postman', app_name='postman')),	# necessary for postman
    
    url(r'^reference/', include(kingdoms_url, namespace='kingdoms')),
    url(r'^campaign/', include(campaign_url, namespace='campaign')),
    url(r'^central/', include(central_url, namespace='central')),
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', BV.not_found, name='not_found'),
]

