"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
KINGDOMS/VIEWS.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import json
import random

from django.shortcuts import render
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import user_passes_test

import common.utility as CU
import kingdoms.kingdoms as KK


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
REFERENCE 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def kingdoms(request):
    kingdoms = KK.Reporter.GetKingdoms()
    #kingdoms = ['Amniss', 'Dee\'Ench', 'Azzroth', 'Fahanzel', 'Labuluu', 'Qsi Tesan']
    cKingdom = random.choice(kingdoms)
    props = KK.Reporter.GetKingdomProperties(cKingdom)
    deck = KK.Reporter.GetKingdomDeck(cKingdom)
    
    context = {
        'kingdoms': mark_safe(json.dumps(kingdoms)),
        'cKingdom': cKingdom,
        'props': mark_safe(json.dumps(props)),
        'deck': mark_safe(json.dumps(deck)),
    }
    return render(request, 'kingdoms.html', context)


def special_cards(request):
    context = {
        'topRanks': mark_safe(json.dumps({})),
    }
    return render(request, 'special_cards.html', context)


def game_rules(request):
    context = {
        'topRanks': mark_safe(json.dumps({})),
    }
    return render(request, 'game_rules.html', context)


def reference_jx(request, command):
    
    CU.prog_lg.info("ajax command: " + command)
    
    
    if command == 'refresh_kingdom':
        kingdom = request.GET.get('kingdom')        
        props = KK.Reporter.GetKingdomProperties(kingdom)
        deck = KK.Reporter.GetKingdomDeck(kingdom)
        
        results = {
            'props': props,
            'deck': deck,
        }
        return JsonResponse(results, safe=False)
    
    
    else:
        msg = "command invalid: " + command
        CU.excp_lg.error(msg)
        return JsonResponse(msg, safe=False, status=404)  


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DATA MANAGER 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def data_load(request):
    kingdomCards = KK.Importer.GetKingdomCards()
    cardReport = KK.Reporter.GetCardReport()

    context = {
        'kingdomCards': mark_safe(json.dumps(kingdomCards)),
        'cardReport': mark_safe(json.dumps(cardReport)),
    }
    return render(request, 'data_load.html', context)


def manager_jx(request, command):
    
    CU.prog_lg.info("ajax command: " + command)
    
    
    if command == 'import_kingdoms':
        KK.Importer.ImportKingdoms()
        results = KK.Importer.GetKingdomCards()
        return JsonResponse(results, safe=False)
    
    elif command == 'import_cards':
        KK.Importer.ImportCards()
        results = KK.Importer.GetKingdomCards()
        return JsonResponse(results, safe=False)
    
    elif command == 'clear_tables':
        KK.Importer.ClearTables()
        results = KK.Importer.GetKingdomCards()
        return JsonResponse(results, safe=False)
    
    
    else:
        msg = "command invalid: " + command
        CU.excp_lg.error(msg)
        return JsonResponse(msg, safe=False, status=404)  




"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
END OF FILE
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""