from __future__ import unicode_literals

from django.db import models
from . import settings

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    thread = models.CharField(max_length=255)

    
    
