# AI-Assisted ML for Cybersecurity

A graduate module for the *Applied AI for Cybersecurity* course (IT7075C). This module teaches
**traditional machine learning methods to process and analyze cybersecurity datasets and create
predictions** — from data preparation through classical models, advanced analytics, and a first
look at deep learning. Throughout, students use AI coding assistants to accelerate the work while
remaining responsible for validating every result.

It consolidates what were previously four separate modules (ML Foundations, Applied ML, Advanced
ML, and Deep Learning) plus the capstone block into one continuous arc, and it is the home of the
course's final project, **Project 4 — AI-Assisted ML Capstone**.

## Starter notebooks

Four hands-on starter notebooks, one per subtopic, in the same format as the rest of the course —
each topic is a **slide**, an **instructor script**, and a **runnable code** cell. They all run
**fully offline** on a small synthetic "connection events" dataset generated in-notebook (no API
key, no downloads), so you can run them in class and then swap in a real Kaggle dataset for
Project 4.

- **[01_ml_foundations.ipynb](01_ml_foundations.ipynb)** — load, inspect, clean, engineer features,
  visualize, split, and the cardinal sin of **data leakage**.
- **[02_applied_ml_detection.ipynb](02_applied_ml_detection.ipynb)** — baseline classifiers and the
  metrics that matter in a SOC (confusion matrix, precision/recall/F1, ROC-AUC, threshold tuning).
- **[03_advanced_ml_analytics.ipynb](03_advanced_ml_analytics.ipynb)** — random forest, gradient
  boosting, feature importance, class-imbalance handling, clustering, and anomaly detection.
- **[04_deep_learning.ipynb](04_deep_learning.ipynb)** — a small **PyTorch** network, the training
  loop, and an honest benchmark against a classical baseline.

Like the other modules, the notebooks are **generated from `_build_*.py` scripts**. To change a
lecture, edit the build script and re-run it (`python _build_01_ml_foundations.py`), then re-execute
to refresh outputs (`jupyter nbconvert --to notebook --execute --inplace 01_ml_foundations.ipynb`).

---

## Subtopics

The module is organized into the four original topic areas, taught in sequence, followed by a
capstone clinic.

### 1. ML Foundations for Cybersecurity
The end-to-end ML workflow and why data preparation dominates security analytics.
- Supervised, unsupervised, and reinforcement learning concepts
- Cybersecurity dataset selection and documentation
- Data cleaning, feature engineering, visualization, and train/test splitting
- Leakage, bias, imbalance, and reproducibility
- Baseline modeling preparation

### 2. Applied ML for Security Detection
Building and *evaluating* baseline detectors, with the metrics that actually matter in a SOC.
- Security classification tasks and model baselines
- Confusion matrix, precision, recall, F1, ROC-AUC, and thresholds
- False-positive / false-negative trade-offs
- Phishing URLs, malware-related features, and SMS spam detection
- Model interpretation and reporting

### 3. Advanced ML for Security Analytics
Ensembles, imbalance handling, and unsupervised discovery of suspicious behavior.
- Random forests and gradient boosting
- XGBoost and feature importance
- Class imbalance, class weights, and train-only resampling
- Clustering and anomaly detection
- Network intrusion and log anomaly analytics

### 4. Deep Learning for Cybersecurity
When neural networks help, when they don't, and how to compare them honestly to classical models.
- Neural network fundamentals and PyTorch basics
- Loss functions, optimizers, training loops, and overfitting
- Deep learning for sequence and log analysis
- Comparison with classical ML baselines
- Explainability, robustness, and deployment considerations

### 5. Capstone Clinic, Checkpoint & Presentations
Turning the work above into a complete, defensible project.
- Project scoping and dataset validation
- Model refinement and evaluation review
- Explainability and limitations discussion
- Professional reporting and presentation preparation
- Actionable security recommendations

---

## Project 4 — AI-Assisted ML Capstone

An individual, end-to-end ML project that produces **comprehensive analysis on an up-to-date
cybersecurity dataset and high-ranking results**, with help from AI tools.

- **Pick a current dataset** from [kaggle.com](https://www.kaggle.com/datasets) (or another
  instructor-approved source such as UCI, NSL-KDD, CIC-IDS2017, or Loghub). Prefer recent,
  well-documented security datasets — phishing, intrusion detection, malware, fraud, or log anomaly.
- **Do the full pipeline:** problem framing → data preparation → feature engineering → modeling
  (classical and/or deep) → evaluation → interpretation → reporting.
- **Aim for high-ranking results.** If the dataset has a Kaggle leaderboard or an established
  benchmark, target competitive scores; otherwise, beat a documented baseline and justify the gain.
- **Use AI as an assistant, not an author.** AI tools may help with brainstorming, code generation,
  debugging, and interpretation — but you must validate every output and include a brief **AI-use
  statement** (tool used, purpose, how you verified or modified the output).
- **Deliverables:** a reproducible notebook/repo, a technical report (evidence, analysis,
  limitations, recommendations), and a final presentation.

> **Datasets to consider:** Kaggle phishing / URL datasets, CIC-IDS2017, NSL-KDD, HDFS / Loghub
> logs, SMS spam, and other recent security datasets approved by the instructor.

---

## Suggested workflow

1. Start with **ML Foundations**: load, clean, visualize, and split your dataset; watch for leakage.
2. Build **baseline detectors** and choose evaluation metrics tied to SOC impact.
3. Move to **advanced analytics**: ensembles (RF/XGBoost), imbalance handling, clustering/anomaly.
4. Add a **deep-learning** comparison (PyTorch) where the data justifies it.
5. Refine, document, and present in the **capstone clinic**.

## Setup

```bash
pip install -r requirements.txt
```

Then open any notebook in Jupyter, VS Code, or Google Colab and run the cells top to bottom (Colab
is convenient for a GPU when training the deep-learning notebook, though it runs fine on CPU). The
four starter notebooks need no API key. For **Project 4**, `pip install kagglehub` (or use the
Kaggle CLI) to pull your chosen dataset, and keep any keys in the repository-root `.env` — never
commit secrets.

## Ethics & scope

All work stays within approved datasets and the authorized class environment. Frame results as
**defensive** analysis, be explicit about limitations and data-leakage risks, and never present an
unvalidated model as production-ready.

---

*Recommended readings (from the syllabus):* Géron, *Hands-On Machine Learning* (Ch. 1–3, 7, 9, 10);
Chio & Freeman, *Machine Learning and Security* (Ch. 2–4, 6); Stevens et al., *Deep Learning with
PyTorch* (Ch. 1–5); plus the scikit-learn, XGBoost, and PyTorch documentation.
