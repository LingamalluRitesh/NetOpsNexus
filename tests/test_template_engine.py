"""
Unit tests for Jinja2 Configuration Template Engine.
"""

import pytest
from backend.app.configurations.template_engine import ConfigTemplateEngine


def test_template_variable_extraction():
    tmpl_text = "hostname {{ hostname }}\ninterface {{ int_name }}\n ip address {{ ip }} {{ mask }}\n no shutdown\n"
    engine = ConfigTemplateEngine()
    vars_found = engine.extract_variables(tmpl_text)
    assert set(vars_found) == {"hostname", "int_name", "ip", "mask"}


def test_template_rendering_success():
    tmpl_text = "hostname {{ hostname }}\ninterface {{ int_name }}\n ip address {{ ip }} {{ mask }}\n no shutdown\n"
    engine = ConfigTemplateEngine()
    res = engine.render_template(
        tmpl_text,
        {"hostname": "RTR-TEST-01", "int_name": "GigabitEthernet0/1", "ip": "10.100.1.1", "mask": "255.255.255.0"}
    )
    assert res.syntax_valid is True
    assert "hostname RTR-TEST-01" in res.rendered_config
    assert "GigabitEthernet0/1" in res.rendered_config


def test_template_missing_variable_error():
    tmpl_text = "hostname {{ hostname }}\ninterface {{ int_name }}\n"
    engine = ConfigTemplateEngine()
    res = engine.render_template(tmpl_text, {"hostname": "RTR-TEST-01"})
    assert res.syntax_valid is False
    assert len(res.errors) > 0
