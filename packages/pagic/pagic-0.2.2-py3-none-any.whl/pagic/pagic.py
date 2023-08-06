"""Main module."""
import types
from collections import defaultdict

from devtools import debug
from flask import Flask, g

from pagic.page import Page, Route
from pagic.routing import url_for
from pagic.scanner import scan_modules


class Pagic:
    app: Flask | None
    roots: list
    all_page_classes: list

    def __init__(self, app: Flask | None = None):
        self.roots = []
        self.all_page_classes = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        if "pagic" in app.extensions:
            raise RuntimeError(
                "This extension is already registered on this Flask app."
            )

        self.app = app
        app.extensions["pagic"] = self

        app.before_request(self.before_request)
        app.context_processor(self.inject_extra_context)
        app.template_global("url_for")(url_for)

    def scan_pages(self, module_name: str):
        if not module_name:
            app_name = self.app.name
            module_name = app_name + ".pages"

        def register_module(module):
            for obj in module.__dict__.values():
                if not isinstance(obj, type) or not issubclass(obj, Page):
                    continue

                page = obj
                debug(page)
                if not hasattr(page, "name") or not page.name:
                    continue

                self.register_page(page)

        scan_modules(module_name, callback=register_module)

    def before_request(self):
        g.menus = defaultdict(list)

        for page_class in self.all_page_classes:
            menu_name = page_class.menu
            if not menu_name:
                continue

            page: Page = page_class()
            endpoint = page.endpoint
            label = page.label
            url = url_for(endpoint)
            menu_item = {
                "label": label,
                "endpoint": endpoint,
                "url": url,
                "active": False,
            }
            g.menus[menu_name].append(menu_item)

    def inject_extra_context(self):
        return {
            "url_for": url_for,
            "pagic": self,
        }

    # TODO
    # def register_macros(app, path):
    #     scanner = venusian.Scanner()
    #     scanner.scan(importlib.import_module(path))
    #
    #     for macro in MACROS:
    #         app.template_global(macro.__name__)(macro)

    #
    # New registration API
    #
    def register_roots(self, roots):
        self.roots = roots
        for page_class in roots:
            self.register_page(page_class)

    def register_page(self, page_class, ancestors: list | None = None):
        self.all_page_classes.append(page_class)

        if ancestors is None:
            ancestors = []

        methods = ["GET", "POST"]
        route = Route(page_class)

        # if hasattr(page_class, "routes"):
        #     for _route in page_class.routes:
        #         self.app.add_url_rule(_route, page_class.name, route, methods=methods)
        #     return

        if page_class.path is None:
            page_class.path = page_class.name

        path_list = []
        for p in ancestors + [page_class]:
            if p.path:
                path_list.append(p.path)
        path = "/" + "/".join(path_list)
        self.app.add_url_rule(path, route.endpoint, route, methods=methods)

        if hasattr(page_class, "children"):
            for child_class in page_class.children:
                self.register_page(child_class, ancestors + [page_class])

        # if hasattr(cls, "routes"):
        #     for _route in cls.routes:
        #         blueprint.add_url_rule(_route, route.endpoint, route, methods=methods)
        #     return
        #
        # if not hasattr(cls, "path"):
        #     cls.path = cls.name

        # blueprint.add_url_rule(cls.path, route.endpoint, route, methods=methods)

        for method_name in self.get_exposed_method_names(page_class):
            route = Route(page_class, method_name)
            self.app.add_url_rule(route.path, route.endpoint, route, methods=methods)

    @staticmethod
    def get_exposed_method_names(page_class):
        result = []
        for name, method in vars(page_class).items():
            if not isinstance(method, types.FunctionType):
                continue

            if not hasattr(method, "_pagic_metadata"):
                continue

            metadata = method._pagic_metadata  # type: ignore
            if not metadata.get("exposed"):
                continue

            result.append(name)

        return result

    #
    # Old API
    #
    # def register_pages(self, path=None):
    #     self.scan_pages(path)
    #
    #     for page_cls in Page.__all__pages__.values():
    #         print(f"Registering pags: {page_cls}")
    #         self.register_page(page_cls)
    #
    # def scan_pages(self, path):
    #     if not path:
    #         path = "tests"
    #     module = importlib.import_module(path)
    #     scanner = venusian.Scanner()
    #     scanner.scan(module)
    #
    # def register_page(self, cls):
    #     methods = ["GET", "POST"]
    #
    #     route = Route(cls)
    #     if hasattr(cls, "routes"):
    #         for _route in cls.routes:
    #             self.app.add_url_rule(_route, cls.name, route, methods=methods)
    #         return
    #
    #     if not hasattr(cls, "path"):
    #         cls.path = cls.name
    #
    #     self.app.add_url_rule(cls.path, cls.name, route, methods=methods)
