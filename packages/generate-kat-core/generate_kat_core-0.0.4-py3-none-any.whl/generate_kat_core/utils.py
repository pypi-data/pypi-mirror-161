#!/usr/bin/env python

class GeneralError(Exception):
    pass


class KATError(GeneralError):
    pass


class KATParseError(KATError):
    pass


class GenerateKatGeneralError(Exception):
    pass


class GenerateKatKATError(GenerateKatGeneralError):
    pass


class GenerateKatKATParseError(GenerateKatKATError):
    pass


class GenerateKatCryptoCheckError(GenerateKatGeneralError):
    pass


class GenerateKatCryptoSelfTestError(GenerateKatCryptoCheckError):
    pass


class GenerateKatCryptoAuthenticationError(GenerateKatCryptoCheckError):
    pass


class GenerateKatArgError(GenerateKatGeneralError):
    pass


class GenerateKatConfigError(GenerateKatArgError):
    pass
