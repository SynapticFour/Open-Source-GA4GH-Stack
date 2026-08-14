# Helm umbrella chart

`lab-stack generate helm` copies this tree into the project directory (or uses it in-place in a git checkout) and writes `values.generated.yaml`.

Before `helm install` or `helm template`, vendor dependencies:

```bash
cd deploy/helm
helm dependency build .
helm template test . -f values.yaml -f values.generated.yaml
```

Enable services in `values.yaml` or rely on `values.generated.yaml` from `lab-stack generate helm`. Subchart values are aliased (`wes` → Sapporo, `tes` → Funnel, `oauth2Proxy` → oauth2-proxy).
