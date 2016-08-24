from importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from collections import Counter

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
        self.active = Counter()

    def get_active(self):
        return set(self.active.keys())

    def is_active(self, uid):
        return self.active[uid] > 0

    def add_active(self, uid):
        self.active[uid] += 1
        assert self.active[uid] >= 0

    def remove_active(self, uid):
        self.active[uid] = max(0, self.active[uid] - 1)
