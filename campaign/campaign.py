"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CAMPAIGN/CAMPAIGN.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import random
import time
import json         
import datetime 
import pytz
from collections import OrderedDict
from threading import Timer
from channels import Group

from django.db import models
# from django.db.models import Count, F, Q 
from django.utils import timezone
import django.contrib.auth.models as AM

import common.utility as CU
import kingdoms.kingdoms as KK
import members.models.tables as MT


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
MODEL CLASSES
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class PlayerInGame(models.Model):
    UserFK = models.ForeignKey(AM.User)
    RosterFK = models.ForeignKey(MT.UserDeck, null=True)

    Deck = models.CharField(max_length=1000, default="[]")
    Hand = models.CharField(max_length=1000, default="[]")
    Discard = models.CharField(max_length=1000, default="[]")
    Power = models.CharField(max_length=20, default="")

    LifePnts = models.IntegerField(null=True)
    Status = models.CharField(max_length=100, default="[]")     # {'type': mytype, 'value': myvalue}


class LiveGame(models.Model):
    Player1FK = models.ForeignKey(PlayerInGame, related_name='player_one')
    Player2FK = models.ForeignKey(PlayerInGame, related_name='player_two')
    Stage = models.CharField(max_length=20, null=True)
    CreateDate = models.DateTimeField(default=timezone.now)

    Round = models.IntegerField(default=1)
    PlayerTurn = models.IntegerField(default=0)                             # 1 = player1, 2 = player2
    Phase = models.CharField(max_length=10, default="setup")
    FirstPlayer = models.IntegerField(default=0)                            # 1 = player1, 2 = player2
    PhaseStart = models.DateTimeField(default=timezone.now)


class Progress(models.Model):
    UserFK = models.OneToOneField(AM.User)
    NextStage = models.CharField(max_length=20, default='stage 1')



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
LOGIC CLASSES
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


WORLD_USER = "World of Era"
CAMPAIGN_TIMERS = {}        # timer = ('cg_username': Timer)
MAINT_DURATION = 10
BATTLE_DURATION = 20
ENEMY_DURATION = 5



class Manager(object):
    

    @staticmethod
    def StartGame(p_user_m, p_stage, p_deck):

        exists = LiveGame.objects.filter(Player1FK__UserFK=p_user_m)
        if exists: 
            return False


        # create the user's roster  

        deck_m = MT.UserDeck.objects.get(UserFK=p_user_m, KingdomFK__Name=p_deck)
        life = KK.Kingdom.objects.get(Name=p_deck).LifePoints

        deck_ls = KK.Reporter.ShuffleDeck(p_deck, None)
        hand_ls = []
        for d in range(1, 5):
            hand_ls.append(deck_ls.pop(0))

        player1_m, crtd = PlayerInGame.objects.get_or_create(
                UserFK=p_user_m, RosterFK=deck_m,
                Deck=json.dumps(deck_ls), Hand=json.dumps(hand_ls), 
                Power='', LifePnts=life)


        # create the enemy's roster  

        enemy_m = AM.User.objects.get(username=WORLD_USER)
        kingdoms = KK.Reporter.GetKingdoms()
        enemyKgdm = random.choice(kingdoms)
        enemyKgdm_m = KK.Kingdom.objects.get(Name=enemyKgdm)
        powerCards = '[]'

        enemyRoster_m, crtd = MT.UserDeck.objects.get_or_create(
            UserFK=enemy_m, KingdomFK=enemyKgdm_m, PowerCards=powerCards)
        life = KK.Kingdom.objects.get(Name=enemyKgdm).LifePoints

        deck_ls = KK.Reporter.ShuffleDeck(enemyKgdm, None)
        hand_ls = []
        for d in range(1, 5):
            hand_ls.append(deck_ls.pop(0))

        player2_m, crtd = PlayerInGame.objects.get_or_create(
                UserFK=enemy_m, RosterFK=enemyRoster_m,
                Deck=json.dumps(deck_ls), Hand=json.dumps(hand_ls), 
                Power='', LifePnts= life)

        # create the game

        firstPl = 2 #random.randint(1, 2)

        game_m, crtd = LiveGame.objects.get_or_create(
            Player1FK=player1_m, Player2FK=player2_m, 
            Stage=p_stage, FirstPlayer=firstPl)
        
        # start the phases timer
        # the user must connect to this group in the ws_add handler

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)
        newTimer = Timer(2, GameEngine.MoveToFirstTurn, [game_m.id])
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()

        return crtd


    @staticmethod
    def StartMovie(p_user_m, p_stage, p_deck):

        exists = LiveGame.objects.filter(Player1FK__UserFK=p_user_m)
        if exists: 
            return False


        # create the user's roster  

        deck_m = MT.UserDeck.objects.get(UserFK=p_user_m, KingdomFK__Name=p_deck)
        life = KK.Kingdom.objects.get(Name=p_deck).LifePoints

        deck_ls = KK.Reporter.ShuffleDeck(p_deck, None)
        hand_ls = []
        for d in range(1, 5):
            hand_ls.append(deck_ls.pop(0))

        player1_m, crtd = PlayerInGame.objects.get_or_create(
                UserFK=p_user_m, RosterFK=deck_m,
                Deck=json.dumps(deck_ls), Hand=json.dumps(hand_ls), 
                Power='', LifePnts= life)


        # create the enemy's roster  

        enemy_m = AM.User.objects.get(username=WORLD_USER)
        kingdoms = KK.Reporter.GetKingdoms()
        enemyKgdm = "Ak Shabakk" 
        enemyKgdm_m = KK.Kingdom.objects.get(Name=enemyKgdm)
        powerCards = '[]'

        enemyRoster_m, crtd = MT.UserDeck.objects.get_or_create(
            UserFK=enemy_m, KingdomFK=enemyKgdm_m, PowerCards=powerCards)
        life = KK.Kingdom.objects.get(Name=enemyKgdm).LifePoints

        deck_ls = KK.Reporter.ShuffleDeck(enemyKgdm, None)
        hand_ls = []
        for d in range(1, 5):
            hand_ls.append(deck_ls.pop(0))

        player2_m, crtd = PlayerInGame.objects.get_or_create(
                UserFK=enemy_m, RosterFK=enemyRoster_m,
                Deck=json.dumps(deck_ls), Hand=json.dumps(hand_ls), 
                Power='', LifePnts= life)

        # create the game

        firstPl = 1 

        game_m, crtd = LiveGame.objects.get_or_create(
            Player1FK=player1_m, Player2FK=player2_m, 
            Stage=p_stage, FirstPlayer=firstPl)
        
        # start the phases timer
        # the user must connect to this group in the ws_add handler

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)
        newTimer = Timer(2, GameEngine.MoveToFirstTurn, [game_m.id])
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()

        return crtd


    @staticmethod
    def DeleteGame(p_user_m):
        
        game_mdl = LiveGame.objects.filter(Player1FK__UserFK=p_user_m)
        for game_m in game_mdl:
            game_m.Player1FK.delete()
            game_m.Player2FK.delete()
            game_m.delete();

        try:
            group = Manager.GetGroupName(p_user_m.username)
            cTimer = CAMPAIGN_TIMERS[group]
            cTimer.cancel()
            CAMPAIGN_TIMERS.pop(group, None)
        except:
            CU.excp_lg.warning('deleted game\'s timer not found')

        return True


    @staticmethod
    def GetGameDX(p_user_m):
        try:
            game_m = LiveGame.objects.get(Player1FK__UserFK=p_user_m)
        except: 
            game_m = None
            return {}

        # user's data 

        plig_m = game_m.Player1FK

        kingdom_m = plig_m.RosterFK.KingdomFK
        handRaw = json.loads(plig_m.Hand)
        hand_dt = []
        for card in handRaw:
            card_dt = OrderedDict()
            card_dt['name'] = card
            card_dt['cType'] = KK.Card.objects.get(KingdomFK=kingdom_m, Name=card).Type
            card_dt['file'] = KK.FileSystem.GetFilePath(kingdom_m.Name, card)
            hand_dt.append(card_dt)

        discard_ls = json.loads(plig_m.Discard)
        if len(discard_ls) == 0:
            discardPath = KK.FileSystem.GetNoCardPath()
        else:
            discardPath = KK.FileSystem.GetFilePath(kingdom_m.Name, discard_ls[0])

        plig1_dx = OrderedDict()
        plig1_dx['user'] = plig_m.UserFK.username
        plig1_dx['kingdom'] = kingdom_m.Name
        plig1_dx['maxlp'] = kingdom_m.LifePoints
        plig1_dx['currlp'] = plig_m.LifePnts
        plig1_dx['deckCnt'] = len(json.loads(plig_m.Deck))
        plig1_dx['discardCnt'] = len(discard_ls)
        plig1_dx['discardPath'] = discardPath
        plig1_dx['power'] = plig_m.Power
        plig1_dx['hand'] = hand_dt
        plig1_dx['roster_im'] = KK.FileSystem.GetRosterPath(kingdom_m.Name)


        # enemy's data is masked

        plig_m = game_m.Player2FK

        kingdom_m = plig_m.RosterFK.KingdomFK
        handRaw = json.loads(plig_m.Hand)
        hand_dt = []
        for card in handRaw:
            card_dt = OrderedDict()
            card_dt['name'] = "Secret"
            card_dt['cType'] = "N"
            card_dt['file'] = KK.FileSystem.GetCardBackPath()
            hand_dt.append(card_dt)

        discard_ls = json.loads(plig_m.Discard)
        if len(discard_ls) == 0:
            discardPath = KK.FileSystem.GetNoCardPath()
        else:
            discardPath = KK.FileSystem.GetFilePath(kingdom_m.Name, discard_ls[0])

        plig2_dx = OrderedDict()
        plig2_dx['user'] = plig_m.UserFK.username
        plig2_dx['kingdom'] = kingdom_m.Name
        plig2_dx['maxlp'] = kingdom_m.LifePoints
        plig2_dx['currlp'] = plig_m.LifePnts
        plig2_dx['deckCnt'] = len(json.loads(plig_m.Deck))
        plig2_dx['discardCnt'] = len(discard_ls)
        plig2_dx['discardPath'] = discardPath
        plig2_dx['power'] = plig_m.Power
        plig2_dx['hand'] = hand_dt
        plig2_dx['roster_im'] = KK.FileSystem.GetRosterPath(kingdom_m.Name)


        # general game data

        firstPl = plig1_dx['user']   if game_m.FirstPlayer == 1   else plig2_dx['user'] 
        utcnow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        remainDuration = 10 - (utcnow - game_m.PhaseStart).total_seconds()

        game_dx = OrderedDict()
        game_dx['player1'] = plig1_dx
        game_dx['player2'] = plig2_dx
        game_dx['round'] = game_m.Round
        game_dx['playerTurn'] = game_m.PlayerTurn
        game_dx['phase'] = game_m.Phase
        game_dx['firstPl'] = firstPl
        game_dx['remainDuration'] = remainDuration

        return game_dx


    @staticmethod
    def GetGroupName(p_user):
        group = p_user #.replace(" ", "")
        return "cg_{}".format(group)



    @staticmethod
    def CreateCampaignUser():
                
        try:
            exist_m = AM.User.objects.get(username=WORLD_USER)
        except Exception as ex:
            exist_m = None
        
        if exist_m:
            return False
        
        # create user, profile and verify email
        
        email = "campaign@eraboardgames.com"
        newUser = AM.User.objects.create_user(WORLD_USER, email, '9j7g5f3m1z')
        
        newUser.is_superuser = True
        newUser.is_staff = True
        newUser.save()
        
        prof_m = MT.Profile.objects.get(UserFK=newUser)
        prof_m.Country = "United States"
        prof_m.TimeZone = "America/New_York"
        prof_m.save()
        
        import allauth.account.models as LM
        emdd_m, crtd = LM.EmailAddress.objects.get_or_create(
            user=newUser, email=email, verified=True, primary=True)
        
        return True


    @staticmethod
    def CampaignRoster(p_user_m, p_quant):


        return 


    @staticmethod
    def GetProgress(p_user_m):
        if p_user_m.is_authenticated():
            prog_m = Progress.objects.get(UserFK=p_user_m)
            progress = prog_m.NextStage
        else:
            progress = ''
        
        return progress



class GameEngine(object):
    

    @staticmethod
    def MoveToFirstTurn(p_gameId):
        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        CU.prog_lg.debug(game_m.Phase)

        oldPhase = "setup"
        nextPlayer = game_m.FirstPlayer
        thisPhase = "draw"
        nextRound = 1
        remainDuration = MAINT_DURATION

        game_m.PlayerTurn = nextPlayer
        game_m.Phase = thisPhase
        game_m.Round = nextRound
        game_m.save()

        if game_m.PlayerTurn == 1:
            newTimer = Timer(remainDuration, GameEngine.NextPlayerPhase, [p_gameId])
        else:
            newTimer = Timer(ENEMY_DURATION, EnemyTurn.EnemyDraw, [p_gameId])

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()

        data = {
            'round': nextRound,
            'playerTurn': nextPlayer,
            'phase': thisPhase,
            'oldPhase': oldPhase,
            'remainDuration': remainDuration,
        }
        chanInfo = {
            'type': 'NEXT_PHASE',
            'data': data,
        }
        Group(group).send({'text': json.dumps(chanInfo)})


    # advance to the next phase or turn
    # designed for users, enemy needs a different event loop
    @staticmethod
    def NextPlayerPhase(p_gameId):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        CU.prog_lg.debug(game_m.Phase)

        # get new generic member values

        oldPhase = game_m.Phase
        thisPhase = ""
        nextPlayer = game_m.PlayerTurn 
        nextRound = game_m.Round

        chanInfo = {
            'type': 'NEXT_PHASE',
            'data': {
                'playerTurn': nextPlayer,
                'round': nextRound,
                'oldPhase': oldPhase,
            }
        }

        # add to chan-info any customizations

        if game_m.Phase == "draw":     
            thisPhase = "attack"
            remainDuration = BATTLE_DURATION

            drawRes = GameEngine.DrawFromDeck(game_m, game_m.PlayerTurn, 1)
            chanInfo['type'] = 'DRAW_NEXT'
            chanInfo['data'] = { **chanInfo['data'], **drawRes }


        elif game_m.Phase == "attack" or game_m.Phase == "resolve":     
            thisPhase = "spell"
            remainDuration = BATTLE_DURATION

        elif game_m.Phase == "spell":     
            thisPhase = "discard"
            remainDuration = MAINT_DURATION

        elif game_m.Phase == "discard": 
            thisPhase = "draw"               
            remainDuration = MAINT_DURATION

            if game_m.PlayerTurn == 1: 
                nextPlayer = 2
                if game_m.FirstPlayer == 2:
                    nextRound = game_m.Round +1

            elif game_m.PlayerTurn == 2:
                nextPlayer = 1
                if game_m.FirstPlayer == 1:
                    nextRound = game_m.Round +1

            chanInfo['data']['round'] = nextRound
            chanInfo['data']['playerTurn'] = nextPlayer

        
        # update the game model and client info 
        # the group is added to in the ws_add handler

        game_m.Round = nextRound
        game_m.PlayerTurn = nextPlayer
        game_m.Phase = thisPhase
        game_m.save()

        chanInfo['data']['phase'] = thisPhase
        chanInfo['data']['remainDuration'] = remainDuration


        # create timer for next phase 

        if game_m.Round >= 50:
            return

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)

        if game_m.PlayerTurn == 1:
            newTimer = Timer(remainDuration, GameEngine.NextPlayerPhase, [p_gameId])
            CAMPAIGN_TIMERS[group] = newTimer
            newTimer.start()

        else:
            newTimer = Timer(ENEMY_DURATION, EnemyTurn.EnemyDraw, [p_gameId])
            newTimer.start()

        #newTimer.setName( "P{} {}".format(nextPlayer, thisPhase) )
        #CU.prog_lg.debug("{}, A: {}".format(newTimer.getName(), newTimer.is_alive()))

        Group(group).send({'text': json.dumps(chanInfo)})



    # draw from the parameter game and save the new deck and hand
    @staticmethod
    def DrawFromDeck(p_game_m, p_player, p_quant):

        # move cards from deck to hand in database

        if p_player == 1:
            plig_m = p_game_m.Player1FK
        else:
            plig_m = p_game_m.Player2FK

        deck_ls = json.loads(plig_m.Deck)
        hand_ls = json.loads(plig_m.Hand)

        newCard_dict = []
        for c in range(0, p_quant):
            newCard = deck_ls.pop(0)
            hand_ls.insert(0, newCard)
            new_dx = {'card': newCard, 'path': '', 'type': ''}
            newCard_dict.insert(0, new_dx)

        plig_m.Deck = json.dumps(deck_ls)
        plig_m.Hand = json.dumps(hand_ls)

        plig_m.save()

        # create data to play with the new cards

        kingdom_m = plig_m.RosterFK.KingdomFK

        for new_dx in newCard_dict:
            if p_player == 1:
                new_dx['type'] = KK.Card.objects.get(KingdomFK=kingdom_m, Name=newCard).Type
                new_dx['path'] = KK.FileSystem.GetFilePath(kingdom_m.Name, new_dx['card'])
            else:
                new_dx['type'] = "N"
                new_dx['path'] = KK.FileSystem.GetCardBackPath()

        data = {
            'deck': deck_ls,
            'hand': hand_ls,
            'newDict': newCard_dict,
        }
        return data


    # draw from the parameter game and save the new deck and hand
    @staticmethod
    def HandToDiscard(p_game_m, p_player, p_card):

        if not p_card:
            return {'handPos': -1, 'playPath': "", 'discardCnt': -1}

        if p_player == 1:
            plig_m = p_game_m.Player1FK
        else:
            plig_m = p_game_m.Player2FK

        hand_ls = json.loads(plig_m.Hand)
        discard_ls = json.loads(plig_m.Discard)

        handPos = -1
        for c in range(0, len(hand_ls)):
            if hand_ls[c] == p_card:
                handPos = c
                break

        hand_ls.remove(p_card)
        discard_ls = [p_card] + discard_ls         # insert at 0 

        plig_m.Hand = json.dumps(hand_ls)
        plig_m.Discard = json.dumps(discard_ls)
        plig_m.save()

        data = {
            'handPos': handPos,
            'playPath': KK.FileSystem.GetFilePath(plig_m.RosterFK.KingdomFK.Name, p_card),
            'discardCnt': len(discard_ls),
        }
        return data


    # resolve an attack or a spell 
    @staticmethod
    def BattleResolution(p_gameId, p_attackCard_m, p_defenseCard_m):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        if game_m.PlayerTurn == 1:
            attackPlig_m = game_m.Player1FK
            defensePlig_m = game_m.Player2FK

        else:
            attackPlig_m = game_m.Player2FK
            defensePlig_m = game_m.Player1FK


        # apply effects to both players

        total_fx = GameEngine.TotalEffects(game_m, p_attackCard_m, p_defenseCard_m)

        CU.prog_lg.debug(game_m.Phase)

        oldLifeAtt = attackPlig_m.LifePnts
        oldLifeDef = defensePlig_m.LifePnts

        attackPlig_m.LifePnts -= total_fx['attacker'][0]['total']
        defensePlig_m.LifePnts -= total_fx['defender'][0]['total']


        attackPlig_m.save()
        defensePlig_m.save()


        # set timer for upcoming phase 

        resolveDuration = 4      # display just the resolution box
        resolveDuration += 2     # count down LP
        resolveDuration += 2     # cleanup time
        remainDuration = 0

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)

        if game_m.PlayerTurn == 1:
            newTimer = Timer(resolveDuration, GameEngine.NextPlayerPhase, [game_m.id])
            CAMPAIGN_TIMERS[group] = newTimer
        else:
            newTimer = Timer(resolveDuration, EnemyTurn.NextEnemyPhase, [p_gameId])

        newTimer.start()


        # send data to client 

        data = {
            'attName': attackPlig_m.UserFK.username,
            'defName': defensePlig_m.UserFK.username,
            'totalEffects': total_fx,

            'oldLifeAtt': oldLifeAtt,
            'oldLifeDef': oldLifeDef,
            'newLifeAtt': int(attackPlig_m.LifePnts),
            'newLifeDef': int(defensePlig_m.LifePnts),

            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
            'oldPhase': game_m.Phase,
            'remainDuration': remainDuration,
        }

        chanInfo = {
            'type': 'BATTLE_RESOLVE',
            'data': data,
        }

        Group(group).send({'text': json.dumps(chanInfo)})
        return 


    # helper for BattleResolution
    @staticmethod
    def TotalEffects(p_game_m, p_attackCard_m, p_defenseCard_m):

        attack_fx = KK.Reporter.GetCardEffects(p_attackCard_m)
        defense_fx = KK.Reporter.GetCardEffects(p_defenseCard_m)

        # kingdoms.effects = { 'attacker': [], 'defender': [] }


        if p_game_m.PlayerTurn == 1:
            attackPlig_m = p_game_m.Player1FK
            defensePlig_m = p_game_m.Player2FK

        else:
            attackPlig_m = p_game_m.Player2FK
            defensePlig_m = p_game_m.Player1FK



        total_fx = {
            'defender': [{ 'type': 'damage', 'total': 0 }, ],
            'attacker': [{ 'type': 'damage', 'total': 0 }, ],
        }


        # process attack card effects

        for efx in attack_fx['defender']:

            if efx['type'] == 'damage':
                total_fx['defender'][0]['attack'] = efx['amount']
                total_fx['defender'][0]['total'] += efx['amount']
                if 'clause' in efx:
                    total_fx['defender'][0]['clause'] = efx['clause']

            else:
                total_fx['defender'].append(efx)


        for efx in attack_fx['attacker']:

            if efx['type'] == 'damage':
                total_fx['attacker'][0]['attack'] = efx['amount']
                total_fx['attacker'][0]['total'] += efx['amount']

            else:
                total_fx['attacker'].append(efx)



        # process defense card effects

        for efx in defense_fx['defender']:

            if efx['type'] == 'defend':
                total_fx['defender'][0]['defend'] = efx['amount']

            else:
                total_fx['defender'].append(efx)

                

        for efx in defense_fx['attacker']:

            if efx['type'] == 'damage':
                total_fx['attacker'][0]['counter'] = efx['amount']
                total_fx['attacker'][0]['total'] += efx['amount']

            else:
                total_fx['attacker'].append(efx)



        return total_fx



class UserTurn(object):


    @staticmethod
    def UserSkip(p_user_m):

        try:
            game_m = LiveGame.objects.get(Player1FK__UserFK=p_user_m)
        except:
            return False

        # go to next phase
        
        oldPhase = game_m.Phase

        if game_m.Phase == "attack":     
            thisPhase = "spell"
            remainDuration = BATTLE_DURATION

        elif game_m.Phase == "spell":     
            thisPhase = "discard"
            remainDuration = MAINT_DURATION

        game_m.Phase = thisPhase
        game_m.save()

        group = Manager.GetGroupName(p_user_m.username)
        currTimer = CAMPAIGN_TIMERS[group]
        currTimer.cancel()

        newTimer = Timer(remainDuration, GameEngine.NextPlayerPhase, [game_m.id])
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()

        # return next phase data

        data = {
            'playerTurn': game_m.PlayerTurn,
            'phase': thisPhase,
            'oldPhase': oldPhase,
            'remainDuration': remainDuration,
        }
        return data


    @staticmethod
    def UserDraw(p_user_m):

        # draw and save results to model

        try:
            game_m = LiveGame.objects.get(Player1FK__UserFK=p_user_m)
        except:
            return False

        drawRes = GameEngine.DrawFromDeck(game_m, 1, 1)

        # go to next phase

        thisPhase = "attack"
        oldPhase = "draw"
        remainDuration = BATTLE_DURATION

        game_m.Phase = thisPhase
        game_m.save()

        group = Manager.GetGroupName(p_user_m.username)
        currTimer = CAMPAIGN_TIMERS[group]
        currTimer.cancel()

        newTimer = Timer(remainDuration, GameEngine.NextPlayerPhase, [game_m.id])
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()

        # return draw and phase data

        data = {
            'deck': len(drawRes['deck']),
            'hand': drawRes['hand'],
            'newDict': drawRes['newDict'],

            'playerTurn': game_m.PlayerTurn,
            'phase': thisPhase,
            'oldPhase': oldPhase,
            'remainDuration': remainDuration,
        }
        return data
    

    @staticmethod
    def UserAttack(p_user_m, p_card):

        try:
            game_m = LiveGame.objects.get(Player1FK__UserFK=p_user_m)
        except:
            return False

        kingdom_m = game_m.Player1FK.RosterFK.KingdomFK
        card_m = KK.Card.objects.get(KingdomFK=kingdom_m, Name=p_card)

        if card_m.Type != 'A':
            return False

        playCard = GameEngine.HandToDiscard(game_m, 1, card_m.Name)

        # go to next phase

        remainDuration = BATTLE_DURATION

        group = Manager.GetGroupName(p_user_m.username)
        currTimer = CAMPAIGN_TIMERS[group]
        currTimer.cancel()

        newTimer = Timer(ENEMY_DURATION, UserTurn.EnemyDefend, [game_m.id, card_m])
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()

        # return 

        data = {
            'battleCard': card_m.Name,
            'handPos': playCard['handPos'],
            'playPath': playCard['playPath'],
            'discardCnt': playCard['discardCnt'],

            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
            'remainDuration': remainDuration,
        }
        return data


    @staticmethod
    def EnemyDefend(p_gameId, p_attackCard_m):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False


        defenseCard_m = None


        # go to next phase

        remainDuration = 2          # time to play defense card or display "pass"

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)
        currTimer = CAMPAIGN_TIMERS[group]
        currTimer.cancel()

        newTimer = Timer(remainDuration, GameEngine.BattleResolution, [game_m.id, p_attackCard_m, defenseCard_m])      
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()

        # return 

        data = {
            'defenseCard': defenseCard_m.Name   if defenseCard_m   else None,

            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
            'remainDuration': remainDuration,
        }
        chanInfo = {
            'type': 'ENEMY_DEFENSE',
            'data': data,
        }
        Group(group).send({'text': json.dumps(chanInfo)})

        return


    @staticmethod
    def UserSpell(p_user_m, p_card):

        try:
            game_m = LiveGame.objects.get(Player1FK__UserFK=p_user_m)
        except:
            return False

        kingdom_m = game_m.Player1FK.RosterFK.KingdomFK
        card_m = KK.Card.objects.get(KingdomFK=kingdom_m, Name=p_card)

        if card_m.Type != 'S':
            return False

        playCard = GameEngine.HandToDiscard(game_m, 1, card_m.Name)

        # go to next phase

        remainDuration = 2      # display spell card being played

        group = Manager.GetGroupName(p_user_m.username)
        currTimer = CAMPAIGN_TIMERS[group]
        currTimer.cancel()

        newTimer = Timer(remainDuration, GameEngine.BattleResolution, [game_m.id, card_m, None])
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()

        # return 

        data = {
            'battleCard': card_m.Name,
            'handPos': playCard['handPos'],
            'playPath': playCard['playPath'],
            'discardCnt': playCard['discardCnt'],

            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
            'remainDuration': remainDuration,
        }
        return data

 

class EnemyTurn(object):


    @staticmethod
    def EnemyDraw(p_gameId):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        drawRes = GameEngine.DrawFromDeck(game_m, 2, 1)

        # go to next phase

        thisPhase = "attack"
        oldPhase = "draw"
        remainDuration = BATTLE_DURATION

        game_m.Phase = thisPhase
        game_m.save()

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)

        newTimer = Timer(ENEMY_DURATION, EnemyTurn.EnemyAttack, [game_m.id])
        newTimer.start()

        # return draw and phase data

        data = {
            'deck': len(drawRes['deck']),
            'hand': drawRes['hand'],
            'newDict': drawRes['newDict'],

            'playerTurn': game_m.PlayerTurn,
            'phase': thisPhase,
            'oldPhase': oldPhase,
            'remainDuration': remainDuration,
        }

        chanInfo = {
            'type': 'DRAW_NEXT',
            'data': data,
        }

        Group(group).send({'text': json.dumps(chanInfo)})
        return 


    @staticmethod
    def EnemyAttack(p_gameId):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        # remove from hand 

        card_m = EnemyTurn.GetAttackCard(game_m)
        playCard = GameEngine.HandToDiscard(game_m, 2, card_m.Name)

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)

        if not card_m:
            remainDuration = BATTLE_DURATION
            game_m.Phase = "spell"
            game_m.save()

            newTimer = Timer(ENEMY_DURATION, EnemyTurn.EnemySpell, [p_gameId])
            newTimer.start()

        else:
            plig_m = game_m.Player2FK
            status = json.loads(plig_m.Status)
            status.append( {'type': 'attack', 'cardId': card_m.id} )
            plig_m.Status = json.dumps(status)
            plig_m.save()

            remainDuration = BATTLE_DURATION

            newTimer = Timer(remainDuration, EnemyTurn.UserAutoDefend, [p_gameId, card_m])
            CAMPAIGN_TIMERS[group] = newTimer
            newTimer.start()


        data = {
            'battleCard': card_m.Name,
            'handPos': playCard['handPos'],
            'playPath': playCard['playPath'],
            'discardCnt': playCard['discardCnt'],

            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
            'oldPhase': 'attack',
            'remainDuration': remainDuration,
        }

        chanInfo = {
            'type': 'ENEMY_ATTACK',
            'data': data,
        }

        Group(group).send({'text': json.dumps(chanInfo)})
        return 


    # user doesn't respond to enemy attack, so phase automatically progresses
    @staticmethod
    def UserAutoDefend(p_gameId, p_attackCard_m):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        # no defense played, go to resolution

        remainDuration = 2       # time to display 'pass on defense' message

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)

        newTimer = Timer(remainDuration, GameEngine.BattleResolution, [game_m.id, p_attackCard_m, None])      
        newTimer.start()

        # return 

        data = {
            'defenseCard': None,

            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
            'remainDuration': remainDuration,
        }

        chanInfo = {
            'type': 'USER_DEFEND_EXPIRE',
            'data': data,
        }

        Group(group).send({'text': json.dumps(chanInfo)})

        return data


    @staticmethod
    def UserSkipDefend(p_user_m):

        try:
            game_m = LiveGame.objects.get(Player1FK__UserFK=p_user_m)
        except:
            return False

        # no defense played, go to resolution

        plig_m = game_m.Player2FK
        status = json.loads(plig_m.Status)

        for state in status:
            if state['type'] == 'attack':
                attackId = state['cardId']
        attackCard_m = KK.Card.objects.get(id=attackId)

        status[:] = [d for d in status if d.get('type') != 'attack']        # remove the attack from the status
        plig_m.Status = json.dumps(status)
        plig_m.save()

        resolveDuration = 1       # time to ebd defense phase

        group = Manager.GetGroupName(p_user_m.username)
        currTimer = CAMPAIGN_TIMERS[group]
        currTimer.cancel()
 
        newTimer = Timer(resolveDuration, GameEngine.BattleResolution, [game_m.id, attackCard_m, None])      
        newTimer.start()

        # return next phase data

        data = {
            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
        }
        return data


    @staticmethod
    def UserDefend(p_user_m, p_card):

        try:
            game_m = LiveGame.objects.get(Player1FK__UserFK=p_user_m)
        except:
            return False

        plig_m = game_m.Player1FK
        kingdom_m = plig_m.RosterFK.KingdomFK
        card_m = KK.Card.objects.get(KingdomFK=kingdom_m, Name=p_card)

        if card_m.Type != 'D':
            return False



        remainDuration = 0

        # return 

        data = {

            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
            'remainDuration': remainDuration,
        }
        return data


    @staticmethod
    def EnemySpell(p_gameId):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        # do the work of next player phase

        game_m.Phase = 'spell'
        game_m.save()

        # use the AI to get a spell card to play

        card_m = EnemyTurn.GetSpellCard(game_m)
        playCard = GameEngine.HandToDiscard(game_m, 2, card_m.Name)

        # set time for next phase based on if a card is played or not

        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)

        if not card_m:
            remainDuration = MAINT_DURATION

            newTimer = Timer(ENEMY_DURATION, EnemyTurn.EnemyDiscard, [p_gameId])
            newTimer.start()

        else:
            remainDuration = 2          # time enough to play spell

            newTimer = Timer(remainDuration, GameEngine.BattleResolution, [p_gameId, card_m, None])
            CAMPAIGN_TIMERS[group] = newTimer
            newTimer.start()

        # send data as message to client

        data = {
            'battleCard': card_m.Name,
            'handPos': playCard['handPos'],
            'playPath': playCard['playPath'],
            'discardCnt': playCard['discardCnt'],

            'playerTurn': game_m.PlayerTurn,
            'phase': game_m.Phase,
            'oldPhase': 'spell',
            'remainDuration': remainDuration,
        }

        chanInfo = {
            'type': 'ENEMY_SPELL',
            'data': data,
        }

        Group(group).send({'text': json.dumps(chanInfo)})
        return 


    @staticmethod
    def EnemyDiscard(p_gameId):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        # do the work of next player phase

        game_m.Phase = 'discard'
        game_m.save()

        # set the timer for the user's draw phase

        newTimer = Timer(ENEMY_DURATION, GameEngine.NextPlayerPhase, [p_gameId])
        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)
        CAMPAIGN_TIMERS[group] = newTimer
        newTimer.start()


    # proxy function for enemy's battle resolution
    @staticmethod
    def NextEnemyPhase(p_gameId):

        try:
            game_m = LiveGame.objects.get(id=p_gameId)
        except:
            return False

        CU.prog_lg.debug(game_m.Phase)

        # get new generic member values

        nextRound = game_m.Round
        nextPlayer = game_m.PlayerTurn 
        thisPhase = ""
        oldPhase = game_m.Phase

        chanInfo = {
            'type': 'NEXT_PHASE',
            'data': {
                'playerTurn': nextPlayer,
                'round': nextRound,
                'oldPhase': oldPhase,
            }
        }

        # 
        group = Manager.GetGroupName(game_m.Player1FK.UserFK.username)

        if game_m.Phase == "attack":     
            thisPhase = "spell"
            remainDuration = BATTLE_DURATION

            newTimer = Timer(ENEMY_DURATION, EnemyTurn.EnemySpell, [p_gameId])

        elif game_m.Phase == "spell":     
            thisPhase = "discard"
            remainDuration = MAINT_DURATION

            newTimer = Timer(ENEMY_DURATION, EnemyTurn.EnemyDiscard, [p_gameId])


        elif game_m.Phase == "discard": 
            thisPhase = "draw"               
            remainDuration = MAINT_DURATION

            nextPlayer = 1
            if game_m.FirstPlayer == 1:
                nextRound = game_m.Round +1

            chanInfo['data']['round'] = nextRound
            chanInfo['data']['playerTurn'] = nextPlayer


        newTimer.start()
        
        # update the game model and client info 
        # the group is added to in the ws_add handler

        game_m.Round = nextRound
        game_m.PlayerTurn = nextPlayer
        game_m.Phase = thisPhase
        game_m.save()

        chanInfo['data']['phase'] = thisPhase
        chanInfo['data']['remainDuration'] = remainDuration

        Group(group).send({'text': json.dumps(chanInfo)})



    @staticmethod
    def GetAttackCard(p_game_m):
        kingdom_m = p_game_m.Player2FK.RosterFK.KingdomFK
        hand_ls = json.loads(p_game_m.Player2FK.Hand)

        for card in hand_ls:
            card_m = KK.Card.objects.get(KingdomFK=kingdom_m, Name=card)
            if card_m.Type == 'A': 
                break   

        return card_m

  
    @staticmethod
    def GetSpellCard(p_game_m):
        kingdom_m = p_game_m.Player2FK.RosterFK.KingdomFK
        hand_ls = json.loads(p_game_m.Player2FK.Hand)

        for card in hand_ls:
            card_m = KK.Card.objects.get(KingdomFK=kingdom_m, Name=card)
            if card_m.Type == 'S': 
                break   

        return card_m



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SIGNALS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# when a user is created, also create their campaign progress

from django.dispatch import receiver
from django.db.models.signals import post_save
@receiver(post_save, sender=AM.User)
def TriggerProgress(sender, instance, created, **kwargs):
    if created:
        prog_m, crtd = Progress.objects.get_or_create(
            UserFK = instance)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
END FILE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""