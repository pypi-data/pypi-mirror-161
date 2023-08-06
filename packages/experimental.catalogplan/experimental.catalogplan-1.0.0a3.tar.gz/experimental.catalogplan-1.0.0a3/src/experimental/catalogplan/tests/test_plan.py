# -*- coding: utf-8 -*-
import time
import unittest

import six
from Products.PluginIndexes.DateRangeIndex.DateRangeIndex import DateRangeIndex
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
from Products.PluginIndexes.PathIndex.PathIndex import PathIndex
from Products.ZCatalog.Catalog import Catalog
from Products.ZCatalog.plan import MAX_DISTINCT_VALUES
from Products.ZCatalog.ZCatalog import ZCatalog
from zope.testing import cleanup

HERE = __file__


class Dummy(object):

    def __init__(self, num):
        self.num = num

    def big(self):
        return self.num > 5

    def numbers(self):
        return (self.num, self.num + 1)

    def getPhysicalPath(self):
        return '/{0}'.format(self.num)

    def start(self):
        return '2013-07-{0:02d}'.format(self.num + 1)

    def end(self):
        return '2013-07-{0:02d}'.format(self.num + 2)


class TestCatalogPlan(cleanup.CleanUp, unittest.TestCase):

    def assertRegex(self, *args, **kwargs):
        if six.PY2:
            return self.assertRegexpMatches(*args, **kwargs)
        else:
            return super(TestCatalogPlan, self).assertRegex(*args, **kwargs)

    def setUp(self):
        cleanup.CleanUp.setUp(self)
        self.cat = Catalog('catalog')

    def _makeOne(self, catalog=None, query=None):
        from Products.ZCatalog.plan import CatalogPlan
        if catalog is None:
            catalog = self.cat
        return CatalogPlan(catalog, query=query)

    def test_getCatalogPlan_partial(self):
        zcat = ZCatalog("catalog")
        cat = zcat._catalog

        class SlowFieldIndex(FieldIndex):
            def query_index(self, record, resultset=None):
                time.sleep(0.1)
                return super(SlowFieldIndex, self).query_index(
                    record, resultset)

        class SlowerDateRangeIndex(DateRangeIndex):
            def query_index(self, record, resultset=None):
                time.sleep(0.2)
                return super(SlowerDateRangeIndex, self).query_index(
                    record, resultset)

        cat.addIndex("num", SlowFieldIndex("num"))
        cat.addIndex("numbers", KeywordIndex("numbers"))
        cat.addIndex("path", PathIndex("getPhysicalPath"))
        cat.addIndex("date", SlowerDateRangeIndex("date", "start", "end"))

        for i in range(MAX_DISTINCT_VALUES * 2):
            obj = Dummy(i)
            zcat.catalog_object(obj, str(i))

        query1 = {"num": 2, "numbers": 3, "date": "2013-07-03"}
        # query with no result, because of `numbers`
        query2 = {"num": 2, "numbers": -1, "date": "2013-07-03"}

        # without a plan index are orderd alphabetically by default
        self.assertEqual(zcat._catalog.getCatalogPlan(query1).plan(), None)
        self.assertEqual(
            cat._sorted_search_indexes(query1),
            ["date", "num", "numbers"]
        )

        self.assertEqual([b.getPath() for b in zcat.search(query1)], ["2"])
        self.assertRegex(
            zcat.getCatalogPlan(),
            r"(?ms).*'date':\s*\([0-9\.]+, [0-9\.]+, True\)"
        )
        self.assertRegex(
            zcat.getCatalogPlan(),
            r"(?ms).*'num':\s*\([0-9\.]+, [0-9\.]+, True\)"
        )
        self.assertRegex(
            zcat.getCatalogPlan(),
            r"(?ms).*'numbers':\s*\([0-9\.]+, [0-9\.]+, True\)"
        )

        # after first search field are orderd by speed
        self.assertEqual(
            cat.getCatalogPlan(query2).plan(), ["numbers", "num", "date"])

        self.assertEqual([b.getPath() for b in zcat.search(query2)], [])

        # `date', `num`, and `numbers` are all involved to filter the
        #  results(limit flag) despite in the last query search whitin
        #  `num` and `date` wasn't done
        self.assertRegex(
            zcat.getCatalogPlan(),
            r"(?ms).*'date':\s*\([0-9\.]+, [0-9\.]+, True\)"
        )
        self.assertRegex(
            zcat.getCatalogPlan(),
            r"(?ms).*'num':\s*\([0-9\.]+, [0-9\.]+, True\)"
        )
        self.assertRegex(
            zcat.getCatalogPlan(),
            r"(?ms).*'numbers':\s*\([0-9\.]+, [0-9\.]+, True\)"
        )
        self.assertEqual(
            cat.getCatalogPlan(query2).plan(), ["numbers", "num", "date"]
        )

        # search again doesn't change the index order
        self.assertEqual([b.getPath() for b in zcat.search(query1)], ["2"])
        self.assertEqual(
            cat.getCatalogPlan(query2).plan(), ["numbers", "num", "date"]
        )

    def test_not_query(self):
        # not query is generally slower, force this behavior for testing
        class SlowNotFieldIndex(FieldIndex):
            def query_index(self, record, resultset=None):
                if getattr(record, 'not', None):
                    time.sleep(0.1)
                return super(SlowNotFieldIndex, self).query_index(
                    record, resultset)

        zcat = ZCatalog("catalog")
        cat = zcat._catalog
        cat.addIndex(
            'num1', SlowNotFieldIndex('num1', extra={"indexed_attrs": "num"}))
        cat.addIndex(
            'num2', SlowNotFieldIndex('num2', extra={"indexed_attrs": "num"}))
        for i in range(100):
            obj = Dummy(i)
            zcat.catalog_object(obj, str(i))

        query1 = {"num1": {"not": 2}, "num2": 3}
        query2 = {"num1": 2, "num2": {'not': 5}}

        # without a plan index are orderd alphabetically by default
        for query in [query1, query2]:
            self.assertEqual(zcat._catalog.getCatalogPlan(query).plan(), None)
            self.assertEqual(
                cat._sorted_search_indexes(query),
                ["num1", "num2"]
            )

        self.assertEqual([b.getPath() for b in zcat.search(query1)], ['3'])
        self.assertEqual([b.getPath() for b in zcat.search(query2)], ['2'])
        # although there are the same fields, the plans are different, and the
        # slower `not` query put the field as second in the plan
        self.assertEqual(cat.getCatalogPlan(query1).plan(), ["num2", "num1"])
        self.assertEqual(cat.getCatalogPlan(query2).plan(), ["num1", "num2"])

        # search again doesn't change the order
        self.assertEqual([b.getPath() for b in zcat.search(query1)], ['3'])
        self.assertEqual([b.getPath() for b in zcat.search(query2)], ['2'])
        self.assertEqual(cat.getCatalogPlan(query1).plan(), ["num2", "num1"])
        self.assertEqual(cat.getCatalogPlan(query2).plan(), ["num1", "num2"])
