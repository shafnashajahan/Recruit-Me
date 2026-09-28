# 4. Deploy to Azure (free tier) with GitHub Actions

**Service used: Azure Container Apps (Consumption plan).** It runs your Docker image and can scale to zero when nobody uses it.

**Cost (verify on the Azure pricing page, it can change):** each subscription gets a monthly free grant of 180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests. With 0.5 vCPU / 1 GiB that is roughly 100 hours of active running per month, so a demo/portfolio app that scales to zero normally stays free. Set a **budget alert** anyway (Cost Management → Budgets).

> ⚠️ **The LLM caveat.** Free tiers cannot run `llama3` (needs ~5 GB+ RAM). The deployed app will run, and skill matching works, but interview questions and CV generation need an Ollama server. Options: (a) accept "matching only" for the public demo; (b) run Ollama on your own PC and expose it with a tunnel, then set `OLLAMA_BASE_URL`; (c) later replace `llm.py` with a hosted model API. See guide 6.

## Step 1 – Create an Azure account
https://azure.microsoft.com/free → sign up (card needed for verification). New accounts also receive a time-limited credit.

## Step 2 – Run the setup script (one time)
1. Open **Azure Cloud Shell** (the `>_` icon in the portal) → choose **Bash**.
2. Upload or paste `infra/azure/setup.sh`, then:
```bash
chmod +x setup.sh
GITHUB_REPO=<your-username>/recruitme ./setup.sh
```
It creates the resource group, the Container Apps environment and the app (min replicas 0, max 1), creates an Entra ID app registration with a **federated credential** for your repo, and prints the values for the next step. Registration of providers can take a few minutes.

## Step 3 – Add the values to GitHub
Repo → Settings → **Environments → New environment → `azure`** (optionally add yourself as a required reviewer).
Repo → Settings → Secrets and variables → Actions:

| Type | Name | Value (printed by the script) |
|---|---|---|
| Secret | `AZURE_CLIENT_ID` | app id |
| Secret | `AZURE_TENANT_ID` | tenant id |
| Secret | `AZURE_SUBSCRIPTION_ID` | subscription id |
| Variable | `AZURE_RESOURCE_GROUP` | `recruitme-rg` |
| Variable | `AZURE_CONTAINERAPP_NAME` | `recruitme-app` |
| Variable | `DEPLOY_TARGET` | `azure` |
| Variable | `OLLAMA_BASE_URL` | (optional, see below) |

## Step 4 – Make the image pullable
Make the ghcr package public (guide 2, section 2.6). For a private image, add registry credentials once:
```bash
az containerapp registry set -n recruitme-app -g recruitme-rg \
  --server ghcr.io --username <github-user> --password <PAT with read:packages>
```

## Step 5 – Deploy
Push to `main` (or Actions → CD → Run workflow). When the run is green, open the URL printed in Step 2, or:
```bash
az containerapp show -n recruitme-app -g recruitme-rg --query properties.configuration.ingress.fqdn -o tsv
```
The first request after idle takes a while (cold start from zero).

## Step 6 – Pass settings to the app
```bash
az containerapp update -n recruitme-app -g recruitme-rg \
  --set-env-vars OLLAMA_BASE_URL=http://<your-ollama-host>:11434 LLM_MODEL=llama3
```

## Step 7 – Logs and troubleshooting
```bash
az containerapp logs show -n recruitme-app -g recruitme-rg --follow
```
| Symptom | Likely cause |
|---|---|
| `AADSTS700213 / no matching federated identity` | Federated credential subject must be exactly `repo:<owner>/<repo>:environment:azure` (case-sensitive) and the job must use `environment: azure`. |
| `AuthorizationFailed` | The service principal needs **Contributor** on the resource group. |
| Image pull error | Package is private and no registry credentials set. |
| App unreachable | Target port must be 8501 and ingress external. |

## Step 8 – Clean up (stop all cost)
```bash
az group delete --name recruitme-rg --yes
```

**Alternative:** Azure App Service F1 (free) works but is limited to 60 CPU-minutes per day and 1 GB RAM, so Container Apps is the better fit for this app.
