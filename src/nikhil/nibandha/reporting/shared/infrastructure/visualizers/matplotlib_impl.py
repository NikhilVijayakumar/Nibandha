import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from ...domain.grading import GradingThresholds

# Optional dependencies
try:
    import seaborn as sns # type: ignore
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import pandas as pd # type: ignore
    import numpy as np
except ImportError:
    sns = None
    plt = None # type: ignore
    pd = None
    np = None # type: ignore

try:
    import networkx as nx # type: ignore
    HAS_NETWORKX = True
except ImportError:
    nx = None
    HAS_NETWORKX = False

logger = logging.getLogger("nibandha.reporting")

def _check_dependencies() -> bool:
    if not (sns and plt and pd):
        logger.warning("Visualization libraries (seaborn, matplotlib, pandas) not installed. Skipping plots.")
        return False
    return True

def setup_style() -> None:
    """Set the aesthetic style of the plots."""
    if not _check_dependencies(): return
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams["figure.figsize"] = (12, 7)
    plt.rcParams["font.size"] = 12
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10

def _save_plot(output_path: Path, title: str, tight: bool = True) -> None:
    """Helper to save consistent plots."""
    if plt:
        plt.title(title, pad=20, fontsize=16, fontweight='bold')
        if tight:
            plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.debug(f"Saved plot: {output_path}")
        plt.close()

def plot_module_outcomes(module_data: Dict[str, Any], output_path: Path) -> None:
    """Generate a stacked bar chart of Pass/Fail/Error counts per module with Pass Rate overlay."""
    if not _check_dependencies(): return
    setup_style()
    
    data_list = []
    for mod, counts in module_data.items():
        total = counts.get("total", 0)
        # Avoid cluttering with empty modules
        if total == 0: continue
            
        data_list.append({"Module": mod, "Outcome": "Pass", "Count": counts.get("pass", 0)})
        data_list.append({"Module": mod, "Outcome": "Fail", "Count": counts.get("fail", 0)})
        data_list.append({"Module": mod, "Outcome": "Error", "Count": counts.get("error", 0)})
        
    df = pd.DataFrame(data_list)
    if df.empty: return

    # Pivot for stacked bar
    try:
        df_pivot = df.pivot(index="Module", columns="Outcome", values="Count")
    except ValueError:
        return

    # Ensure columns exist and order them
    cols = [c for c in ["Pass", "Fail", "Error"] if c in df_pivot.columns]
    df_pivot = df_pivot[cols]
    
    # Calculate Total and Pass Rate for sorting/overlay
    df_pivot["Total"] = df_pivot.sum(axis=1)
    df_pivot["PassRate"] = (df_pivot.get("Pass", 0) / df_pivot["Total"]) * 100
    df_pivot = df_pivot.sort_values("Total", ascending=False)
    
    # Create figure with secondary axis
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    colors = {"Pass": "#2ecc71", "Fail": "#e74c3c", "Error": "#f1c40f"}
    custom_palette = [colors[c] for c in cols]
    
    # 1. Stacked Bar Chart (Counts)
    df_pivot[cols].plot(kind="bar", stacked=True, color=custom_palette, width=0.7, ax=ax1)
    ax1.set_ylabel("Test Count")
    ax1.set_xlabel("Module")
    ax1.legend(loc="upper left", title="Outcome")
    
    # 2. Line Chart (Pass Rate)
    ax2 = ax1.twinx()
    sns.lineplot(data=df_pivot, x=df_pivot.index, y="PassRate", color="#2c3e50", marker="o", linewidth=2, ax=ax2, label="Pass Rate (%)")
    ax2.set_ylabel("Pass Rate (%)")
    ax2.set_ylim(0, 105) # Little buffer above 100
    ax2.grid(False) # Turn off grid for secondary axis to avoid clutter
    
    # Check if pass rate line is constant 100%, if so annotation might overlap.
    # Add simple annotation for low pass rates
    for i, rate in enumerate(df_pivot["PassRate"]):
        if rate < 90:
            ax2.annotate(f"{rate:.1f}%", (i, rate), xytext=(0, -15), textcoords="offset points", ha='center', color="#c0392b", fontweight='bold')
    
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
    
    _save_plot(output_path, "Module Test Outcomes & Pass Rate Analysis")

def plot_coverage(module_data: Dict[str, float], output_path: Path) -> None:
    """Generate a bar chart for coverage percentage per module with Threshold lines."""
    if not _check_dependencies(): return
    setup_style()
    
    df = pd.DataFrame(list(module_data.items()), columns=["Module", "Coverage"])
    if df.empty: return
    
    # Sort by coverage ascending (lowest coverage first is most important for decision making)
    df = df.sort_values("Coverage", ascending=True)

    plt.figure(figsize=(14, 8)) # Wider
    
    # Define Color Logic based on thresholds (Updated)
    # < 75% -> Red (Fail)
    # 75-85 -> Yellow (C)
    # 85-90 -> Blue (B) - wait, let's keep simple traffic light or 4 colors?
    # Simple traffic light is better for "Risk":
    # < 75: Red
    # 75-90: Yellow/Orange
    # > 90: Green
    colors = []
    for val in df["Coverage"]:
        if val < GradingThresholds.COVERAGE_CRITICAL: colors.append(GradingThresholds.COLOR_CRITICAL) # Fail
        elif val < GradingThresholds.COVERAGE_TARGET: colors.append(GradingThresholds.COLOR_WARNING) # Warning
        else: colors.append(GradingThresholds.COLOR_GOOD) # Good
        
    ax = sns.barplot(data=df, x="Module", y="Coverage", palette=colors, hue="Module", legend=False)
    
    # Add Threshold Lines
    plt.axhline(y=GradingThresholds.COVERAGE_TARGET, color=GradingThresholds.COLOR_GOOD, linestyle='--', linewidth=2, label=f'Target ({GradingThresholds.COVERAGE_TARGET}%)')
    plt.axhline(y=GradingThresholds.COVERAGE_CRITICAL, color=GradingThresholds.COLOR_CRITICAL, linestyle='--', linewidth=2, label=f'Critical ({GradingThresholds.COVERAGE_CRITICAL}%)')
    plt.legend(loc="upper right")
    
    plt.ylabel("Coverage (%)")
    plt.ylim(0, 105)
    plt.xticks(rotation=45, ha="right")
    
    # Add values on top of bars
    for i, v in enumerate(df["Coverage"]):
        ax.text(i, v + 1, f"{v:.1f}%", ha='center', fontsize=9, fontweight='bold')
        
    _save_plot(output_path, "Code Coverage Risk Analysis")

def plot_test_duration_distribution(test_durations: List[float], output_path: Path) -> None:
    """Generate a combined Histogram + KDE + Rug plot for deep duration analysis."""
    if not _check_dependencies(): return
    setup_style()
    if not test_durations: return

    df = pd.DataFrame(test_durations, columns=["Duration"])
    
    plt.figure(figsize=(10, 6))
    
    # Hist + KDE
    sns.histplot(data=df, x="Duration", bins=40, kde=True, color="#3498db", line_kws={'linewidth': 2})
    
    # Rug plot shows exact data points
    sns.rugplot(data=df, x="Duration", color="#2c3e50", height=0.05)
    
    plt.xlabel("Duration (seconds)")
    plt.ylabel("Frequency")
    
    # Use log scale if we have huge outliers (optional, but robust)
    if df["Duration"].max() > 10 * df["Duration"].median() and df["Duration"].median() > 0:
        plt.xscale('log')
        plt.xlabel("Duration (seconds) - Log Scale")
        
    _save_plot(output_path, "Test Duration Distribution Analysis")

def plot_top_slowest_tests(tests: List[Dict[str, Any]], output_path: Path) -> None:
    """Generate a bar chart of the top 10 slowest tests."""
    if not _check_dependencies(): return
    setup_style()
    if not tests: return
    
    # Filter only relevant tests and valid durations
    valid_tests = []
    for t in tests:
        # Extract name and duration
        name = t.get("nodeid", "Unknown").split("::")[-1]
        
        # Duration might constitute call+setup+teardown or just call
        # Try to find duration in seconds
        dur = 0.0
        if "duration" in t and isinstance(t["duration"], (int, float)):
             dur = t["duration"]
        elif "call" in t:
             dur = t["call"].get("duration", 0)
        
        # If it's the summarized dict from data builder, it might have duration field
        if "duration" in t:
             try:
                 if isinstance(t["duration"], str):
                    dur = float(t["duration"].replace("s", ""))
                 else:
                    dur = float(t["duration"])
             except: pass
             
        valid_tests.append({"Test": name, "Duration": dur})
        
    df = pd.DataFrame(valid_tests)
    if df.empty: return
    
    df = df.sort_values("Duration", ascending=False).head(10)
    
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=df, x="Duration", y="Test", palette="magma", hue="Test", legend=False)
    
    plt.title("Top 10 Slowest Tests", fontsize=16, fontweight='bold')
    plt.xlabel("Duration (seconds)")
    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.3fs', padding=3)
        
    _save_plot(output_path, "Performance Bottlenecks: Top 10 Slowest Tests")

def plot_performance_distribution(timings: List[Dict[str, Any]], output_path: Path) -> None:
    """Plot execution time breakdown (Total + 15 Stages)."""
    if not _check_dependencies(): return
    import matplotlib.pyplot as plt # Re-import locally for type checkers
    setup_style()
    if not timings:
        return
        
    # Prepare Data
    data = []
    for t in timings:
        try:
             # handle "1.23s" format
            val = float(str(t["duration"]).replace("s", ""))
            data.append({"Stage": t["stage"], "Duration (s)": val})
        except: continue
        
    if not data: return
    
    df = pd.DataFrame(data)
    # Sort by duration to highlight bottlenecks
    df = df.sort_values("Duration (s)", ascending=False)
    
    # 1. Total Breakdown (Bar Plot)
    plt.figure(figsize=(12, 8))
    
    # Use a sequential palette to highlight heaviest tasks
    ax = sns.barplot(x="Duration (s)", y="Stage", data=df, palette="rocket", hue="Stage", legend=False)
    
    # Add value labels
    for container in ax.containers:
        ax.bar_label(container, fmt='%.3fs', padding=3)
        
    _save_plot(output_path, "Report Generation Bottleneck Analysis")

    # 2. Deviation Analysis (Time vs Average)
    if not df.empty:
        avg_time = df["Duration (s)"].mean()
        
        plt.figure(figsize=(10, 6))
        
        # Calculate deviation
        df["Deviation"] = df["Duration (s)"] - avg_time
        df["Color"] = df["Deviation"].apply(lambda x: "#c0392b" if x > 0 else "#27ae60")
        
        sns.barplot(x="Deviation", y="Stage", data=df, palette=df["Color"].tolist(), hue="Stage", legend=False)
        plt.axvline(x=0, color='black', linestyle='--', linewidth=1)
        plt.xlabel(f"Seconds relative to Mean ({avg_time:.3f}s)")
            
        # Save properly
        dev_path = output_path.parent / "performance_deviation.png"
        _save_plot(dev_path, "Performance Deviation from Mean")

def plot_e2e_outcome(counts: Dict[str, int], output_path: Path) -> None:
    """Generate a donut chart for E2E outcomes."""
    if not _check_dependencies(): return
    setup_style()
    
    labels = []
    sizes = []
    colors = []
    mapping = {"pass": "#2ecc71", "fail": "#e74c3c", "error": "#f1c40f", "skipped": "#95a5a6"}
    
    for k, v in counts.items():
        if v > 0:
            labels.append(k.title())
            sizes.append(v)
            colors.append(mapping.get(k, "#bdc3c7"))
            
    if not sizes: return

    plt.figure()
    # Donut chart
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode=[0.05]*len(sizes))
    
    # Draw circle
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    _save_plot(output_path, "E2E Scenario Outcomes Overview")

def plot_e2e_durations(scenarios: List[Dict[str, Any]], output_path: Path) -> None:
    """Horizontal Bar chart of duration per scenario (better for long names)."""
    if not _check_dependencies(): return
    setup_style()
    
    df = pd.DataFrame(scenarios)
    if df.empty: return
    df = df.sort_values("duration", ascending=False)

    plt.figure(figsize=(12, max(6, len(df) * 0.4))) # Dynamic height
    
    ax = sns.barplot(data=df, x="duration", y="name", hue="name", legend=False, palette="viridis")
    plt.xlabel("Time (s)")
    plt.ylabel("Scenario")
    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2fs', padding=3)

    _save_plot(output_path, "E2E Scenario Performance Ranking")

def plot_type_errors_by_module(module_errors: Dict[str, Any], output_path: Path) -> None:
    """Generate a bar chart showing type errors per module."""
    if not _check_dependencies(): return
    setup_style()
    if not module_errors: return
    
    df = pd.DataFrame(list(module_errors.items()), columns=["Module", "Errors"])
    df = df.sort_values("Errors", ascending=False)
    
    plt.figure(figsize=(14, 8))
    colors = []
    for val in df["Errors"]:
        if val == 0: colors.append("#2ecc71")
        elif val < 20: colors.append("#f1c40f")
        else: colors.append("#c0392b") # Dark Red for high errors
    
    ax = sns.barplot(data=df, x="Module", y="Errors", palette=colors, hue="Module", legend=False)
    plt.ylabel("Number of Type Errors")
    plt.xticks(rotation=45, ha="right")
    
    for i, v in enumerate(df["Errors"]):
        ax.text(i, v + 0.5, str(v), ha='center', fontsize=9, fontweight='bold')

    _save_plot(output_path, "Type Safety Violations by Module")

def plot_error_categories(category_stats: Dict[str, int], output_path: Path) -> None:
    """Generate a horizontal bar chart instead of pie for better readability of categories."""
    if not _check_dependencies(): return
    setup_style()
    if not category_stats: return
    
    sorted_cats = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
    
    # Top 15 categories to avoid clutter
    top_n = 15
    if len(sorted_cats) > top_n:
        top_cats = dict(sorted_cats[:top_n])
    else:
        top_cats = dict(sorted_cats)
    
    df = pd.DataFrame(list(top_cats.items()), columns=["Category", "Count"])
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df, x="Count", y="Category", palette="mako", hue="Category", legend=False)
    
    _save_plot(output_path, "Top Type Error Categories")

def plot_complexity_distribution(complexity_violations: Dict[str, int], output_path: Path) -> None:
    """Generate visualization for complexity violations (Bar Charth + Threshold)."""
    if not _check_dependencies(): return
    setup_style()
    
    if not complexity_violations or sum(complexity_violations.values()) == 0:
        plt.figure()
        plt.text(0.5, 0.5, "✅ Clean Complexity\nAll functions < 10 Cyclomatic Complexity", 
                ha='center', va='center', fontsize=16, color='#2ecc71', fontweight='bold')
        plt.axis('off')
        _save_plot(output_path, "Cyclomatic Complexity Status")
        return
    
    df = pd.DataFrame(list(complexity_violations.items()), columns=["Module", "Violations"])
    df = df.sort_values("Violations", ascending=False)

    plt.figure(figsize=(14, 8))
    # Red palette for violations
    ax = sns.barplot(data=df, x="Module", y="Violations", palette="Reds_r", hue="Module", legend=False)
    
    plt.ylabel("Functions with Complexity > 10")
    plt.xticks(rotation=45, ha="right")
    
    for i, v in enumerate(df["Violations"]):
        if v > 0:
            ax.text(i, v + 0.1, str(int(v)), ha='center', fontsize=10, fontweight='bold')
            
    _save_plot(output_path, "Complexity Hotspots (Cyclomatic > 10)")

def plot_complexity_boxplot(complexity_data: Dict[str, List[int]], output_path: Path) -> None:
    """Generate a boxplot of cyclomatic complexity per module."""
    if not _check_dependencies(): return
    setup_style()
    
    # Flatten data for seaborn
    data_list = []
    for mod, scores in complexity_data.items():
        if not scores: continue
        for s in scores:
            data_list.append({"Module": mod, "Complexity": s})
            
    df = pd.DataFrame(data_list)
    if df.empty: return
    
    # Sort modules by median complexity
    median_order = df.groupby("Module")["Complexity"].median().sort_values(ascending=False).index
    
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=df, x="Module", y="Complexity", order=median_order, palette="coolwarm", hue="Module", legend=False)
    
    # Add threshold line
    plt.axhline(y=10, color='#e74c3c', linestyle='--', linewidth=2, label='Threshold (10)')
    plt.legend(loc="upper right")
    
    plt.title("Cyclomatic Complexity Distribution per Module", fontsize=16, fontweight='bold')
    plt.ylabel("Cyclomatic Complexity")
    plt.xticks(rotation=45, ha="right")
    
    try:
        plt.yscale('log') # Log scale if we have huge outliers
        plt.ylabel("Cyclomatic Complexity (Log Scale)")
    except: pass
    
    _save_plot(output_path, "Module Complexity Distribution (Boxplot)")

def plot_architecture_status(status: str, output_path: Path) -> None:
    """Generate a simple status indicator for architecture."""
    if not _check_dependencies(): return
    setup_style()
    
    plt.figure(figsize=(8, 6))
    if status == "PASS":
        color = "#2ecc71"
        icon = "✓"
        msg = "Architecture Compliant"
        sub = "All dependencies respect layers"
    else:
        color = "#e74c3c"
        icon = "✗"
        msg = "Architecture Violations"
        sub = "Dependency rules broken"
    
    plt.text(0.5, 0.6, icon, ha='center', va='center', fontsize=100, color=color, fontweight='bold')
    plt.text(0.5, 0.4, msg, ha='center', va='center', fontsize=18, color="#2c3e50", fontweight='bold')
    plt.text(0.5, 0.3, sub, ha='center', va='center', fontsize=12, color="#7f8c8d")
    
    plt.axis('off')
    _save_plot(output_path, "Architecture Compliance Status")

def plot_dependency_graph(dependencies: Dict[str, Any], output_path: Path, circular_deps: Optional[List[Any]] = None) -> None:
    """Generate a visual dependency graph using NetworkX."""
    if not _check_dependencies(): return
    if not HAS_NETWORKX:
        _save_fallback_graph_image(output_path)
        return

    G = nx.DiGraph()
    for mod, neighbors in dependencies.items():
        G.add_node(mod)
        for neighbor in neighbors:
            G.add_edge(mod, neighbor)
            
    plt.figure(figsize=(16, 12)) # Large canvas
    
    # Improved Layout calculation
    try:
        # k distance optimized for separation
        pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
    except:
        pos = nx.circular_layout(G)
    
    # Node Colors based on common layers (basic heuristic)
    node_colors = []
    for node in G.nodes():
        n = node.lower()
        if "domain" in n: c = "#3498db" # Blue
        elif "app" in n: c = "#9b59b6" # Purple
        elif "infra" in n: c = "#95a5a6" # Grey
        elif "test" in n: c = "#2ecc71" # Green
        else: c = "#f1c40f" # Yellow default
        node_colors.append(c)

    # Draw
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2500, alpha=0.9, edgecolors="#ecf0f1")
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold", font_color="white")
    
    # Edges
    nx.draw_networkx_edges(G, pos, edge_color="#bdc3c7", arrows=True, arrowsize=15, alpha=0.6)
    
    # Highlight Circular Dependencies
    if circular_deps:
        circ_edges = []
        for a, b in circular_deps:
            if G.has_edge(a, b): circ_edges.append((a, b))
            if G.has_edge(b, a): circ_edges.append((b, a))
        if circ_edges:
            nx.draw_networkx_edges(G, pos, edgelist=circ_edges, edge_color="#e74c3c", width=3, arrowsize=25, connectionstyle="arc3,rad=0.1")
            
    plt.axis('off')
    _save_plot(output_path, "Module Dependency Map", tight=False)

def _save_fallback_graph_image(output_path: Path) -> None:
    plt.figure(figsize=(12, 8))
    plt.text(0.5, 0.5, "Graph Visualization requires 'networkx'", ha='center', va='center', fontsize=14)
    plt.axis('off')
    plt.savefig(output_path)
    plt.close()

def plot_dependency_matrix(dependencies: Dict[str, Any], output_path: Path) -> None:
    """Create a dependency matrix heatmap."""
    if not _check_dependencies(): return
    setup_style()
    if not np: return
    
    modules = sorted(dependencies.keys())
    n = len(modules)
    if n == 0: return
    
    matrix = np.zeros((n, n))
    for i, mod_from in enumerate(modules):
        for j, mod_to in enumerate(modules):
            if mod_to in dependencies.get(mod_from, set()):
                matrix[i][j] = 1
                
    plt.figure(figsize=(12, 10))
    # Use a binary color map (White to Blue)
    sns.heatmap(matrix, xticklabels=modules, yticklabels=modules, cmap="Blues", 
                square=True, cbar=False, linewidths=0.5, linecolor='lightgrey')
    
    plt.title("Dependency Adjacency Matrix", fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.xlabel("Target Module")
    plt.ylabel("Source Module")
    
    _save_plot(output_path, "Dependency Adjacency Matrix")

def plot_documentation_stats(coverage_stats: Dict[str, int], drift_stats: Dict[str, int], output_path: Path, output_path_drift: Path) -> None:
    """Generate charts for documentation."""
    if not _check_dependencies(): return
    setup_style()
    
    # 1. Coverage Donut
    if coverage_stats:
        labels = list(coverage_stats.keys())
        sizes = list(coverage_stats.values())
        if sum(sizes) > 0:
            plt.figure(figsize=(8, 8))
            colors = ["#2ecc71", "#e74c3c", "#95a5a6"] # Green, Red, Grey
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85, explode=[0.02]*len(labels))
            
            # Donut hole
            centre_circle = plt.Circle((0,0), 0.70, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            
            _save_plot(output_path, "Documentation Coverage Overview")

    # 2. Drift Histogram (Days)
    if drift_stats:
        df = pd.DataFrame(list(drift_stats.items()), columns=["Module", "DriftDays"])
        df = df.sort_values("DriftDays", ascending=False) # Oldest drift first
        
        plt.figure(figsize=(14, 8))
        
        colors = []
        for d in df["DriftDays"]:
            if d < 30: colors.append("#2ecc71") # Fresh
            elif d < 90: colors.append("#f39c12") # Warning
            else: colors.append("#e74c3c") # Stale
            
        ax = sns.barplot(data=df, x="Module", y="DriftDays", palette=colors, hue="Module", legend=False)
        
        plt.ylabel("Days Since Last Doc Update")
        plt.xticks(rotation=45, ha="right")
        
        # Thresholds
        plt.axhline(y=30, color='#2ecc71', linestyle='--', label='Fresh (<30d)')
        plt.axhline(y=90, color='#e74c3c', linestyle='--', label='Stale (>90d)')
        plt.legend()
        
        _save_plot(output_path_drift, "Documentation Drift Analysis")

def plot_module_durations(module_durations: Dict[str, float], output_path: Path) -> None:
    """Generate a horizontal bar chart for module durations to identify slow modules."""
    if not _check_dependencies(): return
    setup_style()
    
    if not module_durations: return
    
    df = pd.DataFrame(list(module_durations.items()), columns=["Module", "Duration"])
    # Sort descending
    df = df.sort_values("Duration", ascending=False)
    
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=df, x="Duration", y="Module", hue="Module", legend=False, palette="magma")
    
    plt.xlabel("Execution Time (seconds)")
    plt.title("Module Execution Performance Ranking", fontsize=16, fontweight='bold')
    
    # Add labels
    for container in ax.containers:
        ax.bar_label(container, fmt='%.3fs', padding=3)
        
    _save_plot(output_path, "Module Execution Performance")
