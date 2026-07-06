import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.train import train_all_models

if __name__ == "__main__":
    results = train_all_models()
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)
    for key, metrics in results.items():
        print(f"\n{key.upper()}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
