from jivago.templating.rendered_view import RenderedView
from jivago.wsgi.annotations import Resource
from jivago.wsgi.methods import GET


@Resource("/")
class MainResource(object):

    @GET
    def main(self) -> RenderedView:
        return RenderedView("main.html", {})
