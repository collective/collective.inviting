from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError

from Products.CMFCore.utils import getToolByName

from uu.inviting.interfaces import IContentSubscribers
from uu.subscribe.interfaces import ISubscriptionCatalog, IUIDStrategy

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
        self._catalog = queryUtility(ISubscriptionCatalog)
        self._users = getToolByName(self.context, 'acl_users')
        self._mtool = getToolByName(self.context, 'portal_membership')
        if self._catalog is None:
            raise ComponentLookupError(
                'could not locate installed local subscription catalog; '\
                'is uu.inviting product correctly installed in site?')
        self._provider = IContentSubscribers(context)
        self._load_indexed()
        self.add_result = () #empty result, initially
        self.result_group = None #group name in add form, if used

    def _load_indexed(self):
        self.indexed = {}
        for idx in self.indexes():
            self.indexed[idx] = self._catalog.search({idx:self.uid})

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
        if indexed_for_name is None:
            return False
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
        names = [self._mtool.getMemberInfo(m)['fullname'] for m in users]
        return zip(users, names)

    def all_users(self):
        users = self._users.getUserNames()
        names = [self._mtool.getMemberInfo(m)['fullname'] for m in users]
        return zip(users, names)

    def search_members(self, query):
        """
        Search for users with string query; returns sequence of tuples
        containing (fullname, username).
        """
        matching = [u['userid']
                    for u in self._users.searchUsers(fullname=query)]
        names = [self._mtool.getMemberInfo(m)['fullname'] for m in matching]
        return zip(matching, names)

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
    
    def __call__(self, *args, **kwargs):
        self.update(*args, **kwargs)
        return self.index(*args, **kwargs)

class EventSubscribersView(SubscribersView):
    """Event-specific subscription view"""

    def indexes(self):
        _indexes = ['invited', 'confirmed', 'attended']
        catalog_indexes = super(EventSubscribersView, self).indexes()
        _indexes += [idx for idx in catalog_indexes if idx not in _indexes]
        return tuple(_indexes)

