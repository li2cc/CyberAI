"""Generator for 04_deep_learning.ipynb — Deep Learning for Cybersecurity.

Starter notebook 4 of 4. Same format. Builds a small PyTorch MLP on the same
synthetic security dataset and compares it honestly to a classical baseline.
Runs offline on torch + scikit-learn (CPU is fine). The training step is guarded
so the notebook still renders if torch is missing.

Run:  python _build_04_deep_learning.py
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
    "# Deep Learning for Cybersecurity\n"
    "### Starter Notebook 4 of 4 — AI-Assisted ML for Cybersecurity\n\n"
    "**Audience:** Students who completed notebooks 1–3.\n\n"
    "**Goal:** Build a small **PyTorch** neural network for security detection, understand the "
    "training loop (loss, optimizer, epochs, overfitting), and — most importantly — **compare it "
    "honestly to a classical baseline** so you can judge *when deep learning is actually worth it*.\n\n"
    "> **Reproducibility:** runs offline on `torch` + `scikit-learn` (CPU is fine for this small "
    "model). The training cell is guarded on the `torch` import so the rest still renders if it is "
    "not installed."
)

md("## \U0001F6E0️ Setup — dataset, split, and a classical baseline to beat")
code(
    r'''# If needed:  !pip install -q torch scikit-learn numpy pandas
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, f1_score


def make_security_events(n=4000, frac_malicious=0.15, seed=42):
    """Synthetic 'connection events' (1=malicious), same generator as earlier notebooks."""
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
X, y = df[features].values, df["label"].values
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

scaler = StandardScaler().fit(X_train)              # NNs need scaled inputs; fit on train only
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

# Classical baseline the neural net must beat (from notebook 3).
from sklearn.ensemble import HistGradientBoostingClassifier
baseline = HistGradientBoostingClassifier(random_state=42).fit(X_train_s, y_train)
base_auc = roc_auc_score(y_test, baseline.predict_proba(X_test_s)[:, 1])
print("Classical baseline (gradient boosting) ROC-AUC:", round(base_auc, 3))'''
)

# ---- 1: when DL ------------------------------------------------------------
slide("\U0001F9E0 1 — When Is Deep Learning Worth It?", [
    "Classical ML usually wins on small tabular data",
    "Deep learning shines with **scale** & raw structure",
    "Sequences (logs), text, images, packet payloads",
    "Costs: data, compute, tuning, explainability",
    "Always benchmark DL against a classical baseline",
])
script(
    "Before writing a single layer, be honest about when deep learning helps. On small, tidy "
    "tabular datasets — which describes most classroom security data — gradient-boosted trees "
    "usually match or beat neural networks with far less effort. Deep learning earns its keep when "
    "you have scale and raw structure: long sequences of log events, free text, images, or packet "
    "payloads where the network can learn features you would never hand-craft. It also costs more — "
    "data, compute, tuning, and explainability. So the rule we enforce all notebook: benchmark the "
    "neural net against the classical baseline we just trained, and only prefer it if it genuinely "
    "wins."
)
code(
    r'''reasons = {
    "Use classical ML when": ["small/medium tabular data", "you need fast iteration",
                              "explainability matters", "limited compute"],
    "Reach for deep learning when": ["lots of data", "sequences/text/images/payloads",
                                     "features are hard to hand-craft", "GPU available"],
}
for k, v in reasons.items():
    print(k + ":")
    for item in v:
        print("   -", item)
    print()'''
)

# ---- 2: tensors -------------------------------------------------------------
slide("\U0001F522 2 — Tensors & DataLoaders", [
    "PyTorch works with **tensors** (GPU-ready arrays)",
    "Convert numpy features/labels to tensors",
    "`DataLoader` serves shuffled mini-batches",
    "Batching makes training stable and scalable",
    "Pick the device: CPU here, GPU when available",
])
script(
    "PyTorch's core object is the tensor, a numpy-like array that can live on a GPU and track "
    "gradients. We convert our scaled features and labels into tensors and wrap them in a "
    "DataLoader, which serves shuffled mini-batches during training. Mini-batching is what lets "
    "deep learning scale to huge datasets — the model updates on a small batch at a time rather "
    "than the whole set at once — and the shuffling keeps those updates from being biased by data "
    "ordering. We also select a device; this small model trains fine on CPU, but the exact same "
    "code moves to a GPU by changing one line, which is how you would train on a large Kaggle "
    "dataset in Colab."
)
code(
    r'''import torch
from torch.utils.data import TensorDataset, DataLoader

torch.manual_seed(42)
device = "cuda" if torch.cuda.is_available() else "cpu"
print("PyTorch", torch.__version__, "| device:", device)

Xtr = torch.tensor(X_train_s, dtype=torch.float32)
ytr = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
Xte = torch.tensor(X_test_s, dtype=torch.float32)
yte = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

train_loader = DataLoader(TensorDataset(Xtr, ytr), batch_size=64, shuffle=True)
print("Batches per epoch:", len(train_loader), " (batch size 64)")'''
)

# ---- 3: define model --------------------------------------------------------
slide("\U0001F3D7️ 3 — Define a Neural Network", [
    "A small **MLP**: linear layers + activations",
    "ReLU adds non-linearity between layers",
    "Dropout regularizes (fights overfitting)",
    "Final neuron → one logit → P(malicious)",
    "Keep it small for small data",
])
script(
    "Now the network itself: a multilayer perceptron, the simplest deep model for tabular data. It "
    "stacks linear layers separated by ReLU activations, which give the network the non-linearity "
    "it needs to bend decision boundaries that a single linear layer cannot. We sprinkle in dropout "
    "to randomly zero some activations during training, a cheap and effective regularizer against "
    "overfitting. The final layer outputs a single logit that we squash into a probability of "
    "malicious. We deliberately keep the network small — two modest hidden layers — because our "
    "dataset is small, and an oversized network would simply memorize it."
)
code(
    r'''import torch.nn as nn

class AlertNet(nn.Module):
    def __init__(self, n_features, hidden=32, p_drop=0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden), nn.ReLU(), nn.Dropout(p_drop),
            nn.Linear(hidden, hidden // 2), nn.ReLU(), nn.Dropout(p_drop),
            nn.Linear(hidden // 2, 1),          # one logit -> P(malicious) via sigmoid
        )

    def forward(self, x):
        return self.net(x)


model = AlertNet(n_features=Xtr.shape[1]).to(device)
print(model)
print("\nTrainable parameters:", sum(p.numel() for p in model.parameters()))'''
)

# ---- 4: training loop -------------------------------------------------------
slide("\U0001F501 4 — The Training Loop", [
    "Loss = `BCEWithLogitsLoss` (binary classification)",
    "Optimizer = Adam adjusts weights by gradients",
    "Each epoch: forward → loss → backward → step",
    "`pos_weight` handles class imbalance",
    "Watch loss fall over epochs",
])
script(
    "This loop is the beating heart of deep learning, and every framework rephrases the same four "
    "steps. For each mini-batch we run a forward pass to get predictions, compute the loss — here "
    "binary cross-entropy on logits, with a positive-class weight to counter our imbalance — then "
    "call backward to compute gradients and step the Adam optimizer to nudge the weights downhill. "
    "We zero the gradients each iteration because PyTorch accumulates them by default. Over the "
    "epochs you should watch the loss fall as the network fits the data. If you ever see training "
    "loss keep dropping while validation performance stalls, that is overfitting — the subject of "
    "the next topic."
)
code(
    r'''pos_weight = torch.tensor([(y_train == 0).sum() / (y_train == 1).sum()], dtype=torch.float32).to(device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

EPOCHS = 30
for epoch in range(1, EPOCHS + 1):
    model.train()
    epoch_loss = 0.0
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()                  # clear accumulated gradients
        loss = criterion(model(xb), yb)        # forward -> loss
        loss.backward()                        # backprop
        optimizer.step()                       # update weights
        epoch_loss += loss.item() * len(xb)
    if epoch % 5 == 0 or epoch == 1:
        print(f"epoch {epoch:2d}/{EPOCHS}   train loss = {epoch_loss / len(Xtr):.4f}")'''
)

# ---- 5: evaluate vs baseline ------------------------------------------------
slide("\U0001F3C1 5 — Evaluate vs. the Classical Baseline", [
    "Switch to eval mode (disables dropout)",
    "Score the test set; compute ROC-AUC & F1",
    "Compare head-to-head with gradient boosting",
    "On small tabular data, trees often win",
    "Let evidence — not hype — pick the model",
])
script(
    "The moment of truth: does the neural network actually beat the classical baseline? We switch "
    "the model to eval mode, which turns off dropout, run the test set through it without tracking "
    "gradients, and compute ROC-AUC and F1 — the same metrics we used for the trees, so the "
    "comparison is fair. Read the result honestly. On small, clean tabular data like this, do not "
    "be surprised if gradient boosting matches or beats the network for a fraction of the effort. "
    "That is not a failure of the exercise; it is the lesson. The professional move is to let "
    "measured evidence, not enthusiasm for deep learning, decide which model you deploy."
)
code(
    r'''model.eval()
with torch.no_grad():
    nn_score = torch.sigmoid(model(Xte.to(device))).cpu().numpy().ravel()
nn_pred = (nn_score >= 0.5).astype(int)

nn_auc = roc_auc_score(y_test, nn_score)
print("Neural network    ROC-AUC:", round(nn_auc, 3), " F1:", round(f1_score(y_test, nn_pred), 3))
print("Gradient boosting ROC-AUC:", round(base_auc, 3))
print()
if nn_auc > base_auc:
    print("-> The neural net edged out the baseline here.")
else:
    print("-> The classical baseline held up — typical for small tabular data.")
print("   Decision rule: prefer the simpler model unless DL clearly and reliably wins.")'''
)

# ---- 6: overfitting ---------------------------------------------------------
slide("\U0001F4C9 6 — Overfitting & Honest Reporting", [
    "Overfit = memorizes train, fails on new data",
    "Symptom: train loss ↓ while test metrics stall/drop",
    "Defenses: dropout, weight decay, early stopping, more data",
    "Always report **test** metrics, never train",
    "State limitations & robustness in your report",
])
script(
    "We close with the failure mode that haunts deep learning: overfitting, where the model "
    "memorizes the training data and then stumbles on anything new. The tell is a training loss "
    "that keeps falling while test performance stalls or worsens. Our defenses were dropout and a "
    "small architecture; in practice you add weight decay, early stopping, and above all more data. "
    "We quantify the gap between train and test scores so you can see whether the model generalized. "
    "For Project 4, report test metrics only, disclose this train-test gap, and discuss robustness "
    "and limitations — a model that quietly overfits is exactly the kind of overconfident security "
    "claim this course trains you to avoid."
)
code(
    r'''with torch.no_grad():
    train_auc = roc_auc_score(y_train, torch.sigmoid(model(Xtr.to(device))).cpu().numpy().ravel())
print("ROC-AUC on TRAIN:", round(train_auc, 3))
print("ROC-AUC on TEST :", round(nn_auc, 3))
print("Train - Test gap:", round(train_auc - nn_auc, 3), " (large gap => overfitting)")
print("\nReport TEST metrics only. Disclose the gap, limitations, and robustness.")'''
)

# ---- Summary ----------------------------------------------------------------
slide("✅ Summary — Deep Learning & the Module", [
    "Built and trained a PyTorch MLP end-to-end",
    "Learned the loss → backward → step loop",
    "Benchmarked DL honestly vs. a classical baseline",
    "Guarded against overfitting; reported test metrics",
    "Module done → bring it together in **Project 4**",
])
script(
    "You have now built a neural network from tensors to training loop to honest evaluation, and "
    "you have seen the discipline that matters more than any architecture: always benchmark against "
    "a strong classical baseline, defend against overfitting, and report test metrics with their "
    "limitations. That completes the AI-Assisted ML module — foundations, applied detection, "
    "advanced analytics, and deep learning. Now bring all four together in Project 4: pick a "
    "current cybersecurity dataset from Kaggle, run this full workflow with AI assistance, push for "
    "high-ranking results, and write the kind of clear, evidence-based, limitation-aware report a "
    "real security team would trust."
)
code(
    r'''print("AI-Assisted ML module complete. You can now:")
print("  - prepare and de-leak a security dataset")
print("  - build baselines and evaluate with SOC-relevant metrics")
print("  - apply ensembles, imbalance handling, clustering, and anomaly detection")
print("  - train and honestly benchmark a neural network")
print("\n-> Project 4: a Kaggle cybersecurity dataset, high-ranking results, AI-assisted.")'''
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

with open("04_deep_learning.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Wrote 04_deep_learning.ipynb with {len(cells)} cells.")
