import math
from multiprocessing import cpu_count
from collections import deque
import copy
import random
from icarus.util import Tree
import icarus.registry
import networkx as nx


def random_get_nodes_to_remove(topology_config, percent_removed_nodes):
    """Get list of nodes ro remove from topology"""
    topology_name = topology_config["name"]
    topology = icarus.registry.TOPOLOGY_FACTORY[topology_name](**topology_config)
    cache_nodes = topology.graph["icr_candidates"]
    n_removed_nodes = math.ceil(len(cache_nodes) * (percent_removed_nodes/100))
    # Remove random nodes
    nodes_to_remove = random.sample(list(cache_nodes), n_removed_nodes)
    return nodes_to_remove

def centrality_get_nodes_to_remove(topology_config, percent_removed_nodes):
    topology_name = topology_config["name"]
    topology = icarus.registry.TOPOLOGY_FACTORY[topology_name](**topology_config)
    cache_nodes = topology.graph["icr_candidates"]
    n_removed_nodes = math.ceil(len(cache_nodes) * (percent_removed_nodes / 100))
    # Finds the betweenness centrality of each node and adds the availble nodes
    # to a new dictionary
    centrality = nx.betweenness_centrality(topology)
    available_nodes = {key: value for key, value in centrality.items() if key in cache_nodes}
    nodes = []
    for x in range(n_removed_nodes):
        max_centrality = max(available_nodes.values())
        tmp = int(str([k for k, v in available_nodes.items() if v == max_centrality]).replace('[','').replace(']',''))
        nodes.append(tmp)
        available_nodes.pop(nodes[x])
    nodes_to_remove = nodes
    return nodes_to_remove

def get_links_to_remove(topology_config, percent_removed_links):
    """Get list of nodes ro remove from topology"""
    topology_name = topology_config["name"]
    topology = icarus.registry.TOPOLOGY_FACTORY[topology_name](**topology_config)
    links = topology.edges()
    n_removed_links = math.ceil(len(links) * (percent_removed_links / 100))
    # Remove random links.
    links_to_remove = random.sample(list(links), n_removed_links)
    return links_to_remove


# GENERAL SETTINGS

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = cpu_count()

# Granularity of caching.
# Currently, only OBJECT is supported
CACHING_GRANULARITY = "OBJECT"

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported
RESULTS_FORMAT = "PICKLE"

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 10

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icarus/execution/collectors.py
DATA_COLLECTORS = [
    "LATENCY",
    "CACHE_HIT_RATIO",
    "SUCCESS",
]

# Number of content objects
N_CONTENTS = 10 ** 5 # 100,000

# Number of content requests generated to prepopulate the caches
# These requests are not logged
N_WARMUP_REQUESTS = 20*60*100 # 120,000

# Number of content requests generated after the warmup and logged
# to generate results.
N_MEASURED_REQUESTS = 10 ** 5 # 100,000

# Zipfs distribution
ALPHA = 0.8

# Number of requests per second (over the whole network)
NETWORK_REQUEST_RATE = 12

# List of caching and routing strategies
STRATEGIES = [
    "LCE",  # Leave Copy Everywhere
    "HR_SYMM",  # Symmetric hash-routing
    "HR_ASYMM",  # Asymmetric hash-routing
    "HR_MULTICAST",  # Multicast hash-routing
    "CL4M",  # Cache less for more
    "PROB_CACHE",  # ProbCache
    "LCD",  # Leave Copy Down
    "RAND_CHOICE",  # Random choice: cache in one random cache on path
]

# Percentage of Node/Link removal
PERCENT_REMOVED = [0, 10, 20, 30, 40, 50, 60]

# Type of failures
FAILURE_TYPE = ["RANDOM", "BETWEENNESS", "LINK"]

# Queue of experiments
EXPERIMENT_QUEUE = deque()

# Create experiment
default = Tree()

# Specify topology
TOPOLOGIES = [
    "RANDOM",
    "TISCALI_2",
    "SCALE_FREE",
]

# Set workload
default["workload"] = {
    "name": "STATIONARY",
    "n_contents": N_CONTENTS,
    "n_warmup": N_WARMUP_REQUESTS,
    "n_measured": N_MEASURED_REQUESTS,
    "rate": NETWORK_REQUEST_RATE,
    "alpha": ALPHA,
}

# Set cache placement
default["cache_placement"]["name"] = "UNIFORM"
default["cache_placement"]["network_cache"] = 0.01

# Set content placement
default["content_placement"]["name"] = "UNIFORM"

# Cache replacement policy used by the network caches.
CACHE_POLICY = "LRU"

# Set cache replacement policy
default["cache_policy"]["name"] = CACHE_POLICY

# Loops through all the combinations of topology, strategy, failure type and percent removed
for topology in TOPOLOGIES:
    for strategy in STRATEGIES:
        for percent_removed in PERCENT_REMOVED:
            for failure_type in FAILURE_TYPE:
                experiment = copy.deepcopy(default)
                experiment["topology"]["name"] = topology
                experiment["strategy"]["name"] = strategy
                experiment["workload"]["failure_type"] = failure_type
                experiment["workload"]["percent_removed"] = percent_removed
                if PERCENT_REMOVED != 0:
                    if failure_type == "RANDOM":
                        experiment["topology"]["removed_nodes"] = random_get_nodes_to_remove(experiment["topology"], percent_removed)
                    elif failure_type == "LINK":
                        experiment["topology"]["removed_links"] = get_links_to_remove(experiment["topology"], percent_removed)
                    elif failure_type == "BETWEENNESS":
                        experiment["topology"]["removed_nodes"] = centrality_get_nodes_to_remove(experiment["topology"], percent_removed)
                experiment["desc"] = "Topology: {}, Strategy: {}, Failure Type: {}, Percent removed: {}%".format(
                    topology,
                    strategy,
                    failure_type,
                    str(percent_removed),
                )
                EXPERIMENT_QUEUE.append(experiment)
