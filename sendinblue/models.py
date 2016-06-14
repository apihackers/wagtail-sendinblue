from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.contrib.settings.models import BaseSetting, register_setting

from .utils import mark_safe_lazy


API_KEY_HELP = _('You can retrieve your SendInBlue API Key <a target="_blank" href="%s">here</a>')
API_KEY_URL = 'https://my.sendinblue.com/advanced/apikey'
AUTOMATION_KEY_HELP = _('You can retrieve your SendInBlue Automation API Key <a target="_blank" href="%s">here</a>')
AUTOMATION_KEY_URL = 'https://automation.sendinblue.com/parameters'


@register_setting(icon='fa-envelope')
class SendinBlueSettings(BaseSetting):
    class Meta:
        verbose_name = 'SendInBlue'

    apikey = models.CharField(_('API Key'), max_length=255, null=True, blank=True,
                              help_text=mark_safe_lazy(API_KEY_HELP % API_KEY_URL))

    automation = models.CharField(_('Automation API Key'), max_length=255, null=True, blank=True,
                                  help_text=mark_safe_lazy(AUTOMATION_KEY_HELP % AUTOMATION_KEY_URL))
