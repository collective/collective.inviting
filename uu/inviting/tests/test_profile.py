import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import queryUtility, getSiteManager

from uu.inviting.tests.layers import DEFAULT_PROFILE_TESTING
from uu.subscribe.interfaces import ISubscribers, ISubscriptionCatalog
from uu.subscribe.interfaces import ISubscriptionKeys


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
        assert 'uu_inviting' in tool
        skin = tool.getSkin(self.THEME)
        path = tool.getSkinPath(self.THEME).split(',')
        # check order in path:
        assert path[0] == 'custom' and path[1] == 'uu_inviting'
        # get known object from skin:
        assert getattr(tool, 'uu.inviting.txt', None) is not None
        # try to acquire same object from portal:
        assert getattr(self.portal, 'uu.inviting.txt', None) is not None
    
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


