import os
import csv
import time



from addax.data_structures.graph import Graph
from addax.utilities.dataIO import ReadGraph, WriteGraph, PickleData
from addax.data_structures.enumeration import CalculateAscendingEnumerationIndex



def ConstructGraphFromHemiBrainCSV(MODERATE_THRESHOLD = 4, STRONG_THRESHOLD = 10):
    """
    Construct a graph object for the hemi brain CSV files

    @param MODERATE_THRESHOLD: two neurons with fewer than this number of synapses are not connected
    @param STRONG_THRESHOLD: two neurons with more than this numberof synapses are strongly connected
    """
    # start statistics
    start_time = time.time()

    neurons = set()
    neuron_ids = set()
    edges = {}

    neuron_types = set()

    # open the neuron csv file
    neuron_filename = 'CSVs/HemiBrain/traced-neurons.csv'
    with open(neuron_filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')

        # skip header
        next(csv_reader, None)
        for row in csv_reader:
            neuron_id = int(row[0])
            neuron_type = row[1]

            assert (not neuron_id in neurons)
            # add this neuron to the list of neurons
            neurons.add((neuron_id, neuron_type))
            neuron_ids.add(neuron_id)
            neuron_types.add(neuron_type)

    # read the synapses by region of interest
    synapse_filename = 'CSVs/HemiBrain/traced-roi-connections.csv'
    with open(synapse_filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')

        # skip header
        next(csv_reader, None)
        for row in csv_reader:
            pre_neuron_id = int(row[0])
            post_neuron_id = int(row[1])
            weight = int(row[3])

            assert (pre_neuron_id in neuron_ids)
            assert (post_neuron_id in neuron_ids)

            # update the connective strength between these two neurons
            if not (pre_neuron_id, post_neuron_id) in edges:
                edges[(pre_neuron_id, post_neuron_id)] = weight
            else:
                edges[(pre_neuron_id, post_neuron_id)] += weight

    # create a mapping from type names to ints
    neuron_type_mapping = {}
    for index, type in enumerate(sorted(neuron_types)):
        neuron_type_mapping[type] = index

    # remove edges that are below a threshold, must first convert keys into a list in python 3
    pruned_edges = [(pre, post) for (pre, post), weight in edges.items() if weight < MODERATE_THRESHOLD]
    for (pre, post) in pruned_edges:
        del edges[(pre, post)]

    # construct a directed graph object
    graph = Graph('hemi-brain', directed = True, vertex_colored = True, edge_colored = True)

    # add vertices with communities initially at -1
    for enumeration_index, (neuron, neuron_type) in enumerate(sorted(neurons)):
        # vertices start with  the default coloring of -1, enumeration_index of -1
        graph.AddVertex(neuron, enumeration_index, community = -1, color = neuron_type_mapping[neuron_type])

    # add edges with the synaptic weights
    for (pre_neuron_id, post_neuron_id) in edges.keys():
        # edges between the MODERATE_THRESHOLD and STRONG_THRESHOLD have moderate strength
        # edges with STRONG_THRESHOLD or more synapses are strongly connected
        has_moderate_strength = int(edges[(pre_neuron_id, post_neuron_id)] < STRONG_THRESHOLD)
        # use (1 - has_moderate_strength) to have moderate edges 0 weight and strong edges weight of one
        graph.AddEdge(pre_neuron_id, post_neuron_id, weight = edges[(pre_neuron_id, post_neuron_id)], color = (1 - has_moderate_strength))

    # reverse the type mapping to go from index to name
    vertex_type_mapping = {}
    for neuron_type, index in neuron_type_mapping.items():
        vertex_type_mapping[index] = neuron_type

    edge_type_mapping = {
        0: 'MODERATE STRENGTH',
        1: 'STRONG STRENGTH',
    }

    # set the vertex and edge type mapping
    graph.SetVertexTypeMapping(vertex_type_mapping)
    graph.SetEdgeTypeMapping(edge_type_mapping)

    # write the hemibrain graph to disk
    if not os.path.exists('graphs'):
        os.makedirs('graphs', exist_ok = True)

    # output this graph
    output_filename = 'graphs/hemi-brain.graph.bz2'
    WriteGraph(graph, output_filename)

    # write the condensed CSV neuron and edge files
    with open('CSVs/HemiBrain/condensed-neurons.csv', 'w') as fd:
        fd.write('Neuron ID,Community,Color Index,Color Name\n')
        for neuron in graph.vertices.values():
            fd.write('{},{},{},{}\n'.format(neuron.index, neuron.community, neuron.color, graph.vertex_type_mapping[neuron.color]))

    nstrong_connections = 0
    nmoderate_connections = 0

    with open('CSVs/HemiBrain/condensed-edges.csv', 'w') as fd:
        fd.write('Pre Synaptic Neuron ID,Post Synaptic Neuron ID,Weight,Color Index,Color Name,\n')
        for edge in graph.edges.values():
            fd.write('{},{},{},{},{}\n'.format(edge.source_index, edge.destination_index, edge.weight, edge.color, graph.edge_type_mapping[edge.color]))

            if edge.color: nstrong_connections += 1
            else: nmoderate_connections += 1

    # print statistics
    print ('No. Neurons: {}'.format(len(neurons)))
    print ('No. Edges: {}'.format(len(edges)))
    print ('  Strong Connections: {}'.format(nstrong_connections))
    print ('  Moderate Connections: {}'.format(nmoderate_connections))
    print ('No. Neuron Types: {}'.format(len(neuron_types)))

    print ('Wrote {} in {:0.2f} seconds.'.format(output_filename, time.time() - start_time))

    CalculateAscendingEnumerationIndex(graph, 'minimum')
