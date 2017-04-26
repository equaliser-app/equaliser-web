import logging
import requests

from django.conf import settings
from website.models import Session

logger = logging.getLogger(__name__)

ENDPOINT_BASE = 'http://{0}:{1}'.format(settings.API_HOST, settings.API_PORT)

_REQUESTS_SESSION = None


def get_requests_session():
    global _REQUESTS_SESSION
    if not _REQUESTS_SESSION:
        _REQUESTS_SESSION = requests.session()
    return _REQUESTS_SESSION


def get_kwargs(request, endpoint):
    kwargs = {}
    if 'session' in request.session:
        session = Session.from_session(request.session)
        kwargs['headers'] = {
            'Authorization': session.token
        }
    return kwargs


def get_result(response):
    #logger.debug(response.text)
    json = response.json()
    #logger.debug('Parsed API result: %s', json)
    if not json['success']:
        raise RuntimeError(json['message'])
    return json['result']


def get(request, endpoint, **kwargs):
    """
    Query the Equaliser API

    :param request: The request we are servicing.
    :param endpoint: The endpoint to query.
    :param kwargs:
    :return:
    """
    kw = get_kwargs(request, endpoint)
    kw.update(kwargs)
    logger.debug('Sending GET request to %s with %s', endpoint, kw)

    return get_result(
        get_requests_session().get(ENDPOINT_BASE + endpoint, **kw))


def get_binary(request, endpoint, **kwargs):
    """
    Query the Equaliser API

    :param request: The request we are servicing.
    :param endpoint: The endpoint to query.
    :param kwargs:
    :return:
    """
    kw = get_kwargs(request, endpoint)
    kw.update(kwargs)
    logger.debug('Sending GET request to %s with %s', endpoint, kw)

    return get_requests_session().get(ENDPOINT_BASE + endpoint, **kw)


def post(request, endpoint, attributes, **kwargs):
    """
    Query the Equaliser API

    :param request: The request we are servicing.
    :param endpoint: The endpoint to query.
    :param attributes:
    :param kwargs:
    :return:
    """
    kw = get_kwargs(request, endpoint)
    kw.update(kwargs)
    kw.update({
        'data': attributes
    })
    logger.debug('Sending POST requests to %s with %s', endpoint, kw)
    return get_result(
        get_requests_session().post(ENDPOINT_BASE + endpoint, **kw))
