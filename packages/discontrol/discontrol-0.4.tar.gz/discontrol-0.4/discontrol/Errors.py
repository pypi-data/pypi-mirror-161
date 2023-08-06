class errors:

    class FailedToRunClient(Exception):
        pass

    class FailedToSendMessage(Exception):
        pass

    class FailedToDeleteMessage(Exception):
        pass

    class FailedToEditMessage(Exception):
        pass

    class InvalidStatusIcon(Exception):
        pass

    class FailedToChangeStatusIcon(Exception):
        pass

    class FailedToChangeStatusText(Exception):
        pass

    class InvalidCustomRequestType(Exception):
        pass

    class InvalidResponse(Exception):
        pass