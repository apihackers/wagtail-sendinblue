from django.conf.urls import include, url
from django.core import urlresolvers
from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, ThumbnailMixin, modeladmin_register as register_admin,
)

from . import urls
from .models import SendInBlueForm, SendinBlueSettings
from .views import dashboard, iframe_factory, welcome


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^sendinblue/', include([
            url(r'^dashboard/$', dashboard, name='dashboard'),
            url(r'^lists/$', iframe_factory('lists/index', _('Lists')), name='lists'),
            url(r'^contacts/$', iframe_factory('users/list', _('Contacts')), name='contacts'),
            url(r'^campaigns/$', iframe_factory('camp/listing', _('Campaigns')), name='campaigns'),
            url(r'^templates/$', iframe_factory('camp/listing/type/template', _('Templates')), name='templates'),
            url(r'^automation/$', iframe_factory('https://automation.sendinblue.com/scenarios', _('Automation')), name='automation'),
            url(r'^statistics/$', iframe_factory('camp/message', _('Statistics')), name='statistics'),
            url(r'^settings/$', iframe_factory('users/settings', _('Settings')), name='settings'),
        ], namespace="sendinblue")),
    ]


class FormAdmin(ModelAdmin):
    model = SendInBlueForm
    menu_icon = 'fa-edit'  # change as required
    menu_label = _('Forms')
    list_display = ('name', )
    list_filter = ('name', )
    search_fields = ('name', )

    def need_api_key(self, view_name, request, *args, **kwargs):
        settings = SendinBlueSettings.for_site(request.site)
        if not settings.apikey:
            return welcome(request)
        view_func = getattr(super(), view_name)
        return view_func(request, *args, **kwargs)

    def index_view(self, request, *args, **kwargs):
        return self.need_api_key('index_view', request, *args, **kwargs)

    def create_view(self, request, *args, **kwargs):
        return self.need_api_key('create_view', request, *args, **kwargs)

    def edit_view(self, request, *args, **kwargs):
        return self.need_api_key('edit_view', request, *args, **kwargs)


@register_admin
class SendInBlueAdminGroup(ModelAdminGroup):
    menu_label = 'SendInBlue'
    menu_icon = 'fa-envelope'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    menu_items = (
        (_('Dashboard'), 'sendinblue:dashboard', 'fa-dashboard'),
        (_('Lists'), 'sendinblue:lists', 'fa-list'),
        (_('Contacts'), 'sendinblue:contacts', 'fa-users'),
        (_('Campaigns'), 'sendinblue:campaigns', 'fa-briefcase'),
        (_('Templates'), 'sendinblue:templates', 'fa-newspaper-o'),
        (_('Automation'), 'sendinblue:automation', 'fa-code-fork'),
    )
    items = (
        FormAdmin,
    )
    menu_items_after = (
        (_('Statistics'), 'sendinblue:statistics', 'fa-area-chart'),
        (_('Settings'), 'sendinblue:settings', 'fa-cogs'),
    )

    def get_submenu_items(self):
        items = super().get_submenu_items()
        for (title, urlname, icon) in reversed(self.menu_items):
            items.insert(0, MenuItem(
                title,
                urlresolvers.reverse(urlname),
                classnames='icon icon-{0}'.format(icon),
                order=1
            ))
        for (idx, (title, urlname, icon)) in enumerate(self.menu_items_after):
            items.append(MenuItem(
                title,
                urlresolvers.reverse(urlname),
                classnames='icon icon-{0}'.format(icon),
                order=10000 + idx
            ))
        return items
