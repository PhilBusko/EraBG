"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
KINGDOMS/MODELS/KINGDOMS.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import os
import csv
import random
import re
from collections import OrderedDict

from django.conf import settings
from django.db.models import Count, F, Q

import common.utility as CU


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
MODEL DECLARATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

from django.db import models


class Kingdom(models.Model):
    Name = models.CharField(max_length=20, null=True)
    BoxSet = models.CharField(max_length=20, null=True)
    Race = models.CharField(max_length=20, null=True)
    LifePoints = models.IntegerField(default=1)
    Traits = models.CharField(max_length=200, null=True)


class Card(models.Model):
    KingdomFK = models.ForeignKey(Kingdom)
    Name = models.CharField(max_length=20, null=True)
    Type = models.CharField(max_length=20, null=True)
    Quantity = models.IntegerField(default=0)
    Rules = models.CharField(max_length=500, null=True)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
KINGDOMS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Reporter(object):    
    
    
    @staticmethod
    def GetKingdoms():
        reinos = Kingdom.objects.values_list('Name', flat=True
                                            ).exclude(Name="Power"
                                            ).exclude(Name="Avatar"
                                            ).order_by('Name')
        return list(reinos)
    
    
    @staticmethod
    def GetKingdomProperties(p_kingdom):
        
        try:
            kingdom_dx = Kingdom.objects.values().get(Name=p_kingdom)
        except:
            return {}
        
        kingdom_odx = OrderedDict()
        kingdom_odx['race'] = kingdom_dx['Race']
        kingdom_odx['BoxSet'] = kingdom_dx['BoxSet']
        kingdom_odx['traits'] = kingdom_dx['Traits']
        
        return kingdom_odx
    
    
    @staticmethod
    def GetKingdomDeck(p_kingdom):
        
        deck_mdl = Card.objects.filter(KingdomFK__Name=p_kingdom)
        
        attack_dict = []
        defense_dict = []
        spell_dict = []
        
        attack_cnt = 0
        defense_cnt = 0
        spell_cnt = 0
        
        for card in deck_mdl:
            card_dx = OrderedDict()
            card_dx['name'] = card.Name
            card_dx['quant'] = card.Quantity
            card_dx['rules'] = card.Rules
            
            if card.Type.strip() == "A":
                attack_dict.append(card_dx)
                attack_cnt += card.Quantity
                
            elif card.Type.strip() == "D":
                defense_dict.append(card_dx)
                defense_cnt += card.Quantity
                
            else:
                spell_dict.append(card_dx)
                spell_cnt += card.Quantity        
        
        attack_dict = sorted(attack_dict, key=lambda k: k['name']) 
        defense_dict = sorted(defense_dict, key=lambda k: k['name']) 
        spell_dict = sorted(spell_dict, key=lambda k: k['name']) 
        
        colFmt = {
            'quant': 'format_center',
        }
        
        rtable = {
            'attack': attack_dict,
            'attack_cnt': attack_cnt,
            'defense': defense_dict,
            'defense_cnt': defense_cnt,
            'spell': spell_dict,
            'spell_cnt': spell_cnt,
            'colFmt': colFmt,
        }
        return rtable


    @staticmethod
    def ShuffleDeck(p_deck, p_power):
        card_mdl = Card.objects.filter(KingdomFK__Name=p_deck)

        deck = []
        for card_m in card_mdl:
            quant = card_m.Quantity +1
            for q in range(1, quant):
                deck.append(card_m.Name)

        if p_power:
            deck.append(p_power)

        random.shuffle(deck)    # shuffles in place
        random.shuffle(deck)    # just for the smiles

        return deck


    @staticmethod
    def GetCardEffects(p_card_m):
        
        effects = { 'attacker': [], 'defender': [] }

        if not p_card_m:
            return effects

        # get the rules for each step

        steps_rx = r'([0-9].\s[a-zA-Z0-9\s&]+.)\s?([0-9].\s[a-zA-Z0-9\s&]+.)?\s?([0-9].\s[a-zA-Z0-9\s&]+.)?\s?([0-9].\s[a-zA-Z0-9\s&]+.)?'
        value_rx = r'[0-9].\s([a-zA-Z0-9\s&]+).'

        steps_ls = re.match(steps_rx, p_card_m.Rules)
        values = []

        for fStep in steps_ls.groups():
            if fStep:
                match = re.match(value_rx, fStep)
                value = match.groups()[0].lower()
                values.append(value)

        # get which position is playing the card

        position = 'attacker'
        opposite = 'defender'
        if 'defend' in values[0]:
            position = 'defender'
            opposite = 'attacker'


        # add the effects to the effect data structure

        attack_rx = r'attack for ([0-9]+) pd\s?&?\s?([a-z\s]+)?'
        selfDmg_rx = r'you lose ([0-9]) lp'
        extraAtt_rx = r'may attack ([a-z0-9\s-]+)'
        defend_rx = r'defend ([0-9]) pd'
        magicDmg = r'deal ([0-9]) md to opponent'

        heal_rx = r'heal ([0-9]) lp'
        oppHeal_rx = r'opponent heals ([0-9]) LP'
        selfDraw = r'draw ([0-9]) card'
        oppDiscard = r'opponent discards ([0-9]) card\s?([a-z\s]+)?'
        selfBlock = r'you can not ([a-z\s]+) on the next turn'


        for value in values:


            match = re.match(attack_rx, value)
            if match:
                amount = match.groups()[0]
                clause = match.groups()[1]
                effects['defender'].append({'type': 'damage', 'amount': int(amount), 'clause': clause})
                continue

            match = re.match(selfDmg_rx, value)
            if match:
                amount = match.groups()[0]
                effects['attacker'].append({'type': 'damage', 'amount': int(amount)})
                continue

            match = re.match(extraAtt_rx, value)
            if match:
                clause = match.groups()[0]
                effects['attacker'].append({'type': 'extraAttack', 'clause': clause})
                continue

            match = re.match(defend_rx, value)
            if match:
                amount = match.groups()[0]
                effects['defender'].append({'type': 'defend', 'amount': int(amount)})
                continue

            match = re.match(magicDmg, value)
            if match:
                amount = match.groups()[0]
                effects['defender'].append({'type': 'damage', 'amount': int(amount), 'clause': "MD"})
                continue



            match = re.match(heal_rx, value)
            if match:
                amount = match.groups()[0]
                effects[position].append({'type': 'heal', 'amount': int(amount)})
                continue

            match = re.match(oppHeal_rx, value)
            if match:
                amount = match.groups()[0]
                effects[opposite].append({'type': 'heal', 'amount': int(amount)})
                continue

            match = re.match(selfDraw, value)
            if match:
                amount = match.groups()[0]
                effects[position].append({'type': 'draw', 'amount': int(amount)})
                continue

            match = re.match(oppDiscard, value)
            if match:
                amount = match.groups()[0]
                clause = match.groups()[1]
                effects[opposite].append({'type': 'discard', 'amount': int(amount), 'clause': clause})
                continue

            match = re.match(selfBlock, value)
            if match:
                clause = match.groups()[0]
                effects[position].append({'type': 'block', 'clause': clause})
                continue



            effects['attacker'].append({'type': 'unknown', 'clause': value})

        #CU.prog_lg.debug(effects)

        return effects


    @staticmethod
    def GetCardReport():
        cards_mdl = Card.objects.all()
        card_dict = []

        steps_rx = r'([0-9].\s[a-zA-Z0-9\s&-]+.)\s?([0-9].\s[a-zA-Z0-9\s&-]+.)?\s?([0-9].\s[a-zA-Z0-9\s&-]+.)?\s?([0-9].\s[a-zA-Z0-9\s&-]+.)?'
        value_rx = r'[0-9].\s([a-zA-Z0-9\s&-]+).'

        for card_m in cards_mdl:

            newCard = OrderedDict()
            newCard['name'] = card_m.Name
            newCard['kingdom'] = card_m.KingdomFK.Name
            newCard['type'] = card_m.Type

            steps_ls = re.match(steps_rx, card_m.Rules)

            #CU.prog_lg.debug(steps_ls.groups())

            if steps_ls and steps_ls.groups()[0]:
                rawStep = steps_ls.groups()[0]
                match = re.match(value_rx, rawStep)
                newCard['step1'] = match.groups()[0]
            else:
                newCard['step1'] = ""
            
            if steps_ls and steps_ls.groups()[1]:
                rawStep = steps_ls.groups()[1]
                match = re.match(value_rx, rawStep)
                newCard['step2'] = match.groups()[0]
            else:
                newCard['step2'] = ""
            
            if steps_ls and steps_ls.groups()[2]:
                rawStep = steps_ls.groups()[2]
                match = re.match(value_rx, rawStep)
                newCard['step3'] = match.groups()[0]
            else:
                newCard['step3'] = ""
            
            if steps_ls and steps_ls.groups()[3]:
                rawStep = steps_ls.groups()[3]
                match = re.match(value_rx, rawStep)
                newCard['step4'] = match.groups()[0]
            else:
                newCard['step4'] = ""

            card_dict.append(newCard)

        return card_dict



class FileSystem(object):    


    @staticmethod
    def GetFilePath(p_kingdom, p_card):
        try:
            card_m = Card.objects.get(KingdomFK__Name=p_kingdom, Name=p_card)
        except:
            return None

        kingdom = card_m.KingdomFK.Name.lower().replace(" ", "").replace("’", "")
        ctype = card_m.Type.lower()
        card = card_m.Name.lower().replace(" ", "").replace("-", "").replace("’", "")

        filePath = "/static/cards/{}_{}_{}.png".format(kingdom, ctype, card)
        return filePath


    @staticmethod
    def GetRosterPath(p_kingdom):
        kingdom = p_kingdom.lower().replace(" ", "").replace("’", "");
        filePath = "/static/rosters/{}_r_web.png".format(kingdom)
        return filePath


    @staticmethod
    def GetCardBackPath():
        filePath = "/static/cards/0_cardback.png"
        return filePath


    @staticmethod
    def GetNoCardPath():
        filePath = "/static/cards/0_nocard.png"
        return filePath



class Importer(object):    
    
    
    @staticmethod
    def ImportKingdoms():
        
        inputPath = os.path.join(settings.BASE_DIR, "kingdoms/static/data/kingdoms.csv")        
        if not os.path.isfile(inputPath):
            return False
        
        with open(inputPath) as fhandle:
            reader = csv.reader(fhandle)
            next(reader)  # skip header row
            
            for row in reader:
                name = row[0]
                boxset = row[1]
                race = row[2]
                life = row[3]   if row[3]   else 1
                traits = row[4]
                
                if name:
                    kingd_m, created = Kingdom.objects.get_or_create(
                        Name=name, BoxSet=boxset, Race=race, LifePoints=int(life), Traits=traits )
        
        return True
    
    
    @staticmethod
    def ImportCards():
        
        inputPath = os.path.join(settings.BASE_DIR, "kingdoms/static/data/cardlist.csv")        
        if not os.path.isfile(inputPath):
            return False
        
        with open(inputPath) as fhandle:
            reader = csv.reader(fhandle)
            next(reader)  # skip header row
            
            for row in reader:
                name = row[0]
                kingdom = row[1]
                ctype = row[2]
                quant = row[3]
                rules = row[4]
                
                if name:
                    kingdom_m = Kingdom.objects.get(Name=kingdom)
                    card_m, created = Card.objects.get_or_create(
                        Name=name, KingdomFK=kingdom_m, Type=ctype, Quantity=quant, Rules=rules )
        
        return True
    
    
    @staticmethod
    def ClearTables():
        Kingdom.objects.all().delete()
        Card.objects.all().delete()
        return True
    
    
    # report for admin after importing tables
    @staticmethod
    def GetKingdomCards():
        kings = Kingdom.objects.values_list('Name', flat=True).order_by('Name')
        cardCnts = dict( Card.objects.values_list('KingdomFK__Name').annotate(card_cnt=Count('KingdomFK')) )
        
        result_dict = []
        for kgd in kings:
            newCnt = OrderedDict()
            newCnt['kingdom'] = kgd
            newCnt['cards'] = cardCnts.get(kgd)   if cardCnts.get(kgd)   else 0
            result_dict.append(newCnt)
        
        colFmt = {
            'kingdom': 'format_fixline',
            'cards': 'format_center',
        }
        
        ftable = {
            'data': result_dict,
            'colFmt': colFmt
        }
        return ftable



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
END OF FILE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""