from . import data_provider_pb2_grpc as importStub

class DataProviderService(object):

    def __init__(self, router):
        self.connector = router.get_connection(DataProviderService, importStub.DataProviderStub)

    def getEvent(self, request, timeout=None, properties=None):
        return self.connector.create_request('getEvent', request, timeout, properties)

    def getEvents(self, request, timeout=None, properties=None):
        return self.connector.create_request('getEvents', request, timeout, properties)

    def getMessage(self, request, timeout=None, properties=None):
        return self.connector.create_request('getMessage', request, timeout, properties)

    def getMessageStreams(self, request, timeout=None, properties=None):
        return self.connector.create_request('getMessageStreams', request, timeout, properties)

    def searchMessages(self, request, timeout=None, properties=None):
        return self.connector.create_request('searchMessages', request, timeout, properties)

    def searchEvents(self, request, timeout=None, properties=None):
        return self.connector.create_request('searchEvents', request, timeout, properties)

    def getMessagesFilters(self, request, timeout=None, properties=None):
        return self.connector.create_request('getMessagesFilters', request, timeout, properties)

    def getEventsFilters(self, request, timeout=None, properties=None):
        return self.connector.create_request('getEventsFilters', request, timeout, properties)

    def getEventFilterInfo(self, request, timeout=None, properties=None):
        return self.connector.create_request('getEventFilterInfo', request, timeout, properties)

    def getMessageFilterInfo(self, request, timeout=None, properties=None):
        return self.connector.create_request('getMessageFilterInfo', request, timeout, properties)

    def matchEvent(self, request, timeout=None, properties=None):
        return self.connector.create_request('matchEvent', request, timeout, properties)

    def matchMessage(self, request, timeout=None, properties=None):
        return self.connector.create_request('matchMessage', request, timeout, properties)