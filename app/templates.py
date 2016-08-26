import os

import jinja2

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def render(handler, template_file, values):
    template = environment.get_template(template_file)
    handler.response.write(template.render(values))
