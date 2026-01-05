![DNS DGA Detection Workflow](https://github.com/AymenBoukadida/DGA-detection-workflow/blob/0db2c3b9af1a35bdb38a5a4487b83214f02591db/image.png?raw=true)

# 🛡️ DNS DGA Detection & Automated SOC Pipeline

## 📌 Project Overview

Modern malware families commonly use **Domain Generation Algorithms (DGAs)** to generate large volumes of random-looking domains such as:
ajd92hsjkdqw.biz
mnsf82hdsak.ru


These domains are used for:

- Command-and-Control communication (C2)
- Evasion of static DNS blocklists
- Increasing attacker resilience
- Avoiding domain takedown

Because the domains look random and constantly change, they are hard to detect using traditional tools.  
This project builds an **automated ML-driven pipeline** that detects suspicious DGA-generated domains and triggers a SOC investigation workflow.

---

## 🎯 Project Objective

This project implements an **end-to-end detection & enrichment pipeline** using:

- Machine Learning
- n8n automation
- TheHive case management
- Cortex enrichment
- VirusTotal threat intel
- AI-assisted reporting
- Email notification

---

## 🧠 DGA Detection Logic

Each DNS domain is sent to a Machine Learning API that returns a **probability score**.

| Returned Score | Interpretation |
|----------------|----------------|
| `< 0.6` | Likely Benign |
| `≥ 0.6` | Suspicious / Potential DGA |

Domains above the threshold enter the SOC workflow.

---

## 🔗 Full Workflow

### 🔹 Workflow Name

```

DNS ML + TheHive + Cortex End-to-End

```

### 🔹 Workflow Steps

1️⃣ Receive DNS domain input  
2️⃣ Send domain to ML API  
3️⃣ Parse ML probability score  
4️⃣ If score ≥ 0.6 → mark as suspicious  
5️⃣ Create alert in TheHive  
6️⃣ Promote alert to a case  
7️⃣ Run Cortex VirusTotal analyzer  
8️⃣ Retrieve report and risk verdict  
9️⃣ Summarize using Gemini AI  
🔟 Send final email to SOC analyst  

---

## 🏗 System Components

| Component | Purpose |
|----------|---------|
| **n8n** | Automation engine |
| **ML API** | DGA score classification |
| **TheHive** | Alert & Case management |
| **Cortex** | Analysis engine |
| **VirusTotal Analyzer** | Domain reputation lookup |
| **Gemini AI** | Report summarization |
| **SMTP** | Email delivery |

---

## 📡 Data Flow Diagram

```

DNS Query
↓
ML API
↓
Score ≥ 0.6 ?
↓ Yes
Create Alert in TheHive
↓
Promote to Case
↓
Cortex → VirusTotal
↓
AI Report
↓
Email SOC

```

---

## 📧 Example SOC Report Output

```

Indicator: hlsgafabsduw.ru
Risk Level: Safe
Detection Ratio: 0/90
Verdict: No malicious activity detected
Recommendation: Continue monitoring

```

Another sample:

```

Indicator: yfcjwloujkcmil.biz
Risk Level: Suspicious
Detected URLs: 1/90 engines
Verdict: May be associated with malicious behavior
Recommendation: Block + investigate

````

---

## 🧩 Example Cortex Report Structure

```json
{
  "summary": {
    "taxonomies": [
      {
        "predicate": "GetReport",
        "namespace": "VT",
        "value": "1 detected_url(s)",
        "level": "suspicious"
      }
    ]
  },
  "full": {
    "detected_urls": [
      {
        "total": 90,
        "positives": 1,
        "scan_date": "2023-07-23 23:20:17",
        "url": "https://yfcjwloujkcmil.biz/"
      }
    ]
  },
  "success": true
}
````

---

## 📂 Repository Structure

```
/docs
    architecture.md
    workflow.md
/workflow
    n8n-export.json
README.md
```

---

## 📜 docs/architecture.md

```md
# System Architecture

This document explains the architecture used in the DNS DGA Detection pipeline.

## Components
- ML API detects suspicious DGA-like domains
- n8n automates alerting & enrichment
- TheHive manages investigations
- Cortex + VirusTotal gather threat intel
- Gemini AI summarizes findings
- Email notifies SOC analysts



---

## 📜 docs/workflow.md


# Workflow Description

1. Domain is received
2. ML API returns probability
3. If ≥ 0.6 → suspicious
4. TheHive alert created
5. Alert promoted to case
6. Cortex analyzer runs VirusTotal lookup
7. Results summarized
8. Email sent to SOC



---

## ✉ Email Content (HTML Template)


<h2>DNS DGA Detection Report</h2>

<p><strong>Domain:</strong> {{domain}}</p>
<p><strong>DGA Probability:</strong> {{probability}}</p>
<p><strong>Risk Level:</strong> {{risk_level}}</p>

<h3>VirusTotal Summary</h3>
<p>{{taxonomy}}</p>

<p><strong>Conclusion:</strong> {{summary}}</p>
```

---

## 🚀 Results & Benefits

✔ Faster SOC triage
✔ Automated intelligence gathering
✔ Reduced manual workload
✔ AI-assisted reporting
✔ Better visibility into DNS threats

---

## 🔮 Future Enhancements

* Multi-domain batch analysis
* Dashboarding & visual analytics
* DNS sinkhole integration

---




