# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from msd.digest.testing import MSD_DIGEST_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that msd.digest is properly installed."""

    layer = MSD_DIGEST_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if msd.digest is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('msd.digest'))

    def test_browserlayer(self):
        """Test that IMsdDigestLayer is registered."""
        from msd.digest.interfaces import IMsdDigestLayer
        from plone.browserlayer import utils
        self.assertIn(IMsdDigestLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = MSD_DIGEST_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['msd.digest'])

    def test_product_uninstalled(self):
        """Test if msd.digest is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled('msd.digest'))
