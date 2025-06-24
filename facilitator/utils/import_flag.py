import threading

_local = threading.local()

def set_importing(value: bool):
    _local.importing = value

def is_importing() -> bool:
    return getattr(_local, "importing", False)
