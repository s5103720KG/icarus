#!/usr/bin/env python
"""Plot results read from a result set
"""
import os
import argparse
import logging

import matplotlib.pyplot as plt

from icarus.util import Settings, config_logging
from icarus.results import plot_lines, plot_bar_chart
from icarus.registry import RESULTS_READER


# Logger object
logger = logging.getLogger("plot")

# These lines prevent insertion of Type 3 fonts in figures
# Publishers don't want them
plt.rcParams["ps.useafm"] = True
plt.rcParams["pdf.use14corefonts"] = True

# If True text is interpreted as LaTeX, e.g. underscore are interpreted as
# subscript. If False, text is interpreted literally
plt.rcParams["text.usetex"] = False

# Aspect ratio of the output figures
plt.rcParams["figure.figsize"] = 8, 5

# Size of font in legends
LEGEND_SIZE = 11

# Line width in pixels
LINE_WIDTH = 1.5

# Plot
PLOT_EMPTY_GRAPHS = True

# This dict maps strategy names to the style of the line to be used in the plots
# Off-path strategies: solid lines
# On-path strategies: dashed lines
# No-cache: dotted line
STRATEGY_STYLE = {
    "HR_SYMM": "b-o",
    "HR_ASYMM": "g-D",
    "HR_MULTICAST": "m-^",
    "LCE": "b--p",
    "LCD": "g-->",
    "CL4M": "g-->",
    "PROB_CACHE": "c--<",
    "RAND_CHOICE": "r--<",
}

# This dict maps name of strategies to names to be displayed in the legend
STRATEGY_LEGEND = {
    "LCE": "LCE",
    "LCD": "LCD",
    "HR_SYMM": "HR Symm",
    "HR_ASYMM": "HR Asymm",
    "HR_MULTICAST": "HR Multicast",
    "CL4M": "CL4M",
    "PROB_CACHE": "ProbCache",
    "RAND_CHOICE": "Random (choice)",
}

# Color and hatch styles for bar charts of cache hit ratio and link load vs topology
STRATEGY_BAR_COLOR = {
    "LCE": "red",
    "LCD": "orange",
    "NO_CACHE": "black",
    "HR_ASYMM": "blue",
    "HR_SYMM": "purple",
    "PROB_CACHE": "yellow",
}

STRATEGY_BAR_HATCH = {
    "LCE": None,
    "LCD": "//",
    "NO_CACHE": "x",
    "HR_ASYMM": "+",
    "HR_SYMM": "\\",
}

def plot_cache_hits_vs_percent_removed(resultset, topology, percent_removed, failure_type, strategies, plotdir):
    desc = {}
    desc["title"] = "Cache hit ratio: Topology={} Failure Type:{}".format(topology, failure_type)
    desc["ylabel"] = "Cache hit ratio"
    desc["xparam"] = ("workload", "percent_removed")
    desc["xvals"] = percent_removed
    desc["filter"] = {
        "workload": {"failure_type": failure_type},
        "topology": {"name": topology}
    }

    desc["ymetrics"] = [("CACHE_HIT_RATIO", "MEAN")] * len(strategies)
    desc["ycondnames"] = [("strategy", "name")] * len(strategies)
    desc["ycondvals"] = strategies
    desc["errorbar"] = True
    desc["legend_loc"] = "lower right"
    desc["bar_color"] = STRATEGY_BAR_COLOR
    desc["bar_hatch"] = STRATEGY_BAR_HATCH
    desc["legend"] = STRATEGY_LEGEND
    desc["plotempty"] = PLOT_EMPTY_GRAPHS
    plot_bar_chart(
        resultset,
        desc,
        "Cache hit ratio: Topology={} Failure Type:{}.pdf".format(topology, failure_type),
        plotdir,
    )

def run(config, results, plotdir):
    """Run the plot script

    Parameters
    ----------
    config : str
        The path of the configuration file
    results : str
        The file storing the experiment results
    plotdir : str
        The directory into which graphs will be saved
    """

    settings = Settings()
    settings.read_from(config)
    config_logging(settings.LOG_LEVEL)
    resultset = RESULTS_READER[settings.RESULTS_FORMAT](results)
    # Create dir if not existsing
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    # Parse params from settings
    topologies = settings.TOPOLOGIES
    #cache_sizes = settings.NETWORK_CACHE
    #alphas = settings.ALPHA
    strategies = settings.STRATEGIES
    failure_types = settings.FAILURE_TYPE
    failure_ranges = settings.PERCENT_REMOVED

    for topology in topologies:
        for failure_type in failure_types:
            logger.info(
                "Plotting cache hit ratio for topology %s and failure type %s vs percent removed"
                % (topology, str(failure_type))
            )
            plot_cache_hits_vs_percent_removed(
                resultset, topology, failure_ranges, failure_type, strategies, plotdir
                                               )

    logger.info("Exit. Plots were saved in directory %s" % os.path.abspath(plotdir))

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "-r", "--results", dest="results", help="the results file", required=True
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        help="the output directory where plots will be saved",
        required=True,
    )
    parser.add_argument("config", help="the configuration file")
    args = parser.parse_args()
    run(args.config, args.results, args.output)

if __name__ == "__main__":
    main()