from pagic import Page

# language=jinja2
TEMPLATE = """
<h1>Hello world</h1>

<p>Yadda yadda.</p>
"""


class HomePage(Page):
    name = "home"
    label = "Home"
    path = "/"

    layout = "tests/base.j2"
    template = "tests/home.j2"
