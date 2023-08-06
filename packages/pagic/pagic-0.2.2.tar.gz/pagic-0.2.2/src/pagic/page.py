from dataclasses import dataclass
from typing import Any, Sequence

from flask import render_template, request, url_for
from werkzeug.exceptions import MethodNotAllowed

# from app.flask.lib.view_model import unwrap
# from app.services.json_ld import to_json_ld
# from app.services.opengraph import to_opengraph
# from pagic import url_for

PAGES = {}


def fqdn(cls):
    return f"{cls.__module__}.{cls.__name__}"


def page(cls):
    Page.__all__pages__[fqdn(cls)] = cls
    return cls


def expose(method):
    if not hasattr(method, "_pagic_metadata"):
        method._pagic_metadata = {}
    method._pagic_metadata["exposed"] = True
    return method


class Page:
    __all__pages__ = {}

    name: str
    endpoint: str
    label: str
    path: str | None = None
    layout: str = ""
    menu: str = ""
    parent: Any = None
    children: Sequence = []
    args: dict = {}
    path_args: dict = {}
    query_args: dict = {}
    form_data: dict = {}

    @property
    def template(self) -> str:
        return f"pages/{self.name}.j2"

    @property
    def url(self):
        args = {}
        args.update(self.path_args)
        args.update(self.query_args)
        return url_for(self.endpoint, **args)

    @property
    def endpoint(self):
        return self.name

    @property
    def label(self):
        return self.name.capitalize()

    def context(self):
        """Override in subclasses."""
        return {}

    def get(self):
        return self.render()

    def post(self):
        """Override in subclasses, if needed."""
        raise MethodNotAllowed()

    def render(self):
        ctx = self.context()
        ctx.update(self.extra_context(ctx))
        content = self.content(ctx)
        if not self.layout:
            return content

        ctx["content"] = content
        return render_template(self.layout, **ctx)

    def content(self, ctx):
        return render_template(self.template, **ctx)

    def extra_context(self, ctx):
        d = {}

        if "title" not in ctx:
            d["title"] = self.label

        d["breadcrumbs"] = self.breadcrumbs

        d["json_data"] = {}

        # menus = {
        #     "main": g.nav_data["main"],
        #     "user": g.nav_data["user"],
        # }
        # menus.update(self.menus())
        # d["menus"] = menus
        #
        # if hasattr(self, "view_model") and "model" not in d:
        #     d["model"] = self.view_model

        # if "model" in d:
        #     model = unwrap(d["model"])
        #     d["og_data"] = to_opengraph(model)
        #     d["json_ld"] = to_json_ld(model)

        return d

    def menus(self):
        return {}

    @property
    def breadcrumbs(self):
        breadcrumbs = [
            {"name": self.label, "href": self.url, "current": True},
        ]
        if not self.parent:
            return breadcrumbs

        parent = self.parent()
        while True:
            breadcrumbs += [
                {"name": parent.label, "href": parent.url, "current": False},
            ]
            if not parent.parent:
                break
            parent = parent.parent()

        breadcrumbs.reverse()
        return breadcrumbs


@dataclass
class Route:
    __name__ = "Route"

    def __init__(self, page_class, method_name=""):
        self.page_class = page_class
        self.method_name = method_name

    def __call__(self, **kwargs):
        page = self.page_class()
        page.path_args = kwargs
        page.query_args = request.args
        page.form_data = request.form

        page.args = {}
        page.args.update(page.query_args)
        page.args.update(page.form_data)
        page.args.update(page.path_args)

        if self.method_name:
            return getattr(page, self.method_name)()

        match request.method:
            case "GET":
                return page.get()
            case "POST":
                return page.post()

    @property
    def path(self):
        page_class = self.page_class
        if page_class.path.startswith("/"):
            path = page_class.path
        else:
            path = "/" + page_class.path

        if self.method_name:
            return path + "/" + self.method_name
        else:
            return path

    @property
    def endpoint(self):
        if self.method_name:
            return self.page_class.name + "__" + self.method_name
        else:
            return self.page_class.name

    # @property
    # def __name__(self):
    #     if self.method_name:
    #         return self.page_class.__name__ + "__" + self.method_name
    #     else:
    #         return self.page_class.__name__
