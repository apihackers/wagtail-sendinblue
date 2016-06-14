from django.conf.urls import include, url
from django.core import urlresolvers
from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem
from django.utils.translation import ugettext_lazy as _

from . import urls


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^sendinblue/', include(urls, namespace="sendinblue")),
    ]


@hooks.register('register_admin_menu_item')
def register_styleguide_menu_item():
    return MenuItem(
        'SendInBlue',
        urlresolvers.reverse('sendinblue:dashboard'),
        classnames='icon icon-fa-envelope',
        order=1000
    )
