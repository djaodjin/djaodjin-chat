from ..models import ChatClient, ChatMessage
from channels.sessions import channel_session
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from channels.sessions import channel_session, enforce_ordering
from channels import Channel, Group
import json
import traceback
from datetime import datetime, timedelta


@enforce_ordering()
@channel_session_user_from_http
def ws_connect(message):
    print 'ws connect', message.user.is_staff
    if message.user.is_staff:
        Group('admin').add(message.reply_channel)
    # Group("chat-%s" % message.).add(message.reply_channel)
    pass


def on_chat_message(message, text):
    print 'received chat message'
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    
    guid = message.channel_session['guid']
    client, _ = ChatClient.objects.get_or_create(guid=guid)

    cm = ChatMessage(client=client,
                     message=text,
                     thread=client.guid)
    if not message.user.is_anonymous():
        cm.user = message.user

    cm.save()

    Group('admin').send({
        'text': json.dumps(['broadcastmessage',{
            
            'text': cm.message,
            'thread': cm.thread,
            't': cm.created_at.isoformat(),
            'from': cm.user and cm.user.username,
        }])
    })

    message.reply_channel.send({
        "text": text,
    })


def on_login(message,guid):
    group_id = 'chat-%s' % guid
    Group(group_id).add(message.reply_channel)
    message.channel_session['guid'] = guid
    message.channel_session['group'] = group_id
    print 'logged in'

def on_message_admin(message, to , text):
    guid = message.channel_session['guid']
    client, _ = ChatClient.objects.get_or_create(guid=guid)

    cm = ChatMessage(client=client,
                     message=text,
                     thread=to,
                     user=message.user)
    cm.save()

    Group('chat-%s' % to).send({
        'text': text,
    })
    print 'admin setnt!', to , text

def on_request_recent(message):
    recents = ChatMessage.objects.filter(created_at__gt=datetime.now() - timedelta(minutes=30))

    for recent in recents:
        message.reply_channel.send({
            'text': json.dumps(['broadcastmessage',{
                
                'text': recent.message,
                'thread': recent.thread,
                't': recent.created_at.isoformat(),
                'from': recent.user and recent.user.username,
            }])
        })

def process_message(message, content):
    message.reply_channel.send({
        "text": message.content['text'],
    })

    command, args = (content[0], content[1:])
    print 'process message', command, args
    if command == 'message':
        chat_message = args[0]
        
        on_chat_message(message, chat_message)
    elif command == 'login':
        guid = args[0]
        on_login(message,guid)
    elif message.user.is_staff:
        if command == 'message_admin':
            to, text = args
            on_message_admin(message, to, text)

        elif command == 'get_recent':
            on_request_recent(message)
        


@enforce_ordering()
@channel_session_user
def ws_message(message):
    print 'ws message', message.user.id
    
    try:
        content = json.loads(message.content['text'])
    except ValueError as e:
        print 'error', e
        message.reply_channel.close()
    else:
        try:
            process_message(message, content)
        except Exception as e:
            traceback.print_exc()


@enforce_ordering()
@channel_session_user
def ws_disconnect(message):
    if 'group' in  message.channel_session:
        Group(message.channel_session['group']).discard(message.reply_channel)
        print 'leaving group'

    if message.user.is_staff:
        Group('admin').discard(message.reply_channel)
    print 'closing channel'




