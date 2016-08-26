from importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from collections import Counter
from datetime import datetime, timedelta

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
        inactivity_threshold = timedelta(seconds=settings.ACTIVE_TIMEOUT_SECONDS)
        for uid, last_seen in self.active.items():
            time_since_active = (now - last_seen)
            if time_since_active > inactivity_threshold:
                del self.active[uid]

        return set(self.active.keys())

    def is_active(self, uid):
        if uid in self.active:
            time_since_active = (datetime.now() - self.active[uid])
            if time_since_active < timedelta(seconds=settings.ACTIVE_TIMEOUT_SECONDS):
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
