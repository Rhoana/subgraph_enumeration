import os
import time
import random



from addax.data_structures.graph import Graph
from addax.utilities.dataIO import WriteGraph



def CommunityBasedConfigurationModelRandomGraphs(graph, ngraphs):
    """
    Generate random graphs using a community-based configuration model which
    guarantees approximately the same degree distribution

    @param graph: the input graph to emulate
    @param ngraphs: the number of random graphs to create
    """
    for graph_index in range(ngraphs):
        # print statistics
        total_time = time.time()

        # get a new prefix for the random graph
        prefix = '{}-community-based-configuration-model-random-graph-{:03d}'.format(graph.prefix, graph_index)

        # construct a random graph
        random_graph = Graph(prefix, graph.directed, graph.colored)

        # get the output directory for this random graph
        output_directory = 'random/community-based-configuration-models/graphs'
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok = True)

        # skip if this random graph already exists
        output_filename = '{}/{}.graph.bz2'.format(output_directory, random_graph.prefix)
        if os.path.exists(output_filename): continue

        # create the degree lists for the in and out half edges
        incoming_degree_list = {}
        outgoing_degree_list = {}

        for edge in graph.edges:
            # get the community for both the source and destination
            source_index = edge.source_index
            source_community = graph.vertices[source_index].community

            destination_index = edge.destination_index
            destination_community = graph.vertices[destination_index].community

            # add incoming and outcoming edges for this community pair
            community_one = min(source_community, destination_community)
            community_two = max(source_community, destination_community)

            if not (community_one, community_two) in incoming_degree_list:
                incoming_degree_list[(community_one, community_two)] = []
                outgoing_degree_list[(community_one, community_two)] = []

            incoming_degree_list[(community_one, community_two)].append(source_index)
            outgoing_degree_list[(community_one, community_two)].append(destination_index)

        # shuffle the incoming and outgoing edge lists for every community pair
        for (community_one, community_two) in incoming_degree_list:
            random.shuffle(incoming_degree_list[(community_one, community_two)])
            random.shuffle(outgoing_degree_list[(community_one, community_two)])

        # create vertices for the random graph
        for enumeration_index, vertex_index in enumerate(sorted(graph.vertices.keys())):
            random_graph.AddVertex(vertex_index, enumeration_index, community = graph.vertices[vertex_index].community, color = graph.vertices[vertex_index].color)

        edges = set()

        # add edges to the graph
        for (community_one, community_two) in incoming_degree_list:
            nedges = len(incoming_degree_list[(community_one, community_two)])

            for ie in range(nedges):
                source_index = incoming_degree_list[(community_one, community_two)][ie]
                destination_index = outgoing_degree_list[(community_one, community_two)][ie]

                # skip self loops
                if source_index == destination_index: continue
                # skip multi edges
                if (source_index, destination_index) in edges: continue

                random_graph.AddEdge(source_index, destination_index)

                edges.add((source_index, destination_index))

        # write the graph to file
        WriteGraph(random_graph, output_filename)

        total_time = time.time() - total_time
        print ('Generation time: {:0.2f} seconds'.format(total_time))

        # write timing statistics to disk
        timing_directory = 'timings/community-based-configuration-models/'
        if not os.path.exists(timing_directory):
            os.makedirs(timing_directory, exist_ok = True)
        timing_filename = '{}/{}.txt'.format(timing_directory, random_graph.prefix)

        with open(timing_filename, 'w') as fd:
            fd.write('Generation Time: {:0.2f} seconds\n'.format(total_time))
