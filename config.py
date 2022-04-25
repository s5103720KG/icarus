"""This module contains all configuration information used to run simulations.

Overview
========

This reference configuration file is divided into two parts.
The first part lists generic simulation parameters such as number of processes
to use, logging configuration and so on.
The second part builds an "experiment queue", i.e. a queue of configuration
parameters each representing one single experiment.

Each element of the queue must be an instance of the icarus.util.Tree class,
which is an object modelling a tree of hierarchically organized configuration
parameters. Alternatively nested dictionaries can be used instead of trees. In
this case Icarus will convert them to trees at runtime. It is however suggested
to use Tree objects because they provide methods that simplify the definition
of experiments.

Experiment definition syntax
============================

This figure below represents the parameter structure accepted by Icarus:

 |
 |--- topology
 |        |----- name
 |        |----- topology arg 1
 |        |----- topology arg 2
 |        |----- ..............
 |        |----- topology arg N
 |
 |--- workload
 |        |----- name
 |        |----- workload arg 1
 |        |----- workload arg 2
 |        |----- ..............
 |        |----- workload arg N
 |
 |--- cache_placement
 |        |----- name
 |        |----- cache_placement arg 1
 |        |----- cache_placement arg 2
 |        |----- ......................
 |        |----- cache_placement arg N
 |
 |--- content_placement
 |        |----- name
 |        |----- content_placement arg 1
 |        |----- content_placement arg 2
 |        |----- .......................
 |        |----- content_placement arg N
 |
 |--- strategy
 |        |----- name
 |        |----- strategy arg 1
 |        |----- strategy arg 2
 |        |----- ..............
 |        |----- strategy arg N
 |
 |--- cache_policy
 |        |----- name
 |        |----- cache_policy arg 1
 |        |----- cache_policy arg 2
 |        |----- ..................
 |        |----- cache_policy arg N
 |


Here below are listed all components currently provided by Icarus and lists
all parameters for each of them

topology
--------

Path topology
 * name: PATH
 * args:
    * n: number of nodes

Tree topology
 * name: TREE
 * args:
    * h: height
    * k: branching factor

RocketFuel topologies
 * name: ROCKET_FUEL
 * args:
     * asn: ASN of topology selected (see resources/README.md for further info)
     * source_ratio: ratio of nodes to which attach a content source
     * ext_delay: delay of interdomain links

Internet Topology Zoo topologies
 * name: GARR, GEANT, TISCALI, WIDE, GEANT_2, GARR_2, TISCALI_2
 * args: None


workload
--------

Stationary Zipf workload
 * name: STATIONARY
 * args:
    * alpha : float, the Zipf alpha parameter
    * n_contents: number of content objects
    * n_warmup: number of warmup requests
    * n_measured: number of measured requests
    * rate: requests rate

GlobeTraff workload
 * name: GLOBETRAFF
 * args:
    * reqs_file: the path to a GlobeTraff request file
    * contents_file: the path to a GlobeTraff content file

Trace-driven workload
 * name: TRACE_DRIVEN
 * args:
    * reqs_file: the path to the requests file
    * contents_file: the path to the contents file
    * n_contents: number of content objects
    * n_warmup: number of warmup requests
    * n_measured: number of measured requests


content_placement
-----------------
Uniform (content uniformly distributed among servers)
 * name: UNIFORM
 * args: None


cache_placement
---------------
 * name:
    * UNIFORM -> cache space uniformly spread across caches
    * CONSOLIDATED -> cache space consolidated among nodes with top betweenness centrality
    * BETWEENNESS_CENTRALITY -> cache space assigned to all candidate nodes proportionally to their betweenness centrality
    * DEGREE -> cache space assigned to all candidate nodes proportionally to their degree
 * args
    * For all:
       * network_cache: overall network cache (in number of entries) as fraction of content catalogue
    * For CONSOLIDATED
       * spread: The fraction of top centrality nodes on which caches are deployed (optional, default: 0.5)


strategy
--------
 * name:
    * LCE             ->  Leave Copy Everywhere
    * NO_CACHE        ->  No caching, shorest-path routing
    * HR_SYMM         ->  Symmetric hash-routing
    * HR_ASYMM        ->  Asymmetric hash-routing
    * HR_MULTICAST    ->  Multicast hash-routing
    * HR_HYBRID_AM    ->  Hybrid Asymm-Multicast hash-routing
    * HR_HYBRID_SM    ->  Hybrid Symm-Multicast hash-routing
    * CL4M            ->  Cache less for more
    * PROB_CACHE      ->  ProbCache
    * LCD             ->  Leave Copy Down
    * RAND_CHOICE     ->  Random choice: cache in one random cache on path
    * RAND_BERNOULLI  ->  Random Bernoulli: cache randomly in caches on path
 * args:
    * For PROB_CACHE
       * t_tw : float, optional, default=10. The ProbCache t_tw parameter
    * For HR_HYBRID_AM
       * max_stretch: float, optional, default=0.2.
         The max detour stretch for selecting multicast


cache_policy
------------
 * name:
    * LRU   -> Least Recently Used
    * SLRU  -> Segmeted Least Recently Used
    * LFU   -> Least Frequently Used
    * NULL  -> No cache
    * RAND  -> Random eviction
    * FIFO  -> First In First Out
 * args:
    * For SLRU:
       * segments: int, optional, default=2. Number of segments


desc
----
string describing the experiment (used to print on screen progress information)

Further info
============

To get further information about the models implemented in the simulator you
can inspect the source code which is well organized and documented:
 * Topology implementations are located in ./icarus/scenarios/topology.py
 * Cache placement implementations are located in
   ./icarus/scenarios/cacheplacement.py
 * Caching and routing strategies located in ./icarus/models/strategy.py
 * Cache eviction policy implementations are located in ./icarus/models/cache.py
"""
from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

############################## GENERAL SETTINGS ##############################

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = cpu_count()

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported
RESULTS_FORMAT = "PICKLE"

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 3

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icarus/execution/collectors.py
# Remove collectors not needed
DATA_COLLECTORS = [
    "CACHE_HIT_RATIO",  # Measure cache hit ratio
    "LATENCY",  # Measure request and response latency (based on static link delays)
    "LINK_LOAD",  # Measure link loads
    "PATH_STRETCH",  # Measure path stretch
]


########################## EXPERIMENTS CONFIGURATION ##########################

# Default experiment values, i.e. values shared by all experiments

# Number of content objects
N_CONTENTS = 3 * 10 ** 5

# Number of content requests generated to pre-populate the caches
# These requests are not logged
N_WARMUP_REQUESTS = 3 * 10 ** 5

# Number of content requests that are measured after warmup
N_MEASURED_REQUESTS = 6 * 10 ** 5

# Number of requests per second (over the whole network)
REQ_RATE = 1.0

# Cache eviction policy
CACHE_POLICY = "LRU"

# Zipf alpha parameter, remove parameters not needed
ALPHA = [0.6, 0.8, 1.0]

# Total size of network cache as a fraction of content population
# Remove sizes not needed
NETWORK_CACHE = [0.004, 0.002]


# List of topologies tested
# Topology implementations are located in ./icarus/scenarios/topology.py
# Remove topologies not needed
TOPOLOGIES = [
    "GEANT",
    "WIDE",
    "GARR",
    "TISCALI",
]

# List of caching and routing strategies
# The code is located in ./icarus/models/strategy/*.py
# Remove strategies not needed
STRATEGIES = [
    "LCE",  # Leave Copy Everywhere
    "NO_CACHE",  # No caching, shortest-path routing
    "HR_SYMM",  # Symmetric hash-routing
    "HR_ASYMM",  # Asymmetric hash-routing
    "HR_MULTICAST",  # Multicast hash-routing
    "HR_HYBRID_AM",  # Hybrid Asymm-Multicast hash-routing
    "HR_HYBRID_SM",  # Hybrid Symm-Multicast hash-routing
    "CL4M",  # Cache less for more
    "PROB_CACHE",  # ProbCache
    "LCD",  # Leave Copy Down
    "RAND_CHOICE",  # Random choice: cache in one random cache on path
    "RAND_BERNOULLI",  # Random Bernoulli: cache randomly in caches on path
]

# Instantiate experiment queue
EXPERIMENT_QUEUE = deque()

# Build a default experiment configuration which is going to be used by all
# experiments of the campaign
default = Tree()
default["workload"] = {
    "name": "STATIONARY",
    "n_contents": N_CONTENTS,
    "n_warmup": N_WARMUP_REQUESTS,
    "n_measured": N_MEASURED_REQUESTS,
    "rate": REQ_RATE,
}
default["cache_placement"]["name"] = "UNIFORM"
default["content_placement"]["name"] = "UNIFORM"
default["cache_policy"]["name"] = CACHE_POLICY

# Create experiments multiplexing all desired parameters
for alpha in ALPHA:
    for strategy in STRATEGIES:
        for topology in TOPOLOGIES:
            for network_cache in NETWORK_CACHE:
                experiment = copy.deepcopy(default)
                experiment["workload"]["alpha"] = alpha
                experiment["strategy"]["name"] = strategy
                experiment["topology"]["name"] = topology

                # If you want to simulate a failure, add this configuration
                # option that lists the names of the nodes you want to remove.
                # The name of the nodes to remove (326, 340, 343 in this example)
                # depends on the specific topology. You need to look at the topology
                # what the node names are decide which to remove.
                # To see the list of nodes in a topology, you can run Python and run the following commands.

                # >>> import icarus.registry
                # >>> topology = icarus.registry.TOPOLOGY_FACTORY["TISCALI"]()
                # >>> print(topology.nodes)
                # [16, 214, 341, 153, 203, 303, 319, 320, 326, 340, 343, 363, 390, 391, 159, 207, 217, 235, 236, 237, 239, 590, 176, 178, 177, 188, 219, 179, 196, 197, 199, 210, 238, 241, 242, 243, 190, 180, 184, 186, 209, 181, 183, 185, 208, 218, 224, 249, 250, 227, 187, 191, 189, 221, 192, 270, 193, 269, 194, 195, 201, 245, 200, 266, 198, 220, 212, 228, 231, 257, 259, 211, 213, 204, 205, 222, 252, 256, 253, 254, 355, 530, 531, 532, 535, 536, 223, 232, 234, 251, 589, 225, 226, 405, 408, 409, 412, 418, 429, 431, 432, 433, 439, 233, 230, 229, 413, 419, 423, 430, 434, 435, 436, 437, 438, 447, 449, 450, 265, 267, 244, 246, 261, 247, 248, 260, 262, 268, 567, 300, 302, 305, 316, 362, 301, 304, 327, 306, 374, 313, 312, 513, 548, 315, 321, 322, 345, 346, 509, 377, 522, 523, 330, 339, 332, 333, 334, 527, 528, 335, 525, 336, 337, 338, 351, 352, 353, 354, 356, 357, 358, 378, 389, 348, 342, 533, 537, 347, 393, 371, 506, 507, 508, 540, 516, 361, 368, 364, 367, 541, 542, 372, 373, 551, 383, 392, 547, 379, 380, 381, 382, 553, 387, 388, 394, 440, 406, 441, 407, 414, 442, 443, 444, 410, 415, 446, 411, 452, 453, 416, 417, 424, 458, 459, 460, 420, 422, 425, 421, 427, 426, 451, 448, 445, 455, 456, 457, 454, 534, 543]

                if topology == "TISCALI":
                    experiment["topology"]["removed_nodes"] = [326, 340, 343]

                experiment["cache_placement"]["network_cache"] = network_cache
                experiment[
                    "desc"
                ] = "Alpha: {}, strategy: {}, topology: {}, network cache: {}".format(
                    str(alpha),
                    strategy,
                    topology,
                    str(network_cache),
                )
                EXPERIMENT_QUEUE.append(experiment)
