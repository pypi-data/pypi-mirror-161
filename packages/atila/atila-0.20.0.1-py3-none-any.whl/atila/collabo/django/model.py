from django.db.models import Q

def igNone (**filter):
    k, v = filter.popitem ()
    if v is not None:
        return Q (**filter)
    else:
        return Q ()
