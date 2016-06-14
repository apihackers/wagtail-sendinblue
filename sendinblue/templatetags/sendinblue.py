from django.template import Library

register = Library()


@register.inclusion_tag('sendinblue/js.html', takes_context=True)
def sendinblue():
    pass


@register.filter
def get_item(dictionary, key):
    return dictionary[key]
