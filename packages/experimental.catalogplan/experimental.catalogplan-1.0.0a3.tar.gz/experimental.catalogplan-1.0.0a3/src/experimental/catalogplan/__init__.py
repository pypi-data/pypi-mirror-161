# -*- coding: utf-8 -*-
import logging
import time

from Products.PluginIndexes.interfaces import ILimitedResultIndex
from Products.ZCatalog.plan import Benchmark, CatalogPlan, PriorityMap

logger = logging.getLogger(__name__)


def CatalogPlan_stop(self):
    self.end_time = time.time()
    self.duration = self.end_time - self.start_time
    # Make absolutely sure we never omit query keys from the plan
    current = PriorityMap.get_entry(self.cid, self.key)
    for key in self.query.keys():
        key = self.querykey_to_index.get(key, key)
        if key not in self.benchmark.keys():
            if current and key in current:
                self.benchmark[key] = Benchmark(*current[key])
            else:
                if key in self.catalog.indexes:
                    index = self.catalog.indexes[key]
                    self.benchmark[key] = Benchmark(
                        0, 0, ILimitedResultIndex.providedBy(index)
                    )
                else:
                    self.benchmark[key] = Benchmark(0, 0, False)
    PriorityMap.set_entry(self.cid, self.key, self.benchmark)
    self.log()


def CatalogPlan_make_key(self, query):
    if not query:
        return None
    valueindexes = self.valueindexes()
    key = keys = query.keys()
    values = [name for name in keys if name in valueindexes]
    if values:
        # If we have indexes whose values should be considered, we first
        # preserve all normal indexes and then add the keys whose values
        # matter including their value into the key
        key = [name for name in keys if name not in values]
        for name in values:
            v = query.get(name, [])
            # We need to make sure the key is immutable,
            # repr() is an easy way to do this without imposing
            # restrictions on the types of values.
            key.append((name, repr(v)))

    # --------- >8 ------------------------------------------------
    operatorkeys = [
        name for name in key
        if isinstance(query.get(name), dict)
    ]
    if operatorkeys:
        key = [name for name in key if name not in operatorkeys]
        key.extend([
            (name, tuple(sorted(query[name].keys()))) for name in operatorkeys
        ])
    # --------- 8< ------------------------------------------------

    # Workaround: Python 2.x accepted different types as sort key
    # for the sorted builtin. Python 3 only sorts on identical types.
    tuple_keys = set(key) - set(
        [x for x in key if not isinstance(x, tuple)])
    str_keys = set(key) - tuple_keys
    return tuple(sorted(str_keys)) + tuple(sorted(tuple_keys))


logger.info("*** CatalogPlan.stop monkey patch ***")
CatalogPlan.stop = CatalogPlan_stop

logger.info("*** CatalogPlan.make_key monkey patch ***")
CatalogPlan.make_key = CatalogPlan_make_key
