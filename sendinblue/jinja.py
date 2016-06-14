import jinja2
from jinja2.ext import Extension

# from wagtail.contrib.settings.registry import registry
# from wagtail.wagtailcore.models import Site
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


@jinja2.contextfunction
def sendinblue(context):
    data = render_to_string('sendinblue/js.html', context)
    return mark_safe(data)


class SendinBlueExtension(Extension):
    def __init__(self, environment):
        super(SendinBlueExtension, self).__init__(environment)
        self.environment.globals.update({
            'sendinblue': sendinblue,
        })


settings = SendinBlueExtension
