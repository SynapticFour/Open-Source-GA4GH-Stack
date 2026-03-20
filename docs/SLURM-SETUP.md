# Funnel (TES) on a SLURM login node

Funnel is designed to **submit cluster jobs** (e.g. via `sbatch`) from a node that can reach both the **TES HTTP API clients** and the **scheduler**. On many HPC systems this is the **login node** (policy permitting).

## 1. Install the Funnel binary

Install a **Funnel release** matching your platform on the login node (or use a container with host networking and `sbatch` available — advanced). Verify:

```bash
funnel version
which sbatch
```

## 2. Configure `funnel.conf` for SLURM

Minimal pattern (adjust names and paths):

```yaml
Server:
  HostName: "0.0.0.0"
  HTTPPort: "8000"
  RPCPort: "9090"

Compute: slurm
Slurm:
  Partition: short
  Timelimit: "4:00:00"
```

**Notes:**

- Funnel **workers** typically need shared filesystem visibility to staging directories (`Worker.WorkDir` / storage sections — see [Funnel docs](https://ohsu-comp-bio.github.io/funnel/)).
- Docker-only examples in Compose **do not** replace SLURM configuration on HPC.

## 3. systemd unit

The repository ships `deploy/slurm/funnel.service` as a template. Copy to `/etc/systemd/system/`, adapt `User=` and paths, then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now funnel
```

## 4. SLURM job template expectations

Funnel generates SLURM submission scripts from TES task metadata. You may need site-specific **partition**, **accounting (`-A`)**, **modules**, or **Singularity/Apptainer binds**. Consolidate those in:

- Funnel config (Slurm section / templates), and
- HPC documentation your centre already maintains.

## 5. Pointing Sapporo (WES) at local Funnel (TES)

When workflows should offload tasks to your cluster:

- Expose Funnel’s HTTP endpoint on a DNS name or internal ingress (*not* necessarily public internet).
- Configure the WES/TES integration your lab uses (Sapporo extensions, workflow wrappers, or downstream orchestration) to target `http://<funnel-host>:8000` (or TLS-terminated equivalent).

Exact wiring depends on **your** network boundary model; the Community Stack provides **Compose examples** and **systemd units**, not site security policy.

## 6. Related systemd: Sapporo

For bare-metal WES on a gateway node, see `deploy/slurm/sapporo.service` as a **starting point** — you must align the `ExecStart` line with how Sapporo is installed on your system (`uvicorn` vs packaged binary).
