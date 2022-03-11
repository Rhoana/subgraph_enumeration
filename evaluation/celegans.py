from subgraph_enumeration.utilities.dataIO import ReadGraph



def CompareCElegansSexes():
    """
    Compare the two graphs of the C. elegans sexes
    """
    # read the two graphs
    hermaphrodite_graph = ReadGraph('graphs/C-elegans-sex-hermaphrodite-minimum.graph.bz2')
    male_graph = ReadGraph('graphs/C-elegans-sex-male-minimum.graph.bz2')

    # create a list of the shared neurons
    shared_neurons = set()
    for vertex in male_graph.vertices.values():
        neuron_type = male_graph.vertex_type_mapping[vertex.color]

        # skip neurons that are not in the hermaphrodite
        if not neuron_type in hermaphrodite_graph.vertex_type_mapping.values(): continue

        shared_neurons.add(neuron_type)

    # create a mapping from hermaphrodite vertex types to vertex indices
    hermaphrodite_neuron_type_to_index = {}
    for vertex_index, vertex in hermaphrodite_graph.vertices.items():
        neuron_type = hermaphrodite_graph.vertex_type_mapping[vertex.color]
        assert (not neuron_type in hermaphrodite_neuron_type_to_index)
        hermaphrodite_neuron_type_to_index[neuron_type] = vertex_index

    # print neuron statistics
    print ('Shared Vertices: {}'.format(len(shared_neurons)))
    print ('Male-Only Vertices: {}'.format(len(male_graph.vertices) - len(shared_neurons)))
    print ('Hermaphrodite-Only Vertices: {}'.format(len(hermaphrodite_graph.vertices) - len(shared_neurons)))

    # count the number of shared edges
    shared_edges = 0
    # iterate through every edge in the male worm
    for (source_index, destination_index) in male_graph.edges:
        source_neuron = male_graph.vertex_type_mapping[male_graph.vertices[source_index].color]
        destination_neuron = male_graph.vertex_type_mapping[male_graph.vertices[destination_index].color]

        # skip if this pair is not in the hermaphrodite
        if not source_neuron in hermaphrodite_neuron_type_to_index: continue
        if not destination_neuron in hermaphrodite_neuron_type_to_index: continue

        hermaphrodite_source_index = hermaphrodite_neuron_type_to_index[source_neuron]
        hermaphrodite_destination_index = hermaphrodite_neuron_type_to_index[destination_neuron]

        if (hermaphrodite_source_index, hermaphrodite_destination_index) in hermaphrodite_graph.edges:
            shared_edges += 1

    print ('Shared Edges: {}'.format(shared_edges))
    print ('Male-Only Edges: {}'.format(len(male_graph.edges) - shared_edges))
    print ('Hermaphrodite-Only Edges: {}'.format(len(hermaphrodite_graph.edges) - shared_edges))
