import logging

from zope.component import getSiteManager

from uu.subscribe.interfaces import ISubscribers, ISubscriptionCatalog
from uu.subscribe.subscriber import SubscribersContainer
from uu.subscribe.catalog import SubscriptionCatalog


logger = logging.getLogger('uu.inviting')


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

