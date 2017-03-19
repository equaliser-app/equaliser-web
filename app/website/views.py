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


class Series(View):
    # noinspection PyShadowingBuiltins
    def get(self, request, id):
        return render(request, 'series.html', {
            'user': request.session['session']['user']
             if 'session' in request.session else None,
            'series': api.get(request, '/series/' + id)
        })


class Order(View):
    pass
