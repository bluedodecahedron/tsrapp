import logging


# a filter that adds the ip address of the client to every log record
class IPAddressFilter(logging.Filter):
    def filter(self, record):
        return IPRecord(record).build()


# a log record extended with the ip address of the client
class IPRecord:
    def __init__(self, record):
        self.record = record

    def build(self):
        return self.__add_ip_attr()

    def __add_ip_attr(self):
        if hasattr(self.record, 'request'):
            self.record.ip = self.__get_client_ip(self.record.request)
        else:
            self.record.ip = 'undefined'
        return True

    def __get_client_ip(self, request):
        if hasattr(request, 'META'):  # normal request object with META attribute
            return self.__get_meta_raddr(request.META)
        elif hasattr(request, 'getpeername'):  # request object is a socket
            return self.__get_socket_raddr(request)
        else:
            return 'undefined'

    @staticmethod
    def __get_meta_raddr(meta):
        x_forwarded_for = meta.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        else:
            return meta.get('REMOTE_ADDR')

    @staticmethod
    def __get_socket_raddr(socket):
        return socket.getpeername()[0]
