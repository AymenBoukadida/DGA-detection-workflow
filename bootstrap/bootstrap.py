import json
import os
import sys
import time

import requests

TIMEOUT = 30


def env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        raise SystemExit(f"missing environment variable {name}")
    return value


THEHIVE_URL = env("THEHIVE_URL").rstrip("/")
CORTEX_URL = env("CORTEX_URL").rstrip("/")
N8N_URL = env("N8N_URL").rstrip("/")
THEHIVE_ADMIN_USER = env("THEHIVE_ADMIN_USER")
THEHIVE_ADMIN_PASSWORD = env("THEHIVE_ADMIN_PASSWORD")
CORTEX_ADMIN_USER = env("CORTEX_ADMIN_USER")
CORTEX_ADMIN_PASSWORD = env("CORTEX_ADMIN_PASSWORD")
LAB_ORG = env("LAB_ORG", "soc")
LAB_USER = env("LAB_USER")
LAB_USER_PASSWORD = env("LAB_USER_PASSWORD")
N8N_OWNER_EMAIL = env("N8N_OWNER_EMAIL")
N8N_OWNER_PASSWORD = env("N8N_OWNER_PASSWORD")
N8N_OWNER_FIRST_NAME = env("N8N_OWNER_FIRST_NAME", "SOC")
N8N_OWNER_LAST_NAME = env("N8N_OWNER_LAST_NAME", "Analyst")
VT_API_KEY = env("VT_API_KEY", "")
APININJAS_API_KEY = env("APININJAS_API_KEY", "")
SMTP_FROM = env("SMTP_FROM", "soc@dga.lab")
SMTP_TO = env("SMTP_TO", "analyst@dga.lab")
OUT_DIR = "/out"


def log(message):
    print(f"[bootstrap] {message}", flush=True)


def wait_for(url, name, expected=(200,), attempts=120):
    last = None
    for _ in range(attempts):
        try:
            response = requests.get(url, timeout=10)
            last = response.status_code
            if response.status_code in expected:
                return
        except requests.RequestException as error:
            last = str(error)
        time.sleep(3)
    raise SystemExit(f"{name} is not ready at {url} (last result: {last})")


def cortex_session():
    session = requests.Session()
    response = session.post(
        f"{CORTEX_URL}/api/login",
        json={"user": CORTEX_ADMIN_USER, "password": CORTEX_ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    if response.status_code != 200:
        raise SystemExit(f"cannot log in to Cortex: {response.status_code} {response.text[:300]}")
    return session


def setup_cortex():
    wait_for(f"{CORTEX_URL}/api/status", "Cortex")
    response = requests.post(f"{CORTEX_URL}/api/maintenance/migrate", json={}, timeout=TIMEOUT)
    if response.status_code not in (200, 204):
        raise SystemExit(f"cortex index migration failed: {response.status_code} {response.text[:300]}")

    session = requests.Session()
    login = session.post(
        f"{CORTEX_URL}/api/login",
        json={"user": CORTEX_ADMIN_USER, "password": CORTEX_ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    if login.status_code != 200:
        created = session.post(
            f"{CORTEX_URL}/api/user",
            json={
                "login": CORTEX_ADMIN_USER,
                "name": CORTEX_ADMIN_USER,
                "password": CORTEX_ADMIN_PASSWORD,
                "roles": ["superadmin"],
                "organization": "cortex",
            },
            timeout=TIMEOUT,
        )
        if created.status_code != 201:
            raise SystemExit(f"cannot create Cortex superadmin: {created.status_code} {created.text[:300]}")
        session = cortex_session()
    log("Cortex superadmin ready")

    organisation = session.get(f"{CORTEX_URL}/api/organization/{LAB_ORG}", timeout=TIMEOUT)
    if organisation.status_code != 200:
        created = session.post(
            f"{CORTEX_URL}/api/organization",
            json={"name": LAB_ORG, "description": f"{LAB_ORG} organisation", "status": "Active"},
            timeout=TIMEOUT,
        )
        if created.status_code not in (200, 201):
            raise SystemExit(f"cannot create Cortex organisation: {created.status_code} {created.text[:300]}")
    log(f"Cortex organisation {LAB_ORG} ready")

    org_admin = f"{LAB_ORG}_admin"
    user = session.get(f"{CORTEX_URL}/api/user/{org_admin}", timeout=TIMEOUT)
    if user.status_code != 200:
        created = session.post(
            f"{CORTEX_URL}/api/user",
            json={
                "login": org_admin,
                "name": f"{LAB_ORG} admin",
                "password": LAB_USER_PASSWORD,
                "roles": ["read", "analyze", "orgadmin"],
                "organization": LAB_ORG,
            },
            timeout=TIMEOUT,
        )
        if created.status_code not in (200, 201):
            raise SystemExit(f"cannot create Cortex organisation admin: {created.status_code} {created.text[:300]}")

    key_response = session.get(f"{CORTEX_URL}/api/user/{org_admin}/key", timeout=TIMEOUT)
    key = key_response.text.strip().strip('"')
    if key_response.status_code != 200 or len(key) < 16 or "{" in key:
        key_response = session.post(f"{CORTEX_URL}/api/user/{org_admin}/key/renew", timeout=TIMEOUT)
        key = key_response.text.strip().strip('"')
    if len(key) < 16 or "{" in key:
        raise SystemExit(f"cannot obtain the Cortex API key: {key_response.status_code} {key_response.text[:300]}")
    log("Cortex organisation admin key ready")

    enable_virustotal(session, key)
    return key


def enable_virustotal(session, key):
    headers = {"Authorization": f"Bearer {key}"}
    definitions = requests.get(
        f"{CORTEX_URL}/api/analyzerdefinition?range=all", headers=headers, timeout=TIMEOUT
    )
    definitions.raise_for_status()
    candidates = [
        definition
        for definition in definitions.json()
        if definition.get("name") == "VirusTotal_GetReport"
    ]
    if not candidates:
        candidates = [
            definition
            for definition in definitions.json()
            if "virustotal" in definition.get("name", "").lower()
            and "report" in definition.get("name", "").lower()
        ]
    if not candidates:
        names = sorted({d.get("name", "") for d in definitions.json()})
        raise SystemExit(
            "no VirusTotal report analyzer in the Cortex catalogue. Available: "
            + ", ".join(names[:40])
        )
    definition = sorted(candidates, key=lambda item: item.get("version", ""))[-1]
    analyzer_id = definition["id"]

    enabled = requests.get(
        f"{CORTEX_URL}/api/analyzer?range=all", headers=headers, timeout=TIMEOUT
    )
    enabled.raise_for_status()
    enabled_names = []
    for item in enabled.json():
        if isinstance(item, str):
            enabled_names.append(item)
        elif isinstance(item, dict):
            enabled_names.append(item.get("name") or item.get("id") or "")
    if analyzer_id in enabled_names:
        log(f"analyzer {analyzer_id} already enabled")
        return

    configuration = {
        "key": VT_API_KEY,
        "polling_interval": 30,
        "auto_extract_artifacts": False,
        "check_tlp": True,
        "max_tlp": 2,
        "check_pap": True,
        "max_pap": 2,
    }
    response = requests.post(
        f"{CORTEX_URL}/api/organization/analyzer/{analyzer_id}",
        headers=headers,
        json={"name": analyzer_id, "configuration": configuration, "jobCache": 10, "jobTimeout": 30},
        timeout=TIMEOUT,
    )
    if response.status_code not in (200, 201):
        response = requests.post(
            f"{CORTEX_URL}/api/organization/analyzer/{analyzer_id}",
            headers=headers,
            json={"name": analyzer_id, "configuration": {"key": VT_API_KEY}, "jobCache": 10, "jobTimeout": 30},
            timeout=TIMEOUT,
        )
    if response.status_code not in (200, 201):
        raise SystemExit(f"cannot enable VirusTotal: {response.status_code} {response.text[:300]}")
    log(f"analyzer {analyzer_id} enabled")


def thehive_admin():
    return (THEHIVE_ADMIN_USER, THEHIVE_ADMIN_PASSWORD)


def ensure_thehive_org():
    for path in ("/api/v1/organisation", "/api/organisation"):
        current = requests.get(f"{THEHIVE_URL}{path}/{LAB_ORG}", auth=thehive_admin(), timeout=TIMEOUT)
        if current.status_code == 200:
            log(f"TheHive organisation {LAB_ORG} already exists")
            return
    response = requests.post(
        f"{THEHIVE_URL}/api/v1/organisation",
        auth=thehive_admin(),
        json={"name": LAB_ORG, "description": f"{LAB_ORG} lab organisation"},
        timeout=TIMEOUT,
    )
    if response.status_code not in (200, 201):
        response = requests.post(
            f"{THEHIVE_URL}/api/organisation",
            auth=thehive_admin(),
            json={"name": LAB_ORG, "description": f"{LAB_ORG} lab organisation"},
            timeout=TIMEOUT,
        )
    if response.status_code not in (200, 201):
        raise SystemExit(f"cannot create TheHive organisation: {response.status_code} {response.text[:300]}")
    log(f"TheHive organisation {LAB_ORG} created")


def ensure_thehive_user():
    lookup = requests.get(f"{THEHIVE_URL}/api/v1/user/{LAB_USER}", auth=thehive_admin(), timeout=TIMEOUT)
    if lookup.status_code == 200:
        user = lookup.json()
        log("TheHive analyst already exists")
        return user["_id"]

    created = requests.post(
        f"{THEHIVE_URL}/api/v1/user",
        auth=thehive_admin(),
        json={
            "login": LAB_USER,
            "name": LAB_USER.split("@")[0],
            "organisation": LAB_ORG,
            "profile": "org-admin",
            "password": LAB_USER_PASSWORD,
        },
        timeout=TIMEOUT,
    )
    if created.status_code not in (200, 201):
        raise SystemExit(f"cannot create TheHive analyst: {created.status_code} {created.text[:300]}")
    log("TheHive analyst created")

    user_id = created.json().get("_id") or created.json().get("id")
    requests.put(
        f"{THEHIVE_URL}/api/v1/user/{user_id}/organisations",
        auth=thehive_admin(),
        json={"organisations": [{"organisation": LAB_ORG, "profile": "org-admin"}]},
        timeout=TIMEOUT,
    )
    return user_id


def thehive_api_key(user_id):
    for method, path in (
        ("post", f"/api/v1/user/{user_id}/key"),
        ("get", f"/api/v1/user/{user_id}/key"),
        ("post", f"/api/v1/user/{LAB_USER}/key"),
    ):
        response = getattr(requests, method)(
            f"{THEHIVE_URL}{path}", auth=thehive_admin(), timeout=TIMEOUT
        )
        if response.status_code in (200, 201):
            key = response.text.strip().strip('"')
            if len(key) >= 16 and "{" not in key:
                log("TheHive API key ready")
                return key
    raise SystemExit(f"cannot create a TheHive API key: {response.status_code} {response.text[:300]}")


def ensure_case_template():
    headers = {"X-Organisation": LAB_ORG}
    auth = (LAB_USER, LAB_USER_PASSWORD)
    existing = requests.get(
        f"{THEHIVE_URL}/api/v1/caseTemplate?range=all", headers=headers, auth=auth, timeout=TIMEOUT
    )
    if existing.status_code == 200 and any(
        template.get("name") == "DGA Investigation" for template in existing.json()
    ):
        log("case template already exists")
        return
    created = requests.post(
        f"{THEHIVE_URL}/api/v1/caseTemplate",
        headers=headers,
        auth=auth,
        json={
            "name": "DGA Investigation",
            "displayName": "DGA Investigation",
            "titlePrefix": "[DGA]",
            "severity": 3,
            "tlp": 2,
            "pap": 2,
            "tags": ["dga", "dns"],
            "description": "Domain generated by an algorithm, investigated through the automated DGA pipeline.",
            "tasks": [
                {"order": 0, "title": "Confirm the DGA score", "group": "default"},
                {"order": 1, "title": "Review the VirusTotal report", "group": "default"},
                {"order": 2, "title": "Block the domain on the DNS resolver", "group": "default"},
            ],
        },
        timeout=TIMEOUT,
    )
    if created.status_code not in (200, 201):
        raise SystemExit(f"cannot create the case template: {created.status_code} {created.text[:300]}")
    log("case template created")


def register_cortex_in_thehive(cortex_key):
    config = {
        "statusCheckInterval": "1 minute",
        "refreshDelay": "5 seconds",
        "maxRetryOnError": 3,
        "jobTimeout": "3 hours",
        "servers": [
            {
                "name": "cortex",
                "url": f"{CORTEX_URL}",
                "auth": {"type": "bearer", "key": cortex_key},
                "wsConfig": {
                    "proxy": {"state": "disabled", "protocol": "http", "auth": {}},
                    "ssl": {
                        "loose": {"acceptAnyCertificate": False},
                        "trustManager": {},
                    },
                },
                "filterOrganization": "all",
                "includedTheHiveOrganisations": ["*"],
                "excludedTheHiveOrganisations": [],
            }
        ],
    }
    response = requests.put(
        f"{THEHIVE_URL}/api/v1/admin/config/cortex", auth=thehive_admin(), json=config, timeout=TIMEOUT
    )
    if response.status_code in (200, 204):
        log("Cortex registered in TheHive")
    else:
        log(f"warning: cannot register Cortex in TheHive ({response.status_code})")


def setup_n8n_owner():
    response = requests.post(
        f"{N8N_URL}/rest/owner/setup",
        json={
            "email": N8N_OWNER_EMAIL,
            "firstName": N8N_OWNER_FIRST_NAME,
            "lastName": N8N_OWNER_LAST_NAME,
            "password": N8N_OWNER_PASSWORD,
        },
        timeout=TIMEOUT,
    )
    if response.status_code in (200, 201):
        log("n8n owner account created")
    else:
        log(f"n8n owner setup returned {response.status_code} (already configured?)")


def write_credentials(cortex_key):
    credentials = [
        {
            "id": "cred-thehive",
            "name": "TheHive API",
            "type": "httpBasicAuth",
            "data": {"user": LAB_USER, "password": LAB_USER_PASSWORD},
        },
        {
            "id": "cred-cortex",
            "name": "Cortex API",
            "type": "httpHeaderAuth",
            "data": {"name": "Authorization", "value": f"Bearer {cortex_key}"},
        },
        {
            "id": "cred-apininjas",
            "name": "API-Ninjas",
            "type": "httpHeaderAuth",
            "data": {"name": "X-Api-Key", "value": APININJAS_API_KEY},
        },
        {
            "id": "cred-smtp",
            "name": "MailHog SMTP",
            "type": "smtp",
            "data": {
                "host": "mailhog",
                "port": 1025,
                "user": "",
                "password": "",
                "secure": False,
                "disableStartTls": True,
            },
        },
    ]
    with open(f"{OUT_DIR}/credentials.json", "w", encoding="utf-8") as handle:
        json.dump(credentials, handle, indent=2)
    log("credentials file written")


def main():
    wait_for(f"{THEHIVE_URL}/api/status", "TheHive")
    wait_for(f"{N8N_URL}/healthz", "n8n")
    cortex_key = setup_cortex()
    ensure_thehive_org()
    ensure_thehive_user()
    ensure_case_template()
    register_cortex_in_thehive(cortex_key)
    setup_n8n_owner()
    write_credentials(cortex_key)
    log("done")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
