# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

try:
    from seahub.settings import SEAPAY_URL
except ImportError:
    SEAPAY_URL = None
    
def to_seapay(request):
    assert SEAPAY_URL is not None, "SEAPAY_URL is not set in settings.py."

    return HttpResponseRedirect(SEAPAY_URL)
    


