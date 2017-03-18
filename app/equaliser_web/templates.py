# -*- coding: utf-8 -*-
"""
Functionality needed for template rendering.
"""
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.contrib import messages

from jinja2 import Environment
from babel.dates import format_date, format_timedelta


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
        'get_messages': messages.get_messages
    })
    env.filters['verbose_date'] = verbose_date
    env.filters['verbose_timedelta'] = verbose_timedelta
    return env


def verbose_date(date):
    """
    Format a date.

    :param date: The date to format.
    :return: The date formatted to, e.g. '21 October 2016'.
    """
    return format_date(date, 'd MMMM YYYY')


def verbose_timedelta(delta):
    """
    Format a time difference.

    :param delta: The delta to format.
    :return: The delta with direction, e.g. '7 seconds ago'.
    """
    return format_timedelta(delta, add_direction=True, locale='en_GB')
