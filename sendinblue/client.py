'''
A pure python 3 client for SendinBlue API 2.0

Based on:

- https://github.com/mailin-api/mailin-api-python/blob/master/V2.0/mailin.py
- https://plugins.trac.wordpress.org/browser/mailin/trunk/inc/mailin.php

'''
import requests

from requests.auth import AuthBase

DEFAULT_TIMEOUT = 30
BASE_URL = 'https://api.sendinblue.com/v2.0'
AUTOMATION_API_URL = 'https://in-automate.sendinblue.com/p'


class ApiKey(AuthBase):
    '''Attaches SendInBlue API Key Authentication'''
    def __init__(self, apikey):
        self.apikey = apikey

    def __call__(self, r):
        r.headers['api-key'] = self.apikey
        return r


class Client(object):
    '''A SendInBlue API 2.0 Client'''
    OK = 'success'

    def __init__(self, apikey, timeout=None):
        self.apikey = apikey
        self.timeout = timeout

    def _url(self, path):
        return '/'.join((BASE_URL, path))

    def _kwargs(self, timeout=None):
        return {
            'auth': ApiKey(self.apikey),
            'headers': {'Content-Type': 'application/json'},
            'timeout': timeout or self.timeout or DEFAULT_TIMEOUT,
        }

    def get(self, path, params=None, timeout=None, **kwargs):
        '''GET operation helper'''
        response = requests.get(self._url(path), params=params or kwargs, **self._kwargs(timeout))
        return response.json()

    def post(self, path, data=None, timeout=None, **kwargs):
        '''POST operation helper'''
        response = requests.post(self._url(path), json=data or kwargs, **self._kwargs(timeout))
        return response.json()

    def put(self, path, data=None, timeout=None, **kwargs):
        '''PUT operation helper'''
        response = requests.put(self._url(path), json=data or kwargs, **self._kwargs(timeout))
        return response.json()

    def delete(self, path, timeout=None, **kwargs):
        '''DELETE operation helper'''
        response = requests.delete(self._url(path), **self._kwargs(timeout))
        return response.json()

    def get_access_tokens(self):
        '''Get an access token.

        Undocumented API, extracted from
        https://plugins.trac.wordpress.org/browser/mailin/trunk/inc/mailin.php
        '''
        return self.get('account/token')

    def delete_token(self, token):
        '''Delete an access token.

        Undocumented API, extracted from
        https://plugins.trac.wordpress.org/browser/mailin/trunk/inc/mailin.php

        :param str token: The access token to delete
        '''
        return self.post('account/deletetoken', token=token)

    def get_account(self):
        '''Get account informations'''
        return self.get('account')

    def get_smtp_details(self):
        '''Get SMTP details'''
        return self.get('account/smtpdetail')

    def create_child_account(self, child_email, password, company_org,
                             first_name, last_name,
                             credits=None, associate_ip=None):
        '''Create a child account.

        :param str child_email: Email address of Reseller child
        :param str password: Password of Reseller child to login
        :param str company_org: Name of Reseller child's company
        :param str first_name: First name of Reseller child
        :param str last_name: Last name of Reseller child
        :params object credits: Number of email & sms credits respectively,
            which will be assigned to the Reseller child's account
            - email_credit (*int*) number of email credits
            - sms_credit (*int*) Number of sms credts
        :params list associate_ip: Associate dedicated IPs to reseller child.
            You can use commas to separate multiple IPs
        '''
        return self.post('account', child_email=child_email, password=password,
                         company_org=company_org,
                         first_name=first_name, last_name=last_name,
                         credits=credits, associate_ip=associate_ip)

    def update_child_account(self, auth_key, company_org=None,
                             first_name=None, last_name=None,
                             associate_ip=None, disassociate_ip=None):
        '''Update a child account.

        :param str auth_key: 16 character authorization key of Reseller child to be modified
        :param str company_org: Name of Reseller child's company
        :param str first_name: First name of Reseller child
        :param str last_name: Last name of Reseller child
        :param str password: Password of Reseller child to login
        :params list associate_ip: Associate dedicated IPs to reseller child.
            You can use commas to separate multiple IPs
        :params list disassociate_ip: Disassociate dedicated IPs to reseller child.
            You can use commas to separate multiple IPs
        '''
        return self.put('account', auth_key=auth_key, company_org=company_org,
                        first_name=first_name, last_name=last_name,
                        associate_ip=associate_ip,
                        disassociate_ip=disassociate_ip)

    def delete_child_account(self, auth_key):
        '''Delete a child account.

        :param str auth_key: 16 character authorization key of Reseller child to be deleted
        '''
        return self.delete('account/{key}'.format(auth_key))

    def get_reseller_child(self, auth_key):
        '''Get a reseller child account.

        :param str|object auth_key:
            a 16 character authorization key of a reseller child or an object.
            Example : To get the details of more than one child account,
            use, {"key1":"abC01De2fGHI3jkL","key2":"mnO45Pq6rSTU7vWX"}
        '''
        return self.post('account/getchildv2', auth_key=auth_key)

    def add_remove_child_credits(self, auth_key, add_credit=None, rmv_credit=None):
        '''Add/Remove a reseller child's Email/SMS credits.

        :param str auth_key: 16 character authorization key of Reseller child to modify credits
        :param dict add_credit: Number of email & sms credits to be added.
            (Mandatory: if rmv_credit is empty)
            You can assign either email or sms credits, one at a time other will remain 0.
            - ``email_credit`` (*int*): number of email credits
            - ``sms_credit`` (*int*): Number of sms credts
        :param dict rmv_credit: Number of email & sms credits to be removed.
            (Mandatory: if add_credits is empty)
            You can assign either email or sms credits, one at a time other will remain 0.
            - ``email_credit`` (*int*): number of email credits
            - ``sms_credit`` (*int*): Number of sms credts
        '''
        return self.post('account/addrmvcredit',
                         auth_key=auth_key,
                         add_credit=add_credit,
                         rmv_credit=rmv_credit)

    def send_sms(self, to, _from, text, web_url=None, tag=None, type='marketing'):
        '''Send a transactional SMS.

        :param str to: The mobile number to send SMS to with country code
        :param str _from: The name of the sender.
            The number of characters is limited to 11 (alphanumeric format)
        :param str text: The text of the message.
            The maximum characters used per SMS is 160, if used more than that,
            it will be counted as more than one SMS
        :param str web_url:
            The web URL that can be called once the message is successfully delivered
        :param str tag: The tag that you can associate with the message
        :param str type: Type of message.
            Possible values - marketing (default) & transactional.
            You can use marketing for sending marketing SMS,
            & for sending transactional SMS, use transactional type
        '''
        return self.post('sms', {
            'to': to, 'from': _from, 'text': text,
            'web_url': web_url, 'tag': tag, 'type': type
        })

    def create_sms_campaign(self, name, sender=None, content=None, bat=None, listid=None,
                            exclude_list=None, scheduled_date=None, send_now=0):
        '''Create & Schedule your SMS campaigns.

        :param str name: Name of the SMS campaign
        :param str sender: This allows you to customize the SMS sender.
            The number of characters is limited to 11 ( alphanumeric format )
        :param str content: Content of the message.
            The maximum characters used per SMS is 160, if used more than that,
            it will be counted as more than one SMS
        :param str bat: Mobile number with the country code to send test SMS.
            The mobile number defined here should belong to one of your contacts
            in SendinBlue account and should not be blacklisted
        :param list listid: These are the list ids to which the SMS campaign is sent
            (Mandatory if scheduled_date is not empty)
        :param list exclude_list:
            These are the list ids which will be excluded from the SMS campaign
        :param str scheduled_date: The day on which the SMS campaign is supposed to run
        :param int send_now: Flag to send campaign now.
            - 0 *(default)* means campaign can't be send now
            - 1 means campaign ready to send now
        '''
        # TODO: process dates
        return self.post('sms',
                         name=name,
                         sender=sender,
                         content=content,
                         bat=bat,
                         listid=listid,
                         exclude_list=exclude_list,
                         scheduled_date=scheduled_date,
                         send_now=send_now)

    def update_sms_campaign(self, id, name=None, sender=None, content=None, bat=None,
                            listid=None, exclude_list=None, scheduled_date=None, send_now=0):
        '''Update your SMS campaigns.
        :param int id: Id of the SMS campaign
        :param str name: Name of the SMS campaign
        :param str sender: This allows you to customize the SMS sender.
            The number of characters is limited to 11 ( alphanumeric format )
        :param str content: Content of the message.
            The maximum characters used per SMS is 160, if used more than that,
            it will be counted as more than one SMS
        :param str bat: Mobile number with the country code to send test SMS.
            The mobile number defined here should belong to one of your contacts
            in SendinBlue account and should not be blacklisted
        :param list listid: These are the list ids to which the SMS campaign is sent
            (Mandatory if scheduled_date is not empty)
        :param list exclude_list:
            These are the list ids which will be excluded from the SMS campaign
        :param str scheduled_date: The day on which the SMS campaign is supposed to run
        :param int send_now: Flag to send campaign now.
            - 0 *(default)* means campaign can't be send now
            - 1 means campaign ready to send now
        '''
        # TODO: process dates
        return self.put('sms/{id}'.format(id),
                        name=name,
                        sender=sender,
                        content=content,
                        bat=bat,
                        listid=listid,
                        exclude_list=exclude_list,
                        scheduled_date=scheduled_date,
                        send_now=send_now)

    def send_bat_sms(self, id, to):
        '''Send a Test SMS.

        :param int id: Id of the SMS campaign [Mandatory]
        :pram str to: Mobile number with the country code to send test SMS.
            The mobile number defined here should belong to one of your contacts
            in SendinBlue account and should not be blacklisted
        '''
        return self.get('sms/{id}'.format(id), to=to)

    def get_campaigns_v2(self, type=None, status=None, page=None, page_limit=None):
        '''
        Get all campaigns detail.

        :param str type: Type of campaign. Possible values - classic, trigger, sms, template
        :param str status: Status of campaign. Possible values -
            draft, sent, archive, queued, suspended, in_process, temp_active, temp_inactive
        :param int page: Page number.
            Maximum number of records per request is 500,
            if there are more than 500 campaigns then
            you can use this parameter to get next 500 results
        :param int page_limit: This should be a valid number between 1-500 [Optional]
        '''
        url = 'campaign/detailsv2/'
        if not (type is None or status is None or page is None or page_limit is None):
            url += 'type/{type}/status/{status}/page/{page}/page_limit/{page_limit}/'
            url = url.format(**locals())
        return self.get(url)

    def get_campaign_v2(self, id):
        '''Get a particular campaign detail.

        :param int id: Unique Id of the campaign
        '''
        return self.get('campaign/{id}/detailsv2/'.format(id=id))

    def create_campaign(self, name, subject, category=None, from_name=None, bat=None,
                        html_content=None, html_url=None, listid=None, scheduled_date=None,
                        from_email=None, reply_to=None, to_field=None, exclude_list=None,
                        attachment_url=None, inline_image=0, mirror_active=1, send_now=0):
        '''Create and Schedule your campaigns.

        :param str name: Name of the campaign
        :param str subject: Subject of the campaign
        :param str category: Tag name of the campaign
        :param str from_name: Sender name from which the campaign emails are sent
            (Mandatory for Dedicated IP clients,
            please make sure that the sender details are defined here, and in case of no sender,
            you can add them also via API & for Shared IP clients, if sender exists)
        :param str bat: Email address for test mail
        :param str html_content: Body of the content.
            The HTML content field must have more than 10 characters
            (Mandatory if html_url is empty)
        :param str html_url: Url which content is the body of content
            (Mandatory if html_content is empty)
        :param list listid: These are the lists to which the campaign has been sent
            (Mandatory if scheduled_date is not empty)
        :param str scheduled_date: The day on which the campaign is supposed to run
        :param str from_email: Sender email from which the campaign emails are sent
            (Mandatory for Dedicated IP clients,
            please make sure that the sender details are defined here, and in case of no sender,
            you can add them also via API & for Shared IP clients, if sender exists)
        :param str reply_to: The reply to email in the campaign emails
        :param str to_field: This is to personalize the <<To>> Field.
            If you want to include the first name and last name of your recipient,
            add [PRENOM] [NOM] To use the contact attributes here,
            these should already exist in SendinBlue account
        :param list exclude_list: These are the lists which must be excluded from the campaign
        :param str attachment_url: Provide the absolute url of the attachment
        :param int inline_image: Status of inline image. Possible values:
            - 0 *(default)* means image can't be embedded
            - 1 means image can be embedded, in the email
        :param int mirror_active: Status of mirror links in campaign. Possible values:
            - 0 means mirror links are deactivated
            - 1 (*default)* means mirror links are activated, in the campaign
        :param int send_now: Flag to send campaign now. Possible values:
            - 0 *(default)* means campaign can't be send now
            - 1 means campaign ready to send now
        '''
        # TODO: process dates
        return self.post('campaign',
                         name=name, subject=subject, category=category, from_name=from_name,
                         bat=bat, html_content=html_content, html_url=html_url, listid=listid,
                         scheduled_date=scheduled_date, from_email=from_email, reply_to=reply_to,
                         to_field=to_field, exclude_list=exclude_list,
                         attachment_url=attachment_url, inline_image=inline_image,
                         mirror_active=mirror_active, send_now=send_now)

    def delete_campaign(self, id):
        '''Delete your campaigns.

        :param int id: Id of campaign to be deleted
        '''
        return self.delete('campaign/{id}'.format(id=id))

    def update_campaign(self, id, name=None, subject=None, category=None, from_name=None, bat=None,
                        html_content=None, html_url=None, listid=None, scheduled_date=None,
                        from_email=None, reply_to=None, to_field=None, exclude_list=None,
                        attachment_url=None, inline_image=0, mirror_active=1, send_now=0):
        '''Update your campaign.

        :param int id: Id of campaign to be modified
        :param str name: Name of the campaign
        :param str category: Tag name of the campaign
        :param str subject: Subject of the campaign.
        :param str from_name: Sender name from which the campaign emails are sent
            (Mandatory for Dedicated IP clients,
            please make sure that the sender details are defined here,
            and in case of no sender, you can add them also via API & for Shared IP clients,
            if sender exists)
        :param str bat: Email address for test mail
        :param str html_content: Body of the content.
            The HTML content field must have more than 10 characters
        :param str html_url: Url which content is the body of content
        :param list listid These are the lists to which the campaign has been sent
            (Mandatory if scheduled_date is not empty)
        :param str scheduled_date: The day on which the campaign is supposed to run
        :param str from_email: Sender email from which the campaign emails are sent
            (Mandatory for Dedicated IP clients,
            please make sure that the sender details are defined here,
            and in case of no sender, you can add them also via API & for Shared IP clients,
            if sender exists)
        :param str reply_to: The reply to email in the campaign emails
        :param str to_field: This is to personalize the <<T>> Field.
            If you want to include the first name and last name of your recipient,
            add [PRENOM] [NOM].
            To use the contact attributes here, these should already exist in SendinBlue account
        :param list exclude_list: These are the lists which must be excluded from the campaign
        :param str attachment_url: Provide the absolute url of the attachment
        :param int inline_image: Status of inline image. Possible values:
            - 0 *(default)* means image can't be embedded
            - 1 means image can be embedded, in the email
        :param int mirror_active: Status of mirror links in campaign. Possible values:
            - 0 means mirror links are deactivated
            - 1 (*default)* means mirror links are activated, in the campaign
        :param int send_now: Flag to send campaign now. Possible values:
            - 0 *(default)* means campaign can't be send now
            - 1 means campaign ready to send now
        '''
        # TODO: process dates
        return self.put('campaign/{id}'.format(id=id),
                        name=name, subject=subject, category=category, from_name=from_name,
                        bat=bat, html_content=html_content, html_url=html_url, listid=listid,
                        scheduled_date=scheduled_date, from_email=from_email, reply_to=reply_to,
                        to_field=to_field, exclude_list=exclude_list,
                        attachment_url=attachment_url, inline_image=inline_image,
                        mirror_active=mirror_active, send_now=send_now)

    def campaign_report_email(self, id, email_subject, email_content_type, email_body,
                              email_to=None, email_cc=None, email_bcc=None, lang=None):
        '''Send report of Sent and Archived campaign.

        :param int id: Id of campaign to send its report
        :param str email_subject: Message subject
        :param str email_content_type: Body of the message in text/HTML version.
            Possible values - text & html
        :param str email_body: Body of the message
        :param str email_to: Email address of the recipient(s).
        :param str email_cc: Same as email_to but for Cc
        :param str email_bcc: Same as email_to but for Bcc
        :param str lang: Language of email content. Possible values - fr (default), en, es, it & pt
        '''
        return self.post('campaign/{id}/report'.format(id=id),
                         email_subject=email_subject,
                         email_content_type=email_content_type,
                         email_body=email_body,
                         email_to=email_to,
                         email_cc=email_cc,
                         email_bcc=email_bcc,
                         lang=lang)

    def campaign_recipients_export(self, id, notify_url, type):
        '''Export the recipients of a specified campaign.

        :param int id: Id of campaign to export its recipients
        :param str notify_url: URL that will be called once the export process is finished
        :param str type: Type of recipients. Possible values :
            all, non_clicker, non_opener, clicker, opener, soft_bounces, hard_bounces & unsubscribes
        '''
        return self.post('campaign/{id}/recipients'.format(id=id), notify_url=notify_url, type=type)

    def send_bat_email(self, id, emails):
        '''Send a Test Campaign.

        :param int id: Id of the campaign
        :param list emails: Email address of recipient(s) existing in the one of the lists
            & should not be blacklisted.
        '''
        return self.post('campaign/{id}/test'.format(id=id), emails=emails)

    def create_trigger_campaign(self, trigger_name, subject, category=None, from_name=None,
                                bat=None, html_content=None, html_url=None, listid=None,
                                scheduled_date=None, from_email=None, reply_to=None, to_field=None,
                                exclude_list=None, recurring=0, attachment_url=None,
                                inline_image=0, mirror_active=1, send_now=0):
        '''Create and schedule your Trigger campaigns.

        :param str trigger_name: Name of the campaign
        :param str subject: Subject of the campaign
        :param str category: Tag name of the campaign
        :param str from_name: Sender name from which the campaign emails are sent
            (Mandatory for Dedicated IP clients,
            please make sure that the sender details are defined here,
            and in case of no sender,
            you can add them also via API & for Shared IP clients, if sender exists)
        :param str bat: Email address for test mail
        :param str html_content: Body of the content.
            The HTML content field must have more than 10 characters
            (Mandatory if html_url is empty)
        :param str html_url: Url which content is the body of content
            (Mandatory if html_content is empty)
        :param list listid: These are the lists to which the campaign has been sent
            (Mandatory if scheduled_date is not empty)
        :param str scheduled_date: The day on which the campaign is supposed to run
        :param str from_email: Sender email from which the campaign emails are sent
            (Mandatory for Dedicated IP clients,
            please make sure that the sender details are defined here,
            and in case of no sender,
            you can add them also via API & for Shared IP clients, if sender exists)
        :param str reply_to: The reply to email in the campaign emails
        :param str to_field: This is to personalize the <<To>> Field.
            If you want to include the first name and last name of your recipient,
            add [PRENOM] [NOM].
            To use the contact attributes here, these should already exist in SendinBlue account
        :param list exclude_list: These are the lists which must be excluded from the campaign
        :param int recurring: Type of trigger campaign. Possible values:
            - 0 *(default)* means contact can receive the same Trigger campaign only once
            - 1 means contact can receive the same Trigger campaign several times
        :param str attachment_url: Provide the absolute url of the attachment
        :param int inline_image: Status of inline image. Possible values:
            - 0 *(default)* means image can't be embedded
            - 1 means image can be embedded, in the email
        :param int mirror_active: Status of mirror links in campaign. Possible values:
            - 0 means mirror links are deactivated
            - 1 (*default)* means mirror links are activated, in the campaign
        :param int send_now: Flag to send campaign now. Possible values:
            - 0 *(default)* means campaign can't be send now
            - 1 means campaign ready to send now
        '''
        # TODO: process dates
        return self.post('campaign',
                         trigger_name=trigger_name, subject=subject, category=category,
                         from_name=from_name, bat=bat, html_content=html_content, html_url=html_url,
                         listid=listid, scheduled_date=scheduled_date, from_email=from_email,
                         reply_to=reply_to, to_field=to_field, exclude_list=exclude_list,
                         recurring=recurring, attachment_url=attachment_url,
                         inline_image=inline_image, mirror_active=mirror_active, send_now=send_now)

    def update_trigger_campaign(self, id, trigger_name, subject, category=None, from_name=None,
                                bat=None, html_content=None, html_url=None, listid=None,
                                scheduled_date=None, from_email=None, reply_to=None, to_field=None,
                                exclude_list=None, recurring=0, attachment_url=None,
                                inline_image=0, mirror_active=1, send_now=0):
        '''Update and schedule your Trigger campaigns.

        :param int id: Id of Trigger campaign to be modified
        :param str trigger_name: Name of the campaign
        :param str subject: Subject of the campaign
        :param str category: Tag name of the campaign
        :param str from_name: Sender name from which the campaign emails are sent
            (Mandatory for Dedicated IP clients,
            please make sure that the sender details are defined here,
            and in case of no sender,
            you can add them also via API & for Shared IP clients, if sender exists)
        :param str bat: Email address for test mail
        :param str html_content: Body of the content.
            The HTML content field must have more than 10 characters
            (Mandatory if html_url is empty)
        :param str html_url: Url which content is the body of content
            (Mandatory if html_content is empty)
        :param list listid: These are the lists to which the campaign has been sent
            (Mandatory if scheduled_date is not empty)
        :param str scheduled_date: The day on which the campaign is supposed to run
        :param str from_email: Sender email from which the campaign emails are sent
            (Mandatory for Dedicated IP clients,
            please make sure that the sender details are defined here,
            and in case of no sender,
            you can add them also via API & for Shared IP clients, if sender exists)
        :param str reply_to: The reply to email in the campaign emails
        :param str to_field: This is to personalize the <<To>> Field.
            If you want to include the first name and last name of your recipient,
            add [PRENOM] [NOM].
            To use the contact attributes here, these should already exist in SendinBlue account
        :param list exclude_list: These are the lists which must be excluded from the campaign
        :param int recurring: Type of trigger campaign. Possible values:
            - 0 *(default)* means contact can receive the same Trigger campaign only once
            - 1 means contact can receive the same Trigger campaign several times
        :param str attachment_url: Provide the absolute url of the attachment
        :param int inline_image: Status of inline image. Possible values:
            - 0 *(default)* means image can't be embedded
            - 1 means image can be embedded, in the email
        :param int mirror_active: Status of mirror links in campaign. Possible values:
            - 0 means mirror links are deactivated
            - 1 (*default)* means mirror links are activated, in the campaign
        :param int send_now: Flag to send campaign now. Possible values:
            - 0 *(default)* means campaign can't be send now
            - 1 means campaign ready to send now
        '''
        # TODO: process dates
        return self.put('campaign/{id}'.format(id=id),
                        trigger_name=trigger_name, subject=subject, category=category,
                        from_name=from_name, bat=bat, html_content=html_content, html_url=html_url,
                        listid=listid, scheduled_date=scheduled_date, from_email=from_email,
                        reply_to=reply_to, to_field=to_field, exclude_list=exclude_list,
                        recurring=recurring, attachment_url=attachment_url,
                        inline_image=inline_image, mirror_active=mirror_active, send_now=send_now)

    def share_campaign(self, camp_ids):
        '''Get the Campaign name, subject and share link of the classic type campaigns only which are sent.

        For those which are not sent and the rest of campaign types like trigger, template & sms,
        will return an error message of share link not available.

        :param list camp_ids: Id of campaign to get share link.
        '''
        return self.post('campaign/sharelinkv2', camp_ids=camp_ids)

    def update_campaign_status(self, id, status):
        '''Update the Campaign status.

        :param int id: Id of campaign to update its status
        :param str status: Types of status. Possible values:
            suspended, archive, darchive, sent, queued, replicate and replicate_template
        '''
        return self.put('campaign/{id}/updatecampstatus'.format(id=id), status=status.lower())

    def get_processes(self, page=1, page_limit=50):
        '''Get all the processes information under the account.

        :param int page: Page number
        :param int page_limit: This should be a valid number between 1-50
        '''
        return self.get('process', page=page, page_limit=page_limit)

    def get_process(self, id):
        '''Get a specific process information.

        :param int id: Id of the process
        '''
        return self.get('process/{id}'.format(id=id))

    def get_lists(self, list_parent=None, page=1, page_limit=50):
        '''Get all lists detail.

        :param list_parent: An existing folder id, can be used to get all lists belonging to it
        :param int page: Page number
        :param int page_limit: Page size. This should be a valid number between 1-50
        '''
        return self.get('list', list_parent=list_parent, page=page, page_limit=page_limit)

    def get_list(self, id):
        '''Get a particular list detail.

        :param int id: Id of list to get details
        '''
        return self.get('list/{id}'.format(id=id))

    def create_list(self, list_name, list_parent):
        '''Create a new list.

        :param str list_name: Desired name of the list to be created
        :param int list_parent: Folder ID
        '''
        return self.post('list', list_name=list_name, list_parent=list_parent)

    def delete_list(self, id):
        '''Delete a specific list.

        :param int id: Id of list to be deleted
        '''
        return self.delete('list/{id}'.format(id=id))

    def update_list(self, id, list_parent, list_name=None):
        '''Update a list.

        :param int id: Id of list to be modified
        :param int list_parent: Folder ID
        :param str list_name: Desired name of the list to be modified
        '''
        return self.put('list/{id}'.format(id=id), list_parent=list_parent, list_name=list_name)

    def add_users_list(self, id, users):
        '''Add already existing users in the SendinBlue contacts to the list.

        :param int id: Id of list to link users in it
        :param list users: Email address of the already existing user(s) in the SendinBlue contacts.
        '''
        return self.post('list/{id}/users', users=users)

    def delete_users_list(self, id, users):
        '''Delete already existing users in the SendinBlue contacts from the list.
        :param int id: Id of list to unlink users from it
        :param list users: Email address of the already existing user(s)
            in the SendinBlue contacts to be modified.
        '''
        return self.delete('list/{id}/delusers', users=users)

    def display_list_users(self, ids, timestamp=None, page=1, page_limit=500):
        '''This API call will let you display details of all users for the given lists.

        :param ids: These are the list ids to get their data. The ids found will display records
        :param datetime timestamp: A datetime filter to fetch modified user records >= t.
        :param int page: Page number
        :param int page_limit: Page size. This should be a valid number between 1-50
        '''
        # TODO: process dates
        return self.get('list/display', {
            'listids[]': ids,
            'page': page,
            'page_limit': page_limit,
        })

    def send_email(self, subject, to, _from, html, text=None, cc=None, bcc=None,
                   replyto=None, attachment=None, headers=None, inline_image=None):
        '''Send Transactional Email.

        :param str subject: Message subject
        :param dict to: Email address of the recipient(s).
            It should be a dict(email: label).
            Example: ``{'to@example.net': "to whom"}.``
            You can use commas to separate multiple recipients
        :param list _from: Email address for From header.
            It should be a list or tuple (email, label).
            Example: ``("from@email.com", "from email")``
        :param str html: Body of the message. (HTML version).
            To send inline images,
            use ``<img src="{YourFileName.Extension}" alt="image" border="0" >``,
            the 'src' attribute value inside {} (curly braces)
            should be same as the filename used in 'inline_image' parameter
        :param str text: Body of the message. (text version)
        :param dict cc: Same as ``to`` but for Cc.
        :param dict bcc: Same as ``to`` but for Bcc.
        :param list replyto: Same as ``_from`` but for Reply To.
        :param list attachment: Provide the absolute url of the attachment/s.
            Possible extension values =
            gif, png, bmp, cgm, jpg, jpeg, txt, css, shtml, html, htm,
            csv, zip, pdf, xml, doc, xls, ppt, tar, and ez.
            To send attachment/s generated on the fly you have to pass your attachment/s filename
            and its base64 encoded chunk data as an a :type:`dict`.
            Example: ``{'YourFileName.Extension'=>'Base64EncodedChunkData'}``
        :param list headers: The headers will be sent along with the mail headers in original email.
            Example: ``{'Content-Type': 'text/html; charset=iso-8859-1'}``
        :param list inline_image: Pass your inline image/s filename
            and its base64 encoded chunk data as a :type:`dict`.
            Example: ``{'YourFileName.Extension': 'Base64EncodedChunkData'}``
        '''
        return self.post('email', {
            'subject': subject,
            'to': to, 'from': _from,
            'html': html, 'text': text,
            'cc': cc, 'bcc': bcc, 'replyto': replyto,
            'attachment': attachment,
            'headers': headers,
            'inline_image': inline_image
        })

    def get_webhooks(self, is_plat):
        '''To retrieve details of all webhooks.

        :param str is_plat: Flag to get webhooks. Possible values:
            - `0`: get Transactional webhooks
            - `1`: get Marketing webhooks
            - `''`: get all webhooks
        '''
        return self.get('webhook', is_plat=is_plat)

    def get_webhook(self, id):
        '''To retrieve details of any particular webhook.

        :param int id: Id of webhook to get details
        '''
        return self.get('webhook/{id}'.format(id=id))

    def create_webhook(self, url, events, description=None, is_plat=0):
        '''Create a Webhook.

        :param str url: URL that will be triggered by a webhook [Mandatory]
        :param list events: Set of events. You can use commas to separate multiple events.
            Possible values for Transcational webhook:
            request, delivered, hard_bounce, soft_bounce, blocked, spam,
            invalid_email, deferred, click, opened.
            Possible Values for Marketing webhook:
            spam, opened, click, hard_bounce, unsubscribe, soft_bounce, list_addition.
        :param str description: Webook description
        :param int is_plat: Flag to create webhook type. Possible values:
            - `0` *(default)*: create a Transactional webhooks
            - `1`: create a Marketing webhooks
        '''
        return self.post('webhook',
                         url=url, events=events, description=description, is_plat=is_plat)

    def delete_webhook(self, id):
        '''Delete a webhook.

        :param int id: Id of webhook to be deleted
        '''
        return self.delete('webhook/{id}'.format(id=id))

    def update_webhook(self, id, url, events, description=None):
        '''Update a webhook.

        :param int id: Id of webhook to be modified
        :param str url: URL that will be triggered by a webhook
        :param list events: Set of events. You can use commas to separate multiple events.
            Possible values for Transcational webhook:
            request, delivered, hard_bounce, soft_bounce, blocked,
            spam, invalid_email, deferred, click, opened.
            Possible Values for Marketing webhook:
            spam, opened, click, hard_bounce, unsubscribe, soft_bounce, list_addition
        :param str description: Webook description
        '''
        return self.put('webhook/{id}'.format(id=id),
                        url=url, events=events, description=description)

    def get_statistics(self, aggregate=None, start_date=None, end_date=None, days=None, tag=None):
        '''Aggregate / date-wise report of the SendinBlue SMTP account.

        :param int aggregate: This is used to indicate, you are interested in all-time totals.
            Possible values - ``0`` & ``1``.
            ``0`` means it will not aggregate records, and will show stats per day/date wise
        :param str start_date: The start date to look up statistics.
            Date must be in YYYY-MM-DD format and should be before the end_date [Optional]
        :param str end_date: The end date to look up statistics.
            Date must be in YYYY-MM-DD format and should be after the start_date [Optional]
        :param int days: Number of days in the past to include statistics ( Includes today ).
            It must be an integer greater than 0 [Optional]
        :param str tag: The tag you will specify to retrieve detailed stats.
            It must be an existing tag that has statistics [Optional]
        '''
        # TODO: process dates
        return self.post('statistics', aggregate=aggregate,
                         start_date=start_date, end_date=end_date, days=days, tag=tag)

    def get_user(self, email):
        '''Get Access a specific user Information.

        :param str email: Email address of the already existing user in the SendinBlue contacts
        '''
        return self.get('user/{email}'.format(email=email))

    def delete_user(self, email):
        '''Unlink existing user from all lists.

        :param str email: Email address of the already existing user in the SendinBlue contacts
            to be unlinked from all lists
        '''
        return self.delete('user/{email}'.format(email=email))

    def import_users(self, url=None, body=None, listids=None, notify_url=None,
                     name=None, list_parent=None):
        '''Import Users Information.

        :param str url: The URL of the file to be imported.
            Possible file types - .txt, .csv
            (Mandatory if ``body`` is empty)
        :param str body: The Body with csv content to be imported.
            Example: ``NAME;SURNAME;EMAIL\n"Name1";"Surname1";"example1@example.net"``,
            where ``\n`` separates each user data.
            You can use semicolon to separate multiple attributes
            (Mandatory if ``url`` is empty)
        :param list listids: These are the list ids in which the the users will be imported
            (Mandatory if name is empty)
        :param str notify_url: URL that will be called once the import process is finished.
            In notify_url, we are sending the content using POST method
        :param str name: This is new list name which will be created first
            and then users will be imported in it (Mandatory if ``listids`` is empty)
        :param int list_parent: This is the existing folder id
            and can be used with name parameter to make newly created list's desired parent
        '''
        return self.post('user/import', url=url, body=body, listids=listids,
                         notify_url=notify_url, name=name, list_parent=list_parent)

    def export_users(self, filter, export_attrib=None, notify_url=None):
        '''Export Users Information.

        :param dict filter: Filter can be added to export users.
            Example: ``{'blacklisted': 1}``, will export all blacklisted users
        :param str export_attrib: The name of attribute present in your SendinBlue account.
            You can use commas to separate multiple attributes. Example: ``EMAIL,NAME,SMS``
        :param str notify_url: URL that will be called once the export process is finished
        '''
        return self.post('user/export', filter=filter, export_attrib=export_attrib,
                         notify_url=notify_url)

    def create_update_user(self, email, attributes, blacklisted=None, listid=None,
                           listid_unlink=None, blacklisted_sms=None):
        '''Create or update a user.

        If an email provided as input
        and it doesn't exists in the contact list of your SendinBlue account,
        it will be created,
        otherwise it will update the existing user.

        :param str email: Email address of the user to be created in SendinBlue contacts.
            Already existing email address of user in the SendinBlue contacts to be modified
        :param dict attributes: The name of attribute present in your SendinBlue account.
            It should be sent as an associative array.
            Example: ``{'NAME': 'John Doe'}``.
            You can use commas to separate multiple attributes
        :param int blacklisted: This is used to blacklist/ Unblacklist a user.
            Possible values - 0 & 1. blacklisted = 1 means user has been blacklisted
        :param list listid: The list id(s) to be linked from user
        :param list listid_unlink: The list id(s) to be unlinked from user
        :param list blacklisted_sms: This is used to blacklist/ Unblacklist a user's SMS number.
            Possible values - ``0`` & ``1``. ``1`` means user's SMS number has been blacklisted
        '''
        return self.post('user/createdituser', email=email, attributes=attributes,
                         blacklisted=blacklisted, listid=listid, listid_unlink=listid_unlink,
                         blacklisted_sms=blacklisted_sms)

    def get_attributes(self):
        '''Access all the attributes information under the account.'''
        return self.get('attribute')

    def get_attribute(self, type):
        '''Access the specific type of attribute information.

        :param str type: Type of attribute.
            Possible values - normal, transactional, category, calculated & global
        '''
        return self.get('attribute/{type}'.format(type=type))

    def create_attribute(self, type, data):
        '''Create an Attribute.

        :param str type: Type of attribute.
            Possible values - normal, transactional, category, calculated, global
        :param list data: The name and data type of 'normal' & 'transactional'
            attribute to be created in your SendinBlue account.
            It should be :type:`dict`.
            Example: ``{'ATTRIBUTE_NAME1': 'DATA_TYPE1', 'ATTRIBUTE_NAME2': 'DATA_TYPE2'}``.
            The name and data value of 'category', 'calculated' & 'global',
            should be sent as JSON string.
            Example: ``[{ "name":"ATTRIBUTE_NAME1", "value":"Attribute_value1" }]'.
            You can use commas to separate multiple attributes
        '''
        return self.post('attribute', {'type': type, 'data': data})

    def delete_attribute(self, type, data):
        '''Delete a specific type of attribute information.

        :param int type: Type of attribute to be deleted
        :param list data: The list of attribute to delet
        '''
        return self.post('attribute/{type}'.format(type=type), {'data': data})

    def get_report(self, limit=None, start_date=None, end_date=None, offset=None, date=None,
                   days=None, email=None):
        '''Get Email Event report.

        :param int limit: To limit the number of results returned. It should be an integer
        :param str start_date: The start date to get report from.
            Date must be in YYYY-MM-DD format and should be before the end_date
        :param str end_date: The end date to get report till date.
            Date must be in YYYY-MM-DD format and should be after the start_date
        :param int offset: Beginning point in the list to retrieve from. It should be an integer
        :param str date: Specific date to get its report.
            Date must be in YYYY-MM-DD format and should be earlier than todays date
        :param int days: Number of days in the past (includes today).
            If specified, must be an integer greater than 0
        :param str email: Email address to search report for
        '''
        # TODO: process dates
        return self.post('report', limit=limit, start_date=start_date, end_date=end_date,
                         offset=offset, date=date, days=days, email=email)

    def get_folders(self, page=1, page_limit=50):
        '''Get all folders detail.

        :param int page: The page number
        :param int page_limit: The page size. This should be a valid number between 1-50
        '''
        return self.get('folder', page=page, page_limit=page_limit)

    def get_folder(self, id):
        '''Get a particular folder detail.

        :param int id: Id of folder to get details
        '''
        return self.get('folder/{id}'.format(id=id))

    def create_folder(self, name):
        '''Create a new folder.

        :param str name: Desired name of the folder to be created
        '''
        return self.post('folder', name=name)

    def delete_folder(self, id):
        '''Delete a specific folder information.

        :param int id: Id of folder to be deleted
        '''
        return self.delete('folder/{id}'.format(id=id))

    def update_folder(self, id, name):
        '''Update an existing folder.

        :param int id: Id of folder to be modified
        :param str name: Desired name of the folder to be modified
        '''
        return self.put('folder/{id}'.format(id=id), name=name)

    def delete_bounces(self, start_date=None, end_date=None, email=None):
        '''Delete any hardbounce, which actually would have been blocked due to some temporary ISP failures.

        :param str start_date: The start date to get report from.
            Date must be in YYYY-MM-DD format and should be before the end_date
        :param str end_date: The end date to get report till date.
            Date must be in YYYY-MM-DD format and should be after the start_date
        :param str email: Email address to delete its bounces
        '''
        # TODO: process dates
        return self.post('bounces', start_date=start_date, end_date=end_date, email=email)

    def send_transactional_template(self, id, to, cc=None, bcc=None, attr=None,
                                    attachment_url=None, attachment=None, headers=None):
        '''Send templates created on SendinBlue, through SendinBlue SMTP (transactional mails).

        :param int id: Id of the template created on SendinBlue account
        :param str to: Email address of the recipient(s).
            You can use pipe ( | ) to separate multiple recipients.
            Example: "to-example@example.net|to2-example@example.net"
        :param str cc: Same as to but for Cc
        :param str bcc: Same as to but for Bcc
        :param dict attr: The name of attribute present in your SendinBlue account.
            It should be a :type:`dict`.
            Example: ``{'NAME': 'name'}``.
            You can use commas to separate multiple attributes
        :param str attachment_url: Provide the absolute url of the attachment.
            Url not allowed from local machine. File must be hosted somewhere
        :param dict attachment: To send attachment/s generated on the fly
            you have to pass your attachment/s filename
            and its base64 encoded chunk data as a :type:`dict`
        :param dict headers: This headers will be to those in the mail headers in original email.
            Example: ``{'Content-Type': 'text/html; charset=iso-8859-1'}``.
            You can use commas to separate multiple headers
        '''
        if isinstance(to, (list,tuple)):
            to = '|'.join(to)
        return self.put('template/{id}'.format(id=id), to=to, cc=cc, bcc=bcc, attr=attr,
                        attachment_url=attachment_url, attachment=attachment, headers=headers)

    def create_template(self, subject, template_name, from_name=None, bat=None, html_content=None,
                        html_url=None, from_email=None, reply_to=None, to_field=None,
                        status=0, attachment=0):
        '''Create a Template.

        :param str subject: Subject of the campaign
        :param str template_name: Name of the Template
        :param str from_name: Sender name from which the campaign emails are sent
            (Mandatory for Dedicated IP clients & for Shared IP clients, if sender exists)
        :param str bat: Email address for test mail
        :param str html_content: Body of the content.
            The HTML content field must have more than 10 characters
            (Mandatory if html_url is empty)
        :param str html_url: Url which content is the body of content.
            (Mandatory if html_content is empty)
        :param str from_email: Sender email from which the campaign emails are sent.
            (Mandatory for Dedicated IP clients & for Shared IP clients, if sender exists)
        :param str reply_to: The reply to email in the campaign emails
        :param str to_field: This is to personalize the <<To>> Field.
            If you want to include the first name and last name of your recipient,
            add [PRENOM] [NOM].
            To use the contact attributes here, these should already exist in SendinBlue account
        :param int status: Status of template. Possible values:
            - ``0`` *(default)* means template is inactive
            - ``1`` means template is active
        :param int attachment: Status of attachment. Possible values:
            - ``0`` *(default)* means an attachment can't be sent
            - ``1`` means an attachment can be sent, in the email
        '''
        return self.post('template', subject=subject, template_name=template_name,
                         from_name=from_name, bat=bat, html_content=html_content,
                         html_url=html_url, from_email=from_email, reply_to=reply_to,
                         to_field=to_field, status=status, attachment=attachment)

    def update_template(self, id, subject, template_name, from_name=None, bat=None,
                        html_content=None, html_url=None, from_email=None, reply_to=None,
                        to_field=None, status=0, attachment=0):
        '''Update a Template.

        :param int id: Id of Template to be modified
        :param str subject: Subject of the campaign
        :param str template_name: Name of the Template
        :param str from_name: Sender name from which the campaign emails are sent.
            (Mandatory for Dedicated IP clients & for Shared IP clients, if sender exists)
        :param str bat: Email address for test mail
        :param str html_content: Body of the content.
            The HTML content field must have more than 10 characters.
            (Mandatory if html_url is empty)
        :param str html_url: Url which content is the body of content.
            (Mandatory if html_content is empty)
        :param str from_email: Sender email from which the campaign emails are sent.
            (Mandatory for Dedicated IP clients & for Shared IP clients, if sender exists)
        :param str reply_to: The reply to email in the campaign emails
        :param str to_field: This is to personalize the <<To>> Field.
            If you want to include the first name and last name of your recipient,
            add [PRENOM] [NOM].
            To use the contact attributes here, these should already exist in SendinBlue account
        :param int status: Status of template. Possible values:
            - ``0`` *(default)* means template is inactive
            - ``1`` means template is active
        :param int attachment: Status of attachment. Possible values:
            - ``0`` *(default)* means an attachment can't be sent
            - ``1`` means an attachment can be sent, in the email
        '''
        return self.put('template/{id}'.format(id=id), subject=subject,
                        template_name=template_name, from_name=from_name, bat=bat,
                        html_content=html_content, html_url=html_url, from_email=from_email,
                        reply_to=reply_to, to_field=to_field, status=status, attachment=attachment)

    def get_senders(self, option):
        '''Get Access of created senders information.

        :param str option: Options to get senders.
            Possible options - IP-wise & Domain-wise ( only for dedicated IP clients ).
            Example: to get senders with specific IP, use ``option='1.2.3.4'``,
            to get senders with specific domain use, ``option='domain.com'``,
            and to get all senders, use ``option=''``
        '''
        return self.get('advanced', option=option)

    def create_sender(self, name, email, ip_domain=None):
        '''Create your Senders.

        :param str name: Name of the sender
        :param str email: Email address of the sender
        :param list ip_domain: Pass pipe ( | ) separated Dedicated IP and its associated Domain.
            Example: ``['1.2.3.4|mydomain1.com', '5.6.7.8|mydomain2.com']``.
            You can use commas to separate multiple ip_domain's
            (Mandatory only for Dedicated IP clients,
            for Shared IP clients, it should be kept blank)
        '''
        # TODO: Handle arrays
        return self.post('advanced', name=name, email=email, ip_domain=ip_domain)

    def update_sender(self, id, name, ip_domain=None):
        '''Update your Senders.
        :param int id: Id of sender to be modified [Mandatory]
        :param str name: Name of the sender
        :param list ip_domain: Pass pipe ( | ) separated Dedicated IP and its associated Domain.
            Example: ``['1.2.3.4|mydomain1.com', '5.6.7.8|mydomain2.com']``.
            You can use commas to separate multiple ip_domain's
            (Mandatory only for Dedicated IP clients,
            for Shared IP clients, it should be kept blank)
        '''
        return self.put('advanced/{id}'.format(id=id), name=name, ip_domain=ip_domain)

    def delete_sender(self, id):
        '''Delete your Sender Information.

        :param in id: Id of sender to be deleted
        '''
        return self.delete('advanced/{id}'.format(id=id))


class AutomationClient(object):
    '''A SendInBlue Automation API Client'''
    def __init__(self, apikey, timeout=None):
        self.apikey = apikey
        self.timeout = timeout

    def execute(self, name, **data):
        data['key'] = self.apikey
        data['sib_type'] = name
        response = requests.get(AUTOMATION_API_URL, params=data,
                                timeout=self.timeout or DEFAULT_TIMEOUT)
        return response.json()

    def identify(self, email, **data):
        '''
        See: https://apidocs.sendinblue.com/identify-user/
        https://in-automate.sendinblue.com/p?
            name=James%20Clear&
            email_id=james@example.com&
            id=10001&
            sib_type=identify&key=your_key&session_id=f33234de-cc75-4f28-9e9a-afb0014a5daf'
        '''
        data['email_id'] = email
        return self.execute('identify', **data)

    def track(self, name, **data):
        '''
        See: https://apidocs.sendinblue.com/track-events/
        '''
        data['sib_name'] = name
        return self.execute('track', **data)

    def link(self, name, url, **data):
        '''
        See: https://apidocs.sendinblue.com/track-links/
        '''
        data['name'] = name
        data['href'] = url
        return self.execute('trackLink', **data)

    def page(self, name, **data):
        '''
        See: https://apidocs.sendinblue.com/track-pages/
        '''
        data['name'] = name
        return self.execute('page', **data)
