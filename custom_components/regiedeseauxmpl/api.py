"""API Client for Régie des Eaux Montpellier.

Uses curl_cffi with Chrome TLS impersonation to bypass F5 BIG-IP TLS
fingerprinting, which causes aiohttp requests to be routed to random
backends and lose the application session.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from curl_cffi.requests import AsyncSession

from .const import (
    LOGGER, LOGIN_URL, GENERATE_TOKEN_URL, API_ROOT_URL, BASE_URL,
    WS_APPLICATION_LOGIN, WS_APPLICATION_PWD,
)
from .exceptions import CannotConnect, InvalidAuth, APIError

_IMPERSONATE = "chrome110"


def _generate_conversation_id() -> str:
    """Generate a ConversationId matching the Angular app format.

    Format extracted from app.js:
      "JS-WEB-" + navigator.appName + "-" + uuidv4()
    navigator.appName is "Netscape" in all modern browsers.
    """
    return f"JS-WEB-Netscape-{uuid.uuid4()}"


class RegieDesEauxAPI:
    """API Client to interact with the water provider."""

    def __init__(self, session, username: str, password: str) -> None:
        """Initialize the API client.

        ``session`` is kept for interface compatibility with Home Assistant's
        config_flow/coordinator but is not used internally — we create our own
        curl_cffi AsyncSession to maintain a stable F5 BIG-IP routing cookie.
        """
        self._username = username
        self._password = password
        self._is_authenticated = False
        self._user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        )
        self._app_token: str | None = None
        self._auth_token: str | None = None
        # Persistent curl_cffi session — keeps BIGipServer cookie stable
        self._curl_session: AsyncSession | None = None

    def _get_session(self) -> AsyncSession:
        """Return (or create) the shared curl_cffi session."""
        if self._curl_session is None:
            self._curl_session = AsyncSession(impersonate=_IMPERSONATE)
        return self._curl_session

    def _base_headers(self, token: str, extra: dict | None = None) -> dict:
        """Build standard API request headers."""
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "ConversationId": _generate_conversation_id(),
            "Token": token,
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "User-Agent": self._user_agent,
        }
        if extra:
            headers.update(extra)
        return headers

    async def _async_init_session(self) -> None:
        """Visit the home page to initialise the BIGipServer routing cookie."""
        sess = self._get_session()
        try:
            async with asyncio.timeout(10):
                await sess.get(BASE_URL, headers={"User-Agent": self._user_agent})
                LOGGER.debug("Session cookies initialised")
        except Exception as err:
            LOGGER.warning("Could not initialise session cookies: %s", err)

    async def _async_get_app_token(self) -> str:
        """Obtain a short-lived application token via Acces/generateToken."""
        sess = self._get_session()
        conv_id = _generate_conversation_id()
        payload = {
            "ConversationId": conv_id,
            "ClientId": WS_APPLICATION_LOGIN,
            "AccessKey": WS_APPLICATION_PWD,
        }
        headers = self._base_headers(WS_APPLICATION_PWD, {
            "ConversationId": conv_id,
            "Content-Type": "application/json",
        })

        try:
            async with asyncio.timeout(10):
                resp = await sess.post(GENERATE_TOKEN_URL, json=payload, headers=headers)
                if resp.status_code != 200:
                    LOGGER.error("generateToken failed %s: %s", resp.status_code, resp.text[:200])
                    raise CannotConnect
                data = resp.json()
                token = data.get("token")
                if not token:
                    raise CannotConnect
                LOGGER.debug("App token obtained: %s…", token[:20])
                return token
        except (ConnectionError, TimeoutError, asyncio.TimeoutError) as err:
            raise CannotConnect from err

    async def async_authenticate(self) -> bool:
        """Authenticate with the API (full 3-step flow).

        Step 1 — GET / to set BIGipServer persistence cookie.
        Step 2 — POST Acces/generateToken to get a dynamic app token.
        Step 3 — POST Utilisateur/authentification with identifiant/motDePasse.
               → returns tokenAuthentique (TKN-...) stored as _auth_token.
        """
        LOGGER.debug("Authenticating for user %s", self._username)
        sess = self._get_session()

        await self._async_init_session()
        self._app_token = await self._async_get_app_token()

        payload = {
            "identifiant": self._username,
            "motDePasse": self._password,
        }
        headers = self._base_headers(self._app_token, {
            "Content-Type": "application/json;charset=UTF-8",
        })

        try:
            async with asyncio.timeout(15):
                resp = await sess.post(LOGIN_URL, json=payload, headers=headers)

                if resp.status_code == 401:
                    raise InvalidAuth
                if resp.status_code == 403:
                    raise InvalidAuth
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except Exception:
                        data = {}
                    # tokenAuthentique (TKN-...) must be used for all post-auth API calls
                    self._auth_token = data.get("tokenAuthentique")
                    if not self._auth_token:
                        LOGGER.warning("Authentication succeeded but no tokenAuthentique found")
                    self._is_authenticated = True
                    LOGGER.info("Successfully authenticated for user %s", self._username)
                    return True

                LOGGER.error(
                    "Authentication failed for %s: status %s body %s",
                    self._username, resp.status_code, resp.text[:200],
                )
                raise InvalidAuth

        except (ConnectionError, TimeoutError, asyncio.TimeoutError) as err:
            LOGGER.error("Connection error during authentication: %s", err)
            raise CannotConnect from err

    async def _async_authenticated_get(self, url: str, timeout: int = 10):
        """Perform an authenticated GET, re-authenticating once on 401/403.

        The server-side ``tokenAuthentique`` expires well within the polling
        interval. Without this retry the coordinator stays broken permanently
        after the first expiry: ``_is_authenticated`` would never reset and the
        dead token would be reused on every refresh.
        """
        sess = self._get_session()
        resp = None
        for attempt in (1, 2):
            if not self._is_authenticated:
                await self.async_authenticate()
            token = self._auth_token or self._app_token or ""
            async with asyncio.timeout(timeout):
                resp = await sess.get(url, headers=self._base_headers(token))
            if resp.status_code in (401, 403) and attempt == 1:
                LOGGER.info(
                    "API token rejected (HTTP %s) - re-authenticating",
                    resp.status_code,
                )
                self._is_authenticated = False
                self._app_token = None
                self._auth_token = None
                continue
            break
        return resp

    async def async_get_meters(self) -> list[dict]:
        """Get the list of meters."""
        LOGGER.debug("Fetching meters")

        # The endpoint requires query parameters; bare URL returns 404
        url = (
            f"{API_ROOT_URL}/Abonnement/contrats"
            "?userWebId=&recherche=&tri=NumeroContrat&triDecroissant=false&indexPage=0&nbElements=25"
        )

        try:
            resp = await self._async_authenticated_get(url, timeout=10)
        except (ConnectionError, TimeoutError, asyncio.TimeoutError) as err:
            raise CannotConnect from err

        if resp.status_code in (401, 403):
            # Re-authentication was already retried inside the helper, so the
            # credentials themselves are being rejected.
            self._is_authenticated = False
            raise InvalidAuth
        if resp.status_code != 200:
            raise APIError(f"Unexpected status code: {resp.status_code}")

        try:
            data = resp.json()
        except Exception:
            text = resp.text
            LOGGER.warning("Non-JSON from /Abonnement/contrats: %s", text[:200])
            if "identifiant" in text or "login" in text:
                self._is_authenticated = False
                raise InvalidAuth
            return [{
                "id": "meter_default",
                "name": "Compteur Principal (Fallback)",
                "serial_number": "Unknown",
                "unit": "m³",
            }]

        # Response: {resultats: [...], nbTotalResultats: N}
        meters = []
        items = (
            data.get("resultats", [])
            if isinstance(data, dict)
            else data
        )
        for item in items:
            numero_contrat = item.get("numeroContrat")
            numero_physique = item.get("numeroPhysiqueAppareil")
            libelle = item.get("libelle", "")
            adresse = item.get("adresseLivraisonConstruite", "")
            if numero_contrat:
                meters.append({
                    "id": numero_contrat,
                    "name": f"{libelle.capitalize()} – {adresse}" if libelle else f"Contrat {numero_contrat}",
                    "serial_number": numero_physique or numero_contrat,
                    "unit": "m³",
                    "contract_id": numero_contrat,
                })

        if not meters:
            LOGGER.warning("No meters found in JSON response: %s", data)
            return [{
                "id": "meter_default",
                "name": "Compteur Principal",
                "serial_number": "Unknown",
                "unit": "m³",
            }]
        return meters

    async def async_get_meter_index(self, meter_id: str) -> dict:
        """Get the latest meter index (m³) via listeConsommationsInstanceAlerteChart.

        Uses a 365-day look-back window with daily granularity (granularite=1).
        Returns the most recent 'Réel' entry as {"index": float, "timestamp": str}.
        ``valeurIndex`` is in litres — divide by 1000 for m³.
        """
        LOGGER.debug("Fetching index for meter %s", meter_id)

        now = datetime.now(timezone.utc)
        ts_end = int(now.timestamp())
        ts_start = int((now - timedelta(days=365)).timestamp())

        url = (
            f"{API_ROOT_URL}/Consommation/listeConsommationsInstanceAlerteChart"
            f"/{meter_id}/{ts_start}/{ts_end}/1/true"
        )

        try:
            resp = await self._async_authenticated_get(url, timeout=15)
        except (ConnectionError, TimeoutError, asyncio.TimeoutError) as err:
            raise CannotConnect from err

        if resp.status_code != 200 or not resp.content:
            LOGGER.warning(
                "listeConsommationsInstanceAlerteChart/%s returned %s",
                meter_id, resp.status_code,
            )
            return {"index": None, "timestamp": None}

        try:
            data = resp.json()
        except Exception:
            LOGGER.warning("Non-JSON response for meter index %s", meter_id)
            return {"index": None, "timestamp": None}

        consommations = data.get("consommations", [])
        # Keep only real readings (typeAgregat == "Réel") and pick the latest
        reels = [
            c for c in consommations
            if c.get("typeAgregat") == "Réel" and c.get("valeurIndex") is not None
        ]
        if not reels:
            # Fall back to any entry with a valeurIndex
            reels = [c for c in consommations if c.get("valeurIndex") is not None]

        if not reels:
            LOGGER.info("No index entries found for meter %s", meter_id)
            return {"index": None, "timestamp": None}

        latest = max(reels, key=lambda c: c.get("dateReleve", ""))
        index_m3 = round(float(latest["valeurIndex"]) / 1000.0, 3)
        return {
            "index": index_m3,
            "timestamp": latest.get("dateReleve"),
        }
