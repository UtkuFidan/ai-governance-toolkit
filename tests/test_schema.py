import copy

import pytest
import yaml
from pydantic import ValidationError

from ai_gov.cli import main
from ai_gov.schema import DEFAULT_INVENTORY, AISystem, Inventory, load_inventory


def raw():
    return yaml.safe_load(DEFAULT_INVENTORY.read_text())


def test_default_inventory_valid_and_illustrative():
    inv = load_inventory()
    assert len(inv.systems) >= 10
    assert all(s.illustrative for s in inv.systems)
    assert "llustrative" in inv.disclaimer


def test_owner_is_role_not_person_and_required():
    d = raw()["systems"][0]
    del d["owner"]
    with pytest.raises(ValidationError):
        AISystem.model_validate(d)


def test_bad_id_rejected():
    d = raw()["systems"][0]
    d["id"] = "SYS-1"
    with pytest.raises(ValidationError):
        AISystem.model_validate(d)


def test_unknown_field_rejected():
    d = raw()["systems"][0]
    d["surprise"] = 1
    with pytest.raises(ValidationError):
        AISystem.model_validate(d)


def test_vendor_needs_vendor_name():
    d = copy.deepcopy(raw()["systems"][0])
    d["provenance"] = "vendor"
    d["vendor_or_source"] = ""
    with pytest.raises(ValidationError):
        AISystem.model_validate(d)


def test_duplicate_ids_rejected():
    r = raw()
    r["systems"][1]["id"] = r["systems"][0]["id"]
    with pytest.raises(ValidationError):
        Inventory.model_validate(r)


def test_personal_data_flag():
    inv = load_inventory()
    by = {s.id: s for s in inv.systems}
    assert by["AI-001"].uses_personal_data
    assert not by["AI-007"].uses_personal_data  # sensor telemetry only


def test_bad_incident_severity():
    d = raw()["systems"][1]
    d["incidents"][0]["severity"] = "catastrophic"
    with pytest.raises(ValidationError):
        AISystem.model_validate(d)


def test_cli_validate_ok_and_fail(tmp_path, capsys):
    assert main(["inventory", "validate"]) == 0
    bad = tmp_path / "bad.yaml"
    bad.write_text("disclaimer: x\nsystems: [{id: nope}]\n")
    assert main(["inventory", "validate", "--file", str(bad)]) == 1
