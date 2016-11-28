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

import json

from channels import Group
from rest_framework import serializers
from .. import settings
from .. import threadstore, claimstore
from ..models import ChatMessage

thread_store = threadstore.load_thread_store(  #pylint:disable=invalid-name
    settings.THREAD_STORE)
claim_store = claimstore.load_claim_store(     #pylint:disable=invalid-name
    settings.CLAIM_STORE)
admin_store = threadstore.load_thread_store(   #pylint:disable=invalid-name
    settings.THREAD_STORE)


class EmptySerializer(serializers.Serializer):

    def create(self, validated_data):
        raise RuntimeError(
            "`%s.create()` is not meant to be called." % self.__class__)

    def update(self, instance, validated_data):
        raise RuntimeError(
            "`%s.update()` is not meant to be called." % self.__class__)


class AddClaimSerializer(EmptySerializer):
    thread_id = serializers.CharField(max_length=255)
    claimer = serializers.CharField(
        max_length=255, required=False, allow_null=True)


class GetMessagesSerializer(EmptySerializer):
    thread_id = serializers.CharField(max_length=255, allow_null=True)
    cursor = serializers.DateTimeField(format='iso-8601', allow_null=True)


class RemoveClaimSerializer(EmptySerializer):
    thread_id = serializers.CharField(max_length=255)
    claimer = serializers.CharField(
        max_length=255, required=False, allow_null=True)


class SendSerializer(EmptySerializer):
    text = serializers.CharField(max_length=255)


class SendToSerializer(EmptySerializer):
    thread_id = serializers.CharField(max_length=255)
    text = serializers.CharField(max_length=255)


class SetClaimsSerializer(EmptySerializer):
    thread_id = serializers.CharField(max_length=255)
    claimers = serializers.ListField(
        serializers.CharField(max_length=255, required=False))


class SubscribeToSerializer(EmptySerializer):
    thread_id = serializers.CharField(max_length=255)


class UnsubscribeSerializer(EmptySerializer):
    thread_id = serializers.CharField(max_length=255)


def serialize_with(serializer):
    def s_decorator(func):
        func.serializer = serializer
        return func

    return s_decorator


@serialize_with(SendSerializer)
def send(message, text):
    thread_id = message.http_session['chat-thread']
    chat_message = ChatMessage(# client=client,
                     message=text,
                     thread=thread_id)
    if not message.user.is_anonymous():
        chat_message.user = message.user

    chat_message.save()

    Group(thread_id).send({
        "text": json.dumps(['message', text]),
    })

    if not admin_store.get_active():
        Group(thread_id).send({
            "text": json.dumps(['message_from', {
                'text': 'Please wait for a representative to be with you.',
                'thread': thread_id,
                'from': 'Bot',
            }])
        })

    if message.user.is_anonymous():
        message_from = message.http_session.session_key
    else:
        message_from = message.user.username

    Group('%s-admin' % thread_id).send({
        "text": json.dumps(['message_from', {
            'text': text,
            'thread': thread_id,
            'from': message_from,
        }]),
    })


@serialize_with(EmptySerializer)
def subscribe(message):
    if 'chat-thread' in message.http_session:
        thread_id = message.http_session['chat-thread']
    else:
        thread_id = message.http_session.session_key
        message.http_session['chat-thread'] = thread_id
        message.http_session.save()

    Group(thread_id).add(message.reply_channel)


@serialize_with(EmptySerializer)
def subscribe_active(message):
    Group('__active').add(message.reply_channel)

    message.reply_channel.send({
        'text': json.dumps(['became_active', list(thread_store.get_active())])
    })


@serialize_with(EmptySerializer)
def subscribe_claims(message):
    Group('__claims').add(message.reply_channel)
    message.reply_channel.send({
        'text': json.dumps(['claimed', claim_store.get_claims()])
    })


@serialize_with(SubscribeToSerializer)
def subscribe_to(message, thread_id):
    Group('%s-admin' % thread_id).add(message.reply_channel)


@serialize_with(UnsubscribeSerializer)
def unsubscribe_to(message, thread_id):
    Group(thread_id).discard(message.reply_channel)

    # not sure we want to try to proactively remove people
    # since you can't tell the difference between changing pages
    # and intentionally quitting

    if not thread_store.is_active(thread_id):
        Group('__active').send({
            'text': json.dumps(['became_inactive', [thread_id]])
        })


@serialize_with(GetMessagesSerializer)
def get_messages(message, thread_id=None, cursor=None):
    queryset = ChatMessage.objects

    if thread_id is None:
        queryset = queryset.filter(thread=message.http_session['chat-thread'])
    else:
        assert message.user.is_staff
        queryset = queryset.filter(thread=thread_id)

    queryset = queryset.order_by('-created_at')

    if cursor:
        queryset = queryset.filter(created_at__lt=cursor)

    message_batch = []
    for chat_message in queryset.all()[:20]:
        message_info = {
            'text': chat_message.message,
            't' : chat_message.created_at.isoformat()}
        if chat_message.user:
            message_info['from'] = chat_message.user.username
        message_batch.append(message_info)

    reply = {'messages': message_batch}

    if thread_id:
        reply['thread'] = thread_id,
    if message_batch:
        reply['cursor'] = message_batch[-1]['t']

    message.reply_channel.send({
        'text': json.dumps(['get_messages_reply', reply])
    })


@serialize_with(AddClaimSerializer)
def add_claim(message, thread_id, claimer=None):

    if claimer is None:
        claimer = message.user.username

    claim_store.add_claim(thread_id, claimer)
    Group('__claims').send({
        'text': json.dumps(['claimed', {thread_id: claimer}])
    })


@serialize_with(RemoveClaimSerializer)
def remove_claim(message, thread_id, claimer=None):
    if claimer is None:
        claimer = message.user.username

    success = claim_store.remove_claim(thread_id, claimer)
    if success:
        Group('__claims').send({
            'text': json.dumps(['unclaimed', {thread_id: claimer}])
        })


@serialize_with(SendToSerializer)
def send_to(message, thread_id, text):
    chat_message = ChatMessage(
                     message=text,
                     thread=thread_id,
                     user=message.user)
    chat_message.save()


    Group(thread_id).send({
        "text": json.dumps(['message_from', {
            'text': text,
            'from': message.user.username
        }]),
    })
    Group('%s-admin' % thread_id).send({
        "text": json.dumps(['message_from', {
            'text': text,
            'thread': thread_id,
            'from': message.user.username
        }]),
    })



@serialize_with(EmptySerializer)
def whoami(message):
    message.reply_channel.send({
        'text': json.dumps(['youare', message.user.username])
    })


@serialize_with(EmptySerializer)
def ping(message):
    if 'chat-thread' in message.http_session:
        thread_id = message.http_session['chat-thread']

        thread_store.add_active(thread_id)
        Group('__active').send({
            'text': json.dumps(['became_active', [thread_id]])
        })

    if message.user.is_staff:
        admin_store.add_active(message.http_session.session_key)


def logout(message):
    if 'chat-thread' in message.http_session:
        unsubscribe_to(message, message.http_session['chat-thread'])

    Group('__active').discard(message.reply_channel)
