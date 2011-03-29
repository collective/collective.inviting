from uu.subscribe.interfaces import ISubscribersOf, IItemsFor


class IContentSubscribers(ISubscribersOf):
    """
    Content adapter interface to find subscribers, index subscriptions
    by subsription name.  In addition to base interface find() method, this
    interface declares index() and unindex() methods to maintain relationships
    in context of content and a site.
    
    For simplicity, the methods of this adapter work on singular subscription
    relationship names, not querying for multiple names.
    """
    
    def index(name, subscriber):
        """
        Given relationship name, and subscriber (as instance providing 
        uu.subscribe.interfaces.IItemSubscriber or as a signature tuple),
        index the subscription in the local subscription catalog.
        """
    
    def unindex(name, subscriber):
        """
        Given relationship name, and subscriber (as instance providing 
        uu.subscribe.interfaces.IItemSubscriber or as a signature tuple),
        remove/unindex any matching subscription in the local subscription
        catalog.
        """


class ISubscriberItems(IItemsFor):
    """
    Content adapter interface to find items, index subscriptions by
    subscription name. In addition to base interface find() method, this
    interface declares index() and unindex() methods to maintain relationships
    in context of a subscriber and a site.
    
    For simplicity, the methods of this adapter work on singular subscription
    relationship names, not querying for multiple names.
    """
    
    def index(name, item):
        """
        Given relationship name, and item (as content instance or as a
        [U]UID), index the subscription in the local subscription catalog.
        """
    
    def unindex(name, item):
        """
        Given relationship name, and item (as content instance or as a
        [U]UID), remove/unindex any matching subscription in the local
        subscription catalog.
        """

