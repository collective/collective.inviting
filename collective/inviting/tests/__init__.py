import unittest2 as unittest


class PkgTest(unittest.TestCase):
    """basic unit tests for package"""
    
    def test_pkg_import(self):
        import collective.inviting
        from collective.inviting.zope2 import initialize

