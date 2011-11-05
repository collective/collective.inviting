from zope.component import queryUtility
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

from collective.subscribe.interfaces import ISubscriptionKeys
from collective.inviting.interfaces import IContentSubscribers


VIEW_TRAVERSAL_NAME = '@@status' #should match ZCML browser:page registration


class RSVPRedirect(object):
    """
    Gets confirmation token, looks up content item uid in ISubscriptionKeys 
    utility; resolves item and then redirects to its view URL.
    
    This should be registered as a view on the site root with the name
    defined in VIEW_TRAVERSAL_NAME.
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.subkeys = queryUtility(ISubscriptionKeys)
        self.user_message = ''  #template should assume possible rich/html
        self.form_error = False
        self.portal = getSite()
    
    def error(self):
        """We are unable to find an invitation for the token"""
        self.form_error = True #template can check for this.
        return 'Our apologies: we are unable to find an invitation for the '\
                'token provided or the event has been removed.'
    
    def __call__(self, *args, **kwargs):
        form = self.request.form
        token = form.get('token', None)
        if token is None or token not in self.subkeys:
            self.user_message = self.error()
            return
        relname, signature, uid = self.subkeys[token]
        catalog = getToolByName(self.portal, 'portal_catalog')
        brains = catalog.search({'UID':uid})
        if not brains:
            self.user_message = self.error()
            return
        item = brains[0].getObject()
        view_url = '/'.join((item.absolute_url(), VIEW_TRAVERSAL_NAME))
        self.request.response.redirect('%s?token=%s' % (view_url, token))


class RSVP(object):
    """ RSVP confirm / decline view: user clicks button indicating status"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.user_message = ''  #template should assume possible rich/html
        self.form_error = False
        self.token = request.form.get('token', None)
        if self.token is None:
            self.user_message = self.error()
        self.subkeys = queryUtility(ISubscriptionKeys)
        self.portal = getSite()
    
    def greeting(self):
        return 'Please confirm or decline your availablity for this event. '\
               'Your current status is listed as: %s' % self.status()

    def resolve(self):
        """
        return tuple of 3 items: relationship name, subscriber signature
        item uid; note: item UID should validate against context, return
        None if no UID does not match context.
        """
        relname, signature, uid = self.subkeys[self.token]
        if self.context.UID() != uid:
            self.user_message = self.error()
            return None
        return relname, signature, uid
    
    def error(self):
        """We are unable to find an invitation for the token"""
        self.form_error = True #template can check for this.
        return 'Our apologies: we are unable to find an invitation for the '\
                'token provided.'
    
    def status(self):
        relname, signature, uid = self.resolve()
        adapted = IContentSubscribers(self.context)
        relnames = adapted.subscriptions_for(signature)
        if not relnames:
            return 'Unknown'
        return ', '.join(relnames)
    
    def _mark_subname(self, token, relname="confirmed"):
        invite_relname, signature, uid = self.resolve()
        adapted = IContentSubscribers(self.context)
        if relname == 'confirmed':
            adapted.unindex('declined', signature)
        if relname == 'declined':
            adapted.unindex('confirmed', signature)
        adapted.index(relname, signature) #index subscriber signature for rel
    
    def decline(self, token):
        self._mark_subname(token, relname="declined")
        relname, signature, uid = self.resolve()
        self.user_message = 'You have marked "decline" for this event.'
    
    def confirm(self, token):
        self._mark_subname(token, relname="confirmed")
        self.user_message = 'You have been confirmed for this event.'
    
    def update(self, *args, **kwargs):
        form = self.request.form
        token = form.get('token', None)
        if token is None or token not in self.subkeys:
            self.user_message = self.error()
            return
        if 'button-confirm' in form:
            self.confirm(token)
        elif 'button-decline' in form:
            self.decline(token)
        else:
            self.user_message = self.greeting() #initial form, not submitted.
    
    def __call__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        return self.index(*args, **kwargs)

