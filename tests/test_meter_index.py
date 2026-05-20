"""Test: retrieve the latest index for every accessible contract and store it.

Storage format mirrors hass.helpers.storage.Store so the data file can be
loaded directly by the integration once it runs inside Home Assistant:

    .storage/regiedeseauxmpl.json
    {
        "version": 1,
        "minor_version": 1,
        "key": "regiedeseauxmpl",
        "data": {
            "<contract_id>": {
                "index": <float m³>,
                "timestamp": "<ISO-8601>"
            },
            ...
        }
    }

Run:
    REGIE_USERNAME=your@email REGIE_PASSWORD=yourpwd python tests/test_meter_index.py
or via pytest:
    REGIE_USERNAME=... REGIE_PASSWORD=... pytest tests/test_meter_index.py -s
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Minimal Home Assistant stubs so the integration modules can be imported
# without a running HA instance.
# ---------------------------------------------------------------------------
for mod in [
    "homeassistant",
    "homeassistant.exceptions",
    "homeassistant.config_entries",
    "homeassistant.core",
    "homeassistant.helpers",
    "homeassistant.helpers.aiohttp_client",
    "homeassistant.helpers.update_coordinator",
    "homeassistant.components",
    "homeassistant.components.sensor",
    "homeassistant.const",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

class _HomeAssistantError(Exception):
    pass

sys.modules["homeassistant"].exceptions.HomeAssistantError = _HomeAssistantError
sys.modules["homeassistant.exceptions"].HomeAssistantError = _HomeAssistantError

# ---------------------------------------------------------------------------

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
import pytest

from custom_components.regiedeseauxmpl.api import RegieDesEauxAPI
from custom_components.regiedeseauxmpl.exceptions import CannotConnect, InvalidAuth

USERNAME = os.getenv("REGIE_USERNAME", "test_user")
PASSWORD = os.getenv("REGIE_PASSWORD", "test_pass")

# Where to write the HA-compatible storage file
STORAGE_DIR = Path(".storage")
STORAGE_KEY = "regiedeseauxmpl"
STORAGE_FILE = STORAGE_DIR / f"{STORAGE_KEY}.json"


def _save_ha_store(data: dict) -> None:
    """Write *data* to .storage/<key>.json in HA Store format."""
    STORAGE_DIR.mkdir(exist_ok=True)
    payload = {
        "version": 1,
        "minor_version": 1,
        "key": STORAGE_KEY,
        "data": data,
    }
    STORAGE_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"\nStored → {STORAGE_FILE.resolve()}")


@pytest.mark.skipif(
    not (os.getenv("REGIE_USERNAME") and os.getenv("REGIE_PASSWORD")),
    reason="REGIE_USERNAME and REGIE_PASSWORD environment variables required for real API test"
)
@pytest.mark.asyncio
async def test_meter_index():
    """Fetch the latest index for each contract and persist in HA Store format."""

    async with aiohttp.ClientSession() as session:
        api = RegieDesEauxAPI(session, USERNAME, PASSWORD)

        print(f"\nAuthentification pour : {USERNAME}")
        try:
            await api.async_authenticate()
        except InvalidAuth:
            pytest.fail("Identifiants invalides")
        except CannotConnect:
            pytest.fail("Impossible de joindre l'API")
        print("Authentification réussie !")

        meters = await api.async_get_meters()
        print(f"{len(meters)} contrat(s) trouvé(s)")

        store_data: dict = {}
        for meter in meters:
            contract_id = meter["id"]
            name = meter["name"]
            print(f"\n  Contrat {contract_id} — {name}")

            result = await api.async_get_meter_index(contract_id)
            index_m3 = result.get("index")
            timestamp = result.get("timestamp")

            if index_m3 is None:
                print(f"    Aucun relevé disponible")
            else:
                print(f"    Index : {index_m3} m³  (relevé le {timestamp})")

            assert result is not None, "async_get_meter_index doit retourner un dict"

            store_data[contract_id] = {
                "index": index_m3,
                "timestamp": timestamp,
            }

        _save_ha_store(store_data)
        print(f"\nDonnées sauvegardées : {json.dumps(store_data, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(test_meter_index())
