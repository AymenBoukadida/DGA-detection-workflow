# DNS DGA Detection and SOC Pipeline

Local lab that scores domains with a machine learning API, raises TheHive alerts and cases, runs VirusTotal through Cortex, enriches with WHOIS and DNS, then sends one AI-written SOC report by email.

Everything runs in Docker Compose. No cloud account is needed except API keys for VirusTotal, API-Ninjas and an LLM provider.

## Stack

| Service | URL |
|---|---|
| n8n | http://localhost:5678 |
| TheHive | http://localhost:9000/thehive |
| Cortex | http://localhost:9001/cortex |
| ML API docs | http://localhost:8000/docs |
| MailHog inbox | http://localhost:8025 |

Published ports bind to `127.0.0.1` only.

## Screenshots

Real screenshots from a local run:

- [n8n execution](docs/n8n-execution.png)
- [TheHive cases](docs/thehive-cases.png)
- [TheHive case detail](docs/thehive-case.png)
- [Cortex jobs](docs/cortex-jobs.png)
- [Cortex VirusTotal report](docs/cortex-report.png)
- [SOC report in MailHog](docs/mailhog-report.png)
- [ML API](docs/ml-api.png)

## Quick start

Requirements: Docker Desktop with about 10 GB of memory available, and API keys for VirusTotal, API-Ninjas and a free LLM key from Groq (console.groq.com). Gemini is also supported through `LLM_PROVIDER`.

```powershell
Copy-Item .env.example .env
# edit .env: set the CHANGEME values and the three API keys
.\lab.ps1
```

The script builds the ML API, starts the stack, creates the TheHive organisation and analyst, enables the VirusTotal analyzer in Cortex, creates the n8n owner and imports the workflow.

Then:

1. Open n8n, open **DGA Detection to SOC Report**, click **Execute workflow**.
2. Watch the run in n8n.
3. Check the alert and case in TheHive.
4. Check the report in MailHog.

Default accounts are in `.env`. TheHive starts a 14-day Platinum trial; request the free Community licence for a long-lived lab.

## Workflow

```
Start -> pick VirusTotal analyzer -> load 12 domains
      -> POST /predict on the ML API
      -> score >= 0.6 ?
           yes -> TheHive alert -> case -> Cortex VirusTotal job -> poll -> report
           no  -> WHOIS + DNS
      -> collect -> LLM summary -> email
```

Scores map to TheHive severity: `0.6-0.69` low, `0.7-0.79` medium, `>= 0.8` high.

## Layout

```
ml-api/            DGA classifier (FastAPI + scikit-learn)
workflow/          importable n8n workflow
bootstrap/         one-shot setup for Cortex, TheHive, n8n
config/            TheHive and Cortex configuration
docs/              architecture and screenshots
docker-compose.yml
lab.ps1
```

## Configuration

All settings live in `.env`:

| Variable | Purpose |
|---|---|
| `VT_API_KEY` | VirusTotal, used by the Cortex analyzer |
| `LLM_API_KEY` | report summary, Groq or Gemini key |
| `LLM_PROVIDER`, `LLM_MODEL` | `groq` or `gemini`, and the model name |
| `APININJAS_API_KEY` | WHOIS enrichment |
| `THEHIVE_SECRET`, `CORTEX_SECRET`, `N8N_ENCRYPTION_KEY` | service secrets |
| `LAB_ORG`, `LAB_USER` | TheHive organisation and analyst |
| `SMTP_FROM`, `SMTP_TO` | report sender and recipient |

## Notes

- The workflow reads secrets from n8n credentials, never from the workflow file.
- Cortex runs analyzers as Docker containers, so it mounts the host Docker socket. This is lab-only.
- An API-Ninjas key was committed in the old workflow file. Rotate it if it is still active; see `SECURITY.md`.
- `docker compose down -v` removes all lab data.
