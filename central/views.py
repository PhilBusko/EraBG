"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CENTRAL/VIEWS.py
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

import json

from django.shortcuts import render
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import ensure_csrf_cookie

import common.utility as CU
import kingdoms.kingdoms as KK
import members.models.members as MM


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CENTRAL PAGES
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def landing_page(request):
    context = {
        'topRanks': mark_safe(json.dumps({})),
    }
    return render(request, 'landing_page.html', context)


def headquarters(request):
    userDecks = MM.Decks_Reporter.GetDecksFT(request.user)
    kingdoms = KK.Reporter.GetKingdoms()
    arenaReport = None
    tourneyReport = None
    context = {
        'userDecks': mark_safe(json.dumps(userDecks)),
        'kingdoms': mark_safe(json.dumps(kingdoms)),
    }
    return render(request, 'headquarters.html', context)


@ensure_csrf_cookie
def master(request):
    kingdomCards = KK.Importer.GetKingdomCards()
    context = {
        'kingdomCards': mark_safe(json.dumps(kingdomCards)),
    }
    return render(request, 'data_master.html', context)

