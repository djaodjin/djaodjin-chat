# Copyright (c) 2016, DjaoDjin inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import inspect, json, logging, traceback
from datetime import datetime, timedelta
from importlib import import_module

from channels.auth import (http_session_user,
                           channel_session_user,
                           channel_session_user_from_http)
from channels.sessions import (channel_session,
                               enforce_ordering)
from channels import Channel, Group

from . import api
from .. import settings
from ..models import ChatMessage


LOGGER = logging.getLogger(__name__)


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
    '/chat-api/get_messages': api.get_messages,
    '/chat-api/ping': api.ping,
}


@enforce_ordering()
@channel_session_user_from_http
def ws_connect(message):
    message.channel_session['http_session_key'] \
        = message.http_session.session_key


@enforce_ordering()
@channel_session_user
def ws_message(message):
    session_engine = import_module(settings.SESSION_ENGINE)
    http_session = session_engine.SessionStore(
        session_key=message.channel_session['http_session_key'])
    message.http_session = http_session

    try:
        content = json.loads(message.content['text'])
    except ValueError as err:
        LOGGER.exception(err)
        raise err
    else:
        func_path = content[0]
        args = content[1:]

        func = MESSAGE_FUNCTIONS[func_path]

        arg_spec = inspect.getargspec(func)
        # first arg is always the channel message object
        arg_names = arg_spec.args[1:]

        kws = {arg_name: arg_val
               for arg_name, arg_val in zip(arg_names, args)}

        max_arg_count = len(arg_names)
        if arg_spec.defaults:
            min_arg_count = max_arg_count - len(arg_spec.defaults)
        else:
            min_arg_count = max_arg_count

        arg_count = len(args)
        if arg_count > max_arg_count or arg_count < min_arg_count:
            raise RuntimeError("%d args was expected to be in [%d, %d]" % (
                arg_count, min_arg_count, max_arg_count))

        serializer = func.serializer(data=kws)
        if not serializer.is_valid():
            LOGGER.error("%s has invalid args %s", func_path, args)
            raise RuntimeError("%s has invalid args %s" % (func_path, args))

        func(message, **serializer.validated_data)
        api.ping(message)


@enforce_ordering()
@channel_session_user
def ws_disconnect(message):
    session_engine = import_module(settings.SESSION_ENGINE)
    http_session = session_engine.SessionStore(
        session_key=message.channel_session['http_session_key'])
    message.http_session = http_session
    api.logout(message)
