from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from collective.inviting.interfaces import IMailSender, IMailRecipient


class MailSender(object):
    implements(IMailSender)
    def __init__(self,
                 from_address,
                 from_name=None,
                 reply_address=None,
                 reply_name=None):
        self.from_address = from_address
        self.from_name = from_name
        self.reply_address = reply_address or from_address
        self.reply_name = reply_name or from_name


class MailRecipient(object):
    implements(IMailRecipient)
    def __init__(self, address, name=None):
        self.address = address
        if isinstance(name, str):
            name = name.decode('utf-8')
        self.name = name


def invitation_sender(portal):
    mtool = getToolByName(portal, 'portal_membership')
    site_email = portal.getProperty('email_from_address')
    site_from_name = portal.getProperty('email_from_name')
    member = mtool.getAuthenticatedMember()
    return MailSender(from_address=site_email,
                      from_name=member.getProperty(
                        'fullname', None) or site_from_name,
                      reply_address=member.getProperty('email', None))

