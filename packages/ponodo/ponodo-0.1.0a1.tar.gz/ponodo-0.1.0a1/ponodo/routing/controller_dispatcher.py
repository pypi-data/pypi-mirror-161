import inspect

from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map

from ponodo.helpers import import_class
from ponodo.http import Request


class ControllerDispatcher:
    def __init__(self, app):
        self.app = app

    def run(self):
        request = self.app.instances["request"]

        # todo: configurable routing registration
        from app.routes.web import routes

        routes_map = Map()
        for route in routes:
            if route.map is not None:
                route.map = None
            routes_map.add(route)

        # todo: Save routes_map to cache for faster decision
        adapter = routes_map.bind_to_environ(request.environ)

        try:
            endpoint, params = adapter.match()
        except HTTPException as e:
            return e(
                request.environ, self.app.instances["response"].werkzeug_start_response
            )

        controller, action = endpoint.split("@")
        controller = import_class(controller)
        executor = getattr(controller(app=self), action)

        arg_spec = inspect.getfullargspec(executor)
        annotations = arg_spec.annotations
        kwargs = params

        for annotation in annotations:

            if annotations[annotation] == Request:
                kwargs[annotation] = request

        # if 'request' in args:
        #     kwargs['request'] = request
        controller_result = executor(**kwargs)

        response = self.app.instances["response"]
        return response(controller_result)
