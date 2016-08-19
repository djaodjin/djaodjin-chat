from ..models import ChatMessage
from channels.sessions import channel_session, http_session
from channels.auth import (http_session_user,
                           channel_session_user,
                           channel_session_user_from_http)

from channels.sessions import (channel_session,
                               enforce_ordering)
from channels import Channel, Group
import json
import traceback
from datetime import datetime, timedelta
import inspect
from . import api
from importlib import import_module
from django.conf import settings



MESSAGE_FUNCTIONS = {
    '/chat-api/send': api.send,
    '/chat-api/subscribe': api.subscribe,
    '/chat-api/subscribe_active': api.subscribe_active,
    '/chat-api/subscribe_claims': api.subscribe_claims,
    # '/chat-api/list_recent': api.list_recent,
    '/chat-api/subscribe_to': api.subscribe_to,
    '/chat-api/unsubscribe_to': api.unsubscribe_to,
    '/chat-api/add_claim': api.add_claim,
    '/chat-api/remove_claim': api.remove_claim,
    '/chat-api/send_to': api.send_to,
    '/chat-api/whoami': api.whoami,
}


@enforce_ordering()
@channel_session_user_from_http
def ws_connect(message):
    message.channel_session['http_session_key'] = message.http_session.session_key

@enforce_ordering()
@channel_session_user
def ws_message(message):

    session_engine = import_module(settings.SESSION_ENGINE)
    http_session = session_engine.SessionStore(session_key=message.channel_session['http_session_key'])
    message.http_session = http_session

    try:
        content = json.loads(message.content['text'])
    except ValueError as e:
        print 'error', e
        raise e
    else:
        try:
            fn_path = content[0]
            args = content[1:]

            fn = MESSAGE_FUNCTIONS[fn_path]

            arg_spec = inspect.getargspec(fn)
            # first arg is always the channel message object
            arg_names = arg_spec.args[1:]


            kws = {arg_name: arg_val
                   for arg_name, arg_val in zip(arg_names,
                                                args)}

            max_arg_count = len(arg_names)
            if arg_spec.defaults:
                min_arg_count = max_arg_count - len(arg_spec.defaults)
            else:
                min_arg_count = max_arg_count

            arg_count = len(args)
            if arg_count > max_arg_count or arg_count < min_arg_count:
                raise Exception('Wrong Number of Args')


            serializer = fn.serializer(data=kws)
            if not serializer.is_valid():
                raise Exception('invalid args')

            fn(message, **serializer.validated_data)

        except Exception as e:
            traceback.print_exc()
            raise e


@enforce_ordering()
@channel_session_user
def ws_disconnect(message):
    session_engine = import_module(settings.SESSION_ENGINE)
    http_session = session_engine.SessionStore(session_key=message.channel_session['http_session_key'])
    message.http_session = http_session

    if 'chat-thread' in message.http_session:
        api.unsubscribe_to(message, message.http_session['chat-thread'])

    Group('__active').discard(message.reply_channel)

