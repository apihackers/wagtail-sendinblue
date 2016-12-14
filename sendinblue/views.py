from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.vary import vary_on_headers

from .client import Client, AutomationClient
from .forms import SendInBlueDynamicForm
from .models import SendinBlueSettings, SendInBlueForm


CAMPAIGN_STATUS = (
    ('Sent', _('Sent'), 'send'),
    ('Draft', _('Draft'), 'pencil-square-o'),
    ('Queued', _('Queued'), 'clock-o')
)

SENDINBLUE_URL = 'https://www.sendinblue.com/?ae=312'
SENDINBLUE_LINK = '<a href="{0}" title="SendInBlue" target="_blank">SendInBlue</a>'.format(SENDINBLUE_URL)


def welcome(request):
    '''Render the welcome screen'''
    return render(request, 'sendinblue/admin-welcome.html', {
        'sendinblue_url': SENDINBLUE_URL,
        'sendinblue_link': SENDINBLUE_LINK,
    })


def dashboard(request):
    '''Display the admin dahsboard view'''
    settings = SendinBlueSettings.for_site(request.site)
    if not settings.apikey:
        return welcome(request)

    api = Client(settings.apikey)

    data = api.get_account()
    infos = data['data'][-1]
    plans = data['data'][:-1]

    data = api.get_lists()
    list_ids = []
    if data['code'] == 'success':
        for listdata in data['data']['lists']:
            list_ids.append(listdata['id'])
        users_data = api.display_list_users(list_ids)
        total_contacts = users_data['data']['total_list_records']
    else:
        total_contacts = 0

    return render(request, 'sendinblue/admin.html', {
        'title': 'SendInBlue - {0}'.format(_('Dashboard')),
        'infos': infos,
        'plans': plans,
        'total_contacts': total_contacts,
        'campaigns': get_campaign_stats(api),
        'campaigns_order': ('classic', 'sms', 'trigger'),
        'campaign_status': CAMPAIGN_STATUS,
    })


def iframe_factory(name, title):
    def view(request):
        settings = SendinBlueSettings.for_site(request.site)
        if not settings.apikey:
            return welcome(request)

        api = Client(settings.apikey)

        data = api.get_access_tokens()
        access_token = data['data']['access_token']

        ctx = {
            # 'name': name,
            'title': title,
            'access_token': access_token,
        }
        if name.startswith('http'):
            ctx.update(url=name)
        else:
            ctx.update(name=name)

        return render(request, 'sendinblue/admin-iframe.html', ctx)

    return view


def get_campaign_stats(api):
    response = api.get_campaigns_v2()

    data = {
        'classic': {
            'name': _('Email campaigns'),
            'icon': 'fa-envelope',
            'stats':  defaultdict(lambda: 0),
        },
        'sms': {
            'name': _('SMS campaigns'),
            'icon': 'fa-mobile',
            'stats':  defaultdict(lambda: 0),
        },
        'trigger': {
            'name': _('Trigger marketing'),
            'icon': 'fa-toggle-right',
            'stats':  defaultdict(lambda: 0),
        }
    }

    campaigns = response['data']['campaign_records'] if response['code'] == api.OK else []
    for campaign in campaigns:
        if campaign['type'] == 'template' or not campaign['type'] == '':
            continue
        data[campaign['type']]['stats'][campaign['status']] += 1

    return data


@vary_on_headers('HTTP_X_REQUESTED_WITH')
def submit_form(request, pk):
    sib_form = SendInBlueForm.objects.get(pk=int(pk))
    if request.method == 'POST':
        form = SendInBlueDynamicForm(request.POST, builder=sib_form.definition)
        if form.is_valid():
            data = dict(**form.cleaned_data)
            email = data.pop('EMAIL')
            settings = SendinBlueSettings.for_site(request.site)
            api = Client(settings.apikey)

            api.create_update_user(email, data)

            if sib_form.target_list:
                api.add_users_list(sib_form.target_list, [email])

            data_formated = dict((k, v.replace('\n', '<br/>')) for k, v in data.items())
            data_formated.update(EMAIL=email)

            if sib_form.confirm_template:
                api.send_transactional_template(sib_form.confirm_template, email, attr=data_formated)
            if sib_form.notify_template and settings.notify_email:
                api.send_transactional_template(sib_form.notify_template, settings.notify_email, attr=data_formated)

            if settings.automation:
                session_id = request.session.session_key
                data['session_id'] = session_id
                automation = AutomationClient(settings.automation)
                if settings.track_users or sib_form.send_event:
                    automation.identify(email, **data)
                if sib_form.send_event:
                    automation.track(sib_form.send_event, session_id=session_id, email_id=email)

            if request.is_ajax():
                return JsonResponse({
                    'title': sib_form.thankyou_title,
                    'text': sib_form.thankyou_text,
                })
            else:
                return render(request, 'sendinblue/thankyou.html', {
                    'form': sib_form,
                })
