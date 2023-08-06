from requests_file import FileAdapter



class RequestsFileAdapter(FileAdapter):
    def send(self, request, **kwargs):
        resp = super().send(request, **kwargs)
        resp.request = request
        return resp


class FileRequestsMixin:

    def load_session(self):
        session = super().load_session()
        session.mount('file:///', RequestsFileAdapter())
        return session

    