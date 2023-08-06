from pagic.html import h


def test():
    assert h("h1", "test") == "<h1>test</h1>"
    assert h("h1", {}, _=["test"]) == "<h1>test</h1>"
    assert h("h1", ["test", "toto"]) == "<h1>test\ntoto</h1>"
