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

from django.conf import settings

_SETTINGS = {
    'THREAD_STORE': 'chat.threadstore.InMemoryThreadStore',
    'CLAIM_STORE': 'chat.claimstore.InMemoryClaimStore',
    'ACTIVE_TIMEOUT_SECONDS' : 10,
}

_SETTINGS.update(getattr(settings, 'CHAT', {}))


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL')
SESSION_ENGINE = getattr(settings, 'SESSION_ENGINE')

THREAD_STORE = _SETTINGS.get('THREAD_STORE')
CLAIM_STORE = _SETTINGS.get('CLAIM_STORE')
ACTIVE_TIMEOUT_SECONDS = _SETTINGS.get('ACTIVE_TIMEOUT_SECONDS')
