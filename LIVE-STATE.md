# What is deployed, and where it lives

Last aligned with the live box: 2026-11-01. The live box wins any disagreement with this repo.

## Where the running configuration is

| Thing | Location on the box | In this repo |
|---|---|---|
| Home Assistant YAML config | Home Assistant's config folder (`/homeassistant`) | repo root (`configuration.yaml`, `automations.yaml`, `scripts.yaml`, `scenes.yaml`, `groups.yaml`, `logbook.yaml`, `zone.yaml`, `ui-lovelace.yaml`) |
| **AppDaemon, the copy that runs** | The add-on's own folder, `/app_configs/a0d7b954_appdaemon/` | `appdaemon/` (see below) |
| AppDaemon, a stale copy | `/homeassistant/appdaemon/` | Nothing reads it |

### The two AppDaemon folders

AppDaemon reads its config and apps from its own add-on folder. Issue #131 records that it moved there in 2025. The live `appdaemon.yaml` has a top-level `app_dir: /homeassistant/appdaemon/apps` line, but AppDaemon only honours that key under the `appdaemon:` section, so it is ignored and the add-on folder is what runs. The `.py` files in the two folders are identical, and match this repo. Differences:

- Running `apps.yaml` has `disable: true` on `systemHealthCheck` (it crashes AppDaemon 4.5.13 start-up). `eviesSleepAlarm` is still enabled.
- Running folder also has `hello.py`, the add-on's sample app. It is not in the repo.
- Running `appdaemon.yaml` holds the Home Assistant token as a literal. **The repo copy replaces it with `!secret appdaemon_ha_token`.** Never commit the real file.
- The admin interface and API are bound to `0.0.0.0:5050` with no password.

## What is not in git

- `secrets.yaml`, `known_devices.yaml`, `google_calendars.yaml`, `.storage/`, the database and backups.
- Anything stored in Home Assistant's hidden storage: integrations, devices and entities, helpers created in the UI, zones, persons, and Companion app registrations. Full backups cover these.
- Third-party code in `custom_components/`. Live contents (some are leftovers): `alexa_media`, `clean_up_snapshots_service`, `hacs`, `motioneye`, `sonoff`.

## Deployment

There is none at present. The Git Pull add-on is stopped, and was set to `git_command: reset` from the branch `2025-05-cleanup`. Do not restart it without repointing it: a reset overwrites the live configuration.

## Known issues in what is deployed

- `ui-lovelace.yaml`: the Living Room TV row uses `sony_xr_65a80j`, which is not a valid entity ID (it should be `media_player.sony_xr_65a80j`).
- `configuration.yaml` still contains obsolete blocks (`nmap_tracker`, `history: exclude`, the snapshot pruner, `ios:`).
- Several automations, scenes and scripts reference entities that no longer exist.
- `appdaemon/apps/activateNetflix.py` and the volume-sync app are dead.

## How this was aligned

Live files were copied to a workstation (config and code only, no secrets) and compared with `master` and with the branch the box was deployed from, `2025-05-cleanup`. Apart from the differences above, the live files matched that branch.
