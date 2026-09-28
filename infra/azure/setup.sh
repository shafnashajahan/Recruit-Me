#!/usr/bin/env bash
# One-time Azure setup for RecruitMe (Container Apps + GitHub OIDC login).
# Run in Azure Cloud Shell (bash) or a terminal where `az login` is done.
# Usage: GITHUB_REPO=youruser/recruitme ./setup.sh
set -euo pipefail

: "${GITHUB_REPO:?Set GITHUB_REPO=owner/repo}"
RG="${RG:-recruitme-rg}"
LOCATION="${LOCATION:-centralindia}"
ENV_NAME="${ENV_NAME:-recruitme-env}"
APP_NAME="${APP_NAME:-recruitme-app}"
IMAGE="${IMAGE:-mcr.microsoft.com/k8se/quickstart:latest}"   # placeholder; CD replaces it

az extension add --name containerapp --upgrade --only-show-errors
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait

az group create --name "$RG" --location "$LOCATION"
az containerapp env create --name "$ENV_NAME" --resource-group "$RG" --location "$LOCATION"

# scale-to-zero keeps you inside the free monthly grant when nobody is using the app
az containerapp create \
  --name "$APP_NAME" --resource-group "$RG" --environment "$ENV_NAME" \
  --image "$IMAGE" --target-port 8501 --ingress external \
  --cpu 0.5 --memory 1.0Gi --min-replicas 0 --max-replicas 1

# --- GitHub Actions login via OIDC (no passwords stored in GitHub) ---
SUB_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
APP_ID=$(az ad app create --display-name "recruitme-github" --query appId -o tsv)
az ad sp create --id "$APP_ID" >/dev/null
az role assignment create --assignee "$APP_ID" --role Contributor \
  --scope "/subscriptions/$SUB_ID/resourceGroups/$RG" >/dev/null
az ad app federated-credential create --id "$APP_ID" --parameters "{
  \"name\": \"github-azure-env\",
  \"issuer\": \"https://token.actions.githubusercontent.com\",
  \"subject\": \"repo:${GITHUB_REPO}:environment:azure\",
  \"audiences\": [\"api://AzureADTokenExchange\"]
}" >/dev/null

FQDN=$(az containerapp show -n "$APP_NAME" -g "$RG" --query properties.configuration.ingress.fqdn -o tsv)
cat <<OUT

==== Add these in GitHub: Settings > Secrets and variables > Actions ====
Secrets:   AZURE_CLIENT_ID=$APP_ID
           AZURE_TENANT_ID=$TENANT_ID
           AZURE_SUBSCRIPTION_ID=$SUB_ID
Variables: AZURE_RESOURCE_GROUP=$RG
           AZURE_CONTAINERAPP_NAME=$APP_NAME
           DEPLOY_TARGET=azure
App URL:   https://$FQDN
OUT
