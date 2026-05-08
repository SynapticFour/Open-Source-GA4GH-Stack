# GA4GH Community Stack

**Ein kuratiertes Deployment-Kit aus den besten verfügbaren Open-Source-GA4GH-Implementierungen** — für Kerninstitute, ELIXIR-/GHGA-/GDI-nahe Piloten, HPC-Gateways und Lehrlabs, die Standard-APIs ohne Vendor-Kit evaluieren wollen.

Dieses Projekt ist **kein** „billiger Ersatz“ für integrierte Komplett-Lösungen wie das **Ferrum Lab Kit**. Es ist der **OSS-Referenzstack** mit derselben Deployment-Zielsetzung (Docker Compose, Helm, SLURM/HPC). Den dokumentierten Vergleich siehe [COMPARISON.md](COMPARISON.md); Grenzen und Lücken [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

**Lizenz:** MIT (dieses Repo); Upstream-Komponenten siehe Komponentenliste im [README.md](README.md) (englisch).

---

## Warum für GHGA, NFDI und de.NBI relevant?

- **Interoperabilität:** GA4GH-konforme Endpunkte (Beacon v2, WES, TES, DRS) für nationale Forschungsdateninfrastrukturen und EU-Ökosysteme (z. B. GDI).
- **Transparenz:** Nachvollziehbare Upstream-Projekte (EGA, OHSU, GA4GH Starter Kits, Sapporo) statt „Black Box“.
- **Kosten für den Betrieb:** OSS ohne Lizenz-Gate — dafür höherer **Integrationsaufwand** (mehrere Config-Formate, kein einheitliches Passport-Handling am Edge).

---

## Schnellstart (Beacon)

```bash
pip install ga4gh-community-stack    # oder: ./install.sh (wenn auf PyPI)
pip install -e "./cli[dev]"          # aus dem Repo
mkdir ~/ga4gh-lab && cd ~/ga4gh-lab   # bei pip-Install: schreibbares Projektverzeichnis
lab-stack init
lab-stack demo start
# http://localhost:5050/ga4gh/beacon/v2
```

Das Paket enthält Templates & Compose-Fragmente im Wheel (`community_stack/_bundled/`). Details: [docs/RELEASING.md](docs/RELEASING.md).

---

## Dokumentation

| Dokument | Inhalt |
|----------|--------|
| [docs/COMPONENTS.md](docs/COMPONENTS.md) | Upstream-Details |
| [docs/LIMITATIONS.md](docs/LIMITATIONS.md) | Ehrliche Grenzen |
| [docs/ELIXIR-AAI.md](docs/ELIXIR-AAI.md) | LS Login & oauth2-proxy |
| [docs/SLURM-SETUP.md](docs/SLURM-SETUP.md) | Funnel auf Login-Node |
| [docs/DATA-INGEST.md](docs/DATA-INGEST.md) | Beacon-Ingest |

Englische Haupt-README: [README.md](README.md).
