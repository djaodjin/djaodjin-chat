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

from datetime import datetime, timedelta
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured

from . import settings


def load_thread_store(path):
    dot_pos = path.rfind('.')
    module, attr = path[:dot_pos], path[dot_pos + 1:]
    try:
        mod = import_module(module)
    except (ImportError, ValueError)  as err:
        raise ImproperlyConfigured(
            'Error importing thread store %s: "%s"' % (path, err))
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s"'\
' thread store' % (module, attr))
    return cls()


class ThreadStore(object):
    def get_active(self):
        pass

    def is_active(self, uid):
        pass

    def add_active(self, uid):
        pass

    def remove_active(self, uid):
        pass


class InMemoryThreadStore(ThreadStore):
    def __init__(self):
        self.active = {}

    def get_active(self):
        now = datetime.now()
        inactivity_threshold = timedelta(
            seconds=settings.ACTIVE_TIMEOUT_SECONDS)
        for uid, last_seen in self.active.items():
            time_since_active = (now - last_seen)
            if time_since_active > inactivity_threshold:
                del self.active[uid]

        return set(self.active.keys())

    def is_active(self, uid):
        if uid in self.active:
            time_since_active = (datetime.now() - self.active[uid])
            if time_since_active < timedelta(
                    seconds=settings.ACTIVE_TIMEOUT_SECONDS):
                return True
            else:
                del self.active[uid]

        return False

    def add_active(self, uid):
        self.active[uid] = datetime.now()

    def remove_active(self, uid):
        try:
            del self.active[uid]
        except KeyError:
            pass
