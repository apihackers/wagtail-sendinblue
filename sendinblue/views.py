from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from collections import defaultdict

from .client import Client
from .models import SendinBlueSettings


CAMPAIGN_STATUS = (
    ('Sent', _('Sent'), 'send'),
    ('Draft', _('Draft'), 'pencil-square-o'),
    ('Queued', _('Queued'), 'clock-o')
)


def dashboard(request):
    settings = SendinBlueSettings.for_site(request.site)
    if not settings.apikey:
        return render(request, 'sendinblue/admin-welcome.html')

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

    data = api.get_access_tokens()
    access_token = data['data']['access_token']

    return render(request, 'sendinblue/admin.html', {
        'infos': infos,
        'plans': plans,
        'total_contacts': total_contacts,
        'campaigns': get_campaign_stats(api),
        'campaigns_order': ('classic', 'sms', 'trigger'),
        'campaign_status': CAMPAIGN_STATUS,
        'access_token': access_token,
    })


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
