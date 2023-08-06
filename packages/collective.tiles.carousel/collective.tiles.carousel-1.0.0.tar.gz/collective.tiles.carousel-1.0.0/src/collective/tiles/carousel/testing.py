from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.tiles.carousel


class CollectiveTilesCarouselLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        import plone.app.mosaic

        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=plone.app.mosaic)
        self.loadZCML(package=collective.tiles.carousel)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.tiles.carousel:default")


COLLECTIVE_TILES_CAROUSEL_FIXTURE = CollectiveTilesCarouselLayer()


COLLECTIVE_TILES_CAROUSEL_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_TILES_CAROUSEL_FIXTURE,),
    name="CollectiveTilesCarouselLayer:IntegrationTesting",
)


COLLECTIVE_TILES_CAROUSEL_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_TILES_CAROUSEL_FIXTURE,),
    name="CollectiveTilesCarouselLayer:FunctionalTesting",
)


COLLECTIVE_TILES_CAROUSEL_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_TILES_CAROUSEL_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CollectiveTilesCarouselLayer:AcceptanceTesting",
)
