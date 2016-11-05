from django.forms import Select
from django.utils.functional import lazy
from wagtail.wagtailcore.models import Site

from .client import Client


class ApiSelect(Select):
    def __init__(self, attrs=None, **kwargs):
        super(ApiSelect, self).__init__(attrs, ())
        self.choices = lazy(self._get_choices, tuple)()

    def _get_choices(self):
        from .models import SendinBlueSettings
        site = Site.objects.first()
        settings = SendinBlueSettings.for_site(site)
        api = Client(settings.apikey)
        return self.get_choices(api)

    def get_choices(self, api):
        raise NotImplementedError


class AttributesSelect(ApiSelect):
    def get_choices(self, api):
        data = api.get_attributes()
        attributes = data['data']['normal_attributes']
        names = [a['name'] for a in attributes]
        return map(lambda n: (n, n), names)


class ListSelect(ApiSelect):
    def get_choices(self, api):
        data = api.get_lists()
        choices = [
            (l['id'], l['name'])
            for l in data['data']['lists']
        ]
        return choices if self.is_required else [(None, '')] + choices
