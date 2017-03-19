# -*- coding: utf-8 -*-
"""
Contains the logic needed to present and validate all <form> elements. Each form
is contained within its own class. This is the closest we have to the 'C' in
MVC.
"""
import logging

from django import forms
from django.core.validators import RegexValidator
from django.forms import Form
from django.template.defaultfilters import filesizeformat
from phonenumber_field import formfields

from website import api
from website.models import Session

logger = logging.getLogger(__name__)

_ALPHANUMERIC = alphanumeric = RegexValidator(
    r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')


class RestrictedFileField(forms.FileField):
    """
    A file upload field that constrains both the file type and size that can be
    uploaded.
    """

    KB = 1024
    MB = 1024 * KB

    JPEG = ['image/jpeg']

    def __init__(self, *args, **kwargs):
        """
        Initialise a new file field.

        :param args: Positional arguments.
        :param kwargs: Keyword arguments. `content_types` is optionally a list
                       of allowed MIME types. `max_size` is the largest file
                       size in bytes that can be uploaded.
        """
        self.content_types = kwargs.pop('content_types', None)
        self.max_size = kwargs.pop('max_size', None)
        if self.content_types:
            kwargs['widget'] = forms.FileInput(attrs={
                'accept': ','.join(self.content_types)
            })
        if self.max_size and 'help_text' not in kwargs:
            kwargs['help_text'] = 'Max ' + filesizeformat(self.max_size)

        super(RestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """
        Validate the field contents.

        :param data: Data received by the form.
        :param initial: Defaults.
        :return: The cleaned data.
        """
        cleaned = super(RestrictedFileField, self).clean(data, initial)

        if not self.required:
            return cleaned

        if self.content_types and \
                cleaned.content_type not in self.content_types:
            raise forms.ValidationError('File type not allowed.')

        if self.max_size and cleaned.size > self.max_size:
            raise forms.ValidationError(
                'File size cannot be larger than {0}.'.format(
                    filesizeformat(self.max_size)))

        return cleaned


class LoginForm(Form):

    username = forms.CharField(validators=[_ALPHANUMERIC])
    password = forms.CharField(min_length=6)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def login(self):
        logger.debug('Attempting log in with user %s',
                     self.cleaned_data['username'])
        result = api.post(self.request, '/auth/first', {
            'username': self.cleaned_data['username'],
            'password': self.cleaned_data['password']
        })
        token = result['token']['token']
        logger.debug('Received login token: %s', token)
        self.request.session['login_token'] = token


class VerificationForm(Form):

    code = forms.CharField(min_length=6, max_length=6)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(VerificationForm, self).__init__(*args, **kwargs)

    def login(self):
        logger.debug('Attempting log in with token %s and code %s',
                     self.request.session['login_token'],
                     self.cleaned_data['code'])
        result = api.post(self.request, '/auth/second', {
            'token': self.request.session['login_token'],
            'code': self.cleaned_data['code']
        })
        del self.request.session['login_token']
        session = Session.from_json(result['session'])
        session.to_session(self.request.session)


class RegisterForm(Form):

    forename = forms.CharField()
    surname = forms.CharField()
    email = forms.EmailField()
    phone = formfields.PhoneNumberField(max_length=20)
    photo = RestrictedFileField(max_size=RestrictedFileField.MB * 5,
                                content_types=RestrictedFileField.JPEG)
    username = forms.CharField(min_length=2, validators=[_ALPHANUMERIC])
    password = forms.CharField(min_length=10)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(RegisterForm, self).__init__(*args, **kwargs)

    def register(self):
        phone = str(self.cleaned_data['phone'])
        area_code = phone[3:7]
        subscriber_number = phone[7:]
        photo = self.cleaned_data['photo']
        result = api.post(self.request, '/register', {
            'username': self.cleaned_data['username'],
            'countryId': 1,
            'forename': self.cleaned_data['forename'],
            'surname': self.cleaned_data['surname'],
            'email': self.cleaned_data['email'],
            'areaCode': area_code,
            'subscriberNumber': subscriber_number,
            'password': self.cleaned_data['password']
        }, {
            'photo': (photo.name, photo.file, photo.content_type)
        })
        token = result['token']['token']
        logger.debug('Received login token: %s', token)
        self.request.session['login_token'] = token
