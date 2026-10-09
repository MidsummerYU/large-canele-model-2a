from pathlib import Path

import matplotlib
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator, NullFormatter

SURFACE, INK, INK_SECONDARY, MUTED, GRID, BASELINE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = ("#2a78d6", "#eb6834")
GRADE_COLOURS = {"correct": "#2a78d6", "incorrect": "#eb6834", "not_attempted": "#c3c2b7"}

STYLE = {
    # Bundled with matplotlib, so the SVGs come out identical on every machine.
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "svg.hashsalt": "booklet-nli",
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SECONDARY,
    "axes.titlesize": 9,
    "axes.titlecolor": INK,
    "axes.titlelocation": "left",
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_SECONDARY,
    "ytick.labelcolor": INK_SECONDARY,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": GRID,
    "grid.linewidth": 0.5,
    "legend.frameon": False,
}



def tradeoff(scores: dict[str, dict], split: str, path: Path) -> None:
    """Macro-F1 against mean input tokens per claim for the advanced runs, with the beginner score for reference."""

    def point(key: str) -> tuple[float, float]:
        s = scores[key]["all"]["all"]
        return s["input_tokens"] / s["n"], s["macro_f1"]

    fig = Figure(figsize=(6.6, 2.8), layout="constrained")
    ax = fig.subplots()
    curve = sorted(
        (k for k in scores if k.startswith("8B/advanced-") and k.endswith(f"-advanced-{split}")), key=lambda k: point(k)[0]
    )
    xs, ys = zip(*(point(k) for k in curve))
    ax.plot(xs, ys, color=SERIES[0], linewidth=2, marker="o", markersize=6, markeredgecolor=SURFACE, label="8B, retrieved pages and whole booklet")
    for key, x, y in zip(curve, xs, ys):
        context = key.split("-")[1]
        ax.annotate("whole booklet" if context == "full" else f"{context[1:]} pages", (x, y), textcoords="offset points", xytext=(6, -10), fontsize=7, color=INK_SECONDARY)
    others = [k for k in scores if k.startswith(("8B/advanced-", "70B/advanced-")) and k not in curve and k.endswith(f"-{split}")]
    for key in others:
        x, y = point(key)
        model, prompt = key.split("/")[0], key.rsplit("-", 2)[-2]
        ax.scatter(x, y, s=40, color=SERIES[1] if model == "70B" else SERIES[0], marker="D" if prompt.endswith("v2") else "s",
                   edgecolors=SURFACE, linewidths=1, zorder=3, label=f"{model}, 3 pages, {'point-by-point prompt' if prompt.endswith('v2') else 'base prompt'}")
    beginner = scores.get(f"8B/beginner-{split}")
    if beginner:
        ax.axhline(beginner["all"]["all"]["macro_f1"], color=BASELINE, linewidth=1, linestyle=(0, (4, 3)))
        ax.annotate("8B, gold passage given (beginner)", (xs[0], beginner["all"]["all"]["macro_f1"]), textcoords="offset points", xytext=(0, 4), fontsize=7, color=INK_SECONDARY)
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(FixedLocator([1000, 3000, 10000, 30000]))
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:,.0f}")
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("mean input tokens per claim (log scale)")
    ax.set_ylabel("macro-F1")
    ax.set_ylim(0.5, 1.0)
    ax.legend(loc="lower left", fontsize=7)
    fig.savefig(path, metadata={"Date": None})


def write_figures(scores: dict[str, dict], split: str, figures_dir: Path) -> list[Path]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    path = figures_dir / f"tradeoff_{split}.svg"
    with matplotlib.rc_context(STYLE):
        tradeoff(scores, split, path)
    return [path]
