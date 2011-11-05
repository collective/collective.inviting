from zope.interface import Interface
from zope import schema

from collective.subscribe.interfaces import ISubscribersOf, IItemsFor


class IContentSubscribers(ISubscribersOf):
    """
    Content adapter interface to find subscribers, index subscriptions
    by subsription name.  In addition to base interface find() and 
    subscribers_for() methods providing query of subscribers in context, this
    interface declares index() and unindex() methods to maintain relationships
    in context of content and a site.
    
    For simplicity, the methods of this adapter work on singular subscription
    relationship names, not querying for multiple names.
    """
    
    def index(name, subscriber):
        """
        Given relationship name, and subscriber (as instance providing 
        collective.subscribe.interfaces.IItemSubscriber or as a signature tuple),
        index the subscription in the local subscription catalog.
        """
    
    def unindex(name, subscriber):
        """
        Given relationship name, and subscriber (as instance providing 
        collective.subscribe.interfaces.IItemSubscriber or as a signature tuple),
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


class IMailSender(Interface):
    """Email sender metadata"""
    
    from_name = schema.TextLine(required=False)
    from_address = schema.BytesLine()
    reply_name = schema.TextLine(required=False)
    reply_address = schema.BytesLine()


class IMailRecipient(Interface):
    """Email recipient metadata"""
    address = schema.BytesLine(title=u'Email address', required=True)
    name = schema.TextLine(title=u'Name',
                           description=u'Full name',
                           required=False)

