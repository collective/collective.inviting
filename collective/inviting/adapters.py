from zope.interface import implements
from zope.component import adapts, queryUtility
from zope.app.component.hooks import getSite
from Products.Archetypes.interfaces import IReferenceable

from collective.inviting.interfaces import IContentSubscribers, ISubscriberItems
from collective.subscribe.interfaces import (ISubscribers, IItemSubscriber, 
    ISubscriptionCatalog, IUIDStrategy, IItemResolver)

class ContentSubscribers(object):
    """
    adapter for content item specific context (via adaptation/construction)
    in assumed general context of the local (Plone) site (via getSite()). 
    Manages search, indexing, unindexing of subscription relationships for
    the adapted context.
    
    For simplicity, the methods of this adapter work on singular subscription
    relationship names, not querying for multiple names.
    """
    implements(IContentSubscribers)
    adapts(IReferenceable)
        
    def __init__(self, context):
        self.context = context
        self.uid = IUIDStrategy(context).getuid()
        self.catalog = queryUtility(ISubscriptionCatalog)
        self.container = queryUtility(ISubscribers)
    
    def find(self, name=None):
        """
        Find subscribers for which an index entry exists for the provided
        named subscription relationship, and for which a subscriber object
        exists (no orphaned index signature entries are included).
        """
        container = self.container
        if name is None:
            signatures = self.catalog.search(self.uid)
        else:
            signatures = self.catalog.search({ name : self.uid })
        if not signatures:
            return []
        return [container.get(s) for s in signatures if s in container]
    
    def subscriptions_for(self, subscriber):
        """Find subscription names for a given subscriber for the context"""
        relnames = []
        if IItemSubscriber.providedBy(subscriber):
            subscriber = subscriber.signature()
        for relname, index in self.catalog.indexes.items():
            if subscriber in index.subscribers_for(self.uid):
                relnames.append(relname)
        return relnames
     
    def index(self, name, subscriber):
        """ """
        # ensure subscriber is in container of subscribers
        container = self.container        
        if IItemSubscriber.providedBy(subscriber):
            if subscriber not in container:
                signature, subscriber = container.add(subscriber)
        else:
            if not (isinstance(subscriber, tuple) and len(subscriber)==2):
                raise ValueError('Subscriber signature malformed.')
            if subscriber not in container:
                #signature without backing item subscriber instance, so
                # create one.
                if subscriber[0] == 'email':
                    container.add(namespace='email', email=str(subscriber[1]))
                else:
                    container.add(namespace=subscriber[0], user=subscriber[1])
        
        # index in catalog
        self.catalog.index(subscriber, self.uid, names=(name,))
    
    def unindex(self, name, subscriber):
        """ """
        self.catalog.unindex(subscriber, self.uid, names=(name,))


class SubscriberItems(object):
    """
    Adapter for context of a subscriber within a site, used for looking up
    and indexing (or unindexing) named subscription relationships to content
    items.
    """
    implements(ISubscriberItems)
    adapts(IItemSubscriber)
    
    def __init__(self, context):
        if not IItemSubscriber.providedBy(context):
            raise ValueError('context must provided IItemSubscriber')
        self.context = context
        self.signature = context.signature()
        self.catalog = queryUtility(ISubscriptionCatalog)
        self.container = queryUtility(ISubscribers)
        if self.signature not in self.container:
            self.container.add(context)
    
    def find(self, name=None):
        """ """
        resolver = queryUtility(IItemResolver)
        if name is None:
            uids = self.catalog.search(self.signature)
        else:
            uids = self.catalog.search({ name : self.signature })
        if not uids:
            return []
        return [o for o in [resolver.get(uid) for uid in uids] if o]
    
    def index(self, name, item):
        """
        Get UID for item, then index in catalog for named subscription
        relationship of adapted subscriber to the item uid
        """
        uid = IUIDStrategy(item).getuid()
        self.catalog.index(self.signature, uid, names=(name,))
    
    def unindex(self, name, item):
        """ """
        uid = IUIDStrategy(item).getuid()
        self.catalog.unindex(self.signature, uid, names=(name,))


