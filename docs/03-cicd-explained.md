# 3. CI/CD explained

**CI (Continuous Integration)** = automatically check every change. **CD (Continuous Delivery/Deployment)** = automatically ship a checked change.

```
 developer pushes / opens PR
            │
            ▼
 ┌────────────── CI  (.github/workflows/ci.yml) ──────────────┐
 │  test job (Python 3.10 and 3.11, in parallel)               │
 │    install deps → ruff lint → pytest                        │
 │  docker job (only if tests passed)                          │
 │    build the Docker image to prove it builds                │
 └─────────────────────────────────────────────────────────────┘
            │ green, and branch is main
            ▼
 ┌────────────── CD  (.github/workflows/cd.yml) ──────────────┐
 │  build-and-push: build image → push to ghcr.io (tag = sha)  │
 │        ├── DEPLOY_TARGET=azure → deploy-azure               │
 │        └── DEPLOY_TARGET=aws   → deploy-aws                 │
 └─────────────────────────────────────────────────────────────┘
```

## CI file, line by line (concepts)

| Part | Meaning |
|---|---|
| `on: push / pull_request` | When to run. PRs are checked *before* merging. |
| `concurrency … cancel-in-progress` | A newer push cancels the older still-running check. |
| `permissions: contents: read` | Least privilege: CI can only read the code. |
| `matrix: python: [3.10, 3.11]` | Runs the tests on both versions. |
| `cache: pip` | Re-uses downloaded packages, faster runs. |
| `pip install -e .` | Installs the `recruitme` package like a user would. |
| `ruff check .` | Static analysis: unused imports, likely bugs, import order. |
| `pytest` | Runs everything in `tests/`. |
| `needs: test` | Docker job starts only if tests pass. |

## CD file, line by line (concepts)

| Part | Meaning |
|---|---|
| `workflow_run` on CI `completed` | CD starts only after CI finished on `main`; the job checks `conclusion == 'success'`. |
| `workflow_dispatch` | Adds a **Run workflow** button so you can redeploy manually. |
| `packages: write` | Lets the built-in `GITHUB_TOKEN` push to ghcr.io – no extra password. |
| Image tag = first 7 chars of the commit SHA | Every deployment is traceable to an exact commit, and rollback = redeploy an older tag. |
| `id-token: write` + `azure/login` | **OIDC**: GitHub proves its identity to Azure with a short-lived token. No Azure password is stored anywhere. |
| `vars.DEPLOY_TARGET == 'azure'` | One switch chooses the cloud. |
| `environment: azure / aws` | Optional gate: in repo **Settings → Environments** you can require a manual approval before production deploys. |

## Rollback

Actions → **CD** → *Run workflow*, or directly:
- Azure: `az containerapp update -n <app> -g <rg> --image ghcr.io/<you>/recruitme:<older-sha>`
- AWS: SSH in, `docker rm -f recruitme`, `docker run …` with the older tag.

## Reading a failed run

Click the red ✗ → the failing job → the failing step → read the last lines. Reproduce locally with the same command (`make lint`, `make test`, `docker build .`).
