"""Budget ceilings, daemon accounting and invalid operator configuration."""
import os
import unittest
from unittest.mock import patch
from budget import Cost, TOOL_COST, BudgetError, check, limits, live_cost
from runtime import Result


class BudgetTests(unittest.TestCase):
    def test_dimensions_and_daemon_capacity(self):
        maximum = limits({'NCPU': 4, 'MemTotal': 4*1024**3})
        self.assertEqual((maximum.cpus, maximum.memory), (4_000_000_000, 4*1024**3))
        check(TOOL_COST, TOOL_COST, maximum)
        for cost in (Cost(cpus=1), Cost(memory=1), Cost(pids=1), Cost(containers=1)):
            with self.assertRaisesRegex(BudgetError, 'budget exceeded'):
                check(maximum, cost, maximum)
        with patch.dict(os.environ, {'PWNDEN_RUNTIME_CPUS': '0'}):
            with self.assertRaises(BudgetError):
                limits({'NCPU': 4, 'MemTotal': 4*1024**3})

    def test_created_managed_containers_only(self):
        def call(*args, **kwargs):
            if args[0:2] == ('container', 'ls'):
                return Result(0, '{"ID":"managed","Labels":"pwnden.managed=true","Names":"created"}\n'
                              '{"ID":"other","Labels":"app=postgres","Names":"database"}')
            self.assertEqual(args[-1], 'managed')
            return Result(0, '{"NanoCpus":2000000000,"Memory":2147483648,"PidsLimit":256}')
        self.assertEqual(live_cost(call), TOOL_COST)

    def test_unbounded_legacy_container_blocks_new_creation(self):
        def call(*args, **kwargs):
            if args[1] == 'ls':
                return Result(0, '{"ID":"old","Labels":"pwnden.kind=terminal","Names":"old"}')
            return Result(0, '{}')
        with self.assertRaisesRegex(BudgetError, 'no resource ceilings'):
            live_cost(call)
