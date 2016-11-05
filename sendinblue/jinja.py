import jinja2
from jinja2.ext import Extension

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .models import SendinBlueSettings


@jinja2.contextfunction
def sendinblue(context):
    request = context['request']
    settings = SendinBlueSettings.for_site(request.site)
    ctx = context.get_all()
    ctx.update(sendinblue_settings=settings)
    data = render_to_string('sendinblue/template_tag.html', ctx)
    return mark_safe(data)


class SendinBlueExtension(Extension):
    def __init__(self, environment):
        super(SendinBlueExtension, self).__init__(environment)
        self.environment.globals.update({
            'sendinblue': sendinblue,
        })


settings = SendinBlueExtension
