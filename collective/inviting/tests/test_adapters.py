import unittest2 as unittest
from plone.app.testing import TEST_USER_ID, setRoles
from zope.component import queryUtility, getSiteManager

from collective.inviting.interfaces import IContentSubscribers, ISubscriberItems
from collective.inviting.adapters import ContentSubscribers, SubscriberItems
from collective.inviting.tests.layers import DEFAULT_PROFILE_TESTING
from collective.subscribe.interfaces import ISubscribers, ISubscriptionCatalog
from collective.subscribe.interfaces import IItemSubscriber
from collective.subscribe.subscriber import ItemSubscriber


class AdapterTest(unittest.TestCase):
    """Test default profile's installed configuration settings"""
    
    layer = DEFAULT_PROFILE_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'f1', title=u'Ex')
        self.content = self.portal['f1']
        self.content.reindexObject()
        self.content_uid = self.content.UID()
        self.container = queryUtility(ISubscribers)
        self.catalog = queryUtility(ISubscriptionCatalog)
        self.sub = ItemSubscriber(email='me@example.com', namespace='email')
    
    def test_lookups(self):
        """test adapter lookups"""
        assert isinstance(ISubscriberItems(self.sub),
                          SubscriberItems)
        assert isinstance(IContentSubscribers(self.content),
                          ContentSubscribers)
    
    def test_content_subscribers(self):
        """Content subscribers adapter search, index, unindex tests"""
        csubs = IContentSubscribers(self.content)
        relnames = ('invited', 'confirmed', 'attended')
        # test that there are no subscribers for any of the relnames for 
        # content yet
        assert self.sub not in self.container #not yet, at least
        for name in relnames:
            assert len(csubs.find(name)) == 0
        # index, and verify via find:
        csubs.index('invited', self.sub)
        assert self.sub in self.container # result of index through adapter
        assert self.sub in csubs.find('invited')
        assert 'invited' in csubs.subscriptions_for(self.sub)
        assert IItemSubscriber.providedBy(csubs.find('invited')[0])
        assert len(csubs.find('confirmed')) == 0
        assert len(csubs.find('attended')) == 0
        assert len(csubs.find()) == 1 #unamed, one subscription so far
        # index another name:
        csubs.index('confirmed', self.sub)
        assert self.sub in csubs.find('invited')
        assert self.sub in csubs.find('confirmed')
        assert 'confirmed' in csubs.subscriptions_for(self.sub)
        assert self.sub in csubs.find()
        # unindex, make sure item is not found:
        csubs.unindex('invited', self.sub)
        assert self.sub not in csubs.find('invited') #removed
        assert 'invited' not in csubs.subscriptions_for(self.sub)
        assert self.sub in csubs.find('confirmed')  #this still exists
        assert 'confirmed' in csubs.subscriptions_for(self.sub)
        # verify that we can look from the other direction at what we've done:
        subitems = ISubscriberItems(self.sub)
        assert self.content in subitems.find('confirmed')
        # finally, clean up:
        for name in relnames:
            csubs.unindex(name, self.sub)
            assert len(csubs.find(name)) == 0
    
    def test_subscriber_items(self):
        """Subscriber items adapter search, index, unindex tests"""
        subitems = ISubscriberItems(self.sub)
        relnames = ('invited', 'confirmed', 'attended')
        # verify that we are starting with a clean slate:
        for name in relnames:
            assert len(subitems.find(name)) == 0
        # index subscription to invited for self.content:
        subitems.index('invited', self.content)
        assert self.content in subitems.find('invited')
        # verify relationship from the other direction using the other adapter:
        csubs = IContentSubscribers(self.content)
        assert self.sub in csubs.find('invited')
        # finally, clean up:
        subitems.unindex('invited', self.content)
        for name in relnames:
            assert len(subitems.find(name)) == 0

