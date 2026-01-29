import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Optional dependencies
try:
    import seaborn as sns # type: ignore
    import matplotlib.pyplot as plt
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
    sns.set_theme(style="whitegrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["font.size"] = 12

def plot_module_outcomes(module_data: Dict[str, Any], output_path: Path) -> None:
    """Generate a stacked bar chart of Pass/Fail/Error counts per module."""
    if not _check_dependencies(): return
    setup_style()
    
    data_list = []
    for mod, counts in module_data.items():
        data_list.append({"Module": mod, "Outcome": "Pass", "Count": counts.get("pass", 0)})
        data_list.append({"Module": mod, "Outcome": "Fail", "Count": counts.get("fail", 0)})
        data_list.append({"Module": mod, "Outcome": "Error", "Count": counts.get("error", 0)})
        
    df = pd.DataFrame(data_list)
    if df.empty: return

    plt.figure()
    try:
        df_pivot = df.pivot(index="Module", columns="Outcome", values="Count")
    except ValueError:
        return

    cols = [c for c in ["Pass", "Fail", "Error"] if c in df_pivot.columns]
    df_pivot = df_pivot[cols]
    
    colors = {"Pass": "#2ecc71", "Fail": "#e74c3c", "Error": "#f1c40f"}
    custom_palette = [colors[c] for c in cols]
    
    if not df_pivot.empty:
        ax = df_pivot.plot(kind="bar", stacked=True, color=custom_palette, width=0.8)
        plt.title("Test Outcome by Module")
        plt.xlabel("Module")
        plt.ylabel("Test Count")
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Outcome")
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        logger.debug(f"Saved plot: {output_path}")
    plt.close()

def plot_coverage(module_data: Dict[str, float], output_path: Path) -> None:
    """Generate a bar chart for coverage percentage per module."""
    if not _check_dependencies(): return
    setup_style()
    
    df = pd.DataFrame(list(module_data.items()), columns=["Module", "Coverage"])
    if df.empty: return

    plt.figure()
    colors = []
    for val in df["Coverage"]:
        if val < 50: colors.append("#e74c3c")
        elif val < 80: colors.append("#f1c40f")
        else: colors.append("#2ecc71")
        
    ax = sns.barplot(data=df, x="Module", y="Coverage", palette=colors)
    plt.title("Code Coverage by Module")
    plt.ylabel("Coverage (%)")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 100)
    
    for i, v in enumerate(df["Coverage"]):
        ax.text(i, v + 1, f"{v:.1f}%", ha='center', fontsize=10)
        
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    logger.debug(f"Saved plot: {output_path}")
    plt.close()

def plot_test_duration_distribution(test_durations: List[float], output_path: Path) -> None:
    """Generate a histogram of test durations."""
    if not _check_dependencies(): return
    setup_style()
    if not test_durations: return

    df = pd.DataFrame(test_durations, columns=["Duration"])
    plt.figure()
    sns.histplot(data=df, x="Duration", bins=30, kde=True, color="#3498db")
    plt.title("Test Duration Distribution")
    plt.xlabel("Duration (seconds)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_e2e_outcome(counts: Dict[str, int], output_path: Path) -> None:
    """Generate a pie chart for E2E outcomes."""
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
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title("E2E Scenario Outcomes")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    logger.debug(f"Saved plot: {output_path}")
    plt.close()

def plot_e2e_durations(scenarios: List[Dict[str, Any]], output_path: Path) -> None:
    """Bar chart of duration per scenario."""
    if not _check_dependencies(): return
    setup_style()
    
    df = pd.DataFrame(scenarios)
    if df.empty: return

    plt.figure()
    ax = sns.barplot(data=df, x="name", y="duration", hue="name", legend=False, palette="viridis")
    plt.title("E2E Scenario Durations")
    plt.xlabel("Scenario")
    plt.ylabel("Time (s)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_type_errors_by_module(module_errors: Dict[str, Any], output_path: Path) -> None:
    """Generate a bar chart showing type errors per module."""
    if not _check_dependencies(): return
    setup_style()
    if not module_errors: return
    
    df = pd.DataFrame(list(module_errors.items()), columns=["Module", "Errors"])
    df = df.sort_values("Errors", ascending=False)
    
    plt.figure()
    colors = []
    for val in df["Errors"]:
        if val == 0: colors.append("#2ecc71")
        elif val < 20: colors.append("#f1c40f")
        else: colors.append("#e74c3c")
    
    ax = sns.barplot(data=df, x="Module", y="Errors", palette=colors, hue="Module", legend=False)
    plt.title("Type Errors by Module", fontsize=14, fontweight='bold')
    plt.ylabel("Number of Errors")
    plt.xlabel("Module")
    plt.xticks(rotation=45, ha="right")
    
    for i, v in enumerate(df["Errors"]):
        ax.text(i, v + 1, str(v), ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_error_categories(category_stats: Dict[str, int], output_path: Path) -> None:
    """Generate a pie chart showing error distribution by category."""
    if not _check_dependencies(): return
    setup_style()
    if not category_stats: return
    
    sorted_cats = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_cats) > 8:
        top_cats = dict(sorted_cats[:8])
        other_count = sum(count for _, count in sorted_cats[8:])
        if other_count > 0: top_cats["other"] = other_count
    else:
        top_cats = dict(sorted_cats)
    
    labels = list(top_cats.keys())
    sizes = list(top_cats.values())
    colors = plt.cm.Set3(range(len(labels))) # type: ignore
    
    plt.figure(figsize=(10, 8))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title("Error Distribution by Category", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_complexity_distribution(complexity_violations: Dict[str, int], output_path: Path) -> None:
    """Generate visualization for complexity violations."""
    if not _check_dependencies(): return
    setup_style()
    
    if not complexity_violations or sum(complexity_violations.values()) == 0:
        plt.figure()
        plt.text(0.5, 0.5, "✅ No Complexity Violations\nAll functions below threshold (10)", 
                ha='center', va='center', fontsize=14, color='#2ecc71', fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=100)
        plt.close()
        return
    
    df = pd.DataFrame(list(complexity_violations.items()), columns=["Module", "Violations"])
    plt.figure()
    ax = sns.barplot(data=df, x="Module", y="Violations", color="#e74c3c", hue="Module", legend=False)
    plt.title("Complexity Violations by Module", fontsize=14, fontweight='bold')
    plt.ylabel("Number of Violations (>10)")
    plt.xlabel("Module")
    plt.xticks(rotation=45, ha="right")
    for i, v in enumerate(df["Violations"]):
        ax.text(i, v + 0.5, str(int(v)), ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_architecture_status(status: str, output_path: Path) -> None:
    """Generate a simple status indicator for architecture."""
    if not _check_dependencies(): return
    setup_style()
    
    plt.figure(figsize=(8, 6))
    if status == "PASS":
        color = "#2ecc71"
        icon = "✅"
        msg = "Clean Architecture\nCompliant"
    else:
        color = "#e74c3c"
        icon = "❌"
        msg = "Architecture Violations\nDetected"
    
    plt.text(0.5, 0.5, f"{icon}\n{msg}", ha='center', va='center', fontsize=16, color=color, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_dependency_graph(dependencies: Dict[str, Any], output_path: Path, circular_deps: Optional[List[Any]] = None) -> None:
    """Generate a visual dependency graph."""
    if not _check_dependencies(): return
    if not HAS_NETWORKX:
        _save_fallback_graph_image(output_path)
        return

    G = nx.DiGraph()
    for mod, neighbors in dependencies.items():
        G.add_node(mod)
        for neighbor in neighbors:
            G.add_edge(mod, neighbor)
            
    plt.figure(figsize=(12, 10))
    pos = _calculate_graph_layout(G)
    
    _draw_graph_nodes(G, pos)
    
    nx.draw_networkx_edges(G, pos, edge_color="#95a5a6", arrows=True, arrowsize=15)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold", font_color="white")
    
    if circular_deps:
        _highlight_circular_deps(G, pos, circular_deps)
             
    plt.title("Module Dependency Graph", fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    logger.debug(f"Saved plot: {output_path}")
    plt.close()

def _save_fallback_graph_image(output_path: Path) -> None:
    plt.figure(figsize=(12, 8))
    plt.text(0.5, 0.5, "Graph Visualization requires 'networkx'", ha='center', va='center', fontsize=14)
    plt.axis('off')
    plt.savefig(output_path)
    plt.close()

def _calculate_graph_layout(G: Any) -> Any:
    try:
        return nx.spring_layout(G, k=2, iterations=50, seed=42)
    except:
        return nx.circular_layout(G)

def _draw_graph_nodes(G: Any, pos: Any) -> None:
    node_colors = []
    for node in G.nodes():
        n = node.lower()
        if n in ["auth", "security"]: c = "#e74c3c"
        elif n in ["storage", "database"]: c = "#3498db"
        elif n in ["bot", "workflow"]: c = "#2ecc71"
        elif n in ["api"]: c = "#f39c12"
        else: c = "#95a5a6"
        node_colors.append(c)

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.9, edgecolors="black")

def _highlight_circular_deps(G: Any, pos: Any, circular_deps: List[Any]) -> None:
    circ_edges = []
    for a, b in circular_deps:
        if G.has_edge(a, b): circ_edges.append((a, b))
        if G.has_edge(b, a): circ_edges.append((b, a))
    if circ_edges:
        nx.draw_networkx_edges(G, pos, edgelist=circ_edges, edge_color="#e74c3c", width=2, arrowsize=20)

def plot_dependency_matrix(dependencies: Dict[str, Any], output_path: Path) -> None:
    """Create a dependency matrix heatmap."""
    if not _check_dependencies(): return
    if not np: return
    
    modules = sorted(dependencies.keys())
    n = len(modules)
    if n == 0: return
    
    matrix = np.zeros((n, n))
    for i, mod_from in enumerate(modules):
        for j, mod_to in enumerate(modules):
            if mod_to in dependencies.get(mod_from, set()):
                matrix[i][j] = 1
                
    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix, xticklabels=modules, yticklabels=modules, cmap="YlOrRd", square=True, cbar=False)
    plt.title("Dependency Matrix")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=100)
    plt.close()

def plot_documentation_stats(coverage_stats: Dict[str, int], drift_stats: Dict[str, int], output_path: Path, output_path_drift: Path) -> None:
    """
    Generate charts for documentation.
    """
    if not _check_dependencies(): return
    setup_style()
    
    # 1. Coverage Pie
    if coverage_stats:
        labels = list(coverage_stats.keys())
        sizes = list(coverage_stats.values())
        if sum(sizes) > 0:
            plt.figure(figsize=(8, 8))
            colors = ["#2ecc71", "#e74c3c", "#95a5a6"]
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title("Documentation Coverage (All Modules)", fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(output_path, dpi=100)
            plt.close()
            logger.debug(f"Saved plot: {output_path}")

    # 2. Drift Histogram
    if drift_stats:
        df = pd.DataFrame(list(drift_stats.items()), columns=["Module", "DriftDays"])
        plt.figure(figsize=(10, 6))
        
        colors = []
        for d in df["DriftDays"]:
            if d < 30: colors.append("#2ecc71")
            elif d < 90: colors.append("#f1c40f")
            else: colors.append("#e74c3c")
            
        sns.barplot(data=df, x="Module", y="DriftDays", palette=colors)
        plt.title("Documentation Drift (Days since last update)", fontsize=14, fontweight='bold')
        plt.xlabel("Module")
        plt.ylabel("Days")
        plt.xticks(rotation=45, ha="right")
        
        plt.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Fresh (<30d)')
        plt.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='Stale (>90d)')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(output_path_drift, dpi=100)
        plt.close()
        logger.debug(f"Saved plot: {output_path_drift}")
