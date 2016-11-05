# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-05 12:07
from __future__ import unicode_literals

from django.db import migrations, models
import sendinblue.forms
import wagtail.wagtailcore.blocks
import wagtail.wagtailcore.fields
import wagtail.wagtailembeds.blocks
import wagtail.wagtailimages.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('sendinblue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendinblueform',
            name='intro_subtitle',
            field=models.CharField(blank=True, help_text='A subtitle to use for the introduction', max_length=255, null=True, verbose_name='Introduction subtitle'),
        ),
        migrations.AddField(
            model_name='sendinblueform',
            name='intro_text',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, help_text='The text to use for the introduction', null=True, verbose_name='Introduction text'),
        ),
        migrations.AddField(
            model_name='sendinblueform',
            name='intro_title',
            field=models.CharField(blank=True, help_text='Title to use for the introduction', max_length=255, null=True, verbose_name='Introduction title'),
        ),
        migrations.AlterField(
            model_name='sendinblueform',
            name='definition',
            field=wagtail.wagtailcore.fields.StreamField((('text_field', wagtail.wagtailcore.blocks.StructBlock((('label', wagtail.wagtailcore.blocks.CharBlock(help_text='The text displayed aside the field', label='Label', max_length=255, required=False)), ('required', wagtail.wagtailcore.blocks.BooleanBlock(default=True, label='Required', required=False)), ('attribute', sendinblue.forms.SendInBlueAttributeBlock(required=True)), ('placeholder', wagtail.wagtailcore.blocks.CharBlock(help_text='The text displayed inside the field when empty', label='Placeholder', max_length=255, required=False))))), ('text', wagtail.wagtailcore.blocks.RichTextBlock()), ('image', wagtail.wagtailimages.blocks.ImageChooserBlock()), ('html', wagtail.wagtailcore.blocks.RawHTMLBlock()), ('embed', wagtail.wagtailembeds.blocks.EmbedBlock()))),
        ),
    ]
