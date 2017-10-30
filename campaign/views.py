"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CAMPAIGN/VIEWS.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import json

from django.shortcuts import render
from django.http import JsonResponse
from django.utils.safestring import mark_safe

import common.utility as CU
import kingdoms.kingdoms as KK
import members.models.members as MM
import campaign.campaign as GG


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CAMPAIGN PAGES
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def campaign(request):

	liveGame = GG.Manager.GetGameDX(request.user)

	if not liveGame:
	    progress = GG.Manager.GetProgress(request.user)
	    world = ["stage 1", "stage 2", "stage 3"]
	    userDecks = MM.Decks_Reporter.GetDecksLS(request.user)

	    context = {
	    	'progress': progress,
	    	'world': world,
	    	'userDecks': mark_safe(json.dumps(list(userDecks))),
	    }
	    return render(request, 'campaign_map.html', context)

	else:
		gameData = GG.Manager.GetGameDX(request.user)
		context = {
			'gameData': mark_safe(json.dumps(gameData)),
            'noCard': KK.FileSystem.GetNoCardPath(),
            'cardBack': KK.FileSystem.GetCardBackPath(),
		}
		return render(request, 'campaign_game.html', context)


def campaign_jx(request, command):
    
    CU.prog_lg.info("ajax command: " + command)
    
    
    if command == 'start_game':
        stage = request.POST.get('stage')        
        deck = request.POST.get('deck')        
        results = GG.Manager.StartGame(request.user, stage, deck)
        return JsonResponse(results, safe=False)
     
    elif command == 'start_movie':
        stage = request.POST.get('stage')        
        deck = request.POST.get('deck')        
        results = GG.Manager.StartMovie(request.user, stage, deck)
        return JsonResponse(results, safe=False)

    elif command == 'delete_game':
        results = GG.Manager.DeleteGame(request.user)
        return JsonResponse(results, safe=False)

    elif command == 'create_user':
        results = GG.Manager.CreateCampaignUser()
        return JsonResponse(results, safe=False)

    elif command == 'delete_decks':
        results = MM.Decks_Editor.DeleteDecks(request.user)
        return JsonResponse(results, safe=False)
    

    elif command == 'draw_next':
        results = GG.UserTurn.UserDraw(request.user)
        return JsonResponse(results, safe=False)

    elif command == 'skip_phase':
        results = GG.UserTurn.UserSkip(request.user)
        return JsonResponse(results, safe=False)
    
    elif command == 'user_attack':
        card = request.POST.get('card')                
        results = GG.UserTurn.UserAttack(request.user, card)
        return JsonResponse(results, safe=False)

    elif command == 'user_spell':
        card = request.POST.get('card')                
        results = GG.UserTurn.UserSpell(request.user, card)
        return JsonResponse(results, safe=False)


    elif command == 'user_skipDefend':
        results = GG.EnemyTurn.UserSkipDefend(request.user)
        return JsonResponse(results, safe=False)

    elif command == 'user_defend':
        card = request.POST.get('card')                
        results = GG.EnemyTurn.UserDefend(request.user, card)
        return JsonResponse(results, safe=False)


    else:
        msg = "command invalid: " + command
        CU.excp_lg.error(msg)
        return JsonResponse(msg, safe=False, status=404)  

