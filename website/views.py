# -*- coding: utf-8 -*-
"""
Each class corresponds to a page, and each method a verb on that page. We bind
URLs to views in `urls.py`, and Django takes care of executing the right method,
which returns the page to show to the user. This is the 'V' in MVC.
"""
import logging

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.shortcuts import render
from website import api, forms
from website import models
from website.models import Session

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class Index(View):
    """
    The homepage at /.
    """

    def get(self, request):
        """
        Show the homepage.
        """
        return render(request, 'index.html', {
            'user': request.session['session']['user']
                        if 'session' in request.session else None,
            'showcase': api.get(request, '/series/showcase'),
            'music': api.get(request, '/series/tag/music'),
            'theatre': api.get(request, '/series/tag/theatre'),
            'sports': api.get(request, '/series/tag/sports')
        })


# TODO should not be able to access page if logged in
# noinspection PyMethodMayBeStatic
class Login(View):
    """
    Login form at /login.
    """

    def get(self, request):
        """
        Show the login form.
        """
        if 'session' in request.session:
            return HttpResponseRedirect(reverse('index'))

        return render(request, 'login.html', {
            'showcase': api.get(request, '/series/showcase'),
            'form': forms.LoginForm(request)
        })

    def post(self, request):
        """
        Process a login attempt.
        """
        form = forms.LoginForm(request, request.POST)
        if form.is_valid():
            try:
                form.login()
                return HttpResponseRedirect(reverse('verification'))
            except RuntimeError:
                # login failed
                form.add_error(None, ValidationError('Invalid credentials'))
        return render(request, 'login.html', {
            'showcase': api.get(request, '/series/showcase'),
            'form': form
        })


# TODO only allow if not logged in
# noinspection PyMethodMayBeStatic
class Register(View):
    def get(self, request):
        if 'session' in request.session:
            return HttpResponseRedirect(reverse('index'))

        return render(request, 'register.html', {
            'showcase': api.get(request, '/series/showcase'),
            'form': forms.RegisterForm(request)
        })

    def post(self, request):
        form = forms.RegisterForm(request, request.POST, request.FILES)
        if form.is_valid():
            try:
                form.register()
                return HttpResponseRedirect(reverse('verification'))
            except RuntimeError as e:
                # registration failed
                form.add_error(None, ValidationError(str(e)))
        return render(request, 'register.html', {
            'showcase': api.get(request, '/series/showcase'),
            'form': form
        })


# TODO only allow if we have a request.session['login_token']
# noinspection PyMethodMayBeStatic
class Verification(View):
    """
    2FA form at /login.
    """

    def get(self, request):
        """
        Show the verification form.
        """
        if 'session' in request.session:
            return HttpResponseRedirect(reverse('index'))

        return render(request, 'verification.html', {
            'showcase': api.get(request, '/series/showcase'),
            'form': forms.VerificationForm(request)
        })

    def post(self, request):
        """
        Process a verification attempt.
        """
        form = forms.VerificationForm(request, request.POST)
        if form.is_valid():
            try:
                form.login()
                return HttpResponseRedirect(reverse('index'))
            except RuntimeError:
                # login failed
                form.add_error(None, ValidationError('Invalid code'))
        return render(request, 'verification.html', {
            'showcase': api.get(request, '/series/showcase'),
            'form': form
        })


# noinspection PyMethodMayBeStatic
class Account(View):
    def get(self, request):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        return render(request, 'account.html', {
            'user': request.session['session']['user'],
            'security_events': api.get(request, '/account/security-events'),
            'showcase': api.get(request, '/series/showcase'),
            'form': forms.RegisterForm(request)
        })


# noinspection PyMethodMayBeStatic
class EphemeralToken(View):
    def get(self, request):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        response = api.get_binary(request, '/auth/ephemeral', stream=True)
        return HttpResponse(response.raw.read(), content_type='image/png')


# noinspection PyMethodMayBeStatic
class Series(View):
    # noinspection PyShadowingBuiltins
    def get(self, request, id):
        return render(request, 'series.html', {
            'user': request.session['session']['user']
             if 'session' in request.session else None,
            'series': api.get(request, '/series/' + id)
        })


# noinspection PyMethodMayBeStatic
class Order(View):
    def get(self, request, fixture, tier):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        fixture_json = api.get(request, '/fixtures/' + fixture)

        fixture = int(fixture)
        tier = int(tier)
        logger.debug('Searching for fixture %d and tier %d', fixture, tier)

        tier_ = None
        for sample in fixture_json['tiers']:
            logger.debug('Trying %d', sample['id'])
            if sample['id'] == tier:
                tier_ = sample
                break

        if not tier_:
            return HttpResponseRedirect(reverse('index'))

        return render(request, 'place-order.html', {
            'user': request.session['session']['user'],
            'fixture': fixture_json,
            'tier': tier_
        })

    def post(self, request, fixture, tier):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        logger.debug('Received order POST: fixture: %s, tier: %s, data: %s',
                     fixture, tier, request.POST)
        attendees = request.POST.getlist('attendees[]')
        logger.debug('Attendees: %s', attendees)
        guests = request.POST.getlist('guests[]')
        logger.debug('Guests: %s', attendees)
        fixture_json = api.get(request, '/fixtures/' + fixture)

        fixture = int(fixture)
        tier = int(tier)
        logger.debug('Searching for fixture %d and tier %d', fixture, tier)

        tier_ = None
        for sample in fixture_json['tiers']:
            logger.debug('Trying %d', sample['id'])
            if sample['id'] == tier:
                tier_ = sample
                break

        if not tier_:
            return HttpResponseRedirect(reverse('index'))

        try:
            result = api.post(request, '/group/create', {
                'tierId': tier,
                'attendees': attendees,
                'guests': guests
            })

            logger.debug('Create group result: %s', result)

            return HttpResponseRedirect(
                reverse('group', kwargs={'id': result['group']['id']}))
        except RuntimeError:
            return HttpResponseRedirect(reverse('index'))


# noinspection PyMethodMayBeStatic
class Groups(View):
    def get(self, request):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        session = Session.from_session(request.session)

        groups = api.get(request, '/group/list')
        logger.debug('Received %d groups', len(groups))
        for group in groups:
            # from my perspective
            group['my_status'] = \
                models.user_group_status(group, session.user.username)

        return render(request, 'groups.html', {
            'showcase': api.get(request, '/series/showcase'),
            'user': request.session['session']['user'],
            'groups': groups
        })


# noinspection PyMethodMayBeStatic
class Group(View):
    # noinspection PyShadowingBuiltins
    def get(self, request, id):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        session = Session.from_session(request.session)

        group = api.get(request, '/group/' + id)
        group['my_status'] = models.user_group_status(
            group, session.user.username)

        user_is_leader = group['leader']['username'] == session.user.username
        user_is_payee = False
        user_is_attendee = False

        # TODO this should be done by the api, not us
        for payment_group in group['paymentGroups']:
            payment_group['resolved_status'] = \
                models.payment_group_status(group, payment_group['id'])
            if payment_group['payee']['username'] == session.user.username:
                user_is_payee = True
            for attendee in payment_group['attendees']:
                if attendee['username'] == session.user.username:
                    user_is_attendee = True

        logger.debug('is_leader: %s', user_is_leader)
        logger.debug('is_payee: %s', user_is_payee)
        logger.debug('is_attendee: %s', user_is_attendee)

        return render(request, 'group.html', {
            'showcase': api.get(request, '/series/showcase'),
            'user': request.session['session']['user'],
            'group': group,
            'user_is_leader': user_is_leader,
            'user_is_payee': user_is_payee,
            'user_is_attendee': user_is_attendee
        })


# noinspection PyMethodMayBeStatic,PyShadowingBuiltins
class GroupPay(View):
    def get(self, request, id):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        # TODO validation

        group = api.get(request, '/group/' + id)
        return render(request, 'pay.html', {
            'user': request.session['session']['user'],
            'group': group
        })

    def post(self, request, id):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        group = api.get(request, '/group/' + id)
        try:
            result = api.post(request, '/group/' + id + '/pay', {})
            return HttpResponseRedirect(reverse('group',
                                                kwargs={'id': group['id']}))
        except RuntimeError:
            return HttpResponseRedirect(reverse('groups'))


# noinspection PyMethodMayBeStatic,PyShadowingBuiltins
class GroupTiers(View):
    def get(self, request, id):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        session = Session.from_session(request.session)

        group = api.get(request, '/group/' + id)
        if group['leader']['username'] != session.user.username:
            return HttpResponseRedirect(reverse('index'))

        selected_tiers = group['tiers']
        selected_tier_ids = [tier['id'] for tier in selected_tiers]
        unselected_tiers = [tier for tier in group['fixture']['tiers']
                            if tier['id'] not in selected_tier_ids]
        unselected_tiers = sorted(unselected_tiers, key=lambda e: e['id'])
        logger.debug('Selected tiers: %s', selected_tiers)
        logger.debug('Remaining tiers: %s', unselected_tiers)

        return render(request, 'tier-selection.html', {
            'user': request.session['session']['user'],
            'group': group,
            'selected_tiers': selected_tiers,
            'unselected_tiers': unselected_tiers
        })

    def post(self, request, id):
        if 'session' not in request.session:
            return HttpResponseRedirect(reverse('index'))

        priorities = {field: request.POST[field] for field in request.POST
                      if field != 'csrfmiddlewaretoken'}
        logger.debug('Priorities: %s', priorities)

        try:
            result = api.post(request, '/group/' + id + '/tiers', priorities)
            return HttpResponseRedirect(reverse('group',
                                                kwargs={'id': id}))
        except RuntimeError:
            return HttpResponseRedirect(reverse('groups'))
