# 5. Deploy to AWS (free tier) with GitHub Actions

**Service used: one EC2 virtual machine running Docker.** It is the simplest option that stays inside AWS's free offering.

**Free-tier facts (verify on aws.amazon.com/free, rules changed in July 2025):**
- Accounts created **on/after 15 July 2025** choose a *Free plan*: $100 credit on sign-up (up to $200 by completing activities). The plan ends after **6 months or when credits run out**, whichever is first, and no charges occur unless you upgrade. Eligible EC2 types include `t3.micro`, `t3.small`, `t4g.micro`, `t4g.small`.
- Older accounts (created before that date) keep 750 hours/month of `t2.micro`/`t3.micro` for their first 12 months.
- Use **`t3.small` (2 GB RAM)** if your account allows it; `t3.micro` (1 GB) is tight for Streamlit + FAISS, and the bootstrap script adds swap.

> ⚠️ **The LLM caveat** from guide 4 applies: the free VM cannot run `llama3`. Matching works; interview questions/CV generation need `OLLAMA_BASE_URL` pointing to an Ollama server.

## Step 1 – Account and safety net
Create an account at aws.amazon.com/free and choose the **Free plan**. Then set a **budget alert**: Billing → Budgets → Create budget ($1–5).

## Step 2 – Launch the instance
EC2 → **Launch instance**:
- Name `recruitme`; AMI **Ubuntu Server 24.04 LTS**; type `t3.small` (or `t3.micro`).
- **Key pair**: create new (RSA, `.pem`) and download it. Keep it private.
- **Network / security group** – allow inbound: SSH (22) **from My IP only**, HTTP (80) from anywhere.
- Storage 20–30 GB gp3.
- Launch. Note the **public IPv4 address**. (Tip: allocate an Elastic IP so the address does not change on restart; release it if unused.)

## Step 3 – Install Docker on the server
```bash
chmod 400 recruitme.pem
scp -i recruitme.pem infra/aws/ec2-bootstrap.sh ubuntu@<EC2-IP>:~
ssh -i recruitme.pem ubuntu@<EC2-IP> "bash ec2-bootstrap.sh"
```
Log out and in again so the docker group applies. Test: `docker run --rm hello-world`.

## Step 4 – Add the values to GitHub
Repo → Settings → **Environments → New environment → `aws`**, then Secrets and variables → Actions:

| Type | Name | Value |
|---|---|---|
| Secret | `EC2_HOST` | the public IP |
| Secret | `EC2_USER` | `ubuntu` |
| Secret | `EC2_SSH_KEY` | full contents of `recruitme.pem` (including BEGIN/END lines) |
| Variable | `DEPLOY_TARGET` | `aws` |
| Variable | `OLLAMA_BASE_URL` | e.g. `http://<ollama-host>:11434` (leave empty to run without LLM) |

## Step 5 – Image access
Make the ghcr package public (guide 2, section 2.6). For a private image, on the server run once: `echo <PAT with read:packages> | docker login ghcr.io -u <github-user> --password-stdin`.

## Step 6 – Deploy
Push to `main` or run **CD** manually. The job SSHes in, pulls the new image, replaces the container and prunes old images. Open `http://<EC2-IP>`.

Note: port 80 is plain HTTP. For HTTPS put Caddy or an Application Load Balancer + ACM certificate in front (the load balancer is not free).

## Step 7 – Logs and troubleshooting
```bash
ssh -i recruitme.pem ubuntu@<EC2-IP>
docker ps
docker logs -f recruitme
```
| Symptom | Likely cause |
|---|---|
| Action fails at SSH | Security group SSH rule does not allow GitHub's IPs. GitHub-hosted runners have changing IPs, so for a demo allow 22 from `0.0.0.0/0` **with key-only login**, or use AWS SSM instead of SSH. |
| `permission denied` on docker | Log out/in after bootstrap. |
| Container exits / restarts | Out of memory → use `t3.small` and check swap: `free -h`. |
| `pull access denied` | Package private and server not logged in to ghcr. |

## Step 8 – Clean up
Terminate the instance (EC2 → Instance state → Terminate), release any Elastic IP, delete unused EBS volumes.
