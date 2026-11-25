# Security note

The previous version of `n8n-workflow.json` contained a hardcoded API-Ninjas key:

The key is not reproduced here.

It was committed to a public repository, so treat it as compromised. Revoke it in the API-Ninjas dashboard and create a new key. Do not reuse it anywhere.

The workflow now reads the key from an n8n credential created from `.env`.

Other lab defaults (`admin@thehive.local / secret`, Cortex `admin / secret`) are for a local machine only. Change them before exposing any port outside localhost.
