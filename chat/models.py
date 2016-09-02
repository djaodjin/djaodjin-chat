from __future__ import unicode_literals

from django.db import models
from . import settings

class ChatMessage(models.Model):
    "Model for storing chat messages."

    class Meta:
        index_together = [
            ['thread', 'created_at'],
        ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    thread = models.CharField(max_length=255)

    def __unicode__(self):
        if self.user:
            user = self.user.username
        else:
            user = 'anonymous'
        return '#%s %s: %s' % (self.thread, user, self.message)

