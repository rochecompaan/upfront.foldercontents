# coding=utf-8

from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='upfront.foldercontents',
      version=version,
      description="A folder contents implementation for Plone that does not depend on the portal_catalog",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='',
      author='Roché Compaan',
      author_email='roche@upfrontsystems.co.za',
      url='http://svn.plone.org/svn/collective/upfront.foldercontents',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['upfront'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.content',
          'zope.index',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
