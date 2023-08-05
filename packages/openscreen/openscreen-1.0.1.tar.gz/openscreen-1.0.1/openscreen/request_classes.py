from typing import Generic, TypeVar, Any

PathParam = TypeVar('PathParam')
QueryParam = TypeVar('QueryParam')
RequestBody = TypeVar('RequestBody')
ResponseBody = TypeVar('ResponseBody')
T = TypeVar('T')


class BaseClass(Generic[T]):  # Scope of `T` is the class:
    def __init__(self, value: T):  # Providing some `T` on `__init__`
        self._value = value  # defines the class' `T`


class ClassT(BaseClass[ResponseBody]):  # "is a" BaseClass where `T = T'`
    @property
    def value(self) -> ResponseBody:
        return self._value


class Request(Generic[PathParam, QueryParam, RequestBody, ResponseBody]):

    def __init__(self, session, route_segments):
        self.session = session
        self.route_segments = route_segments

    def go(self, path_parameters: PathParam, request_body: RequestBody,
           query_string_parameters: QueryParam, response_body_class, options=None) -> None:
        if options is None:
            options = {}


class RequestGet(Request[PathParam, QueryParam, RequestBody, ResponseBody]):
    def __init__(self, session, route_segments):
        super(RequestGet, self).__init__(session, route_segments)

    def go(self, path_parameters: PathParam, request_body: RequestBody = None,
           query_string_parameters: QueryParam = None, response_body_class=dict,options=None) -> ResponseBody:
        if options is None:
            options = {}
        return self.session.go('get', self.route_segments, query_string_parameters, path_parameters,
                                      request_body, response_body_class, **options)


class RequestPatch(Request[PathParam, QueryParam, RequestBody, ResponseBody]):
    def __init__(self, session, route_segments):
        super(RequestPatch, self).__init__(session, route_segments)

    def go(self, path_parameters: PathParam, request_body: RequestBody = None,
           query_string_parameters: QueryParam = None, response_body_class=dict, options=None) -> ResponseBody:
        if options is None:
            options = {}
        return self.session.go('patch', self.route_segments, query_string_parameters, path_parameters,
                                      request_body, response_body_class, **options)


class RequestPost(Request[PathParam, QueryParam, RequestBody, ResponseBody]):
    def __init__(self, session, route_segments):
        super(RequestPost, self).__init__(session, route_segments)

    def go(self, path_parameters: PathParam, request_body: RequestBody = None,
           query_string_parameters: QueryParam = None, response_body_class=dict, options=None) -> ResponseBody:
        if options is None:
            options = {}
        return self.session.go('post', self.route_segments, query_string_parameters, path_parameters,
                                      request_body, response_body_class, **options)


class RequestDelete(Request[PathParam, QueryParam, RequestBody, ResponseBody]):
    def __init__(self, session, route_segments):
        super(RequestDelete, self).__init__(session, route_segments)

    def go(self, path_parameters: PathParam, request_body: RequestBody = None,
           query_string_parameters: QueryParam = None, response_body_class=dict,options=None) -> ResponseBody:
        if options is None:
            options = {}
        return self.session.go('delete', self.route_segments, query_string_parameters, path_parameters,
                                      request_body, response_body_class, **options)
