from fastapi import Depends, Response
import jinja2

from chlore.request import get_request


class JinjaResponse(Response):
    media_type = "text/html"

    def __init__(
        self,
        template: jinja2.Template,
        context: dict,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background=None,
    ):
        super().__init__(template.render(context), status_code, headers, media_type, background)


def _build_jinja_env(loader: jinja2.BaseLoader) -> jinja2.Environment:
    def url_for(name: str, **path_params) -> str:
        return get_request().url_for(name, **path_params)

    def static(name: str) -> str:
        return url_for("static", path=name)

    env = jinja2.Environment(loader=loader, autoescape=True)
    env.globals["url_for"] = url_for
    env.globals["static"] = static
    return env


class JinjaTemplateLookupError(Exception):
    pass


class JinjaResponseBuilder:
    def __init__(self, loader: jinja2.BaseLoader):
        self.env = _build_jinja_env(loader)

    @classmethod
    def with_root(cls, root: str) -> "JinjaResponseBuilder":
        def load_template(name: str) -> str:
            if ":" in name:
                namespace, name = name.split(":", maxsplit=1)
                path = f"{namespace}/templates/{name}"
            else:
                path = f"templates/{name}"
            try:
                with open(f"{root}/{path}", "r") as f:
                    return f.read()
            except OSError:
                raise JinjaTemplateLookupError(path)

        return cls(jinja2.FunctionLoader(load_template))

    def __call__(
        self,
        name: str,
        context: dict,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background=None,
    ) -> JinjaResponse:
        return JinjaResponse(self.env.get_template(name), context, status_code, headers, media_type, background)


def jinja_mixin_with_response_builder(builder: JinjaResponseBuilder):
    """
    Create a controller mixin class with a JinjaResponseBuilder dependency

    :param builder:    the response builder to use
    """

    class _JinjaMixin:
        render: JinjaResponseBuilder = Depends(lambda: builder)

    return _JinjaMixin
