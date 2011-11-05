import logging

from zope.component import getSiteManager

from collective.subscribe.interfaces import ISubscribers, ISubscriptionCatalog
from collective.subscribe.interfaces import ISubscriptionKeys
from collective.subscribe.subscriber import SubscribersContainer
from collective.subscribe.catalog import SubscriptionCatalog
from collective.subscribe.keys import SubscriptionKeys


logger = logging.getLogger('collective.inviting')


def _install_local_utility(context, component, iface, name=u''):
    sm = getSiteManager(context.getSite())
    if sm.queryUtility(iface) is None:
        sm.registerUtility(component, provided=iface, name=name)
        logger.info('Install %s local utility in site.' % iface)


def install_subscribers_container(context):
    container = SubscribersContainer()
    _install_local_utility(context, container, ISubscribers)


def install_subscription_catalog(context):
    catalog = SubscriptionCatalog()
    _install_local_utility(context, catalog, ISubscriptionCatalog)


def install_subscription_keys(context):
    subkeys = SubscriptionKeys()
    _install_local_utility(context, subkeys, ISubscriptionKeys)


def _uninstall_local_utility(context, iface, name=u''):
    sm = getSiteManager(context.getSite())
    component = sm.queryUtility(iface)
    if component is not None:
        if name:
            sm.unregisterUtility(component, iface, name=name)
        else:
            sm.unregisterUtility(component, iface)
        logger.info('Uninstall %s local utility in site.' % iface)
        del component
        if not name:
            sm.utilities.unsubscribe((), iface)
        if iface in sm.utilities.__dict__['_provided']:
            del sm.utilities.__dict__['_provided'][iface]
        if iface in sm.utilities._subscribers[0]:
            del sm.utilities._subscribers[0][iface]


def uninstall_local_components(context):
    _uninstall_local_utility(context, ISubscribers)
    _uninstall_local_utility(context, ISubscriptionCatalog)
    _uninstall_local_utility(context, ISubscriptionKeys)

