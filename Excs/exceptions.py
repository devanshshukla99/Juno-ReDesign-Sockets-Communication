
class username_error(Exception):
    """
    Exception Occurs when the client ident fails!
    """
    def __init__(self, message="Client IDENT Failed!"):
        self.message = message

        super().__init__(self.message)

    pass


class UIDInvalid(Exception):
    """
    Exception Occurs when the UID is Invalid!
    """
    def __init__(self, message='In-valid UID!'):
        self.message = message
        super().__init__(self.message)

    pass


class IllegalReceipt(Exception):
    """
    Exception Occurs when the Receipt is In-Valid!
    """
    def __init__(self, message='Illegal Receipt!'):
        self.message = message
        super().__init__(self.message)

    pass
