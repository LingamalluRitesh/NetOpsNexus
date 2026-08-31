"""
Unit tests for Configuration Diff Engine.
"""

import pytest
from backend.app.configurations.diff_engine import ConfigDiffEngine


def test_diff_identical_configs():
    cfg = "hostname RTR-CORE-01\ninterface Gi0/1\n no shutdown\n"
    res = ConfigDiffEngine.compare_configs(cfg, cfg)
    assert res.is_identical is True
    assert res.additions == 0
    assert res.deletions == 0


def test_diff_modifications_and_additions():
    src = "hostname RTR-CORE-01\ninterface Gi0/1\n shutdown\n"
    tgt = "hostname RTR-CORE-01\ninterface Gi0/1\n no shutdown\n description Uplink to Spine\n"
    res = ConfigDiffEngine.compare_configs(src, tgt)
    assert res.is_identical is False
    assert res.additions > 0
    assert res.deletions > 0
    assert len(res.diff_lines) > 0
    assert "- shutdown" in res.unified_diff
    assert "+ no shutdown" in res.unified_diff
