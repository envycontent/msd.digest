# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import msd.digest


class MsdDigestLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=msd.digest)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'msd.digest:default')


MSD_DIGEST_FIXTURE = MsdDigestLayer()


MSD_DIGEST_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MSD_DIGEST_FIXTURE,),
    name='MsdDigestLayer:IntegrationTesting'
)


MSD_DIGEST_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MSD_DIGEST_FIXTURE,),
    name='MsdDigestLayer:FunctionalTesting'
)


MSD_DIGEST_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MSD_DIGEST_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='MsdDigestLayer:AcceptanceTesting'
)
