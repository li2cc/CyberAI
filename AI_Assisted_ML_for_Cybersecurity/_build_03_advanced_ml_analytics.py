"""Generator for 03_advanced_ml_analytics.ipynb — Advanced ML for Security Analytics.

Starter notebook 3 of 4. Same format. Runs offline on scikit-learn (gradient
boosting via HistGradientBoostingClassifier so no xgboost dependency is needed;
XGBoost shown in comments). Focus: ensembles, feature importance, class
imbalance handling, clustering, and anomaly detection.

Run:  python _build_03_advanced_ml_analytics.py
"""
import json

cells = []


def md(source):
    cells.append({"cell_type": "markdown", "metadata": {},
                  "source": source.splitlines(keepends=True)})


def code(source):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": source.rstrip("\n").splitlines(keepends=True)})


def slide(title, bullets):
    md(f"# {title}\n\n" + "\n".join(f"- {b}" for b in bullets))


def script(text):
    md("> ### \U0001F3A4 Instructor Script\n>\n> " + text.replace("\n", "\n> "))


# ---------------------------------------------------------------------------
md(
    "# Advanced ML for Security Analytics\n"
    "### Starter Notebook 3 of 4 — AI-Assisted ML for Cybersecurity\n\n"
    "**Audience:** Students who completed notebooks 1–2.\n\n"
    "**Goal:** Move beyond a single baseline to **ensembles** (random forest, gradient boosting), "
    "read **feature importance**, handle **class imbalance** correctly, and use **unsupervised** "
    "methods — clustering and anomaly detection — to surface suspicious behavior you have no labels "
    "for.\n\n"
    "> **Reproducibility:** runs offline on `scikit-learn`. We use "
    "`HistGradientBoostingClassifier` (no `xgboost` install needed); the XGBoost equivalent is shown "
    "in comments. Same synthetic dataset as the earlier notebooks, but more imbalanced."
)

md("## \U0001F6E0️ Setup — a more imbalanced dataset & split")
code(
    r'''# If needed:  !pip install -q numpy pandas scikit-learn matplotlib   (xgboost optional)
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def make_security_events(n=4000, frac_malicious=0.08, seed=42):
    """Synthetic 'connection events' (1=malicious). Default here is MORE imbalanced (8%)."""
    rng = np.random.default_rng(seed)
    n_mal = int(n * frac_malicious); n_ben = n - n_mal

    def block(size, fl, bs, br, dur, hr, ports):
        return pd.DataFrame({
            "failed_logins": rng.poisson(fl, size),
            "bytes_sent":    rng.normal(*bs, size).clip(0),
            "bytes_recv":    rng.normal(*br, size).clip(0),
            "duration_s":    rng.normal(*dur, size).clip(0),
            "unusual_hour":  rng.binomial(1, hr, size),
            "ports_touched": rng.poisson(ports, size),
        })

    benign = block(n_ben, 0.5, (2000, 600), (5000, 1500), (30, 10), 0.05, 1.5); benign["label"] = 0
    malicious = block(n_mal, 4.0, (8000, 3000), (3000, 1500), (80, 40), 0.5, 8.0); malicious["label"] = 1
    df = pd.concat([benign, malicious], ignore_index=True)
    return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)


df = make_security_events()
features = ["failed_logins", "bytes_sent", "bytes_recv", "duration_s", "unusual_hour", "ports_touched"]
X, y = df[features], df["label"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)
print("Train:", X_train.shape, " malicious rate:", round(y_train.mean(), 3),
      "  (tree models don't need scaling)")'''
)

# ---- 1: random forest -------------------------------------------------------
slide("\U0001F333 1 — Random Forest", [
    "An **ensemble** of decision trees voting together",
    "Each tree sees a random subset of data & features",
    "Averaging many weak trees → strong, stable model",
    "Handles non-linear boundaries, needs no scaling",
    "A strong, low-effort baseline for tabular security data",
])
script(
    "Ensembles are the workhorses of tabular security ML, so we start with the random forest. A "
    "single decision tree is easy to overfit, but a forest trains many trees, each on a random "
    "subset of rows and features, and lets them vote. The randomness decorrelates their errors, so "
    "the average is far more accurate and stable than any one tree. Forests handle non-linear "
    "boundaries, need no feature scaling, and work well out of the box, which makes them an "
    "excellent strong baseline. We fit one and check ROC-AUC against the logistic baseline from "
    "notebook two — you should see a clear jump."
)
code(
    r'''from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score

rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=1).fit(X_train, y_train)
rf_score = rf.predict_proba(X_test)[:, 1]
print("Random Forest  ROC-AUC:", round(roc_auc_score(y_test, rf_score), 3),
      " F1:", round(f1_score(y_test, rf.predict(X_test)), 3))'''
)

# ---- 2: gradient boosting ---------------------------------------------------
slide("⚡ 2 — Gradient Boosting", [
    "Trees built **sequentially**, each fixing the last's errors",
    "Often the top performer on tabular data",
    "scikit-learn: `HistGradientBoostingClassifier` (fast)",
    "Industry favorite: **XGBoost** / LightGBM (same idea)",
    "More powerful, but more hyperparameters to tune",
])
script(
    "Where a forest builds trees independently, gradient boosting builds them in sequence, each new "
    "tree focusing on the examples the previous ones got wrong. This targeted error-correction "
    "usually makes boosting the top performer on tabular data, which is why XGBoost and LightGBM "
    "dominate Kaggle leaderboards. We use scikit-learn's histogram-based booster so nothing extra "
    "needs installing, and we leave the XGBoost call in comments so you can swap it in for Project "
    "4. The trade-off is tuning: boosting has more knobs — learning rate, depth, number of trees — "
    "and is easier to overfit, so disciplined validation matters."
)
code(
    r'''from sklearn.ensemble import HistGradientBoostingClassifier

gb = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                    random_state=42).fit(X_train, y_train)
gb_score = gb.predict_proba(X_test)[:, 1]
print("Gradient Boosting  ROC-AUC:", round(roc_auc_score(y_test, gb_score), 3),
      " F1:", round(f1_score(y_test, gb.predict(X_test)), 3))

# --- XGBoost equivalent (pip install xgboost) ---
# from xgboost import XGBClassifier
# xgb = XGBClassifier(n_estimators=300, learning_rate=0.08, max_depth=4,
#                     subsample=0.9, eval_metric="logloss", random_state=42)
# xgb.fit(X_train, y_train)
# xgb_score = xgb.predict_proba(X_test)[:, 1]'''
)

# ---- 3: feature importance --------------------------------------------------
slide("\U0001F50D 3 — Feature Importance", [
    "Which signals drive the model's decisions?",
    "Tree models expose importances directly",
    "**Permutation importance** is more reliable",
    "Explainability builds analyst trust",
    "Sanity-check: do the top features make sense?",
])
script(
    "A detector you cannot explain is hard to trust and hard to defend. Tree ensembles let us ask "
    "which features mattered most. We use permutation importance, which measures how much "
    "performance drops when each feature's values are shuffled — a model-agnostic and more honest "
    "measure than the built-in impurity importances. The ranking should match security intuition: "
    "failed logins and ports touched ought to sit near the top. If a nonsensical feature dominates, "
    "that is a red flag for leakage or a data artifact. This kind of explainability is exactly what "
    "the course's Explainable-AI outcomes are about, and what you will report to stakeholders."
)
code(
    r'''from sklearn.inspection import permutation_importance

perm = permutation_importance(gb, X_test, y_test, n_repeats=10, random_state=42, n_jobs=1)
importance = (pd.Series(perm.importances_mean, index=features)
              .sort_values(ascending=False))
print("Permutation importance (drop in score when a feature is shuffled):\n")
print(importance.round(4).to_string())
print("\nTop drivers should match intuition: failed_logins, ports_touched, ...")'''
)

# ---- 4: imbalance -----------------------------------------------------------
slide("⚖️ 4 — Handling Class Imbalance", [
    "Attacks are rare → models ignore the minority",
    "Fix 1: **class weights** (penalize minority errors more)",
    "Fix 2: **resample** — but on the TRAINING data only",
    "Never oversample before the split (leakage!)",
    "Re-check recall on the attack class after",
])
script(
    "With only eight percent attacks, models are tempted to ignore the minority class. Two standard "
    "fixes: tell the model to weight minority errors more heavily with class weights, or resample "
    "the training set to rebalance it. We show class weighting because it is simple and leak-free. "
    "The critical rule for any resampling — including SMOTE — is that it happens on the training "
    "data only, after the split; oversample before splitting and copies of the same attack land in "
    "both train and test, inflating your scores. After applying weights, we re-check recall on the "
    "attack class, which is the number that should improve."
)
code(
    r'''from sklearn.metrics import recall_score, precision_score

rf_plain = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=1).fit(X_train, y_train)
rf_bal = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=1,
                                class_weight="balanced").fit(X_train, y_train)

for name, m in [("plain", rf_plain), ("class_weight=balanced", rf_bal)]:
    pred = m.predict(X_test)
    print(f"{name:22s} recall(attack)={recall_score(y_test, pred):.3f}  "
          f"precision(attack)={precision_score(y_test, pred):.3f}")

print("\nResampling reminder: fit SMOTE/oversampling on TRAIN ONLY, never before the split.")'''
)

# ---- 5: clustering ----------------------------------------------------------
slide("\U0001F9E9 5 — Clustering (Unsupervised)", [
    "No labels? Group events by similarity",
    "**K-Means** partitions data into k clusters",
    "Small/odd clusters can flag suspicious groups",
    "Useful for triage and discovering attack families",
    "Scale features first (distance-based)",
])
script(
    "Often you have telemetry but no labels. Unsupervised learning finds structure anyway. K-Means "
    "groups events into clusters by similarity; we then peek at the true labels — which the model "
    "never saw — to see whether any cluster concentrates the attacks. In real triage, a small, "
    "unusual cluster is a lead worth investigating, and clustering can reveal attack families you "
    "did not know existed. Because K-Means uses distances, we scale the features first. Treat the "
    "clusters as hypotheses, not verdicts: they point an analyst toward where to look rather than "
    "deciding guilt."
)
code(
    r'''from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

Xs = StandardScaler().fit_transform(X)              # unsupervised: use all rows, scaled
km = KMeans(n_clusters=4, n_init=10, random_state=42).fit(Xs)

summary = (pd.DataFrame({"cluster": km.labels_, "is_attack": y.values})
           .groupby("cluster")["is_attack"].agg(["size", "mean"])
           .rename(columns={"size": "events", "mean": "attack_fraction"}))
print("Per-cluster attack concentration (labels were NOT used to fit):\n")
print(summary.round(3).to_string())
print("\nA cluster with a high attack_fraction is a strong triage lead.")'''
)

# ---- 6: anomaly detection ---------------------------------------------------
slide("\U0001F6A8 6 — Anomaly Detection", [
    "Model 'normal', then flag what doesn't fit",
    "**Isolation Forest** isolates rare points fast",
    "Trains on mostly-benign traffic (no attack labels)",
    "Great for zero-day / novel behavior",
    "Tune contamination = expected anomaly rate",
])
script(
    "Supervised models only catch attacks resembling past labels. Anomaly detection takes the "
    "opposite tack: learn what normal looks like and flag deviations, which is how you stand a "
    "chance against novel or zero-day behavior. Isolation Forest works by randomly partitioning the "
    "data; anomalous points get isolated in very few splits, so they are cheap to find. We train it "
    "on predominantly benign traffic, set the contamination to roughly the rate of anomalies we "
    "expect, and then measure how many real attacks land in its flagged set. It will not be "
    "perfect, but as an unsupervised tripwire that needs no attack labels, it is a valuable layer "
    "in a defense-in-depth detection stack."
)
code(
    r'''from sklearn.ensemble import IsolationForest

iso = IsolationForest(contamination=0.08, random_state=42).fit(Xs)
flags = iso.predict(Xs)                              # -1 = anomaly, 1 = normal
is_anomaly = (flags == -1).astype(int)

detected = ((is_anomaly == 1) & (y.values == 1)).sum()
total_attacks = int(y.sum())
print(f"Flagged {is_anomaly.sum()} of {len(y)} events as anomalies.")
print(f"Attacks caught by anomaly detection: {detected}/{total_attacks} "
      f"({detected / total_attacks:.0%}) — with NO attack labels used.")'''
)

# ---- Summary ----------------------------------------------------------------
slide("✅ Summary — Advanced Analytics", [
    "Ensembles (RF, gradient boosting) beat single models",
    "Explain models with permutation importance",
    "Handle imbalance with weights / train-only resampling",
    "Clustering finds structure without labels",
    "Anomaly detection catches novel attacks",
    "Next → deep learning, and when it's worth it",
])
script(
    "We leveled up from a single baseline to the techniques that win real security-analytics work: "
    "random forests and gradient boosting for accuracy, permutation importance for explainability, "
    "class weights and train-only resampling for imbalance, and two unsupervised tools — K-Means "
    "clustering and Isolation Forest anomaly detection — for the common case where labels are "
    "scarce. For Project 4 on a Kaggle dataset, this is your toolkit: boost for the leaderboard, "
    "explain for the report, and lean on unsupervised methods when labels run out. Next we ask "
    "whether deep learning earns its complexity over these strong classical baselines."
)
code(
    r'''print("Model comparison (ROC-AUC on the test set):")
print("  Random Forest    :", round(roc_auc_score(y_test, rf_score), 3))
print("  Gradient Boosting:", round(roc_auc_score(y_test, gb_score), 3))
print("\nNext: 04_deep_learning.ipynb -> a PyTorch model vs. these classical baselines.")'''
)

# ---------------------------------------------------------------------------
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": []},
    },
    "cells": cells,
}

with open("03_advanced_ml_analytics.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Wrote 03_advanced_ml_analytics.ipynb with {len(cells)} cells.")
