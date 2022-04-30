"""Configuration file for running a single simple simulation.
"""
from multiprocessing import cpu_count
from collections import deque
import copy
import random
from icarus.util import Tree
import icarus.registry


def get_nodes_to_remove(topology_config, n_removed_nodes):
    """Get list of nodes ro remove from topology"""
    topology_name = topology_config["name"]
    topology = icarus.registry.TOPOLOGY_FACTORY[topology_name]()
    cache_nodes = topology.graph["icr_candidates"]

    # Remove random nodes. You can replace this line with more sophisticated
    # logic, like removing nodes based on their centrality etc...
    nodes_to_remove = random.sample(sorted(cache_nodes), n_removed_nodes)

    return nodes_to_remove


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
N_REPLICATIONS = 1

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icarus/execution/collectors.py
DATA_COLLECTORS = ["LATENCY", "CACHE_HIT_RATIO", "SUCCESS"]

# Number of content objects
N_CONTENTS = 10 ** 5

# Number of content requests generated to prepopulate the caches
# These requests are not logged
N_WARMUP_REQUESTS = 10 ** 2

# Number of content requests generated after the warmup and logged
# to generate results.
N_MEASURED_REQUESTS = 4 * 10 ** 2

ALPHA = 1.0

# Number of requests per second (over the whole network)
NETWORK_REQUEST_RATE = 1

# List of caching and routing strategies
# The code is located in ./icarus/models/strategy.py
STRATEGIES = [
    "LCE",  # Leave Copy Everywhere
    "NO_CACHE",  # No caching, shorest-path routing
    "HR_SYMM",  # Symmetric hash-routing
    "HR_ASYMM",  # Asymmetric hash-routing
    "HR_MULTICAST",  # Multicast hash-routing
    "CL4M",  # Cache less for more
    "PROB_CACHE",  # ProbCache
    "LCD",  # Leave Copy Down
    "RAND_CHOICE",  # Random choice: cache in one random cache on path
    "RAND_BERNOULLI",  # Random Bernoulli: cache randomly in caches on path
]

# Queue of experiments
EXPERIMENT_QUEUE = deque()

# Create experiment
default = Tree()

# Specify topology
#default["topology"]["name"] = "ROCKET_FUEL"
#default["topology"]["asn"] = 1221

TOPOLOGIES = "GEANT"

default["topology"]["name"] = TOPOLOGIES

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
# Supported policies are: 'LRU', 'LFU', 'FIFO', 'RAND' and 'NULL'
# Cache policy implmentations are located in ./icarus/models/cache.py
CACHE_POLICY = "LRU"

# Set cache replacement policy
default["cache_policy"]["name"] = CACHE_POLICY

default["desc"] = "testing"

default["topology"]["removed_nodes"] = get_nodes_to_remove(default["topology"], 3)

for strategy in STRATEGIES:
    experiment = copy.deepcopy(default)
    experiment["strategy"]["name"] = strategy
    EXPERIMENT_QUEUE.append(experiment)
