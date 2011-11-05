
from zope.component import adapts
from zope.interface import implements
from zope.app.component.hooks import getSite
from Products.Archetypes.interfaces import IReferenceable

from collective.subscribe.interfaces import IUIDStrategy, IItemResolver

# conditional imports to support various framework components:
try:
    from plone.uuid.interfaces import IUUID
    HAS_PLONE_UUID = True #has plone.uuid framework component in sys.path
except ImportError:
    HAS_PLONE_UUID = False
try:
    import plone.app.uuid
    HAS_PLONE_APP_UUID = True
except ImportError:
    HAS_PLONE_APP_UUID = False
try:
    from Products.CMFCore.utils import getToolByName
    from Products.CMFCore.interfaces import ICatalogTool
    HAS_CMF = True #is CMF, possibly Plone
except ImportError:
    HAS_CMF = False
try:
    from Products.Archetypes.interfaces import IReferenceable
    HAS_AT = True and HAS_CMF #is Plone/CMF with Archetypes
except ImportError:
    HAS_AT = False


class ItemUID(object):
    implements(IUIDStrategy)
    if HAS_AT:
        adapts(IReferenceable)
    
    def __init__(self, context):
        self.context = context
    
    def getuid(self):
        if HAS_PLONE_UUID:
            uid = IUUID(self.context, None)
            if uid is not None:
                return uid
        if HAS_AT:
            if IReferenceable.providedBy(self.context):
                return self.context.UID()
        return None
    
    __call__ = getuid


class ItemResolver(object):
    """utility class for local UID to object lookups"""
    
    implements(IItemResolver)
    
    def ___init__(self):
        pass #TODO rewrite ctor
    
    def get(self, uid):
        """return resolved object for uid or None"""
        site = getSite()
        if HAS_AT or HAS_PLONE_APP_UUID:
            # common assumption: UID is an index in the catalog
            uidcat = getToolByName(site, 'portal_catalog')
            brains = uidcat(UID=str(uid))
            if len(brains) >= 1:
                return brains[0].getObject()
        return None

