from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

try:
    import pandas as pd # type: ignore
    import seaborn as sns # type: ignore
    import matplotlib.pyplot as plt
    import numpy as np # type: ignore
except ImportError:
    pd = None
    sns = None
    plt = None
    np = None

try:
    import networkx as nx # type: ignore
    HAS_NETWORKX = True
except ImportError:
    nx = None
    HAS_NETWORKX = False

from ..core.base_plotter import BasePlotter

class DependencyPlotter(BasePlotter):
    """Plotter for Dependency Graphs and Matrices."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("nibandha.reporting.visualizers.dependency")

    def plot(self, data: Dict[str, Any], output_dir: Path) -> Dict[str, str]:
        """Generate dependency charts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        charts = {}
        try:
            # Matrix
            matrix_path = output_dir / "dependency_matrix.png"
            self.plot_dependency_matrix(data, matrix_path)
            if matrix_path.exists(): charts["dependency_matrix"] = str(matrix_path)
            
            # Graph
            graph_path = output_dir / "module_dependencies.png"
            # Assuming circular_deps might be extracted if available, or just pass None
            # Standardizing on data dict for now. 
            circular_deps = data.get("circular_dependencies") # Optional extraction
            # If data is just definition map, circular_deps won't be there unless passed in a wrapper dict.
            # In current usage, 'run_dependency_checks' returns a dict with 'dependencies', 'circular_dependencies', etc.
            # So 'data' is likley the full report dict.
            # But wait, 'generate_dependency_charts' in DefaultVisualizer took 'dependencies: Dict[str, Any]'.
            # Let's see how it was called. 
            # It seems it was passed the raw dependency map in some cases?
            # Actually, `dep_reporter.generate` returns a dict with `dependencies`, `circular_dependencies`.
            # If `dependencies` arg in `generate_dependency_charts` was just the map, we need to be careful.
            # Checking DefaultVisualizer again... 
            # `def generate_dependency_charts(self, dependencies: Dict[str, Any], output_dir: Path)`
            # It uses `dependencies` for both matrix and graph.
            # If circular deps are needed, they weren't passed to `DefaultVisualizer`! 
            # So `DefaultVisualizer` only plotted the graph without highlighting circular deps (or `dependencies` contained it?).
            # `plot_dependency_graph` takes `circular_deps` as optional arg.
            # `DefaultVisualizationProvider.generate_dependency_charts` called `self.dependency_plotter.plot_dependency_graph(dependencies, graph_path)`.
            # So it didn't pass `circular_deps`.
            # I will follow suit for now, but `data` here should be the dependency map itself based on previous usage?
            # Or should `data` be the full result object?
            # Ideally `data` is the full result from `DependencyReporter`.
            # If I change the signature in `DependencyReporter` to pass the full object to `viz_provider`, I can extract circular deps!
            # For now, I'll assume `data` IS the dependency map (key->list of deps), compatible with existing `DefaultVisualizationProvider`.
            # But wait, looking at `BasePlotter.plot`, `data` is `Dict[str, Any]`.
            self.plot_dependency_graph(data, graph_path) 
            if graph_path.exists(): charts["module_dependencies"] = str(graph_path)
        except Exception as e:
            self.logger.error(f"Error generating dependency charts: {e}")
        return charts

    def plot_dependency_graph(self, dependencies: Dict[str, Any], output_path: Path, circular_deps: Optional[List[Any]] = None) -> None:
        """Generate a visual dependency graph using NetworkX."""
        if not self._check_dependencies(): return
        if not HAS_NETWORKX:
            self._save_fallback_graph_image(output_path, "Graph Visualization requires 'networkx'")
            return

        G = nx.DiGraph()
        for mod, neighbors in dependencies.items():
            G.add_node(mod)
            for neighbor in neighbors:
                G.add_edge(mod, neighbor)
                
        plt.figure(figsize=(16, 12))
        
        try:
            pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
        except:
            pos = nx.circular_layout(G)
        
        node_colors = []
        for node in G.nodes():
            n = node.lower()
            if "domain" in n: c = "#3498db"
            elif "app" in n: c = "#9b59b6"
            elif "infra" in n: c = "#95a5a6"
            elif "test" in n: c = "#2ecc71"
            else: c = "#f1c40f"
            node_colors.append(c)

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2500, alpha=0.9, edgecolors="#ecf0f1")
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold", font_color="white")
        nx.draw_networkx_edges(G, pos, edge_color="#bdc3c7", arrows=True, arrowsize=15, alpha=0.6)
        
        if circular_deps:
            circ_edges = []
            for a, b in circular_deps:
                if G.has_edge(a, b): circ_edges.append((a, b))
                if G.has_edge(b, a): circ_edges.append((b, a))
            if circ_edges:
                nx.draw_networkx_edges(G, pos, edgelist=circ_edges, edge_color="#e74c3c", width=3, arrowsize=25, connectionstyle="arc3,rad=0.1")
                
        plt.axis('off')
        self._save_plot(output_path, "Module Dependency Map", tight=False)

    def plot_dependency_matrix(self, dependencies: Dict[str, Any], output_path: Path) -> None:
        """Create a dependency matrix heatmap."""
        if not self._check_dependencies(): return
        self.setup_style()
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
        sns.heatmap(matrix, xticklabels=modules, yticklabels=modules, cmap="Blues", 
                    square=True, cbar=False, linewidths=0.5, linecolor='lightgrey')
        
        plt.title("Dependency Adjacency Matrix", fontsize=16, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.xlabel("Target Module")
        plt.ylabel("Source Module")
        
        self._save_plot(output_path, "Dependency Adjacency Matrix")
