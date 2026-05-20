import sys
from unittest.mock import MagicMock

# Create mock objects that act as packages
homeassistant = MagicMock()
homeassistant.exceptions = MagicMock()
homeassistant.config_entries = MagicMock()
homeassistant.core = MagicMock()
homeassistant.helpers = MagicMock()
homeassistant.helpers.aiohttp_client = MagicMock()
homeassistant.helpers.update_coordinator = MagicMock()
homeassistant.components = MagicMock()
homeassistant.components.sensor = MagicMock()
homeassistant.const = MagicMock()

# Set up the sys.modules to satisfy imports
sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.exceptions"] = homeassistant.exceptions
sys.modules["homeassistant.config_entries"] = homeassistant.config_entries
sys.modules["homeassistant.core"] = homeassistant.core
sys.modules["homeassistant.helpers"] = homeassistant.helpers
sys.modules["homeassistant.helpers.aiohttp_client"] = homeassistant.helpers.aiohttp_client
sys.modules["homeassistant.helpers.update_coordinator"] = homeassistant.helpers.update_coordinator
sys.modules["homeassistant.components"] = homeassistant.components
sys.modules["homeassistant.components.sensor"] = homeassistant.components.sensor
sys.modules["homeassistant.const"] = homeassistant.const

# Define base error class if needed by the integration
class HomeAssistantError(Exception):
    """Base error."""
homeassistant.exceptions.HomeAssistantError = HomeAssistantError

import os
import asyncio
import aiohttp
import pytest
from custom_components.regiedeseauxmpl.api import RegieDesEauxAPI
from custom_components.regiedeseauxmpl.exceptions import CannotConnect, InvalidAuth

# On peut utiliser des variables d'environnement pour passer les identifiants réels lors des tests
# EXPORT REGIE_USERNAME="votre_email"
# EXPORT REGIE_PASSWORD="votre_password"
USERNAME = os.getenv("REGIE_USERNAME", "test_user")
PASSWORD = os.getenv("REGIE_PASSWORD", "test_pass")

@pytest.mark.skipif(
    not (os.getenv("REGIE_USERNAME") and os.getenv("REGIE_PASSWORD")),
    reason="REGIE_USERNAME and REGIE_PASSWORD environment variables required for real API test"
)
@pytest.mark.asyncio
async def test_authentication():
    """Test l'authentification sur l'API Régie des Eaux."""
    async with aiohttp.ClientSession() as session:
        api = RegieDesEauxAPI(session, USERNAME, PASSWORD)
        
        print(f"\nTentative d'authentification pour : {USERNAME}")
        try:
            result = await api.async_authenticate()
            assert result is True
            print("Authentification réussie !")
            
            # Si réussi, on tente de lister les compteurs pour valider la session
            meters = await api.async_get_meters()
            print(f"Compteurs trouvés : {len(meters)}")
            for m in meters:
                print(f"- {m['name']} (ID: {m['id']})")
                
                # Test de récupération d'index pour le premier compteur
                index = await api.async_get_meter_index(m['id'])
                print(f"  Index actuel : {index['value']} m³ (le {index['timestamp']})")
                
        except InvalidAuth:
            pytest.fail("Échec d'authentification : Identifiants invalides")
        except CannotConnect:
            pytest.fail("Erreur de connexion : Impossible de joindre l'API")
        except Exception as e:
            pytest.fail(f"Erreur inattendue : {e}")

if __name__ == "__main__":
    if USERNAME == "test_user":
        print("ATTENTION : Vous utilisez les identifiants de test par défaut.")
        print("Veuillez définir les variables d'environnement REGIE_USERNAME et REGIE_PASSWORD.")
    asyncio.run(test_authentication())
