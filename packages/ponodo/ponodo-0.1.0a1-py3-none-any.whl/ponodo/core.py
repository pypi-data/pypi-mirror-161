from werkzeug import Request as WerkzeugRequest

from ponodo.http import Request, Response
from ponodo.routing import ControllerDispatcher


class Facade:
    app = None


class Container:
    """ """

    def __init__(self):
        # Binding abstract to concrete
        self.bindings = {}

        # Instance of class or plain object
        self.instances = {}

    def make(self, abstract):
        if abstract in self.instances:
            return self.instances[abstract]


class Application(Container):
    is_routes_bound = False

    def __init__(self):
        super(Application, self).__init__()

    def set_werkzeug_request(self, request):
        self.instances["request"] = Request(app=self, werkzeug_request=request)
        return self

    def set_werkzeug_response(self, response):
        self.instances["response"] = Response(
            app=self, werkzeug_start_response=response
        )
        return self

    def handle(self):
        return ControllerDispatcher(app=self).run()


def handle_application(environ, start_response):
    application = Application()
    application.set_werkzeug_request(WerkzeugRequest(environ))
    application.set_werkzeug_response(start_response)
    return application.handle()
