from app.model import train_model
from training.generate import build_dataset


def test_dataset_is_balanced_and_large():
    domains, labels = build_dataset()
    assert len(domains) >= 6000
    assert labels.count(1) == labels.count(0)
    assert len(set(domains)) == len(domains)


def test_training_is_deterministic():
    first = train_model()
    second = train_model()
    assert first.metrics == second.metrics
    assert first.training_samples == second.training_samples
    assert first.dataset_samples == second.dataset_samples
    assert first.predict_proba(["google.com"]).tolist() == second.predict_proba(
        ["google.com"]
    ).tolist()
