import math
import matplotlib.pyplot as plt
import numpy as np


def _score_solubility(val: float) -> float:
    x = max(-10, min(2, val))
    return (x + 10) / 12


def _score_caco2(val: float) -> float:
    return max(0, min(1, val))


def _score_herg(val: float) -> float:
    return 1 - max(0, min(1, val))


def _score_lipophilicity(val: float) -> float:
    return max(0, 1 - abs(val - 2) / 4)


def _score_pgp(val: float) -> float:
    return 1 - max(0, min(1, val))


def _score_cyp(val: float) -> float:
    return 1 - max(0, min(1, val))


def _score_ames(val: float) -> float:
    return 1 - max(0, min(1, val))


def _score_bioavailability(val: float) -> float:
    return max(0, min(1, val))


def _score_ppbr(val: float) -> float:
    return max(0, min(1, val / 100))


RADAR_CONFIG = [
    ("Solubility (logS)", _score_solubility),
    ("Caco-2 Permeability", _score_caco2),
    ("hERG Safety", _score_herg),
    ("Lipophilicity (logD)", _score_lipophilicity),
    ("P-gp Safety", _score_pgp),
    ("CYP3A4 Safety", _score_cyp),
    ("CYP2D6 Safety", _score_cyp),
    ("Ames Safety", _score_ames),
    ("Bioavailability", _score_bioavailability),
    ("PPB (plasma binding)", _score_ppbr),
]


SOURCE_KEYS = [
    "Solubility (logS)",
    "Caco-2 Permeability",
    "hERG Toxicity Risk",
    "Lipophilicity (logD)",
    "P-gp Inhibition",
    "CYP3A4 Inhibition",
    "CYP2D6 Inhibition",
    "Ames Mutagenicity",
    "Bioavailability",
    "PPB (plasma binding)",
]

LABEL_KEYS_EN = [
    "Solubility",
    "Caco-2\nPermeability",
    "hERG Safety",
    "Lipophilicity",
    "P-gp Safety",
    "CYP3A4\nSafety",
    "CYP2D6\nSafety",
    "Ames Safety",
    "Bioavailability",
    "PPB Binding",
]

LABEL_KEYS_RU = [
    "Растворимость",
    "Caco-2\nпроницаемость",
    "hERG\nбезопасность",
    "Липофильность",
    "P-gp\nбезопасность",
    "CYP3A4\nбезопасность",
    "CYP2D6\nбезопасность",
    "Ames\nбезопасность",
    "Биодоступность",
    "Связ. с\nбелками",
]


def compute_scores(result: dict) -> list[float]:
    scores = []
    for source_key, scorer in zip(SOURCE_KEYS, [cfg[1] for cfg in RADAR_CONFIG]):
        val = result.get(source_key)
        if val is None or not isinstance(val, (int, float)) or math.isnan(val):
            scores.append(0)
        else:
            scores.append(scorer(val))
    return scores


def plot_radar(scores: list[float], lang: str = "ru") -> plt.Figure:
    n = len(scores)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    vals = scores + scores[:1]
    labels = LABEL_KEYS_RU if lang == "ru" else LABEL_KEYS_EN

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75])
    ax.set_yticklabels(["0.25", "0.5", "0.75"], fontsize=8)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)

    ax.plot(angles, vals, "o-", linewidth=2, color="#1f77b4")
    ax.fill(angles, vals, alpha=0.15, color="#1f77b4")

    fig.tight_layout()
    return fig
