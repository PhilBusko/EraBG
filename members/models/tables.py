"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
MEMBERS/MODELS/TABLES.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

from decimal import Decimal

from django.db import models
import django.contrib.auth.models as AM

import common.utility as CU
import kingdoms.kingdoms as KK


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
MODEL DECLARATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Profile(models.Model):
    UserFK = models.OneToOneField(AM.User, on_delete=models.CASCADE)
    
    HashID = models.CharField(max_length=16)
    IP = models.CharField(max_length=16, null=True)
    TimeZone = models.CharField(max_length=60, null=True)
    Region = models.CharField(max_length=30, null=True)
    Country = models.CharField(max_length=30, null=True)
    City = models.CharField(max_length=30, null=True)
    
    Slogan = models.CharField(max_length=100, null=True)   
    Icon = models.CharField(max_length=100, null=True)    
    
    Diamonds = models.IntegerField(default=10)
    LifetimeDiamonds = models.IntegerField(default=10)
    

class UserDeck(models.Model):
    UserFK = models.ForeignKey(AM.User, on_delete=models.CASCADE)
    KingdomFK = models.ForeignKey(KK.Kingdom)
    PowerCards = models.CharField(max_length=100, null=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
END OF FILE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""