"""
CertiNexus AI — EDA (Exploratory Data Analysis)

Generates dataset statistics, class distribution, text analysis,
and saves results as JSON + figures for the web dashboard.
"""

import json
import os
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "processed", "cleaned_dataset.csv")
EDA_DIR = os.path.join(BASE_DIR, "ml", "evaluation", "eda")
FIGURES_DIR = os.path.join(BASE_DIR, "ml", "evaluation", "figures")

os.makedirs(EDA_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


def run_eda():
    """Run full EDA and save results."""
    print("=" * 60)
    print("CertiNexus AI — Exploratory Data Analysis")
    print("=" * 60)

    df = pd.read_csv(DATASET_PATH)
    text_col = 'clean_text' if 'clean_text' in df.columns else 'raw_text'

    print(f"\n  Dataset shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")

    # ---- 1. Basic Statistics ----
    stats = {
        "total_samples": len(df),
        "total_categories": df['category'].nunique(),
        "categories": sorted(df['category'].unique().tolist()),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_texts": int(df[text_col].duplicated().sum()),
    }

    # ---- 2. Class Distribution ----
    class_dist = df['category'].value_counts().to_dict()
    class_dist_sorted = dict(sorted(class_dist.items()))
    stats["class_distribution"] = class_dist_sorted

    # Imbalance ratio
    max_count = max(class_dist.values())
    min_count = min(class_dist.values())
    stats["imbalance_ratio"] = round(max_count / min_count, 2) if min_count > 0 else float('inf')
    stats["majority_class"] = max(class_dist, key=class_dist.get)
    stats["minority_class"] = min(class_dist, key=class_dist.get)

    print(f"\n  Class distribution:")
    for cat, count in sorted(class_dist.items()):
        bar = '*' * (count // 2)
        print(f"    {cat:25s}: {count:4d} {bar}")

    # ---- 3. Text Length Analysis ----
    df['text_length'] = df[text_col].fillna('').str.len()
    df['word_count'] = df[text_col].fillna('').str.split().str.len()

    text_stats = {
        "text_length": {
            "mean": round(df['text_length'].mean(), 1),
            "median": round(df['text_length'].median(), 1),
            "std": round(df['text_length'].std(), 1),
            "min": int(df['text_length'].min()),
            "max": int(df['text_length'].max()),
        },
        "word_count": {
            "mean": round(df['word_count'].mean(), 1),
            "median": round(df['word_count'].median(), 1),
            "std": round(df['word_count'].std(), 1),
            "min": int(df['word_count'].min()),
            "max": int(df['word_count'].max()),
        },
    }
    stats["text_statistics"] = text_stats

    # Per-category text length
    per_cat_text_len = {}
    for cat in df['category'].unique():
        cat_df = df[df['category'] == cat]
        per_cat_text_len[cat] = {
            "mean_text_length": round(cat_df['text_length'].mean(), 1),
            "mean_word_count": round(cat_df['word_count'].mean(), 1),
        }
    stats["per_category_text_stats"] = per_cat_text_len

    print(f"\n  Text length: mean={text_stats['text_length']['mean']}, "
          f"median={text_stats['text_length']['median']}")
    print(f"  Word count: mean={text_stats['word_count']['mean']}, "
          f"median={text_stats['word_count']['median']}")

    # ---- 4. Vocabulary Analysis ----
    all_text = ' '.join(df[text_col].fillna('').tolist())
    all_words = all_text.lower().split()
    word_freq = Counter(all_words)

    # Common stopwords to exclude from "top terms"
    STOPWORDS = {
        'the', 'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'and', 'but', 'or', 'nor', 'not',
        'so', 'yet', 'both', 'either', 'neither', 'each', 'every', 'all',
        'this', 'that', 'these', 'those', 'it', 'its', 'he', 'she', 'they',
        'them', 'their', 'we', 'you', 'i', 'me', 'my', 'your', 'his', 'her',
        'our', 'us', 'who', 'whom', 'which', 'what', 'where', 'when', 'how'
    }

    meaningful_words = {w: c for w, c in word_freq.items()
                       if w not in STOPWORDS and len(w) > 2}

    vocab_stats = {
        "total_tokens": len(all_words),
        "unique_tokens": len(word_freq),
        "vocabulary_richness": round(len(word_freq) / len(all_words), 4) if all_words else 0,
        "top_30_terms": dict(Counter(meaningful_words).most_common(30)),
    }
    stats["vocabulary"] = vocab_stats

    # Top terms per category
    top_terms_per_category = {}
    for cat in df['category'].unique():
        cat_text = ' '.join(df[df['category'] == cat][text_col].fillna('').tolist())
        cat_words = cat_text.lower().split()
        cat_freq = Counter(w for w in cat_words if w not in STOPWORDS and len(w) > 2)
        top_terms_per_category[cat] = dict(cat_freq.most_common(15))
    stats["top_terms_per_category"] = top_terms_per_category

    print(f"\n  Vocabulary size: {vocab_stats['unique_tokens']}")
    print(f"  Total tokens: {vocab_stats['total_tokens']}")

    # ---- 5. Source Distribution ----
    if 'source' in df.columns:
        stats["source_distribution"] = df['source'].value_counts().to_dict()

    # ---- Save EDA Results ----
    eda_path = os.path.join(EDA_DIR, "eda_results.json")
    with open(eda_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"\n  EDA results saved to {eda_path}")

    # ---- Generate Figures ----
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns

        # 1. Class distribution bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        cats = sorted(class_dist.keys())
        counts = [class_dist[c] for c in cats]
        bars = ax.barh(cats, counts, color=plt.cm.Set3(np.linspace(0, 1, len(cats))))
        ax.set_xlabel('Count')
        ax.set_title('Class Distribution')
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    str(count), va='center', fontsize=10)
        plt.tight_layout()
        fig.savefig(os.path.join(FIGURES_DIR, "class_distribution.png"), dpi=150)
        plt.close()
        print("  Saved class_distribution.png")

        # 2. Text length distribution histogram
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        axes[0].hist(df['text_length'], bins=30, color='steelblue', edgecolor='white', alpha=0.8)
        axes[0].set_xlabel('Character Count')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Text Length Distribution')

        axes[1].hist(df['word_count'], bins=30, color='coral', edgecolor='white', alpha=0.8)
        axes[1].set_xlabel('Word Count')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Word Count Distribution')
        plt.tight_layout()
        fig.savefig(os.path.join(FIGURES_DIR, "text_length_distribution.png"), dpi=150)
        plt.close()
        print("  Saved text_length_distribution.png")

        # 3. Text length by category (boxplot)
        fig, ax = plt.subplots(figsize=(14, 6))
        df.boxplot(column='word_count', by='category', ax=ax, rot=45)
        ax.set_title('Word Count by Category')
        ax.set_xlabel('Category')
        ax.set_ylabel('Word Count')
        plt.suptitle('')
        plt.tight_layout()
        fig.savefig(os.path.join(FIGURES_DIR, "word_count_by_category.png"), dpi=150)
        plt.close()
        print("  Saved word_count_by_category.png")

        # 4. Top terms bar chart
        top_terms = Counter(meaningful_words).most_common(20)
        words, freqs = zip(*top_terms) if top_terms else ([], [])
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(list(reversed(words)), list(reversed(freqs)), color='mediumpurple')
        ax.set_xlabel('Frequency')
        ax.set_title('Top 20 Terms (Excluding Stopwords)')
        plt.tight_layout()
        fig.savefig(os.path.join(FIGURES_DIR, "top_terms.png"), dpi=150)
        plt.close()
        print("  Saved top_terms.png")

        print("\n✓ All EDA figures generated!")

    except ImportError:
        print("  matplotlib/seaborn not available, skipping figures")

    return stats


if __name__ == "__main__":
    run_eda()
