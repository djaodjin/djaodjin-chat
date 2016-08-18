from importlib import import_module
from django.core.exceptions import ImproperlyConfigured

def load_claim_store(path):
    dot_pos = path.rfind('.')
    module, attr = path[:dot_pos], path[dot_pos + 1:]
    try:
        mod = import_module(module)
    except (ImportError, ValueError)  as err:
        raise ImproperlyConfigured(
            'Error importing claim store %s: "%s"' % (path, err))
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s"'\
' claim store' % (module, attr))
    return cls()



class ClaimStore(object):
    def get_claims(self):
        pass

    def add_claim(self, uid, thread_id):
        pass

    def remove_claim(self, thread_id, uid):
        pass


class InMemoryClaimStore(ClaimStore):
    def __init__(self):
        self.claims = {}

    def get_claims(self):
        return dict(self.claims)

    def add_claim(self, thread_id, uid):
        self.claims[thread_id] = uid

    def remove_claim(self, thread_id, uid):
        if self.claims.get(thread_id) == uid:
            del self.claims[thread_id]
            return True
        else:
            return False








