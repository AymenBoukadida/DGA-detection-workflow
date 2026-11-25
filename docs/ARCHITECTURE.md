# Lab architecture

## Components

| Service | Image | Port | Role |
|---|---|---|---|
| ml-api | built from `ml-api/` | 8000 | DGA classifier, `POST /predict` |
| n8n | `n8nio/n8n:2.50.1` | 5678 | workflow engine |
| TheHive | `strangebee/thehive:6.0.0-3` | 9000 | alerts and cases |
| Cortex | `thehiveproject/cortex:4.2.0` | 9001 | analyzer engine, runs VirusTotal |
| Cassandra | `cassandra:4.1.12` | internal | TheHive graph store |
| Elasticsearch | `elasticsearch:8.19.25` | internal | TheHive and Cortex index |
| MailHog | `mailhog/mailhog:v1.0.1` | 1025 / 8025 | SMTP sink and web inbox |

## Data flow

```
n8n Start
  -> List Cortex analyzers, pick the VirusTotal instance
  -> Load domains (12 samples)
  -> POST /predict on ml-api  (score, severity)
  -> score >= 0.6 ?
       yes -> TheHive alert -> case -> Cortex VirusTotal job
                                            -> poll job (max 8 x 5 s)
                                            -> fetch report
                                            -> API-Ninjas WHOIS
       no  -> API-Ninjas WHOIS -> Google DNS A/NS
  -> collect results (one report after all 12 domains)
  -> LLM summary (Groq or Gemini)
  -> SMTP to MailHog
```

## Network

All services share the default Compose network and reach each other by service name. Only the UI and API ports are published to the host.

Cortex starts analyzer containers on the host Docker daemon through `/var/run/docker.sock`. A named `cortex-jobs` volume is mounted at `/tmp/cortex-jobs` in Cortex. An init container gives the Cortex user write access. `CORTEX_JOB_DIR` holds the volume path seen by the Docker daemon, so analyzer containers read the same job files.

## Notes

- TheHive 6 starts a 14-day Platinum trial on a fresh install. Request the free Community licence for a long-lived lab.
- TheHive and Cortex secrets come from `.env`. The repo contains no credential.
- API keys for VirusTotal, the LLM and API-Ninjas are read from `.env`. They are never committed.
