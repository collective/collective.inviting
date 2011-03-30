from zope.component import queryUtility

from uu.inviting.interfaces import IContentSubscribers
from uu.subscribe.interfaces import ISubscriptionCatalog

class SubscribersView(object):
    """
    Subscribers view of content item, shows lists of 
    subscriptions to content object.
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._catalog = queryUtility(ISubscriptionCatalog)
        self._provider = IContentSubscribers(context)

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


class EventSubscribersView(SubscribersView):
    """Event-specific subscription view"""

    def indexes(self):
        catalog_indexes = super(EventSubscribersView, self).indexes()
        return tuple(set(['invited', 'confirmed', 'attended']) | 
                     set(catalog_indexes))

