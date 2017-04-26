# -*- coding: utf-8 -*-
"""
WSGI config for equaliser web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

# Calculate the paths based on the location of the WSGI script.
APACHE_CONFIGURATION = os.path.dirname(__file__)
PROJECT = os.path.dirname(APACHE_CONFIGURATION)
WORKSPACE = os.path.dirname(PROJECT)
sys.path.append(WORKSPACE)
sys.path.append(PROJECT)

# We use the official settings file for production.
os.environ['DJANGO_SETTINGS_MODULE'] = 'equaliser_web.settings'

# Find the wsgi application.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
