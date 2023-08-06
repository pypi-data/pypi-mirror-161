========================
experimental.catalogplan
========================

.. image:: https://badge.fury.io/py/experimental.catalogplan.svg
    :target: https://badge.fury.io/py/experimental.catalogplan
    :alt: latest release version badge by Badge Fury

.. image:: https://coveralls.io/repos/github/mamico/experimental.catalogplan/badge.svg
    :target: https://coveralls.io/github/mamico/experimental.catalogplan
    :alt: Coveralls status

Introduction
============


* fix plan for unused index in a query https://github.com/zopefoundation/Products.ZCatalog/pull/138
  This fix is now released in Products.ZCatalog 6.3.

* avoid to have DateRecurringIndex between the valueindexes https://github.com/collective/Products.DateRecurringIndex/pull/8

* Fix catalog plan for query with operators https://github.com/zopefoundation/Products.ZCatalog/pull/139
  This fix (only for `not` operator) is now released in Products.ZCatalog 6.3.

Usage
=====

Plone::

    [instance]
    recipe = plone.recipe.zope2instance
    eggs =
        experimental.catalogplan

Zope::

    [instance]
    recipe = plone.recipe.zope2instance
    eggs =
        experimental.catalogplan
    zcml =
        experimental.catalogplan


Warning
=======

This is an experimental addon, mostly safe, but still experimental

**USE AT YOUR OWN RISK**
