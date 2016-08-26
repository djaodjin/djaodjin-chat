from channels import Group
from ..models import ChatMessage
from rest_framework import serializers
from .. import settings
from .. import threadstore, claimstore
import json

thread_store = threadstore.load_thread_store(settings.THREAD_STORE)
claim_store = claimstore.load_claim_store(settings.CLAIM_STORE)
admin_store = threadstore.load_thread_store(settings.THREAD_STORE)

def s(serializer):
    def s_decorator(func):
        func.serializer = serializer
        return func

    return s_decorator

class EmptySerializer(serializers.Serializer):
    pass

class SendSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=255)

@s(SendSerializer)
def send(message, text):

    thread_id = message.http_session['chat-thread']

    cm = ChatMessage(# client=client,
                     message=text,
                     thread=thread_id)
    if not message.user.is_anonymous():
        cm.user = message.user

    cm.save()

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

@s(EmptySerializer)
def subscribe(message):
    if 'chat-thread' in message.http_session:
        thread_id = message.http_session['chat-thread']
    else:
        thread_id = message.http_session.session_key
        message.http_session['chat-thread'] = thread_id
        message.http_session.save()

    Group(thread_id).add(message.reply_channel)


@s(EmptySerializer)
def subscribe_active(message):

    Group('__active').add(message.reply_channel)

    message.reply_channel.send({
        'text': json.dumps(['became_active', list(thread_store.get_active()) ])
    })

@s(EmptySerializer)
def subscribe_claims(message):

    Group('__claims').add(message.reply_channel)
    message.reply_channel.send({
        'text': json.dumps(['claimed', claim_store.get_claims()])
    })

class SubscribeToSerializer(serializers.Serializer):
    thread_id = serializers.CharField(max_length=255)

@s(SubscribeToSerializer)
def subscribe_to(message, thread_id):
    Group('%s-admin' % thread_id).add(message.reply_channel)

class UnsubscribeSerializer(serializers.Serializer):
    thread_id = serializers.CharField(max_length=255)

@s(UnsubscribeSerializer)
def unsubscribe_to(message, thread_id):
    Group(thread_id).discard(message.reply_channel)

    # not sure we want to try to proactively remove people
    # since you can't tell the difference between changing pages
    # and intentionally quitting

    if not thread_store.is_active(thread_id):
        Group('__active').send({
            'text': json.dumps(['became_inactive', [thread_id]])
        })

class GetMessagesSerializer(serializers.Serializer):
    thread_id = serializers.CharField(max_length=255, allow_null=True)
    cursor = serializers.DateTimeField(format='iso-8601', allow_null=True)

@s(GetMessagesSerializer)
def get_messages(message, thread_id=None, cursor=None):

    ms = ChatMessage.objects

    if thread_id is None:
        ms = ms.filter(thread=message.http_session['chat-thread'])
    else:
        assert message.user.is_staff

        ms = ms.filter(thread=thread_id)

    ms = ms.order_by('-created_at')

    if cursor:
        ms = ms.filter(created_at__lt=cursor)

    message_batch = []
    for m in ms.all()[:20]:
        message_info = {
            'text': m.message,
            't' : m.created_at.isoformat(),
        }
        if m.user:
            message_info['from'] = m.user.username

        message_batch.append(message_info)


    reply = {
        'messages': message_batch
    }

    if thread_id:
        reply['thread'] = thread_id,
    if message_batch:
        reply['cursor'] = message_batch[-1]['t']

    message.reply_channel.send({
        'text': json.dumps(['get_messages_reply', reply])
    })


class AddClaimSerializer(serializers.Serializer):
    thread_id = serializers.CharField(max_length=255)
    claimer = serializers.CharField(max_length=255, required=False, allow_null=True)

@s(AddClaimSerializer)
def add_claim(message, thread_id, claimer=None):

    if claimer is None:
        claimer = message.user.username

    claim_store.add_claim(thread_id, claimer)
    Group('__claims').send({
        'text': json.dumps(['claimed', {thread_id: claimer}])
    })


class RemoveClaimSerializer(serializers.Serializer):
    thread_id = serializers.CharField(max_length=255)
    claimer = serializers.CharField(max_length=255, required=False, allow_null=True)

@s(RemoveClaimSerializer)
def remove_claim(message, thread_id, claimer=None):
    if claimer is None:
        claimer = message.user.username

    success = claim_store.remove_claim(thread_id, claimer)
    if success:
        Group('__claims').send({
            'text': json.dumps(['unclaimed', {thread_id: claimer}])
        })


class SetClaimsSerializer(serializers.Serializer):
    thread_id = serializers.CharField(max_length=255)
    claimers = serializers.ListField(serializers.CharField(max_length=255, required=False))


class SendToSerializer(serializers.Serializer):
    thread_id = serializers.CharField(max_length=255)
    text = serializers.CharField(max_length=255)

@s(SendToSerializer)
def send_to(message, thread_id, text):
    cm = ChatMessage(# client=client,
                     message=text,
                     thread=thread_id,
                     user=message.user)
    cm.save()


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



@s(EmptySerializer)
def whoami(message):
    message.reply_channel.send({
        'text': json.dumps(['youare', message.user.username])
    })


@s(EmptySerializer)
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
