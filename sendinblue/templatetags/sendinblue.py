from django.template import Library

from ..models import SendinBlueSettings

register = Library()


@register.inclusion_tag('sendinblue/template_tag.html', takes_context=True)
def sendinblue(context):
    request = context['request']
    settings = SendinBlueSettings.for_site(request.site)
    context.update(sendinblue_settings=settings)
    return context


@register.filter
def get_item(dictionary, key):
    return dictionary[key]
