# -*- coding: utf-8 -*-
"""
Functionality needed for template rendering.
"""
from __future__ import unicode_literals
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.contrib import messages

from website import api
from jinja2 import Environment, escape
from babel.dates import format_datetime, format_timedelta
import datetime
import re


def environment(**options):
    """
    Create a context for rendering templates.
    This is called by Django.

    :param options: Additional options.
    :return: The Jinja2 context.
    """
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        'get_messages': messages.get_messages,
        'api': api.ENDPOINT_BASE
    })
    env.filters['key'] = key
    env.filters['nl2br'] = nl2br
    env.filters['to_datetime'] = _to_datetime
    env.filters['verbose_date'] = verbose_date
    env.filters['verbose_timedelta'] = verbose_timedelta
    env.filters['unix_timestamp_weekday_day'] = unix_timestamp_weekday_day
    env.filters['unix_timestamp_day_month'] = unix_timestamp_day_month
    env.filters['unix_timestamp_time_24hr'] = unix_timestamp_time_24hr
    env.filters['format_unix_timestamp'] = format_unix_timestamp
    return env


def _ordinal(day):
    return 'th' if 11 <= day <= 13 else {
        1: 'st',
        2: 'nd',
        3: 'rd'}.get(day % 10, 'th')


def _ordinal_strftime(format_, date):
    return date.strftime(format_) \
        .replace('{S}', '{0}{1}'.format(date.day, _ordinal(date.day)))


def _to_datetime(unix_timestamp):
    return datetime.datetime.fromtimestamp(unix_timestamp)  # TODO timezone?


def key(dict_, key_):
    return dict_[key_]


def nl2br(value):
    matches = re.compile(r'(?:\r\n|\r|\n){2,}').split(escape(value))
    paras = ['<p>{0}</p>'.format(p.strip().replace('\n', '<br>\n'))
             for p in matches]
    return ''.join(paras)


def verbose_date(date):
    """
    Format a date.

    :param date: The date to format.
    :return: The date formatted to, e.g. '21st October 2016'.
    """
    return _ordinal_strftime('{S} %B %Y', date)


# unix timestamp -> Friday 10th
def unix_timestamp_weekday_day(seconds):
    return _ordinal_strftime('%A {S}', _to_datetime(seconds))


# unix timestamp -> 27th June
def unix_timestamp_day_month(seconds):
    return _ordinal_strftime('{S} %B', _to_datetime(seconds))


# unix timestamp -> 19:00
def unix_timestamp_time_24hr(seconds):
    return _ordinal_strftime('%H:%M', _to_datetime(seconds))


def format_unix_timestamp(seconds):
    return format_datetime(_to_datetime(seconds), 'yyyy-MM-dd HH:mm:ss.SSS')


def verbose_timedelta(delta):
    """
    Format a time difference.

    :param delta: The delta to format.
    :return: The delta with direction, e.g. '7 seconds ago'.
    """
    return format_timedelta(delta, add_direction=True, locale='en_GB')
