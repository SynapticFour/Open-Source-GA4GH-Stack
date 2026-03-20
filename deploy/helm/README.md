# Helm umbrella chart

Subcharts live in `charts/`. Before `helm install` or `helm template`, vendor dependencies:

```bash
cd deploy/helm
helm dependency build .
helm template test . -f values.yaml
```

Enable services in `values.yaml` (all disabled by default). Optionally merge `values.generated.yaml` from `lab-stack generate helm`.
