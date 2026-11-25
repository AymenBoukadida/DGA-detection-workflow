from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import FunctionTransformer

from app.features import NUMERIC_FEATURE_NAMES, numeric_features
from training.generate import build_dataset, curated_benign_domains

MODEL_VERSION = "1.0.0"
RANDOM_STATE = 42
THRESHOLD = 0.6
TEST_SIZE = 0.2

TEXT_FEATURES = {
    "type": "tfidf",
    "analyzer": "char_wb",
    "ngram_range": (2, 4),
    "min_df": 2,
    "sublinear_tf": True,
}


@dataclass(frozen=True)
class TrainedModel:
    pipeline: Pipeline
    metrics: dict[str, float]
    training_samples: int
    dataset_samples: int

    def predict_proba(self, domains: list[str]) -> np.ndarray:
        return self.pipeline.predict_proba(domains)[:, 1]


def _build_pipeline() -> Pipeline:
    features = FeatureUnion(
        [
            (
                "text",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=TEXT_FEATURES["ngram_range"],
                    min_df=TEXT_FEATURES["min_df"],
                    sublinear_tf=TEXT_FEATURES["sublinear_tf"],
                    lowercase=True,
                ),
            ),
            ("numeric", FunctionTransformer(numeric_features, validate=False)),
        ]
    )
    classifier = LogisticRegression(
        max_iter=2000,
        C=4,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    return Pipeline([("features", features), ("classifier", classifier)])


def train_model(seed: int = RANDOM_STATE) -> TrainedModel:
    domains, labels = build_dataset(seed=seed)
    curated = set(curated_benign_domains())

    generated_idx = [i for i, domain in enumerate(domains) if domain not in curated]
    curated_idx = [i for i, domain in enumerate(domains) if domain in curated]

    generated_domains = [domains[i] for i in generated_idx]
    generated_labels = [labels[i] for i in generated_idx]

    x_train, x_test, y_train, y_test = train_test_split(
        generated_domains,
        generated_labels,
        test_size=TEST_SIZE,
        random_state=seed,
        stratify=generated_labels,
    )

    x_train.extend(domains[i] for i in curated_idx)
    y_train.extend(labels[i] for i in curated_idx)

    pipeline = _build_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
    }

    return TrainedModel(
        pipeline=pipeline,
        metrics=metrics,
        training_samples=len(x_train),
        dataset_samples=len(domains),
    )


def model_info(model: TrainedModel) -> dict:
    return {
        "version": MODEL_VERSION,
        "training_samples": model.training_samples,
        "dataset_samples": model.dataset_samples,
        "features": {
            "text": {
                "type": TEXT_FEATURES["type"],
                "analyzer": TEXT_FEATURES["analyzer"],
                "ngram_range": list(TEXT_FEATURES["ngram_range"]),
                "min_df": TEXT_FEATURES["min_df"],
                "sublinear_tf": TEXT_FEATURES["sublinear_tf"],
            },
            "numeric": list(NUMERIC_FEATURE_NAMES),
        },
        "metrics": model.metrics,
        "threshold": THRESHOLD,
    }
