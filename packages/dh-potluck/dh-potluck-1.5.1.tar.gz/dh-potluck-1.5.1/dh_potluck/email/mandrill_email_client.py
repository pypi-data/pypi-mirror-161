from enum import Enum
from typing import Dict, List, Optional

import mandrill
from flask import current_app


class MandrillMergeLanguage(Enum):
    """
    Enum for templating languages supported by mailchimp.
    'mailchimp' is the default in Mandrill
    """

    MAILCHIMP = 'mailchimp'
    HANDLEBARS = 'handlebars'


class MandrillEmailClient:
    _DEFAULT_EMAIL_PROPS = {
        'from_name': 'Dash Hudson',
        'from_email': 'noreply@dashhudson.com',
        'preserve_recipients': True,
        'track_clicks': True,
        'track_opens': True,
        'inline_css': True,
    }

    _mandrill_client: mandrill.Mandrill

    def __init__(self):
        self._mandrill_client = mandrill.Mandrill(current_app.config['DH_POTLUCK_MANDRILL_API_KEY'])

    def send_email_template(
        self,
        recipients: List[Dict],
        template_name: str,
        template_vars: List[Dict[str, str]],
        subject: Optional[str] = None,
        merge_language: Optional[MandrillMergeLanguage] = None,
    ) -> None:
        message = {
            'preserve_recipients': self._DEFAULT_EMAIL_PROPS['preserve_recipients'],
            'track_clicks': self._DEFAULT_EMAIL_PROPS['track_clicks'],
            'track_opens': self._DEFAULT_EMAIL_PROPS['track_opens'],
            'from_name': self._DEFAULT_EMAIL_PROPS['from_name'],
            'from_email': self._DEFAULT_EMAIL_PROPS['from_email'],
            'to': recipients,
            'global_merge_vars': template_vars,
        }
        if subject:
            message['subject'] = subject

        if merge_language:
            message['merge_language'] = merge_language.value

        self._mandrill_client.messages.send_template(
            template_name=template_name, message=message, template_content=[]
        )

    def send_email_html(
        self, recipients: List[Dict], subject: str = None, html: str = None
    ) -> None:
        message = {
            'preserve_recipients': self._DEFAULT_EMAIL_PROPS['preserve_recipients'],
            'track_clicks': self._DEFAULT_EMAIL_PROPS['track_clicks'],
            'track_opens': self._DEFAULT_EMAIL_PROPS['track_opens'],
            'from_name': self._DEFAULT_EMAIL_PROPS['from_name'],
            'from_email': self._DEFAULT_EMAIL_PROPS['from_email'],
            'inline_css': self._DEFAULT_EMAIL_PROPS['inline_css'],
            'to': recipients,
        }
        if html:
            message['html'] = html

        if subject:
            message['subject'] = subject

        self._mandrill_client.messages.send(message=message)
