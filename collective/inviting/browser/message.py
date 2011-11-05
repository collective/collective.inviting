from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from StringIO import StringIO

import icalendar
from Acquisition import aq_inner
from zope.component import queryUtility, getUtility
from zope.app.component.hooks import getSite
from Products.ATContentTypes.lib.calendarsupport import (PRODID, VCS_HEADER,
    VCS_FOOTER, n2rn)
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from collective.subscribe.interfaces import IUIDStrategy
from collective.inviting.interfaces import IMailRecipient
from collective.inviting.mail import MailRecipient, invitation_sender


# Template (format) strings for email invitation messages:
RSVP_URL_TEMPLATE = '%(SITE_URL)s/@@status?token=%(TOKEN)s'
INVITE_EMAIL_SUBJ = 'Invitation: %(ITEM_TITLE)s'
INVITE_EMAIL_BODY = """ 
%(FROM_NAME)s (%(FROM_EMAIL)s) has invited you to an event:

What: %(ITEM_TITLE)s

When: %(DATE_FORMATTED)s
      %(TIME_FORMATTED)s

Description:
%(ITEM_DESCRIPTION)s

You can confirm or decline your attendance of this event with the the meeting
organizer by visiting the following link and indicating your status:

 %(RSVP_URL)s

More information:

 %(ITEM_URL)s

A vCal file, suitable for adding this event to calendaring software such as
iCal, Microsoft Outlook, and Google Calendar is attached.

--- 

Received this email in error?  Have questions?

 Please contact %(FROM_EMAIL)s, the original sender of this
 invitation to you (you can reply to this message to do so).
"""


class InvitationEmail(object):
    """
    view/adapter for one sender, one item on construction to render email
    message multiple recipients, one recipient per call.
    """
    
    def __init__(self, context, request):
        self.context = context #event item
        self.request = request
        self._loaded = False

    def _load_state(self):
        self._loaded = True
        self.uid = IUIDStrategy(self.context).getuid()
        self.portal = getSite()
        altportal = getSite()
        self.sender = invitation_sender(self.portal)
        self.localize = getToolByName(self.portal, 'translation_service')
        self.timefn = self.localize.ulocalized_time
    
    def _recipient_from_request(self):
        form = self.request.form
        address = form.get('address', self.sender.from_address)
        name = form.get('name', self.sender.from_name)
        if isinstance(name, str):
            name = name.decode('utf-8')
        return MailRecipient(address, name)
    
    def _set_headers(self, message, recipient):
        sender = self.sender
        # From: header
        message['From_'] = sender.from_address
        if sender.from_name:
            message['From'] = '%s <%s>' % (sender.from_name.encode('utf-8'),
                                           sender.from_address)
        else:
            message['From'] = sender.from_address
        # To: header
        if recipient.name:
            message['To'] = '%s <%s>' % (recipient.name.encode('utf-8'),
                                         recipient.address)
        else:
            message['To'] = recipient.address
        # Reply-to: header
        if sender.reply_name:
            message['Reply-to'] = '%s <%s>' % (sender.reply_name,
                                                    sender.reply_address)
        else:
            message['Reply-to'] = sender.reply_address
        # Subject: header
        message['Subject'] = 'Invitation: %s' % self.context.Title()
    
    def _vcal(self):
        """
        Make vCal file stream for item context. VCS is modified with use
        of the icalendar library to inject URL to event into the
        description (generate, then parse, modify, reserialize).
        Uses: http://codespeak.net/icalendar/
        """
        url = self.context.absolute_url()
        out = StringIO()
        out.write(VCS_HEADER % { 'prodid' : PRODID })
        out.write(self.context.getVCal())
        out.write(VCS_FOOTER)
        vcs = n2rn(out.getvalue())
        parsed = icalendar.Event.from_string(vcs)
        journal = [c for c in parsed.subcomponents
                    if isinstance(c, icalendar.Journal)]
        if journal:
            description = journal[0].get(
                'description',
                icalendar.vText(), #default empty, if empty desc in vcs
                ).format()
            description = '%s\n\n  More info:\n\n  %s\n\n' % (description, url)
            journal[0].set('description', description)
        return str(parsed) #return modified (description) vcs
    
    def _rsvp_url(self):
        token = self.request.get('token', None)
        if token is None:
            return self.portal.absolute_url()
        return RSVP_URL_TEMPLATE % {'SITE_URL': self.portal.absolute_url(),
                                    'TOKEN' : token}
    
    def __call__(self, *args, **kwargs):
        if not self._loaded:
            self._load_state()
        recipient = kwargs.get('recipient', None)
        if not IMailRecipient.providedBy(recipient):
            recipient = self._recipient_from_request()
        message = MIMEMultipart()
        self._set_headers(message, recipient)
        data = {
            'FROM_NAME' : self.sender.reply_name,
            'FROM_EMAIL' : self.sender.reply_address,
            'DATE_FORMATTED' : self.timefn(self.context.start(),
                                         context=aq_inner(self.context),
                                         request=self.request),
            'TIME_FORMATTED' : self.timefn(self.context.start(),
                                         time_only=True,
                                         context=aq_inner(self.context),
                                         request=self.request),
            'ITEM_TITLE' : self.context.Title(),
            'ITEM_DESCRIPTION' : self.context.Description(),
            'ITEM_URL' : self.context.absolute_url(),
            'RSVP_URL' : self._rsvp_url(),
            }
        body = INVITE_EMAIL_BODY % data
        message.attach(MIMEText(body))
        attachment = MIMEBase('text', 'x-vCalendar')
        attachment.set_payload(self._vcal()) #data
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition',
                              'attachment',
                              filename='event.vcs')
        message.attach(attachment)
        return message.as_string()

