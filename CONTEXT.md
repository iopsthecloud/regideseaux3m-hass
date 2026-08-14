# Context : regiedeseauxmpl

A **Home Assistant custom integration** (HACS) that pulls **water-meter consumption** from
the **Régie des Eaux de Montpellier 3M** customer portal and exposes it as a sensor. The
utility publishes no public API, so the integration talks to the portal's private `webapi`
reverse-engineered from its Angular app. A **standalone wrapper** at the project root runs
the same client without HA installed, for development and API probing.

- **HA domain**: `regiedeseauxmpl` (`custom_components/regiedeseauxmpl/`). Its own git repo,
  published to HACS; deployed to prod "trano" via HACS, **not** the lab SSH script.
- **Decisions / reverse-engineering**: [`API_WORKFLOW.md`](API_WORKFLOW.md) is the canonical
  write-up of how the auth flow and endpoints were discovered; `CHANGELOG.md` is the release
  history. No `docs/adr/` yet.
- Linked memory: `[[regiedeseauxmpl_silent_api]]` (a stuck reading usually means the utility
  hasn't published, not a bug — check that before suspecting code).

## Ubiquitous language

- **Régie des Eaux 3M** — the Montpellier Métropole water utility whose portal is the data
  source. Portal root: `https://ael.regiedeseaux3m.fr`.
- **AEL** — *Agence En Ligne*, the **Somei AEL** software product powering the portal (Angular
  front-end, Java/Spring back-end). Its private JSON API is rooted at `…/webapi/`.
- **Meter index** (`water_index`) — the cumulative meter reading the integration reports. The
  water sensor is `state_class: total_increasing`, `device_class: water`.
- **3-step auth** — the login handshake the API requires, in order: **`GET /`** (obtain the
  session / F5 persistence cookie) → **`POST Acces/generateToken`** (app-level JWT, using the
  baked-in `WS_APPLICATION_LOGIN` / `WS_APPLICATION_PWD` from `app.js`) → **`POST
  Utilisateur/authentification`** (user-level JWT from the account's username/password).
- **ConversationId** — a request header the portal expects, whose format was derived from the
  Angular `app.js`; required for calls to be accepted.
- **F5 BIG-IP / TLS fingerprinting** — the load balancer in front of the portal fingerprints
  the TLS client. A native Python fingerprint drops the session mid-auth (HTTP **412 / "Session
  Inconnue"**), which is *why* the client uses `curl_cffi` (see below), not `aiohttp`.
- **Coordinator** — `RegieDesEauxCoordinator`, a HA `DataUpdateCoordinator` polling on a
  configurable interval (**30 min – 24 h, default 6 h**); `iot_class: cloud_polling`.
- **Standalone wrapper** — `standalone.py` (+ `test_standalone.py`) mocks the `homeassistant.*`
  modules so the component code imports and runs **without HA**, exposing `SimpleRegieAPI` /
  `create_coordinator`. The mechanism for dev, live auth tests, and API probing.

## Key design decisions (see API_WORKFLOW.md for the full story)

- **`curl_cffi` with Chrome TLS impersonation**, not `aiohttp` — defeats the F5 BIG-IP TLS
  fingerprinting that otherwise loses the session during authentication. This is the single
  most load-bearing choice in the codebase; don't "simplify" it back to a stdlib HTTP client.
- **`RestoreSensor`** — the meter reading is restored across HA restarts so history isn't lost
  between the (infrequent) polls.
- **`RegieDesEauxAPI`** encapsulates the whole 3-step handshake; callers ask for meter data,
  not tokens.

## Conventions

- Dev commands run from this dir via the `Makefile` (`make setup / test / test-cov / lint /
  format`, uv-backed); standalone runs need `REGIE_USERNAME` / `REGIE_PASSWORD` (see
  `.env.example`). Live auth probe: `PYTHONPATH=. .venv/bin/python tests/test_api_auth.py`.
- Lab validation follows **Part 1 → Part 3** of `HA_TEST_LAB.md`
  (`COMPONENT_DIR=projets/regiedeseauxmpl/custom_components/regiedeseauxmpl`).
- Before blaming code for a frozen reading, confirm the utility actually published a new value
  — readings update roughly once/day. See `[[regiedeseauxmpl_silent_api]]`.
