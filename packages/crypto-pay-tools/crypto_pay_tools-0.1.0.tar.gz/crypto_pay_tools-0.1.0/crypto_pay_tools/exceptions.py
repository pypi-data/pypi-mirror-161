class Error(Exception):
    pass


class AuthorizationError(Error):
    pass


class InvoiceError(Error):
    pass


class TransferError(Error):
    pass


class GetMeError(Error):
    pass
