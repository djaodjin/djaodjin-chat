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

from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.conf.urls import url, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from .views.app import AppView


class TestChatView(TemplateView):
    template_name = "chat/chat.html"

    def get_context_data(self, **kwargs):
        context = super(TestChatView, self).get_context_data(**kwargs)
        context['other'] = reverse(self.other_page)
        self.request.session.save()

        return context

class TestChatView1(TestChatView):
    other_page = 'chat2'

class TestChatView2(TestChatView):
    other_page = 'chat1'

urlpatterns = [
    url(r'', include('django.contrib.auth.urls')),
    url(r'^chat/$',
        TestChatView1.as_view(template_name="chat/chat.html"), name='chat1'),
    url(r'^chat2/$',
        TestChatView2.as_view(template_name="chat/chat.html"), name='chat2'),
    url(r'^chat-admin/$',
        TemplateView.as_view(template_name="chat/chat_admin.html"),
        name='chat_admin'),
    url(r'^$', AppView.as_view(), name='app')
]
