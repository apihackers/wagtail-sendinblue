from django import forms
from django.forms import fields
from django.utils.functional import cached_property, lazy
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Site
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock

from .client import Client


class SendInBlueAttributeBlock(blocks.FieldBlock):
    class Meta:
        label = _('Attributes')
        icon = 'fa-user'

    @cached_property
    def field(self):
        from .models import SendinBlueSettings
        site = Site.objects.first()
        settings = SendinBlueSettings.for_site(site)
        api = Client(settings.apikey)
        return forms.ChoiceField(choices=self.get_choices(api))

    def get_choices(self, api):
        data = api.get_attributes()
        attributes = data['data']['normal_attributes']
        names = [a['name'] for a in attributes]
        names.insert(0, 'EMAIL')
        return map(lambda n: (n, n), names)


class TextFieldBlock(blocks.StructBlock):
    label = blocks.CharBlock(label=_('Label'), max_length=255, required=False,
                             help_text=_('The text displayed aside the field'))
    required = blocks.BooleanBlock(label=_('Required'), default=True, required=False)
    attribute = SendInBlueAttributeBlock(required=True)

    placeholder = blocks.CharBlock(label=_('Placeholder'), max_length=255, required=False,
                                   help_text=_('The text displayed inside the field when empty'))

    class Meta:
        label = _('SendInBlue field')
        icon = 'fa-edit'
        template = 'sendinblue/blocks/form-field.html'

    def get_context(self, value):
        context = super().get_context(value)
        context['field'] = value
        return context


class TextAreaBlock(blocks.StructBlock):
    label = blocks.CharBlock(label=_('Label'), max_length=255, required=False,
                             help_text=_('The text displayed aside the field'))
    required = blocks.BooleanBlock(label=_('Required'), default=True, required=False)
    rows = blocks.IntegerBlock(label=_('Rows'), default=3, required=True)
    attribute = blocks.CharBlock(label=_('Attribute'), max_length=255, required=True, default='message',
                             help_text=_('The attribute used for transactional template'))
    placeholder = blocks.CharBlock(label=_('Placeholder'), max_length=255, required=False,
                                   help_text=_('The text displayed inside the field when empty'))

    class Meta:
        label = _('SendInBlue textarea')
        icon = 'placeholder'
        template = 'sendinblue/blocks/textarea.html'

    def get_context(self, value):
        context = super().get_context(value)
        context['textarea'] = value
        return context


class FormBuilder(blocks.StreamBlock):
    text_field = TextFieldBlock()
    textarea = TextAreaBlock()
    text = blocks.RichTextBlock()
    image = ImageChooserBlock()
    html = blocks.RawHTMLBlock()
    embed = EmbedBlock()


class SendInBlueDynamicForm(forms.Form):
    '''Dyanmic form built from a form builder'''
    def __init__(self, data=None, builder=None, **kwargs):
        super().__init__(data, **kwargs)
        for block in builder:
            if block.block_type == 'text_field':
                field = dict((k, v.value) for k, v in block.value.bound_blocks.items())
                self.fields[field['attribute']] = forms.CharField(required=field['required'])
            elif block.block_type == 'textarea':
                field = dict((k, v.value) for k, v in block.value.bound_blocks.items())
                self.fields[field['attribute']] = forms.CharField(required=field['required'])
