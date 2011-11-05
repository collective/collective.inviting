import re

try:
    from email._parseaddr import AddressList
except:
    from rfc822 import AddressList

from zope.component import queryUtility, getUtility, getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFCore.utils import getToolByName

from collective.inviting.interfaces import IContentSubscribers
from collective.subscribe.interfaces import ISubscriptionCatalog, IUIDStrategy
from collective.subscribe.interfaces import ISubscribers, ISubscriptionKeys
from collective.inviting.mail import MailRecipient


# Template (format) strings for email invitation messages:
INVITE_EMAIL_SUBJ = 'Invitation: %(ITEM_TITLE)s'


class SubscribersView(object):
    """
    Subscribers view of content item, shows lists of 
    subscriptions to content object.
    
    Caches lookups of subscribers for all index names for this item
    in order to achieve constant running time (instead of quadratic
    efficiency for per-subscriber/per-row lookup).
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.uid = IUIDStrategy(context).getuid()
        self._site = getUtility(ISiteRoot)
        self._catalog = queryUtility(ISubscriptionCatalog)
        self._container = queryUtility(ISubscribers)
        self._users = getToolByName(self.context, 'acl_users')
        self._mtool = getToolByName(self.context, 'portal_membership')
        self._mail = getToolByName(self.context, 'MailHost')
        if self._catalog is None:
            raise ComponentLookupError(
                'could not locate installed local subscription catalog; '\
                'is collective.inviting product correctly installed in site?')
        self._provider = IContentSubscribers(context)
        self._load_indexed()
        self.add_result = () #empty result, initially
        self.result_group = None #group name in add form, if used
        self.sent_to = []
        self.debug_msg_log = []
    
    def _load_indexed(self):
        self.indexed = {}
        for idx in self.indexes():
            self.indexed[idx] = [self._container.get(sig)
                                 for sig in self._catalog.search(
                                    {idx:self.uid})]

    def member_fullname(self, m):
        try:
            info = self._mtool.getMemberInfo(m)
            if info is None:
                return '--'
            v = self._mtool.getMemberInfo(m).get('fullname',None)
        except KeyError:
            v = '--'
        return v

    def indexes(self):
        """return tuple of all subscription index names"""
        return tuple(self._catalog.indexes)

    def subscribers(self, name=None):
        """
        list subscribers of item given a subscription name;
        if None, list all subscribers related to the adapted
        content item, regardless of which named relationships
        they are subscribed to.
        """
        if name is None:
            return self._provider.find() #all subscribers, all indexes
        return self._provider.find(name)
    
    def is_subscribed(self, subscriber, name):
        """
        is subscriber subscribed to this item for relationship named name
        (uses cached values of subscription catalog lookups from view
        construction).
        """
        indexed_for_name = self.indexed.get(name, None)
        if indexed_for_name is None:return False
        return subscriber in indexed_for_name

    def enumerate_groups(self):
        """
        enumerate groups of users; returns sequence containing
        group objects
        """
        return self._users.source_groups.getGroups()

    def group_members(self, groupname):
        """
        enumerate/list members for group name; returns sequence
        of tuples containing (fullname, username).
        """
        group = self._users.source_groups.getGroupById(groupname)
        users = group.getMemberIds()
        names = [self.member_fullname(m) for m in users]
        return zip(users, names)

    def all_users(self):
        users = self._users.getUserNames()
        names = [self.member_fullname(m) for m in users]
        return zip(users, names)

    def search_members(self, query):
        """
        Search for users with string query; returns sequence of tuples
        containing (fullname, username).
        """
        matching = [u['userid']
                    for u in self._users.searchUsers(fullname=query)]
        names = [self.member_fullname(m) for m in matching]
        return zip(matching, names)

    def _parse_email_input(self, input):
        """
        Transform mixture of comma/whitespace into list of tuples of 
        name, email for each address in input.
        """
        input = input.strip()                   #strip leading/trailing \s
        input = re.sub('\r\n','\n', input)      #CRLF  -> LF
        return list(AddressList(input))

    def _get_recipient(self, sub):
        """
        given subscriber as IItemSubscriber object, get recipient
        as IMailRecipient (TODO: create an adapter for this?) or None.
        """
        if sub.namespace == 'member':
            member = self._mtool.getMemberById(sub.user)
            if member is None:
                return None#silently ignoring members with no info
            mto = member.getProperty('email', None)
            if mto is None:
                return None #again, ignore if we have no email
            mto_name = member.getProperty('fullname', '')
        elif sub.namespace == 'email':
            mto = sub.email
            mto_name = ''
        else:
            return None # unhandled subscriber signature namespace
        return MailRecipient(mto, mto_name)
    
    def _send_invitation_message(self, sub, token):
        """given subscriber amd token, render and send invite email"""
        recipient = self._get_recipient(sub) #get IMailRecipient object
        if recipient is None:
            return
        self.request.form['token'] = token # passes token to message
        msg = getMultiAdapter((self.context, self.request),
            name=u'invitation_email')(recipient=recipient)
        if 'nomail' not in self.request.form:
            self._mail.send(msg)
            self.sent_to.append(recipient) # can be usef by template: display log
        if 'debug' in self.request.form:
            self.debug_msg_log.append(msg)
    
    def tokenize(self, sub, idx='invited'):
        subkeys = queryUtility(ISubscriptionKeys)
        token = subkeys.add(idx, sub, self.uid)  # store sub, get token
        return token
    
    def subscriptions_for(self, signature):
        adapted = IContentSubscribers(self.context)
        return adapted.subscriptions_for(signature)
    
    def invite(self, sub, idx='invited'):
        signature = sub.signature()
        previously_invited = 'invited' in self.subscriptions_for(signature)
        if not previously_invited:
            self._catalog.index(sub, self.uid, names=(idx,))
            token = self.tokenize(
                signature,
                idx
                ) #store subscription generate token
            self._send_invitation_message(sub, token)
    
    def update(self, *args, **kwargs):
        form = self.request.form
        if 'listgroup' in form:
            groupname = form['membergroup']
            if groupname:
                self.add_result = self.group_members(groupname)
                get_group = self._users.source_groups.getGroupById
                self.result_group = get_group(groupname)
            else:
                self.add_result = self.all_users()
        if 'membersearch' in form:
            self.add_result = self.search_members(form['membersearch'])
        if 'add_email' in form:
            # member checkboxes or email addresses selected for addition
            add_email_addresses = self._parse_email_input(form['add_email'])
            add_members = [k.split('/')[1] for k,v in form.items() if k.startswith('member/') and v]
            # catalog email addresses and members with 'invited' relatiomship
            for name, addr in add_email_addresses:
                if addr:
                    sig = ('email', addr)
                    if sig not in self._container:
                        sig, sub = self._container.add(
                            namespace=sig[0],
                            email=sig[1],)
                    else:
                        sub = self._container[sig]
                    if name:
                        # always globally store the latest name; note: this
                        # has the consequence of possibly overriding previous
                        # values of name-to-email mappings affecting other
                        # events, but this is the least-evil expedient way
                        # to handle this without storing a name-to-email 
                        # mapping for every event object context.
                        sub.name = name.decode('utf-8')
                    self.invite(sub)
            for sig in [('member',m) for m in add_members]:
                if sig not in self._container:
                    sig, sub = self._container.add(
                        namespace=sig[0],
                        user=sig[1]
                        )
                else:
                    sub = self._container[sig]
                self.invite(sub)
            self._load_indexed() #reload fresh state for re-render
            self.request.form['debug'] = '1' #TODO: remove this
        if 'submatrix_modify' in form:
            for idx in self.indexes():
                existing_subs = set([sub.signature() for sub in self.indexed[idx]])
                checked_subs = set([tuple(k.split('/')[1:]) for k,v in form.items()
                                    if k.startswith('%s/' % idx)])
                remove_subs = existing_subs - checked_subs
                add_subs = checked_subs - existing_subs
                for sub in remove_subs:
                    self._catalog.unindex(sub, self.uid, names=(idx,))
                for sub in add_subs:
                    self._catalog.index(sub, self.uid, names=(idx,))
            self._load_indexed() #reload fresh state for re-render
    
    def __call__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        return self.index(*args, **kwargs)


class EventSubscribersView(SubscribersView):
    """Event-specific subscription view"""

    def indexes(self):
        _indexes = ['invited', 'confirmed', 'declined', 'attended']
        catalog_indexes = super(EventSubscribersView, self).indexes()
        _indexes += [idx for idx in catalog_indexes if idx not in _indexes]
        return tuple(_indexes)

