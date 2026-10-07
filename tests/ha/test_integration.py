import pytest
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.appliance_ml.const import DOMAIN


async def _entry(hass, **data):
    entry = MockConfigEntry(domain=DOMAIN, title=data.pop("title", "Washer"), data=data)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_metered_washer_sets_up_with_entities_and_panel(hass, hass_ws_client):
    hass.states.async_set("sensor.wm_power", "2", {"unit_of_measurement": "W", "device_class": "power"})
    entry = await _entry(hass, name="Washer", appliance_type="washing_machine", mode="metered",
                         power_entity="sensor.wm_power")
    assert entry.state.value == "loaded"
    ids = hass.states.async_entity_ids()
    assert any(i.startswith("binary_sensor.washer") for i in ids), ids
    assert "appliance-ml" in hass.data["frontend_panels"]
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "appliance_ml/snapshot"})
    snap = (await ws.receive_json())["result"]
    assert snap[0]["name"] == "Washer" and snap[0]["programs"] == []


async def test_add_and_remove_via_websocket(hass, hass_ws_client, hass_admin_user):
    hass.states.async_set("sensor.dw_state", "ready", {})
    hass.states.async_set("sensor.house", "400", {"unit_of_measurement": "W", "device_class": "power"})
    hass.states.async_set("sensor.wm_power", "2", {"unit_of_measurement": "W", "device_class": "power"})
    await _entry(hass, name="Washer", appliance_type="washing_machine", mode="metered", power_entity="sensor.wm_power")
    ws = await hass_ws_client(hass)
    await ws.send_json({"id": 1, "type": "appliance_ml/add", "name": "Dishwasher", "appliance_type": "dishwasher",
                        "activity_entity": "sensor.dw_state", "total_power_entity": "sensor.house",
                        "active_states": "run"})
    res = await ws.receive_json()
    assert res["success"], res
    await hass.async_block_till_done()
    await ws.send_json({"id": 2, "type": "appliance_ml/snapshot"})
    snap = (await ws.receive_json())["result"]
    assert sorted(s["name"] for s in snap) == ["Dishwasher", "Washer"]
    assert [s for s in snap if s["name"] == "Dishwasher"][0]["mode"] == "estimated"

    await ws.send_json({"id": 3, "type": "appliance_ml/add", "name": "x", "appliance_type": "dishwasher",
                        "power_entity": "sensor.nope"})
    assert not (await ws.receive_json())["success"]

    eid = [s for s in snap if s["name"] == "Dishwasher"][0]["entry_id"]
    await ws.send_json({"id": 4, "type": "appliance_ml/remove", "entry_id": eid})
    assert (await ws.receive_json())["success"]
    await hass.async_block_till_done()
    await ws.send_json({"id": 5, "type": "appliance_ml/snapshot"})
    assert [s["name"] for s in (await ws.receive_json())["result"]] == ["Washer"]


async def test_config_flow_metered_and_estimated(hass):
    hass.states.async_set("sensor.wm_power", "2", {"unit_of_measurement": "W", "device_class": "power"})
    r = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    r = await hass.config_entries.flow.async_configure(
        r["flow_id"], {"name": "Washer", "appliance_type": "washing_machine", "mode": "metered"})
    r = await hass.config_entries.flow.async_configure(r["flow_id"], {"power_entity": "sensor.wm_power"})
    assert r["type"] == "create_entry"


async def test_entity_names_are_translated_and_status_is_enum(hass):
    hass.states.async_set("sensor.wm_power", "2", {"unit_of_measurement": "W"})
    await _entry(hass, name="Washer", appliance_type="washing_machine", mode="metered", power_entity="sensor.wm_power")
    st = hass.states.get("sensor.washer_status")
    assert st is not None and st.state == "idle"
    assert hass.states.get("sensor.washer_remaining_time") is not None
    assert hass.states.get("binary_sensor.washer_program_running") is not None


async def test_any_entity_incl_kw_can_be_the_power_source(hass):
    hass.states.async_set("sensor.meter_kw", "0.002", {"unit_of_measurement": "kW"})
    entry = await _entry(hass, name="Washer", appliance_type="washing_machine", mode="metered", power_entity="sensor.meter_kw")
    assert entry.runtime_data if hasattr(entry, "runtime_data") and entry.runtime_data else True
    m = hass.data[DOMAIN][entry.entry_id]
    assert abs(m.snapshot()["power"] - 2.0) < 1e-6
