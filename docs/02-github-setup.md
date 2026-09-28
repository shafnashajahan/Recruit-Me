# 2. GitHub setup – from your folder to a repository

## 2.1 One-time: install and identify yourself

```bash
git --version                                   # install Git if this fails
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
```

## 2.2 Create the repository

1. On github.com click **New repository**. Name it `recruitme`. Choose **Private** while learning (Public is fine once you have checked that no personal data is in it). **Do not** tick "Add a README" (you already have one).
2. In your project folder:

```bash
git init -b main
git add .
git status          # CHECK: no .pdf files, no .env, no data/ contents
git commit -m "chore: initial professional project structure"
git remote add origin https://github.com/<your-username>/recruitme.git
git push -u origin main
```

> **Privacy check:** the original zip contained real CV/resume PDFs (`storage/resumes`, CVs in the root). The new `.gitignore` blocks `*.pdf` and `data/`. Never upload other people's resumes to GitHub – even to a private repo. If one was ever committed, deleting it later does **not** remove it from history.

## 2.3 First pipeline run

Open the repo → **Actions** tab. The **CI** workflow should be running. Green tick = tests + Docker build passed.

## 2.4 Protect the `main` branch (recommended)

Repo → **Settings → Branches → Add branch protection rule** for `main`:
- Require a pull request before merging
- Require status checks to pass → select **Lint & test (Python 3.10)**, **Lint & test (Python 3.11)**, **Docker image builds**

Now broken code cannot reach `main`, and so cannot be deployed.

## 2.5 Secrets and variables (used by CD)

Repo → **Settings → Secrets and variables → Actions**.

- **Secrets** are hidden values (keys, IDs). **Variables** are plain settings.
- Which ones you need depends on the target – see guide 4 (Azure) or 5 (AWS).
- Also create the variable **`DEPLOY_TARGET`** = `azure`, `aws` or `none`. With `none` (or unset) the pipeline only builds the image and does not deploy.

## 2.6 GitHub Container Registry (image storage – free)

CD pushes the Docker image to `ghcr.io/<you>/recruitme`. The first time, the package is private. To let Azure/EC2 pull it without credentials: GitHub profile → **Packages → recruitme → Package settings → Change visibility → Public**. (The image contains only code, no personal data.) If you prefer to keep it private, both cloud guides explain how to add pull credentials.
