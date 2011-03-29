import unittest2 as unittest


class PkgTest(unittest.TestCase):
    """basic unit tests for package"""
    
    def test_pkg_import(self):
        import uu.inviting
        from uu.inviting.zope2 import initialize

