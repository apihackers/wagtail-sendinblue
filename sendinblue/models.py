import re

from django.db import models
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailcore.models import Orderable
from wagtail.wagtailsnippets.blocks import SnippetChooserBlock
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, FieldRowPanel, StreamFieldPanel

from .utils import mark_safe_lazy
from .widgets import ListSelect, TemplateSelect
from .forms import FormBuilder


API_KEY_HELP = _('You can retrieve your SendInBlue API Key <a target="_blank" href="%s">here</a>')
API_KEY_URL = 'https://account.sendinblue.com/advanced/api'
AUTOMATION_KEY_HELP = _('You can retrieve your SendInBlue Automation API Key <a target="_blank" href="%s">here</a>')
AUTOMATION_KEY_URL = 'https://automation.sendinblue.com/parameters'

RE_IFRAME = re.compile(r'\<iframe width="(?P<width>\d+)" height="(?P<height>\d+)" src="(?P<src>[^\"]+)".*\>\<\/iframe\>')


@register_setting(icon='fa-envelope')
class SendinBlueSettings(BaseSetting):
    class Meta:
        verbose_name = 'SendInBlue'

    apikey = models.CharField(_('API Key'), max_length=255, null=True, blank=True,
                              help_text=mark_safe_lazy(API_KEY_HELP % API_KEY_URL))

    automation = models.CharField(_('Automation API Key'), max_length=255, null=True, blank=True,
                                  help_text=mark_safe_lazy(AUTOMATION_KEY_HELP % AUTOMATION_KEY_URL))

    track_users = models.BooleanField(_('Enable user tracking'), default=True,
                                      help_text=_('Identify users to SendInBlue to provide deeper automation'))

    notify_email = models.EmailField(_('Notification email'), max_length=255, null=True, blank=True,
                                     help_text=_('Notification mail will be sent to this email'))

    panels = [
        FieldPanel('apikey'),
        MultiFieldPanel([
            FieldPanel('automation'),
            FieldPanel('track_users'),
        ], heading=_('Automation')),
        MultiFieldPanel([
            FieldPanel('notify_email'),
        ], heading=_('Notifications')),
    ]


@register_snippet
class SendInBlueForm(models.Model):
    BUTTON_LAYOUTS = (
        ('default', _('Default')),
        ('center', _('Centered')),
        ('full', _('Full width')),
    )
    BUTTON_VARIANTS = (
        ('default', _('Default')),
        ('primary', _('Primary')),
        ('success', _('Success')),
        ('info', _('Info')),
        ('warning', _('Warning')),
        ('danger', _('Danger')),
        ('link', _('Link')),
    )
    # intro = RichTextField(_('Intrso'), null=True, blank=True,
    #                       help_text=_('The introducion displayed on the standalone contact page'))
    # redirect_to = models.CharField()
    name = models.CharField(_('Name'), max_length=255)
    definition = StreamField(FormBuilder())
    submit_text = models.CharField(_('Button text'), null=True, blank=True,
                                   max_length=128, default=_('Submit'),
                                   help_text=_('The submit button text'))
    submit_layout = models.CharField(_('Button layout'), null=True, blank=True, max_length=8,
                                     choices=BUTTON_LAYOUTS, default='default',
                                     help_text=_('The submit button layout'))
    submit_variant = models.CharField(_('Button variant'), null=True, blank=True, max_length=8,
                                      choices=BUTTON_VARIANTS, default='default',
                                      help_text=_('The submit button tint'))
    target_list = models.IntegerField(_('Target list'), null=True, blank=True,
                                      help_text=_('Add the contact to the given list on form submission'))
    send_event = models.CharField(_('Send event'), null=True, blank=True, max_length=255,
                                    help_text=_('Send a custom event on form submission (requires automation)'))
    intro_title = models.CharField(_('Introduction title'), max_length=255, blank=True, null=True,
                                   help_text=_('Title to use for the introduction'))
    intro_subtitle = models.CharField(_('Introduction subtitle'), max_length=255, blank=True, null=True,
                                      help_text=_('A subtitle to use for the introduction'))
    intro_text = RichTextField(_('Introduction text'), blank=True, null=True,
                               help_text=_('The text to use for the introduction'))
    thankyou_title = models.CharField(_('Thank you title'), max_length=255, default=_('Thank you'),
                                      help_text=_('Title text to use for the "thank you" page'))
    thankyou_text = RichTextField(_('Thank you text'), blank=True,
                                  help_text=_('The text to use for the "thank you" page'))
    notify_template = models.IntegerField(_('Notify template'), null=True, blank=True,
                                          help_text=_('Send a notification mail using this template. '
                                                      'The notify mail should be defined in SendInBlue settings'))
    confirm_template = models.IntegerField(_('Confirmation template'), null=True, blank=True,
                                           help_text=_('Send a confirmation mail to the user using this template'))

    panels = [
        FieldPanel('name', classname="full"),
        StreamFieldPanel('definition'),
        MultiFieldPanel([
            FieldPanel('submit_text', classname='full'),
            FieldPanel('submit_layout'),
            FieldPanel('submit_variant'),
        ], heading=_('Submit button'), classname='collapsible'),
        MultiFieldPanel([
            FieldPanel('target_list', widget=ListSelect),
            FieldPanel('confirm_template', widget=TemplateSelect),
            FieldPanel('notify_template', widget=TemplateSelect),
            FieldPanel('send_event'),
        ], heading=_('On submit'), classname='collapsible'),
        MultiFieldPanel([
            FieldPanel('intro_title', classname='full'),
            FieldPanel('intro_subtitle'),
            FieldPanel('intro_text'),
        ], heading=_('Introduction'), classname='collapsible'),
        MultiFieldPanel([
            FieldPanel('thankyou_title', classname='full'),
            FieldPanel('thankyou_text'),
        ], heading=_('Thank you page'), classname='collapsible'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('SendInBlue Form')
        verbose_name_plural = _('SendInBlue Forms')


class SendInBlueFormBlock(SnippetChooserBlock):
    def __init__(self, **kwargs):
        super().__init__(SendInBlueForm, **kwargs)

    class Meta:
        label = _('SendInBlue form')
        icon = 'fa-edit'
        template = 'sendinblue/blocks/form.html'

    def render(self, value, context=None):
        """
        Add `page_context` kwarg to `get_context`.

        Copy-pasted from 'wagtailcore.blocks.base'
        Temporary fix until https://github.com/torchbox/wagtail/issues/2824
        is adressed
        """
        template = getattr(self.meta, 'template', None)
        if not template:
            return self._render_basic_with_context(value, context=context)

        if context is None:
            new_context = self.get_context(value)
        else:
            new_context = dict(context)
            new_context.update(self.get_context(value, page_context=context))

        return mark_safe(render_to_string(template, new_context))

    def get_context(self, value, page_context=None, **kwargs):
        context = super().get_context(value)
        page_context.update(context)
        page_context['form'] = value
        return page_context


class IFrameFormBlock(blocks.CharBlock):
    def get_context(self, value):
        context = super(IFrameFormBlock, self).get_context(value)
        m = RE_IFRAME.match(value)
        if m:
            context.update(iframe=m.groupdict())
        else:
            context.update(iframe={
                'src': value,
                'width': 540,
                'height': 300,
            })
        return context

    class Meta:
        template = 'sendinblue/blocks/iframe-form.html'
