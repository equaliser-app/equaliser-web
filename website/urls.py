# -*- coding: utf-8 -*-
"""
URL routing regular expressions. This file binds views to URLs, and defines a
name for each one which can be used to create reverse URLs.
"""
from django.conf.urls import url
from django.views.static import serve

from equaliser_web import settings
from website.views import (Index, Login, Series, Register, Verification,
                           EphemeralToken, Account, Order, Group, Groups,
                           GroupTiers, GroupPay)

urlpatterns = [
    url(r'^$',
        Index.as_view(), name='index'),
    url(r'register$',
        Register.as_view(), name='register'),
    url(r'login$',
        Login.as_view(), name='login'),
    url(r'verification$',
        Verification.as_view(), name='verification'),
    url(r'account$',
        Account.as_view(), name='account'),
    url(r'ephemeral-token$',
        EphemeralToken.as_view(), name='ephemeral-token'),
    # url(r'logout$',
    #     Logout.as_view(), name='logout'),
    url(r'series/(?P<id>[\d]+)$',
        Series.as_view(), name='series'),
    url(r'groups$',
        Groups.as_view(), name='groups'),
    url(r'groups/(?P<id>[\d]+)$',
        Group.as_view(), name='group'),
    url(r'groups/(?P<id>[\d]+)/tiers$',
        GroupTiers.as_view(), name='group-tiers'),
    url(r'groups/(?P<id>[\d]+)/pay$',
        GroupPay.as_view(), name='group-pay'),
    url(r'fixture/(?P<fixture>[\d]+)/tier/(?P<tier>[\d]+)/order$',
        Order.as_view(), name='order'),
    url(r'(?P<path>.*)', serve, {'document_root': settings.STATIC_ROOT})
]