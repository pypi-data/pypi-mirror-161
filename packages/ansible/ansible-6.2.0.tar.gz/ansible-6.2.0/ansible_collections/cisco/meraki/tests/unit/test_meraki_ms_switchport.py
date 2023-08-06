import pytest
import cisco.meraki.modules.meraki_ms_switchport as meraki_ms_switchport


def test_main_function(monkeypatch):
    monkeypatch.setattr(meraki_ms_switchport.AnsibleModule, "exit_json", fake_exit_json)
    set_module_args({"api_key": "abc123"})
    meraki_ms_switchport.main()
