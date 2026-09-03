"""
Unit tests for SNMP MIB Dictionary and OID Tree Engine.
"""

import pytest
from backend.app.adapters.mibs.mib_dictionary import MibDictionary, MibSyntax, MibAccess


def test_mib_dictionary_lookups():
    # Lookup sysDescr
    node = MibDictionary.lookup_oid("1.3.6.1.2.1.1.1.0")
    assert node is not None
    assert node.name == "sysDescr"
    assert node.syntax == MibSyntax.OCTET_STRING
    assert node.access == MibAccess.READ_ONLY

    # Lookup ifHCInOctets
    if_node = MibDictionary.lookup_oid("1.3.6.1.2.1.31.1.1.1.6")
    assert if_node is not None
    assert if_node.name == "ifHCInOctets"
    assert if_node.syntax == MibSyntax.COUNTER64

    # Lookup by name
    cpu_node = MibDictionary.lookup_name("cpmCPUTotal5sec")
    assert cpu_node is not None
    assert cpu_node.mib_module == "CISCO-PROCESS-MIB"

    # List module nodes
    if_nodes = MibDictionary.list_by_module("IF-MIB")
    assert len(if_nodes) >= 5
    assert any(n.name == "ifOperStatus" for n in if_nodes)
