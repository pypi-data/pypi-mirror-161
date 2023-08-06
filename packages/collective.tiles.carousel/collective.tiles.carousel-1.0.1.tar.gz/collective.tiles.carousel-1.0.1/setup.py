"""Installer for the collective.tiles.carousel package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="collective.tiles.carousel",
    version="1.0.1",
    description="Slider for plone.app.mosaic based on Bootstrap 5",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Peter Holzer",
    author_email="peter.holzer@agitator.com",
    url="https://github.com/collective/collective.tiles.carousel",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/collective.tiles.carousel",
        "Source": "https://github.com/collective/collective.tiles.carousel",
        "Tracker": "https://github.com/collective/collective.tiles.carousel/issues",
        # 'Documentation': 'https://collective.tiles.carousel.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective", "collective.tiles"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "z3c.jbot",
        "Products.CMFPlone",
        "plone.app.mosaic",
        "plone.app.tiles",
        "plone.tiles",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.testing",
            "plone.app.robotframework[debug]",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = collective.tiles.carousel.locales.update:update_locale
    """,
)
