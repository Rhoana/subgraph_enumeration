import time
import xlrd



from subgraph_enumeration.data_structures.graph import Graph
from subgraph_enumeration.data_structures.enumeration import CalculateAscendingEnumerationIndex
from subgraph_enumeration.utilities.dataIO import ReadGraph, WriteGraph



def ConstructGraphsFromTimelapsedXLSX():
    """
    Construct a set of graphs from the timelapsed xlsx file.
    """
    input_filename = 'CSVs/Timelapsed/connectomes.xlsx'
    workbook = xlrd.open_workbook(input_filename)

    # iterate over all sheets
    nsheets = workbook.nsheets
    for iv in range(nsheets):
        # start statistics
        start_time = time.time()

        sheet = workbook.sheet_by_index(iv)

        # get the size of the adjacency matrix
        nrows = sheet.nrows
        ncols = sheet.ncols

        # create an empty graph
        graph = Graph('C-elegans-timelapsed-{:02}'.format(iv + 1), directed = True, vertex_colored = True, edge_colored = False)

        # craete a mapping from vertex names to indices
        vertex_index_to_name = {}
        for vertex_index, row_index in enumerate(range(2, nrows)):
            # all neuron names are in column B
            neuron_name = sheet.cell_value(row_index, 1)
            vertex_index_to_name[vertex_index] = neuron_name

        # add vertices with communities at -1
        for enumeration_index, (vertex_index, neuron_type) in enumerate(vertex_index_to_name.items()):
            # each vertex receives a unique color since the graphs are stereotyped
            graph.AddVertex(vertex_index, enumeration_index, community = -1, color = vertex_index)

        # add edges based on the wiring diagram
        for pre_synaptic_vertex_index, row_index in enumerate(range(2, nrows)):
            for post_synaptic_vertex_index, col_index in enumerate(range(2, ncols)):
                synaptic_strength = sheet.cell_value(row_index, col_index)
                # skip over edges that do not exist
                if not synaptic_strength: continue

                # skip over self loops
                if pre_synaptic_vertex_index == post_synaptic_vertex_index: continue

                graph.AddEdge(pre_synaptic_vertex_index, post_synaptic_vertex_index, weight=synaptic_strength)

        graph.SetVertexTypeMapping(vertex_index_to_name)

        # get the output filename
        output_filename = 'graphs/{}.graph.bz2'.format(graph.prefix)
        WriteGraph(graph, output_filename)

        # write the condensed CSV neuron and edge files
        with open('CSVs/Timelapsed/C-elegans-timelapsed-{:02d}-condensed-neurons.csv'.format(iv + 1), 'w') as fd:
            fd.write('Neuron ID,Color Name\n')
            for neuron in graph.vertices.values():
                fd.write('{},{}\n'.format(neuron.index, graph.vertex_type_mapping[neuron.color]))

        with open('CSVs/Timelapsed/C-elegans-timelapsed-{:02d}-condensed-edges.csv'.format(iv + 1), 'w') as fd:
            fd.write('Pre Synaptic Neuron ID,Post Synaptic Neuron ID,Weight\n')
            for edge in graph.edges.values():
                fd.write('{},{},{}\n'.format(edge.source_index, edge.destination_index, edge.weight))


        # print statistics
        print ('No. Neurons: {}'.format(len(graph.vertices.keys())))
        print ('No. Edges: {}'.format(len(graph.edges)))

        print ('Wrote {} in {:0.2f} seconds.'.format(output_filename, time.time() - start_time))

        CalculateAscendingEnumerationIndex(graph, 'minimum')



def ConstructGraphsFromSexesXLSX():
    """
    Consutrct a set of graphs from the two different sexes of the C. elegans worm
    """
    # go through connectomes
    input_filename = 'CSVs/Sexes/connectomes.xlsx'
    workbook = xlrd.open_workbook(input_filename)

    # read the four relevant sheets
    sheets = {
        ('male', 'Chemical'): 'male chemical',
        ('male', 'Electrical'): 'male gap jn symmetric',
        ('hermaphrodite', 'Chemical'): 'hermaphrodite chemical',
        ('hermaphrodite', 'Electrical'): 'hermaphrodite gap jn symmetric',
    }

    for sex in ['male', 'hermaphrodite']:
        # start statistics
        start_time = time.time()

        # create a new graph for this connectome
        graph = Graph('C-elegans-sex-{}'.format(sex.lower()), directed = True, vertex_colored = True, edge_colored = True)

        neurons = {}
        edges = {}

        # go through electrical first since it contains a superset of neuronns
        for edge_type in ['Electrical', 'Chemical']:
            sheet = workbook.sheet_by_name(sheets[(sex, edge_type)])

            # get the number of rows and columns
            nrows = sheet.nrows
            ncols = sheet.ncols

            # create a new dictionary for these edges
            edges[edge_type] = {}

            # make sure that no two neurons have the same name
            for row_index in range(3, nrows - 1):
                row_neuron = sheet.cell_value(row_index, 2).lower()

                if not row_neuron in neurons:
                    neurons[row_neuron] = len(neurons)

                # skip the last column
                for col_index in range(3, ncols - 1):
                    col_neuron = sheet.cell_value(2, col_index).lower()

                    if not col_neuron in neurons:
                        neurons[col_neuron] = len(neurons)

                    # get the strength for this synapse
                    synapse_strength = sheet.cell_value(row_index, col_index)

                    # skip if there is no connection
                    if not synapse_strength: continue

                    edges[edge_type][(row_neuron, col_neuron)] = synapse_strength


        # create a mapping from vertex names to indices
        vertex_index_to_name = {}
        for neuron, vertex_index in neurons.items():
            assert (not vertex_index in neurons)
            vertex_index_to_name[vertex_index] = neuron

        for enumeration_index, (vertex_index, neuron_type) in enumerate(vertex_index_to_name.items()):
            # each vertex receives a unique color since the graphs are stereotyped
            graph.AddVertex(vertex_index, enumeration_index, community = -1, color = vertex_index)

        graph.SetVertexTypeMapping(vertex_index_to_name)

        # add edges based on the wiring diagram
        for neuron_one in neurons.keys():
            vertex_one = neurons[neuron_one]
            for neuron_two in neurons.keys():
                vertex_two = neurons[neuron_two]
                # only consider the pairs of vertex one and vertex two in that order
                # tihs implicitly removes self loops from the connectome
                if vertex_two <= vertex_one: continue

                # if there is an electrical synapse, need to see if there are also chemical ones
                if (neuron_one, neuron_two) in edges['Electrical']:
                    electrical_strength = edges['Electrical'][(neuron_one, neuron_two)]
                else:
                    electrical_strength = 0

                if (neuron_one, neuron_two) in edges['Chemical']:
                    pre_neuron_one_strength = edges['Chemical'][(neuron_one, neuron_two)]
                else:
                    pre_neuron_one_strength = 0

                if (neuron_two, neuron_one) in edges['Chemical']:
                    pre_neuron_two_strength = edges['Chemical'][(neuron_two, neuron_one)]
                else:
                    pre_neuron_two_strength = 0

                # edge type 0 is there is no electrical strength
                if not electrical_strength:
                    if pre_neuron_one_strength:
                        graph.AddEdge(vertex_one, vertex_two, weight = pre_neuron_one_strength, color = 0)
                    if pre_neuron_two_strength:
                        graph.AddEdge(vertex_two, vertex_one, weight = pre_neuron_two_strength, color = 0)
                else:
                    if pre_neuron_one_strength:
                        graph.AddEdge(vertex_one, vertex_two, weight = pre_neuron_one_strength + electrical_strength, color = 2)
                    else:
                        graph.AddEdge(vertex_one, vertex_two, weight = electrical_strength, color = 1)
                    if pre_neuron_two_strength:
                        graph.AddEdge(vertex_two, vertex_one, weight = pre_neuron_two_strength + electrical_strength, color = 2)
                    else:
                        graph.AddEdge(vertex_two, vertex_one, weight = electrical_strength, color = 1)

        edge_type_mapping = {
            0: 'Chemical Synapse Only',
            1: 'Electrical Synapse Only',
            2: 'Both',
        }

        graph.SetEdgeTypeMapping(edge_type_mapping)

        output_filename = 'graphs/C-elegans-sex-{}.graph.bz2'.format(sex.lower())
        WriteGraph(graph, output_filename)

        # write the condensed CSV neuron and edge files
        with open('CSVs/Sexes/C-elegans-sex-{}-condensed-neurons.csv'.format(sex.lower()), 'w') as fd:
            fd.write('Neuron ID,Color Name\n')
            for neuron in graph.vertices.values():
                fd.write('{},{}\n'.format(neuron.index, graph.vertex_type_mapping[neuron.color]))
        with open('CSVs/Sexes/C-elegans-sex-{}-condensed-edges.csv'.format(sex.lower()), 'w') as fd:
            fd.write('Pre Synaptic Neuron ID,Post Synaptic Neuron ID,Weight,Color\n')
            for edge in graph.edges.values():
                fd.write('{},{},{},{}\n'.format(edge.source_index, edge.destination_index, edge.weight, graph.edge_type_mapping[edge.color]))

        # print statistics
        nchemical = 0
        nelectrical = 0
        nboth = 0

        for edge in graph.edges.values():
            if edge.color == 0: nchemical += 1
            elif edge.color == 1: nelectrical += 1
            elif edge.color == 2: nboth += 1
            else: assert (False)

        print ('No. Neurons: {}'.format(len(graph.vertices.keys())))
        print ('No. Edges: {}'.format(len(graph.edges)))
        print ('  Chemical Only: {}'.format(nchemical))
        print ('  Electrical Only: {}'.format(nelectrical))
        print ('  Both: {}'.format(nboth))
        print ('Wrote {} in {:0.2f} seconds'.format(output_filename, time.time() - start_time))

        # run enumeration reindexing
        CalculateAscendingEnumerationIndex(graph, 'minimum')
