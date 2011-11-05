import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import queryUtility, getSiteManager

from collective.inviting.tests.layers import DEFAULT_PROFILE_TESTING
from collective.inviting.tests.layers import POST_UNINSTALL_PROFILE_TESTING
from collective.subscribe.interfaces import ISubscribers, ISubscriptionCatalog
from collective.subscribe.interfaces import ISubscriptionKeys


class DefaultProfileTest(unittest.TestCase):
    """Test default profile's installed configuration settings"""
    
    THEME = 'Sunburst Theme'
    
    layer = DEFAULT_PROFILE_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'f1', title=u'Ex')
        self.content = self.portal['f1']
        self.content.reindexObject()
        self.content_uid = self.content.UID()
    
    def test_skin_layer(self):
        tool = self.portal['portal_skins']
        assert 'collective_inviting' in tool
        skin = tool.getSkin(self.THEME)
        path = tool.getSkinPath(self.THEME).split(',')
        # check order in path:
        assert path[0] == 'custom' and path[1] == 'collective_inviting'
        # get known object from skin:
        assert getattr(tool, 'collective.inviting.txt', None) is not None
        # try to acquire same object from portal:
        assert getattr(self.portal, 'collective.inviting.txt', None) is not None
    
    def test_installed_container(self):
        """test locally installed persistent subscribers container utility"""
        container = queryUtility(ISubscribers)
        assert container is not None
        sm = getSiteManager(self.portal)
        assert container is sm.queryUtility(ISubscribers)
    
    def test_installed_catalog(self):
        """test locally installed persistent subscription catalog utility"""
        catalog = queryUtility(ISubscriptionCatalog)
        assert catalog is not None
        sm = getSiteManager(self.portal)
        assert catalog is sm.queryUtility(ISubscriptionCatalog)
    
    def test_installed_subkeys(self):
        """
        locally installed persistent subscription keys mapping utility
        """
        subkeys = queryUtility(ISubscriptionKeys)
        assert subkeys is not None
        sm = getSiteManager(self.portal)
        assert subkeys is sm.queryUtility(ISubscriptionKeys)


class UninstallProfileTest(unittest.TestCase):
    """Test uninstall profile correctly removes configuration, components"""
    
    THEME = 'Sunburst Theme'
    
    layer = POST_UNINSTALL_PROFILE_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
    
    def test_uninstalled_container(self):
        """test uninstall of persistent subscribers container utility"""
        container = queryUtility(ISubscribers)
        assert container is None
        sm = getSiteManager(self.portal)
        assert sm.queryUtility(ISubscribers) is None
        assert ISubscribers not in sm.utilities.__dict__['_provided']
        assert ISubscribers not in sm.utilities._subscribers[0]
    
    def test_uninstalled_catalog(self):
        """test uninstall of persistent subscription catalog utility"""
        catalog = queryUtility(ISubscriptionCatalog)
        assert catalog is None
        sm = getSiteManager(self.portal)
        assert sm.queryUtility(ISubscriptionCatalog) is None
        assert ISubscriptionCatalog not in sm.utilities.__dict__['_provided']
        assert ISubscriptionCatalog not in sm.utilities._subscribers[0]
    
    def test_uninstalled_subkeys(self):
        """
        test uninstalls of persistent subscription keys mapping utility
        """
        subkeys = queryUtility(ISubscriptionKeys)
        assert subkeys is None
        sm = getSiteManager(self.portal)
        assert sm.queryUtility(ISubscriptionKeys) is None
        assert ISubscriptionKeys not in sm.utilities.__dict__['_provided']
        assert ISubscriptionKeys not in sm.utilities._subscribers[0]

