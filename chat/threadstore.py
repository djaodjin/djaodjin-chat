from importlib import import_module
from django.core.exceptions import ImproperlyConfigured

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

    def add_active(self, uid):
        pass

    def remove_active(self, uid):
        pass

class InMemoryThreadStore(ThreadStore):
    def __init__(self):
        self.active = set()

    def get_active(self):
        return set(self.active)

    def add_active(self, uid):
        self.active.add(uid)

    def remove_active(self, uid):
        try:
            self.active.remove(uid)
        except KeyError:
            pass
