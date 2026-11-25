from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BENIGN_DOMAINS = [
    "google.com",
    "wikipedia.org",
    "github.com",
    "amazon.com",
    "nytimes.com",
    "cloudflare.com",
    "python.org",
]

DGA_DOMAINS = [
    "xj3kq9zvtbwrm7p2.com",
    "k8v3n9q2x7z4m1p6.net",
    "a3f9c2b7e1d4085f.org",
    "qzxvbnmkjhgfdsap.info",
]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True}


def test_model_info():
    response = client.get("/model-info")
    assert response.status_code == 200
    body = response.json()
    assert body["version"]
    assert body["training_samples"] >= 4000
    assert body["dataset_samples"] >= 6000
    assert len(body["features"]["numeric"]) == 9
    assert set(body["metrics"]) == {"accuracy", "precision", "recall", "f1"}
    assert body["threshold"] == 0.6


def test_known_benign_domains_score_below_threshold():
    for domain in BENIGN_DOMAINS:
        response = client.post("/predict", json={"domain": domain})
        assert response.status_code == 200, domain
        body = response.json()
        assert body["probability_DGA"] < 0.6, (domain, body)
        assert body["label"] == "benign"
        assert body["severity"] == 0


def test_random_domains_score_at_or_above_threshold():
    for domain in DGA_DOMAINS:
        response = client.post("/predict", json={"domain": domain})
        assert response.status_code == 200, domain
        body = response.json()
        assert body["probability_DGA"] >= 0.6, (domain, body)
        assert body["label"] == "dga"
        assert body["severity"] >= 1


def test_prediction_normalizes_input():
    response = client.post(
        "/predict",
        json={"domain": "HTTPS://Google.COM./search?q=test"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "google.com"
    assert body["probability_DGA"] < 0.6


def test_invalid_domain_returns_422():
    invalid = [
        "",
        "   ",
        "not a domain",
        "localhost",
        "-bad.com",
        "bad-.com",
        "bad..com",
        "bad_domain.com",
        "http://",
        "example.123",
    ]
    for domain in invalid:
        response = client.post("/predict", json={"domain": domain})
        assert response.status_code == 422, domain
        assert response.json()["detail"]


def test_missing_domain_returns_422():
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_batch_predict():
    response = client.post(
        "/predict/batch",
        json={"domains": ["google.com", "xj3kq9zvtbwrm7p2.com"]},
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 2
    assert results[0]["domain"] == "google.com"
    assert results[1]["domain"] == "xj3kq9zvtbwrm7p2.com"
    for result in results:
        assert set(result) == {
            "domain",
            "probability_DGA",
            "label",
            "threshold",
            "severity",
        }
        assert result["threshold"] == 0.6
        assert isinstance(result["probability_DGA"], float)
        assert 0 <= result["severity"] <= 3


def test_batch_invalid_domain_returns_422():
    response = client.post(
        "/predict/batch",
        json={"domains": ["google.com", "bad_domain"]},
    )
    assert response.status_code == 422
    assert "index 1" in response.json()["detail"]


def test_batch_empty_returns_422():
    response = client.post("/predict/batch", json={"domains": []})
    assert response.status_code == 422
