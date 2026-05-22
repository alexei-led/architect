# Fixture: infra-mixed

Operational manifests across several tools, used to exercise the
operational-evidence path (helm, kustomize/k8s, terraform, docker, GitHub
Actions) and the `operational` tool-coverage dimension.

Encoded smells (for `architecture_fitness` / operational coverage):

- App config and infrastructure provisioning are interleaved: the Helm chart
  hardcodes a database endpoint that Terraform also provisions, so deploy units
  and infra units are coupled with no shared source of truth.
- The container runs as root (`Dockerfile`), and the CI workflow deploys
  straight to production with no gate.

Referenced as a lighter-weight fixture: the harness asserts the manifests exist;
no full golden report ships for it.

Git history omitted by design (no nested `.git`).
