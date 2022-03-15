## Installation

This library requires the C++ nauty library found [here](https://pallini.di.uniroma1.it/#howtogetit). Install this library first using their provided instructions.

```
git clone https://github.com/Rhoana/subgraph_enumeration.git
cd subgraph_enumeration
conda create -n motif_env --file requirements.txt
conda activate motif_env
```
Open `kavosh/setup.py` in any text editor. Change line 15 to reference the folder where you installed Nauty.

```
cd kavosh
python setup.py build_ext --inplace
```

From here, we assume that the parent directory of subgraph_enumeration is in the python path.

## Graph Creation

This library uses a custom graph class for subgraph enumeration. First, construct an empty graph:

```
from subgraph_enumeration.data_structures.graph import Graph
from subgraph_enumeration.data_structures.enumeration import CalculateAscendingEnumerationIndex
from subgraph_enumeration.utilities.dataIO import WriteGraph


# @param identifier is a unique string that will be used to differentiate this graph from others.
# Note, this identifier should be globally unique - files will be saved in set locations 
# based on the string value.
# @param directed is a boolean for if edges are directed.
# @param vertex_colored is a boolean for if the vertices have labels or colors.
# @param edge_colored is a boolean for if the edges have labels or colors.

graph = Graph(identifier, directed, vertex_colored, edge_colored)

# add vertices 
for enumeration_index, (neuron, neuron_type) in enumerate(sorted(neurons)):
    # @param neuron: a unique integer identifier for this neuron.
    # @param enumeration_index: the enumeration order (will be optimized later).
    # @param community: what brain region or community the neuron belongs to (default = -1).
    # @param color: the label for the neuron as an integer (strings can be assigned to types later).
    graph.AddVertex(neuron, enumeration_index, community = -1, color = neuron_type)

# add edges
for (pre_neuron_id, post_neuron_id, weight, edge_type) in edges:
    # @param pre_neuron_id: the source node (neuron).
    # @param post_neuron_id: the destination node (neuron).
    # @param weight: the weight of the edge (number of synapses or perceived strength)
    # @param edge_type: the label for the edge as an integer (strings can be assigned to types later).
    graph.AddEdge(pre_neuron_id, post_neuron_id, weight, edge_type)

# these keys correspond to the neuron_type integers above 
vertex_type_mapping = {
    0: 'glial_cell', 
    1: 'end_organ',
    .
    . 
    .
}

# these keys correspond to the edge type integers above 
edge_type_mapping = {
    0: 'excitatory', 
    1: 'inhibitory',
}

graph.SetVertexTypeMapping(vertex_type_mapping)
graph.SetEdgeTypeMapping(edge_type_mapping)

# where to save the file (should end with bz2 for significant space savings)
output_filename = 'graphs/connectome.graph.bz2'
WriteGraph(graph, output_filename)

# recalculate the enumeration index based on methods discussed in paper
# @param graph: the graph data structure created above 
# @param method: should always be minimum (optimal heuristic found)
CalculateAscendingEnumerationIndex(graph, 'minimum')
```

This will create a new graph 'graphs/connectome-minimum.graph.bz2'. This filename should be given as the input to all other functions.

Example of graph construction can be found in `celegans/construction.py` and `hemibrain/construction.py`. The referenced CSV files can be found on the [website](https://www.rhoana.org/subgraph_enumeration).

## Enumeration

```
from subgraph_enumeration.kavosh.enumerate import EnumerateSubgraphsSequentially, CombineEnumeratedSubgraphs

# Call both functions to enumerate subgraphs sequentially.
# @param filename: the location of the graph.bz2 file. It is best to use the created 
# graph from running CalculateAscendingEnumerationIndex.
# @param k: the integer size of the subgraphs to identify.
# @param vertex_color: boolean for motif discovery with vertex colors.
# @param edge_colors: boolean for motif discovery with edge colors.
# @param community: boolean for motif discovery with community divide-and-conquer.
# Note, either vertex color or edge colors may be True, but not both. They can both be false.

EnumerateSubgraphsSequentially(filename, k, vertex_colored, edge_colored, community_based)
CombineEnumeratedSubgraphs(filename, k, vertex_colored, edge_colored, community_based)
```

To run in parallel:

```
from subgraph_enumeration.kavosh.enumerate import EnumerateSubgraphsFromNodes

# @param filename: the location of the graph.bz2 file. 
# It is best to use the created graph from running CalculateAscendingEnumerationIndex.
# @param k: the integer size of the subgraphs to identify.
# @param nodes: the neuron ids to enumerate from.
# @param output_suffix: a unique string identifier for this parallel call. 
# Files are created based on this identifier. Do not use the same identifier for 
# different threads for the same filename.
# @param vertex_color: boolean for motif discovery with vertex colors.
# @param edge_colors: boolean for motif discovery with edge colors.
# @param community: boolean for motif discovery with community divide-and-conquer.
# Note, either vertex color or edge colors may be True, but not both. They can both be false.

EnumerateSubgraphsFromNodes(filename, k, nodes, output_suffix, vertex_colored, edge_colored, community_based)
```
After enumerating from each vertex, you will need to run the following line to aggregate results into one file.

```
from subgraph_enumeration.kavosh.enumerate import CombineEnumeratedSubgraphs

CombineEnumeratedSubgraphs(filename, k, vertex_colored, edge_colored, community_based)
```

There is an optional write_subgraphs flag which will write the subgraphs found to disk. This should only be used on very small graphs since the number of subgraphs becomes exceptionally large and can quickly fill up an entire hard drive!

## Parsing Certificates

There are functions to parse a certificate created by motif discovery. Certificate files have the form:

```
Found N unique subgraphs.
certificate-#1: noccurrences
certificate-#2: noccurrences
certificate-#3: noccurrences
.
.
.
Enumerated M subgraphs in T seconds.
```
To parse a certificate:

```
# Read the graph
from subgraph_enumeration.utilities.dataIO import ReadGraph

# if enumeration did not include vertex colors, you can add an optional parameter 
# of header_only = True to increase speed.
graph = ReadGraph('connectome-minimum.graph.bz2')

from subgraph_enumeration.kavosh.classify import ParseCertificate

# @param graph: a graph data structure object.
# @param k: the integer size of the motifs.
# @param certificate: the string certificate from Nauty to parse
# @param vertex_colored: boolean for neuron labels or types.
# @param edge_colored: boolean for edge labels or types.
# @param directed: boolean for if the graph is directed.
ParseCertificate(graph, k, certificate, vertex_colored, edge_colored, directed):

```

## Citations

If you use this library, please cite [Nauty](https://pallini.di.uniroma1.it/) and our [paper](https://www.rhoana.org/subgraph_enumeration)
