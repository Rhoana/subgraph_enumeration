import os
import time
import random



from addax.data_structures.graph import Graph
from addax.utilities.dataIO import WriteGraph
from addax.visualize.graph import VisualizeGraph



def GenerateSimpleRandomGraphs(N, nnodes, nedges, directed):
    """
    Generate a simple random graph that randomly chooses edges to connect vertices

    @param N: the number of random graphs to generate
    @param nnodes: the number of nodes in the random graph
    @param nedges: the number of edges in the random graph
    @param directed: are the edges directed or not
    """

    for ii in range(N):
        # create an array of vertex indices (connectomes have non consecutive indices)
        vertex_indices = random.sample(range(2**31, 2**32), nnodes)

        # for directed graphs, all combinations of two nodes, outside of self loops, are valid edges
        if directed: edges = [(vertex_one, vertex_two) for vertex_one in vertex_indices for vertex_two in vertex_indices if not vertex_one == vertex_two]
        # for undirected graphs, unique combinations of two nodes are valid (non-parallel) edges
        else: edges = [(vertex_indices[iv1], vertex_indices[iv2]) for iv1 in range(nnodes) for iv2 in range(iv1 + 1, nnodes)]

        # take the first nedges of the edges array to add to the graph
        random.shuffle(edges)
        edges = edges[:nedges]

        # create a new graph object
        prefix = 'nnodes-{}-nedges-{}-directed-{:05d}'.format(nnodes, nedges, ii)
        graph = Graph(directed)

        # add the vertex indices (there are no communities in this simple graph)
        for vertex_index in vertex_indices:
            graph.AddVertex(vertex_index)

        # add the edges for this graph
        for edge in edges:
            # there are no weights in this simple graph
            graph.AddEdge(edge[0], edge[1])

        # write the simple graph to file
        if directed: output_filename = 'random/simple/graphs/{}.graph.bz2'.format(prefix)
        else: output_filename = 'random/simple/graphs/{}.graph.bz2'.format(prefix)

        WriteGraph(graph, output_filename)

        # visualize the graph
        if directed: output_filename = 'random/simple/visuals/{}.dot'.format(prefix)
        else: output_filename = 'random/simple/visuals/{}.dot'.format(prefix)

        VisualizeGraph(graph, output_filename)



def SimpleConfigurationModelRandomGraphs(graph, ngraphs):
    """
    Generate random graphs using a configuration model which guarantees approximately
    the same degree distribution. This simple method ignores all communities.

    @param graph: the input graph to emulate
    @param ngraphs: the number of random graphs to create
    """
    for graph_index in range(ngraphs):
        # print statistics
        total_time = time.time()

        # get a new prefix for the random graph
        prefix = '{}-simple-configuration-model-random-graph-{:03d}'.format(graph.prefix, graph_index)

        # construct a random graph
        random_graph = Graph(prefix, graph.directed, graph.colored)

        # get the output directory for this random graph
        output_directory = 'random/simple-configuration-model/graphs'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok = True)

        # skip if this random graph already exists
        output_filename = '{}/{}.graph.bz2'.format(output_directory, random_graph.prefix)
        if os.path.exists(output_filename): continue

        # create the degree lists for the in and out half edges
        incoming_degree_list = []
        outgoing_degree_list = []

        for edge in graph.edges:
            incoming_degree_list.append(edge.source_index)
            outgoing_degree_list.append(edge.destination_index)

        # shuffle both the incoming and outgoing edge lists
        random.shuffle(incoming_degree_list)
        random.shuffle(outgoing_degree_list)

        # create vertices for the random graph
        for enumeration_index, vertex_index in enumerate(sorted(graph.vertices.keys())):
            random_graph.AddVertex(vertex_index, enumeration_index, community = -1, color = graph.vertices[vertex_index].color)

        edges = set()

        # add edges to the graph
        nedges = len(incoming_degree_list)
        for ie in range(nedges):
            # skip self loops
            if incoming_degree_list[ie] == outgoing_degree_list[ie]: continue
            # skip multi edges
            if (incoming_degree_list[ie], outgoing_degree_list[ie]) in edges: continue

            random_graph.AddEdge(incoming_degree_list[ie], outgoing_degree_list[ie])

            edges.add((incoming_degree_list[ie], outgoing_degree_list[ie]))

        # create the communities for this graph
        partitions = random_graph.DetectCommunities()
        for vertex, partition in partitions.items():
            graph.vertices[vertex].community = partition

        # write the graph to file
        WriteGraph(random_graph, output_filename)

        total_time = time.time() - total_time
        print ('Generation time: {:0.2f} seconds'.format(total_time))

        # write timing statistics to disk
        timing_directory = 'timings/simple-configuration-models/'
        if not os.path.exists(timing_directory):
            os.makedirs(timing_directory, exist_ok = True)
        timing_filename = '{}/{}.txt'.format(timing_directory, random_graph.prefix)

        with open(timing_filename, 'w') as fd:
            fd.write('Generation Time: {:0.2f} seconds\n'.format(total_time))
