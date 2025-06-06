#!/usr/bin/env python3
"""
Requirements Visualization Utility

This script creates visual representations of requirements relationships
from RTM data to help with analysis and reporting.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.colors import CSS4_COLORS
except ImportError:
    print("Required visualization libraries not found. Installing...")
    import subprocess
    subprocess.run(
        ["pip", "install", "matplotlib", "networkx"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.colors import CSS4_COLORS


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RequirementsVisualizer:
    """Class for visualizing requirements relationships."""

    def __init__(self, rtm_data=None):
        """Initialize the visualizer with RTM data."""
        self.rtm_data = rtm_data
        self.graph = nx.DiGraph()
        self.req_categories = {}
        self.category_colors = {
            "FR": "lightblue",
            "NFR": "lightgreen",
            "CF": "lightsalmon",
            "IR": "plum",
            "IM": "khaki",
            "REQ": "lightgray",  # Default
        }

    def load_data(self, data_file):
        """Load requirements data from a JSON or YAML file."""
        file_path = Path(data_file)

        if not file_path.exists():
            logger.error("Data file not found: %s", file_path)
            return False

        try:
            if file_path.suffix.lower() == ".json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.rtm_data = json.load(f)
            elif file_path.suffix.lower() in [".yaml", ".yml"]:
                import yaml
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.rtm_data = yaml.safe_load(f)
            else:
                logger.error("Unsupported file format: %s", file_path.suffix)
                return False

            logger.info("Successfully loaded RTM data from %s", file_path)
            return True
        except Exception as e:
            logger.error("Error loading RTM data: %s", e)
            return False

    def build_graph(self):
        """Build a graph from the RTM data."""
        if not self.rtm_data:
            logger.error("No RTM data available. Load data first.")
            return False

        # Clear existing graph
        self.graph.clear()
        self.req_categories.clear()

        try:
            # Handle different RTM data formats
            if "requirements" in self.rtm_data:
                # Format from traceability matrix
                requirements = self.rtm_data["requirements"]
                for req_id, details in requirements.items():
                    # Extract category from req_id (e.g., "FR-1" -> "FR")
                    category = req_id.split("-")[0] if "-" in req_id else "REQ"
                    self.req_categories[req_id] = category

                    # Add node with attributes
                    self.graph.add_node(
                        req_id,
                        description=details.get("description", ""),
                        status=details.get("status", "Unknown"),
                        category=category
                    )

                    # Add edges for related requirements
                    for related_req in details.get("references", []):
                        if related_req in requirements:
                            self.graph.add_edge(req_id, related_req)

            elif isinstance(self.rtm_data, dict):
                # Simple dict format with req_id as keys
                for req_id, details in self.rtm_data.items():
                    if isinstance(details, dict):
                        category = req_id.split("-")[0] if "-" in req_id else "REQ"
                        self.req_categories[req_id] = category

                        self.graph.add_node(
                            req_id,
                            description=details.get("text", ""),
                            status=details.get("status", "Unknown"),
                            category=category
                        )

                        # Add edges for related requirements
                        for related_req in details.get("references", []):
                            self.graph.add_edge(req_id, related_req)

            logger.info("Built graph with %d nodes and %d edges",
                       self.graph.number_of_nodes(),
                       self.graph.number_of_edges())
            return True
        except Exception as e:
            logger.error("Error building graph: %s", e)
            return False

    def visualize_requirements(self, output_file=None, show_plot=True):
        """Generate and display a visual representation of requirements."""
        if not self.graph:
            if not self.build_graph():
                return False

        try:
            plt.figure(figsize=(12, 10))

            # Define node colors based on requirement categories
            node_colors = []
            for node in self.graph.nodes():
                category = self.req_categories.get(node, "REQ")
                color = self.category_colors.get(category, "lightgray")
                node_colors.append(color)

            # Create layout
            pos = nx.spring_layout(self.graph, seed=42)  # Fixed seed for reproducibility

            # Draw nodes
            nx.draw_networkx_nodes(
                self.graph,
                pos,
                node_color=node_colors,
                node_size=500,
                alpha=0.8
            )

            # Draw edges
            nx.draw_networkx_edges(
                self.graph,
                pos,
                arrowstyle="->",
                arrowsize=15,
                width=1.5,
                alpha=0.7
            )

            # Draw labels
            nx.draw_networkx_labels(
                self.graph,
                pos,
                font_size=10,
                font_family="sans-serif"
            )

            # Add legend for categories
            legend_patches = []
            from matplotlib.patches import Patch
            for category, color in self.category_colors.items():
                if any(self.req_categories.get(node) == category for node in self.graph.nodes()):
                    legend_patches.append(
                        Patch(color=color, label=f"{category}")
                    )

            plt.legend(handles=legend_patches, loc="upper right")
            plt.title("Requirements Relationships Visualization")
            plt.axis("off")

            # Save plot if output file provided
            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_path, bbox_inches="tight", dpi=300)
                logger.info("Visualization saved to %s", output_path)

            # Show plot if requested
            if show_plot:
                plt.show()
            else:
                plt.close()

            return True
        except Exception as e:
            logger.error("Error visualizing requirements: %s", e)
            import traceback
            traceback.print_exc()
            return False

    def generate_metrics(self):
        """Calculate and return metrics about the requirements graph."""
        if not self.graph:
            if not self.build_graph():
                return None

        metrics = {
            "total_requirements": self.graph.number_of_nodes(),
            "total_relationships": self.graph.number_of_edges(),
            "requirement_categories": {},
            "orphaned_requirements": [],
            "most_connected": None,
            "max_connections": 0,
            "average_connections": 0
        }

        # Count requirements by category
        category_counts = {}
        for req_id, category in self.req_categories.items():
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
        metrics["requirement_categories"] = category_counts

        # Find orphaned requirements (no connections)
        for node in self.graph.nodes():
            if self.graph.degree(node) == 0:
                metrics["orphaned_requirements"].append(node)

        # Find most connected requirement
        for node in self.graph.nodes():
            connections = self.graph.degree(node)
            if connections > metrics["max_connections"]:
                metrics["max_connections"] = connections
                metrics["most_connected"] = node

        # Calculate average connections
        if self.graph.number_of_nodes() > 0:
            total_connections = sum(d for _, d in self.graph.degree())
            metrics["average_connections"] = total_connections / self.graph.number_of_nodes()

        return metrics

    def export_metrics(self, output_file):
        """Export metrics to a JSON or YAML file."""
        metrics = self.generate_metrics()
        if not metrics:
            return False

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if output_path.suffix.lower() == ".json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(metrics, f, indent=2)
            elif output_path.suffix.lower() in [".yaml", ".yml"]:
                import yaml
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(metrics, f, default_flow_style=False)
            else:
                logger.error("Unsupported output format: %s", output_path.suffix)
                return False

            logger.info("Metrics exported to %s", output_path)
            return True
        except Exception as e:
            logger.error("Error exporting metrics: %s", e)
            return False

    def print_metrics(self):
        """Print metrics to the console."""
        metrics = self.generate_metrics()
        if not metrics:
            return

        print("\nRequirements Analysis Metrics:")
        print("=" * 30)
        print(f"Total Requirements: {metrics['total_requirements']}")
        print(f"Total Relationships: {metrics['total_relationships']}")

        print("\nRequirements by Category:")
        for category, count in metrics["requirement_categories"].items():
            print(f"  {category}: {count}")

        print(f"\nOrphaned Requirements: {len(metrics['orphaned_requirements'])}")
        if metrics['orphaned_requirements']:
            print("  " + ", ".join(metrics['orphaned_requirements'][:5]))
            if len(metrics['orphaned_requirements']) > 5:
                print(f"  ...and {len(metrics['orphaned_requirements']) - 5} more")

        print(f"\nMost Connected: {metrics['most_connected']} "
              f"({metrics['max_connections']} connections)")
        print(f"Average Connections: {metrics['average_connections']:.2f}")


def main():
    """Main entry point for the requirements visualizer."""
    parser = argparse.ArgumentParser(
        description="Visualize requirements relationships from RTM data"
    )
    parser.add_argument(
        "input_file",
        help="Input RTM data file (JSON or YAML)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to save the visualization image"
    )
    parser.add_argument(
        "-m", "--metrics",
        help="Path to save metrics data (JSON or YAML)"
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Don't display the visualization (just save if --output is provided)"
    )

    args = parser.parse_args()

    # Initialize and load data
    visualizer = RequirementsVisualizer()
    if not visualizer.load_data(args.input_file):
        return 1

    # Generate and show/save visualization
    visualizer.visualize_requirements(
        output_file=args.output,
        show_plot=not args.no_show
    )

    # Print metrics to console
    visualizer.print_metrics()

    # Export metrics if requested
    if args.metrics:
        visualizer.export_metrics(args.metrics)

    return 0


if __name__ == "__main__":
    sys.exit(main())
