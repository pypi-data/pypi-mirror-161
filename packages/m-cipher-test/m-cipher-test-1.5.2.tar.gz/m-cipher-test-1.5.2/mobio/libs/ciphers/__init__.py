from .mobio_crypt_2 import _MobioCrypt2
from .mobio_crypt_3 import _MobioCrypt3


class MobioCrypt2:
    @staticmethod
    def e1(raw):
        return _MobioCrypt2.e1(raw)

    @staticmethod
    def d1(encrypted, enc=None):
        return _MobioCrypt2.d1(encrypted, enc)


class MobioCrypt3:
    @staticmethod
    def encrypt(raw, is_padding=None):
        if not is_padding:
            return _MobioCrypt3.e1(raw)
        else:
            return _MobioCrypt3.e2(raw)

    @staticmethod
    def d1(raw, enc=None):
        return _MobioCrypt3.d1(raw, enc)
