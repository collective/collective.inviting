import unittest2 as unittest

from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import queryUtility
from Acquisition import aq_base

from collective.inviting.tests.layers import DEFAULT_PROFILE_TESTING
from collective.subscribe.interfaces import IUIDStrategy, IItemResolver


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
    
    def test_resolve_item_from_uid(self):
        resolver = queryUtility(IItemResolver)
        assert resolver is not None
        resolved = resolver.get(self.content_uid)
        # they look like the same object, with the same intrinsic properties:
        assert resolved.UID() is self.content_uid
        assert resolved.id == 'f1'
        assert resolved.getPhysicalPath() == self.content.getPhysicalPath()
        # they are the same object with all acquisition wrappers removed:
        assert aq_base(resolved) is aq_base(self.content)
    
    def test_uid_for_item(self):
        assert self.content in self.portal.objectValues()
        assert self.content_uid is not None
        adapted = IUIDStrategy(self.content)
        assert adapted is not None
        assert adapted.getuid() == adapted() == self.content_uid

