from __future__ import unicode_literals

from django.db import models
from . import settings

class ChatClient(models.Model):
    guid = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    client = models.ForeignKey(ChatClient)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    thread = models.CharField(max_length=255)

    
    
