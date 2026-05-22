---
name: tools-infra-operational
description: >-
  Validate and analyze operational config for review evidence — Helm, Kustomize,
  Kubernetes, Terraform/OpenTofu, Docker, GitHub Actions, policy tools, SBOM,
  and vulnerability scanners. Use when a target ships deploy units and you need
  evidence about runtime topology, deploy-time coupling, or supply chain. NOT
  for application source graphs (use the language tool skills).
---

# Infrastructure / operational tools

A system's architecture includes how it deploys and runs. These tools turn
manifests into evidence about deploy units, runtime topology, deploy-time
coupling, and supply-chain risk — the **operational** and **security**
dimensions a source-only review would miss.

Evidence dimensions: **operational**, **security/supply-chain**.

## When to use

Use when the system map finds Helm charts, Kustomize bases, raw k8s manifests,
Terraform/OpenTofu, Dockerfiles, or CI workflows. Render and validate before
judging — a chart's values determine the real topology, not the template text.

## Commands

```sh
# Helm: render to final manifests, then lint
helm template ./chart -f values.yaml | kubeconform -strict -
helm lint ./chart

# Kustomize: build the overlay, then validate
kustomize build overlays/prod | kubeconform -strict -

# Kubernetes manifests: schema + best-practice validation
kubeconform -strict -summary manifests/
kube-linter lint manifests/

# Terraform / OpenTofu: structure + static security
terraform validate          # or: tofu validate
tflint --recursive
tfsec .                     # or: trivy config .

# Docker: image config / Dockerfile lint
hadolint Dockerfile
trivy config Dockerfile

# GitHub Actions: workflow lint + pinned-action / permission checks
actionlint
zizmor .github/workflows     # supply-chain audit of workflows

# Policy as code (if the repo uses it)
conftest test manifests/ -p policy/
opa eval ...

# SBOM + dependency vulnerabilities
syft dir:. -o spdx-json
grype dir:.                 # or: trivy fs .
```

## Confidence impact

- Rendered-then-validated manifests are direct operational evidence:
  `tools_used`, supports claims about deploy units, replica/topology coupling,
  and config drift. Judging from un-rendered templates is weaker — note it.
- `trivy`/`grype`/`govulncheck`-class output is security/supply-chain evidence;
  cite the component and severity, summarize counts, never paste the full table.
- An **existing** CI step running kubeconform / conftest / tfsec is an enforced
  operational fitness check — count it toward `architecture_fitness`.

## Failure and missing-tool handling

- Tool missing → record the operational (or security) dimension `tools_missing`
  - install hint; fall back to reading the manifests directly and label the
    topology claims as un-validated hypotheses.
- `helm template` / `terraform validate` failing on missing values or
  uninitialized backend → `tools_failed` (config state), not "valid." Note what
  was missing.
- Scanners need network for advisory DBs; an offline run with a stale DB is a
  coverage limit — record the DB date.

## When to stop

Render + validate once per deploy unit, then run one supply-chain scan. Stop and
record coverage once topology and the vuln summary are established — don't run
trivy _and_ grype _and_ a manual audit for the same answer. Cluster-runtime
questions you can't answer from manifests (actual running state) are a coverage
gap, not something to infer.

## Hard rules

- Render Helm/Kustomize before judging topology; template text is not the
  deployed shape.
- Distinguish an enforced CI validation step (raises fitness) from a recommended
  one.
- Summarize scanner output; cite component + severity, never dump the table.
- Use the CLIs; do not reimplement manifest validation in package code.
