class DummyCC(object):
    """This is a decorator that can replace Numba CC if something goes wrong with importing the system compiler. This will allow the code to still run using pure python"""
    def export(self, exported_name, sig):
        def decorator(func):
            return func #just a pass through
        return decorator