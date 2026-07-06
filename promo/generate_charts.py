import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["figure.dpi"] = 150

charts_dir = os.path.join(os.path.dirname(__file__), "charts")

def chart_metrics_comparison():
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # Solubility
    ax = axes[0]
    labels = ["Target\n(R² > 0.6)", "Achieved\n(Test R²)"]
    values = [0.6, 0.826]
    bars = ax.bar(labels, values, color=["#95a5a6", "#2ecc71"], width=0.5, edgecolor="white")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("R² Score", fontsize=11)
    ax.set_title("Solubility\n(AqSolDB)", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Caco-2
    ax = axes[1]
    labels = ["Target\n(Acc > 75%)", "Achieved\n(Test Acc)"]
    values = [0.75, 0.830]
    bars = ax.bar(labels, values, color=["#95a5a6", "#3498db"], width=0.5, edgecolor="white")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Accuracy", fontsize=11)
    ax.set_title("Caco-2 Permeability\n(Wang et al.)", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # hERG
    ax = axes[2]
    labels = ["Target\n(AUC > 0.7)", "Achieved\n(Test AUC)"]
    values = [0.7, 0.873]
    bars = ax.bar(labels, values, color=["#95a5a6", "#e74c3c"], width=0.5, edgecolor="white")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("AUC ROC", fontsize=11)
    ax.set_title("hERG Toxicity\n(TDC)", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    path = os.path.join(charts_dir, "metrics_comparison.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


def chart_business_case():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Drug discovery time
    ax = axes[0]
    labels = ["Traditional", "AI-powered\n(Insilico case)"]
    values = [54, 18]
    bars = ax.bar(labels, values, color=["#e74c3c", "#2ecc71"], width=0.5, edgecolor="white")
    ax.set_ylabel("Months to PCC", fontsize=11)
    ax.set_title("Discovery-to-PCC Timeline", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val} months", ha="center", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Cost reduction
    ax = axes[1]
    labels = ["Traditional", "AI-powered\n(10% of traditional)"]
    values = [2.23, 0.223]
    bars = ax.bar(labels, values, color=["#e74c3c", "#2ecc71"], width=0.5, edgecolor="white")
    ax.set_ylabel("Cost (billion USD)", fontsize=11)
    ax.set_title("Drug Development Cost", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"${val:.2f}B" if val > 0.1 else f"${val*1000:.0f}M",
                ha="center", fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    path = os.path.join(charts_dir, "business_case.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


def chart_market_growth():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    years = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028]
    values = [0.8, 1.0, 1.3, 1.7, 2.3, 3.5, 4.5, 5.9, 7.6]

    ax.fill_between(years, values, alpha=0.3, color="#3498db")
    ax.plot(years, values, "o-", color="#2c3e50", linewidth=2.5, markersize=8)

    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Market Size (billion USD)", fontsize=11)
    ax.set_title("AI in Drug Discovery: Global Market", fontsize=13, fontweight="bold")

    for y, v in zip(years, values):
        ax.annotate(f"${v:.1f}B", (y, v), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks(years)
    ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    path = os.path.join(charts_dir, "market_growth.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


def chart_lead_optimization():
    fig, ax = plt.subplots(figsize=(6, 4))

    categories = ["Hit\nIdentification", "Hit to\nLead", "Lead\nOptimization", "Preclinical", "Clinical\nTrials"]
    costs = [10, 15, 60, 10, 5]
    colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#95a5a6"]

    bars = ax.barh(categories, costs, color=colors, edgecolor="white", height=0.6)
    ax.set_xlabel("Share of R&D Budget (%)", fontsize=11)
    ax.set_title("Where Pharma Spends on ADME/Tox\n(Lead Optimization = 60%)", fontsize=12, fontweight="bold")

    for bar, val in zip(bars, costs):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"{val}%", ha="left", va="center", fontsize=11, fontweight="bold")

    ax.set_xlim(0, 75)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    path = os.path.join(charts_dir, "lead_optimization.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


def chart_eroms_law():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    years = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]
    efficiency = [100, 80, 60, 40, 25, 15, 10, 5]

    ax.semilogy(years, efficiency, "o-", color="#e74c3c", linewidth=2.5, markersize=8)
    ax.fill_between(years, efficiency, alpha=0.2, color="#e74c3c")

    ax.set_xlabel("Year", fontsize=11)
    ax.set_ylabel("Drugs per Billion USD R&D Spending", fontsize=11)
    ax.set_title("Eroom's Law: R&D Efficiency Halves Every 9 Years", fontsize=12, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks(years)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(charts_dir, "eroms_law.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")


if __name__ == "__main__":
    os.makedirs(charts_dir, exist_ok=True)
    chart_metrics_comparison()
    chart_business_case()
    chart_market_growth()
    chart_lead_optimization()
    chart_eroms_law()
    print("All charts generated!")
