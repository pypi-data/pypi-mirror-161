import pytest
from flask import Flask

from pagic.pagic import Pagic
from tests.pages.index import HomePage


@pytest.fixture
def app():
    app = Flask(__name__)
    pagic = Pagic(app)
    pagic.scan_pages("tests.pages")
    return app


def test_pagic(app):
    pagic = app.extensions["pagic"]
    assert isinstance(pagic, Pagic)
    assert pagic.app is app
    assert pagic.all_page_classes == [HomePage]


def test_home(app, client):
    # rules = list(app.url_map.iter_rules())
    res = client.get("/")
    assert res.status_code == 200


if __name__ == "__main__":
    _app = app()
    _app.run()
