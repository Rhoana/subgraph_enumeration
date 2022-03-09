import time
import metis



import numpy as np
import networkx as nx
import community as community_louvain



from addax.utilities.dataIO import WriteGraph



def GraphAsUndirectedNetworkx(graph):
    """
    Return the graph as a networkx graph
    """
    # initialize a networkx graph
    G = nx.Graph()

    # add all vertices
    for vertex_index in sorted(graph.vertices.keys()):
        G.add_node(vertex_index)

    # add all edges to the network x graph
    for edge in graph.edges.values():
        G.add_edge(edge.source_index, edge.destination_index, weight=edge.weight)

    return G



def DetectCommunities(graph):
    """
    Returns a list of communities based on a few representative algorithms.

    @param graph: the graph to cluster into communities
    """
    # call metis algorithm
    networkx_graph = GraphAsUndirectedNetworkx(graph)

    # calculate the METIS partitions
    start_time = time.time()
    for partition_target in [5, 10, 15, 20, 25, 30]:
        edgecuts, metis_partition = metis.part_graph(networkx_graph, partition_target)
        print ('Calculated METIS partitions in {:0.2f} seconds'.format(time.time() - start_time))

        for iv, vertex_index in enumerate(sorted(graph.vertices.keys())):
            graph.vertices[vertex_index].community = metis_partition[iv]

        # save the graph
        old_prefix = graph.prefix
        graph.prefix = '{}-metis-{:02d}'.format(graph.prefix, partition_target)

        output_filename = 'graphs/{}.graph.bz2'.format(graph.prefix)
        WriteGraph(graph, output_filename)

        # update the graph prefix to the original
        graph.prefix = old_prefix

        npartitions = np.max(metis_partition) + 1
        partition_counts = [0 for _ in range(npartitions)]

        for iv in range(len(metis_partition)):
            partition_counts[metis_partition[iv]] += 1

        print ('  No. Partitions: {}'.format(npartitions))
        print ('  Max Size: {}'.format(max(partition_counts)))
        print ('  Min Size: {}'.format(min(partition_counts)))

    # calculate the louvain partition
    start_time = time.time()
    louvain_partition = community_louvain.best_partition(networkx_graph)
    print ('Calculated Louvain partitions in {:0.2f} seconds'.format(time.time() - start_time))

    for vertex_index in graph.vertices.keys():
        graph.vertices[vertex_index].community = louvain_partition[vertex_index]

    # save the graph
    old_prefix = graph.prefix
    graph.prefix = '{}-louvain'.format(graph.prefix)

    output_filename = 'graphs/{}.graph.bz2'.format(graph.prefix)
    WriteGraph(graph, output_filename)

    # update the graph prefix to the original
    graph.prefix = old_prefix

    npartitions = np.max(list(louvain_partition.values())) + 1
    partition_counts = [0 for _ in range(npartitions)]

    for partition in louvain_partition.values():
        partition_counts[partition] += 1

    print ('  No. Partitions: {}'.format(npartitions))
    print ('  Max Size: {}'.format(max(partition_counts)))
    print ('  Min Size: {}'.format(min(partition_counts)))
