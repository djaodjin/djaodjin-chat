from channels import Channel, Group
from ..models import ChatMessage
from rest_framework import serializers
from .. import settings
from .. import threadstore, claimstore
import json

thread_store = threadstore.load_thread_store(settings.THREAD_STORE)
claim_store = claimstore.load_claim_store(settings.CLAIM_STORE)

def s(serializer):
    def s_decorator(func):
        func.serializer = serializer
        return func

    return s_decorator

class EmptySerializer(serializers.Serializer):
    pass

class SendSerializer(serializers.Serializer):
    text=serializers.CharField(max_length=255)

# unauthed
@s(SendSerializer)
def send(message, text):
    # guid = message.http_session['guid']
    # client, _ = ChatClient.objects.get_or_create(guid=guid)

    print message.http_session.items()

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
    Group('%s-admin' % thread_id).send({
        "text": json.dumps(['message_from', {
            'text': text,
            'thread': thread_id,
            'from': message.http_session.session_key,
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

    print 'subscribe', thread_id

    Group(thread_id).add(message.reply_channel)
    thread_store.addActive(thread_id)
    Group('__active').send({
        'text': json.dumps(['became_active', [thread_id]])
    })


# authed

@s(EmptySerializer)
def subscribe_active(message):

    Group('__active').add(message.reply_channel)
    message.reply_channel.send({
        'text': json.dumps(['became_active', list(thread_store.getActive())])
    })

@s(EmptySerializer)
def subscribe_claims(message):

    Group('__claims').add(message.reply_channel)
    message.reply_channel.send({
        'text': json.dumps(['claimed', claim_store.getClaims()])
    })

# @s(EmptySerializer)
# def list_recent(message):
#     pass

class SubscribeToSerializer(serializers.Serializer):
    thread_id=serializers.CharField(max_length=255)

@s(SubscribeToSerializer)
def subscribe_to(message, thread_id):
    print 'subscribe to', thread_id
    Group('%s-admin' % thread_id).add(message.reply_channel)

class UnsubscribeSerializer(serializers.Serializer):
    thread_id=serializers.CharField(max_length=255)

@s(UnsubscribeSerializer)
def unsubscribe_to(message, thread_id):
    Group(thread_id).discard(message.reply_channel)
    thread_store.removeActive(thread_id)

    Group('__active').send({
        'text': json.dumps(['became_inactive', [thread_id]])
    })

# def list_subscriptions(message):
#     pass


class AddClaimSerializer(serializers.Serializer):
    thread_id=serializers.CharField(max_length=255)
    claimer=serializers.CharField(max_length=255, required=False,allow_null=True)

@s(AddClaimSerializer)
def add_claim(message, thread_id, claimer=None):
    print 'add_claim', thread_id, claimer

    if claimer is None:
        claimer = message.user.username

    claim_store.addClaim(thread_id, claimer)
    Group('__claims').send({
        'text': json.dumps(['claimed', {thread_id: claimer}])
    })


class RemoveClaimSerializer(serializers.Serializer):
    thread_id=serializers.CharField(max_length=255)
    claimer=serializers.CharField(max_length=255, required=False, allow_null=True)

@s(RemoveClaimSerializer)
def remove_claim(message, thread_id, claimer=None):
    if claimer is None:
        claimer = message.user.username
        
    success = claim_store.removeClaim(thread_id, claimer)
    if success:
        Group('__claims').send({
            'text': json.dumps(['unclaimed', {thread_id: claimer}])
        })


class SetClaimsSerializer(serializers.Serializer):
    thread_id=serializers.CharField(max_length=255)
    claimers=serializers.ListField(serializers.CharField(max_length=255, required=False))


class SendToSerializer(serializers.Serializer):
    thread_id=serializers.CharField(max_length=255)
    text=serializers.CharField(max_length=255)

@s(SendToSerializer)
def send_to(message, thread_id, text):
    cm = ChatMessage(# client=client,
                     message=text,
                     thread=thread_id,
                     user=message.user)
    cm.save()


    Group(thread_id).send({
        'text': json.dumps(['message', text]),
    })
    Group('%s-admin' % thread_id).send({
        "text": json.dumps(['message_from', {
            'text': text,
            'thread': thread_id,
            'from': message.user.username
        }]),
    })

    print 'send_to', thread_id ,text


@s(EmptySerializer)
def whoami(message):
    message.reply_channel.send({
        'text': json.dumps(['youare', message.user.username])
    })
