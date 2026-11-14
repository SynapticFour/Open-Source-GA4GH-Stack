# GA4GH Community Stack

Dieses Kit startet Upstream-Dienste der GA4GH nebeneinander, damit ein Labor diese Anordnung mit einem integrierten Laborkit vergleichen kann.

Für eine Core Facility, ein Lehrlabor oder ein Pilotteam, das jeden Dienst als Upstream-Projekt behalten will und die Unterschiede zwischen den Diensten selbst trägt.

**Status: Es ist kein öffentlicher Status erfasst.** Die Claims-Registry hat keine Reifestufe für dieses Kit. Registereintrag zur Lizenzgrenze: STACK-OSS-001. Die Paketversion in `cli/src/community_stack/__init__.py` ist 0.1.0. Diese Zahl ist kein Status.

Die Integrationsschicht in diesem Repository steht unter MIT. Die Upstream-Images sind nicht eine OSI-Menge. Der Beacon-Pfad enthält MongoDB unter der SSPL. Das ist keine von der OSI anerkannte Open-Source-Lizenz.

Dieses Kit ersetzt das [Ferrum Lab Kit](https://github.com/SynapticFour/Ferrum-Lab-Kit) nicht. Der Vergleich steht in [COMPARISON.md](COMPARISON.md).

Die englische Seite ist [README.md](README.md). Sie ist die Ausgangssprache. Diese Datei ist die Übersetzung.

## Was es tut

- `lab-stack` erzeugt Compose, Helm oder systemd aus einer `stack.yml`.
- `lab-stack demo start` startet Beacon und MongoDB. Die dokumentierte Adresse ist `http://localhost:5050/ga4gh/beacon/v2`.
- HelixTest, wenn ein Lauf gestartet wird, ist ein technisches Signal für Beacon und für WES. Es ist keine GA4GH-Zertifizierung.

## Grenzen

- Die Integrationsschicht steht unter MIT. Nicht jedes Upstream-Image steht unter MIT oder Apache-2.0. MongoDB auf dem Beacon-Pfad ist `mongo:5.0.32` unter der SSPL (STACK-OSS-001).
- Am Rand gibt es keine Prüfung von GA4GH Passports oder Visas. [docs/LIMITATIONS.md](docs/LIMITATIONS.md).
- Caddy bleibt auf dem gleitenden Tag `caddy:2-alpine`.
- RO-Crate und eine signierte Prüfspur bleiben bei [HELIOS](https://github.com/SynapticFour/HELIOS).

## Schnellstart

Voraussetzungen: Python 3.11 oder neuer, und Docker für den Beacon-Pfad.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e "./cli[dev]"
pytest cli/tests/
lab-stack demo start
```

Erwartet: die pytest-Zusammenfassung, dann Beacon unter `http://localhost:5050/ga4gh/beacon/v2`. Die Schritte stehen in [docs/GETTING-STARTED.md](docs/GETTING-STARTED.md).

## Dokumentation

- [Einstieg](docs/GETTING-STARTED.md)
- [Für Prüfende](docs/FOR-EVALUATORS.md)
- [Aufbau](docs/ARCHITECTURE.md)
- [Index](docs/README.md)

## Lizenz

Die Integrationsschicht steht unter der MIT-Lizenz. Die Datei ist [LICENSE](LICENSE). Upstream-Images behalten die Lizenzen in der Tabelle der englischen README, einschließlich MongoDB unter der SSPL.

## Website

- Open Source: [https://synapticfour.com/en/opensource/](https://synapticfour.com/en/opensource/)
- Technisches Profil: [https://synapticfour.com/en/technical/code/](https://synapticfour.com/en/technical/code/)

Dieselben Seiten gibt es auf Deutsch (`/de/opensource/`, `/de/technik/code/`) und auf Französisch (`/fr/opensource/`, `/fr/technique/code/`).

Kontakt: [contact@synapticfour.com](mailto:contact@synapticfour.com)
