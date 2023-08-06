# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

version = '1.0.0a3'

setup(name='experimental.catalogplan',
      version=version,
      description="Experimental ZCatalog plan",
      long_description=(open("README.rst").read() + "\n" +
                        open("CHANGES.rst").read()),
      long_description_content_type="text/x-rst",
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          'Framework :: Zope2',
          'Framework :: Plone',
          'Framework :: Plone :: 4.3',
          'Framework :: Plone :: 5.0',
          'Framework :: Plone :: 5.1',
          'Framework :: Plone :: 5.2',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
      ],
      keywords='monkeypatch traverse',
      author='Mauro Amico',
      author_email='mauro.amico@gmail.com',
      url='https://github.com/mamico/experimental.catalogplan',
      project_urls={
          'Issue Tracker': 'https://github.com/mamico/'
                           'experimental.catalogplan/issues',
          'Sources': 'https://github.com/mamico/experimental.catalogplan',
      },
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['experimental', ],
      include_package_data=True,
      zip_safe=False,
      test_suite="experimental.catalogplan",
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.ZCatalog>3.0,<6.3',
      ],
      extras_require={
          'test': ['Products.CMFPlone[test]']
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
