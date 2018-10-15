from jivago.templating.rendered_view import RenderedView
from jivago.wsgi.annotations import Resource, Path
from jivago.wsgi.methods import GET


@Resource("/")
class MainResource(object):

    @GET
    def main(self) -> RenderedView:
        return RenderedView("main.html", {})

    @GET
    @Path("/robots.txt")
    def robots(self) -> RenderedView:
        return RenderedView("robots.txt", {})
