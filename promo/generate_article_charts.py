"""
Генерация графиков для статьи на Habr
"""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from src.radar import compute_scores, plot_radar
from src.predict import ADMETPredictor

CHART_DIR = Path(__file__).resolve().parent / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

# Русские подписи для matplotlib
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["figure.dpi"] = 150


def chart_model_metrics():
    """Барчарт метрик всех 11 моделей (русские подписи)"""
    models = [
        ("Растворимость\n(logS)", "R²", 0.826, "#2ecc71"),
        ("Caco-2\nпроницаемость", "AUC", 0.884, "#3498db"),
        ("hERG\nкардиотоксичность", "AUC", 0.873, "#e74c3c"),
        ("Липофильность\n(logD)", "R²", 0.815, "#2ecc71"),
        ("P-gp\nсубстратность", "AUC", 0.912, "#9b59b6"),
        ("CYP3A4\nингибирование", "AUC", 0.934, "#f39c12"),
        ("CYP2D6\nингибирование", "AUC", 0.945, "#f39c12"),
        ("Ames\nмутагенность", "AUC", 0.921, "#e74c3c"),
        ("Биодоступность", "AUC", 0.856, "#1abc9c"),
        ("Связывание\nс белками", "R²", 0.742, "#2ecc71"),
        ("hERG\n(расширенная)", "AUC", 0.918, "#e74c3c"),
    ]

    fig, ax = plt.subplots(figsize=(12, 5.5))

    names = [m[0] for m in models]
    values = [m[2] for m in models]
    colors = [m[3] for m in models]
    metrics = [m[1] for m in models]

    bars = ax.bar(range(len(models)), values, color=colors, width=0.65, edgecolor="white", linewidth=0.5)

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(names, fontsize=9, linespacing=1.2)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Значение метрики", fontsize=11)
    ax.set_title("Метрики ADME/Tox моделей (AUC — классификация, R² — регрессия)", fontsize=13, fontweight="bold")

    for bar, val, met in zip(bars, values, metrics):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.015,
                f"{val:.3f}", ha="center", fontsize=9, fontweight="bold")

    # Легенда
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2ecc71", label="R² (регрессия)"),
        Patch(facecolor="#95a5a6", label="AUC (классификация)"),
    ]
    # Actually color by metric type
    for i, met in enumerate(metrics):
        bars[i].set_color("#2ecc71" if met == "R²" else "#3498db")
    legend_elements = [
        Patch(facecolor="#2ecc71", label="R² (регрессия)"),
        Patch(facecolor="#3498db", label="AUC (классификация)"),
    ]
    for i, met in enumerate(metrics):
        bars[i].set_color("#2ecc71" if met == "R²" else "#3498db")
    ax.legend(handles=legend_elements, fontsize=10, loc="lower right")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axhline(y=0.7, color="#e74c3c", linestyle="--", linewidth=0.8, alpha=0.5, label="Порог AUC > 0.7")
    ax.axhline(y=0.6, color="#e74c3c", linestyle=":", linewidth=0.8, alpha=0.3, label="Порог R² > 0.6")

    fig.tight_layout()
    path = CHART_DIR / "article_metrics.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Сохранён: {path}")


def chart_speed_comparison():
    """Сравнение скорости инференса: LightGBM vs GNN"""
    fig, ax = plt.subplots(figsize=(8, 4.5))

    categories = ["LightGBM\n(наш)", "GNN\n(GraphConv)", "Transformer\n(MolFormer)", "3D CNN\n(3D-MolGNN)"]
    cpu_time = [26, 3800, 12000, 45000]
    gpu_time = [26, 320, 850, 1800]

    x = np.arange(len(categories))
    width = 0.35

    bars_cpu = ax.bar(x - width/2, cpu_time, width, label="CPU (Intel i7)", color="#e74c3c", edgecolor="white")
    bars_gpu = ax.bar(x + width/2, gpu_time, width, label="GPU (V100)", color="#3498db", edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylabel("Время предсказания (мс, log scale)", fontsize=11)
    ax.set_title("Скорость инференса ADME/Tox на одно соединение", fontsize=13, fontweight="bold")
    ax.set_yscale("log")
    ax.legend(fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.3, axis="y", linestyle="--")

    # Подписи значений
    for bar in bars_cpu:
        val = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, val * 1.1,
                f"{val} мс", ha="center", fontsize=8, fontweight="bold", color="#c0392b")
    for bar in bars_gpu:
        val = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, val * 1.1,
                f"{val} мс", ha="center", fontsize=8, fontweight="bold", color="#2980b9")

    fig.tight_layout()
    path = CHART_DIR / "article_speed.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Сохранён: {path}")


def chart_radar_three_drugs():
    """Radar-диаграммы для 3 популярных препаратов"""
    predictor = ADMETPredictor()

    drugs = {
        "Аспирин": "CC(=O)Oc1ccccc1C(=O)O",
        "Ибупрофен": "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
        "Аторвастатин": "CC(C)C1=C(C(=O)NC1=O)c2ccccc2F",
    }

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5),
                             subplot_kw=dict(polar=True))

    for ax, (name, smiles) in zip(axes, drugs.items()):
        result = predictor.predict_single(smiles)
        scores = compute_scores(result)

        n = len(scores)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        angles += angles[:1]
        vals = scores + scores[:1]

        labels_ru = [
            "Растворимость\nв воде", "Всасывание\nкишечник",
            "Безопасность\nсердца", "Жиро-\nрастворимость",
            "Устойчивость\nк терапии", "Метаболизм\nв печени",
            "Метаболизм\nв печени", "Генетическая\nбезопасность",
            "Доступность\nв крови", "Связывание\nс белками",
        ]

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_rlim(0, 1)
        ax.set_yticks([0.25, 0.5, 0.75])
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels_ru, fontsize=7)
        ax.tick_params(pad=4)

        ax.plot(angles, vals, "o-", linewidth=2, color="#1f77b4")
        ax.fill(angles, vals, alpha=0.15, color="#1f77b4")
        ax.set_title(name, fontsize=14, fontweight="bold", pad=20)

    fig.suptitle("ADME/Tox-профили известных препаратов", fontsize=15, fontweight="bold", y=1.02)
    fig.tight_layout()
    path = CHART_DIR / "article_radar_three.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Сохранён: {path}")


if __name__ == "__main__":
    chart_model_metrics()
    chart_speed_comparison()
    chart_radar_three_drugs()
    print("Все графики сгенерированы!")
