import networkx as nx



from subgraph_enumeration.kavosh.enumerate import CreateDirectoryStructure
from subgraph_enumeration.utilities.dataIO import ReadGraph



def ParseCertificate(graph, k, certificate, vertex_colored, edge_colored, directed):
    """
    Produce a canonical graph from a certificate

    @ param graph: a graph data structure object
    @param k: motif size
    @param certificate: the certificate from Nauty to parse
    @param vertex_colored: is the graph vertex colored
    @param edge_colored: is the graph edge colored
    @param directed: is the graph directed
    """
    # this will require substantial debugging and validation for k > 256
    # currently skipped since motifs that size are computationally infeasible
    # nauty almost certainly can never run on graphs that size
    assert (k < 256)

    # each vertex gets a certain number of bits in the certificate that contain the adjacency
    # matrix for that vertex. The number of bits is determined by the no_setwords in pynauty. This variable
    # matches the number of 64-bit words (on a 64-bit system) needed to fit all vertices.
    # for vertex colored graphs we also add on 64 bits for each node in the subgraph for vertex coloring
    # for edge colored graph we also add on 64 bits for each (potential edge) in the subgraph for edge coloring
    if vertex_colored:
        # if the graph is colored, there are 16 characters per vertex
        # rest of string represents the canonical labeling and edge coloring
        coloring = certificate[2 * k:]
        certificate = certificate[:2 * k]

        # convert the vertex bytes (in hex) to base 10 integer
        vertex_colors = [int(coloring[2 * iv: 2 * (iv + 1)], 16) for iv in range(k)]

    if edge_colored:
        # if the graph is colored, there are 16 characters per vertex
        # rest of string represents the canonical labeling and edge coloring
        coloring = certificate[2 * k:]
        certificate = certificate[:2 * k]
        # convert the vertex bytes (in hex) to base 10 integer
        edge_colors = [int(coloring[2 * iv:2 * (iv + 1)], 16) for iv in range(len(coloring) // 2)]

    # create a new networkx graph object
    if directed:
        nx_graph = nx.DiGraph()
    else:
        nx_graph = nx.Graph()

    # add a vertex for each of the k nodes in the subgraph
    for index in range(k):
        # colored graphs have labels for their colors
        if vertex_colored:
            if vertex_colors[index] in graph.vertex_type_mapping: nx_graph.add_node(index, label = graph.vertex_type_mapping[vertex_colors[index]])
            else: nx_graph.add_node(index, label = 'Color: {}'.format(vertex_colors[index]))
        else:
            nx_graph.add_node(index)

    # get the number of words per veretx (must be a multiple of 2 * k)
    assert (not (len(certificate) % (2 * k)))
    # based on our output of using hexademical in cpp-enumerate.cpp (i.e., %02x),
    # each byte is written with two letters in our input string (e.g., aa, 02, 10, etc.)
    bytes_per_vertex = len(certificate) // k // 2

    # iterate over every vertex and extract the corresponding adjacency matrix
    edge_index = 0
    for vertex in range(k):
        # multiple by two since we are using two characters in the string per byte (wrriten in hexademical)
        certificate_bytes = certificate[vertex * bytes_per_vertex * 2:(vertex + 1) * bytes_per_vertex * 2]

        for byte_offset, iv in enumerate(range(0, len(certificate_bytes), 2)):
            # get the byte as an integer (using hexadecimal currently)
            byte = int(certificate_bytes[iv:iv+2], 16)
            assert (byte < 256)

            # 8 bits per byte (little endian)
            for bit_offset in range(8):
                bit = byte & (2 ** 7)
                byte = byte << 1

                # if this bit is 1, there is an edge from vertex to this location
                if bit:
                    # determine the neighbor by the byte and bit offset
                    neighbor_vertex = 8 * (bytes_per_vertex - byte_offset - 1) + bit_offset
                    # if there is no edge coloring, we can just add a simple edge
                    if not edge_colored:
                        nx_graph.add_edge(vertex, neighbor_vertex)
                    else:
                        # create a coloringn for edges
                        color = edge_colors[edge_index]

                        # currently colors are based on edge strength (0 = moderate, 1 = strong)
                        nx_graph.add_edge(vertex, neighbor_vertex, penwidth = 2 * color + 1)

                        # update edge index
                        edge_index += 1

    return nx_graph



def ParseCertificates(input_filename, k, vertex_colored = False, edge_colored = False, community_based = False):
    """
    Parse the certificates generated for this subgraph

    @param input_filename: location for the graph to enumerate
    @parak k: the motif subgraph size to find
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    """
    # read the graph
    graph = ReadGraph(input_filename, vertices_only = True)

    # get the temp directory
    temp_directory = CreateDirectoryStructure(input_filename, vertex_colored, edge_colored, community_based, False)

    # get the input directory
    input_directory = 'subgraphs/{}'.format('/'.join(temp_directory.split('/')[1:]))

    # read the combined enumerated subgraphs file
    subgraphs_filename = '{}/motif-size-{:03d}-certificates.txt'.format(input_directory, k)

    with open(subgraphs_filename, 'r') as fd:
        # get the number of unique subgraphs found
        unique_subgraphs = fd.readline().split()[1]
        # get the number of digits needed to encode the largest numbered subgraph in base 10
        index_digits_needed = len(unique_subgraphs)
        # get the number of digits needed to encode the most enumerate subgraph
        subgraph_digits_needed = -1

        # read all of the certificates and enumerated subgraphs
        for subgraph_index, certificate_info in enumerate(fd.readlines()[:-1]):
            certificate = certificate_info.split(':')[0].strip()
            nsubgraphs = int(certificate_info.split(':')[1].strip())

            if subgraph_digits_needed == -1: subgraph_digits_needed = len(str(nsubgraphs))

            # parse the certificate for this graph
            nx_graph = ParseCertificate(graph, k, certificate, vertex_colored, edge_colored, graph.directed)

            # create the graph drawing structure
            A = nx.nx_agraph.to_agraph(nx_graph)

            A.layout(prog='dot')

            # output this enumerate subgraph
            output_filename = '{}/motif-size-{:03d}-motif-{:0{}d}-found-{:0{}d}.dot'.format(input_directory, k, subgraph_index, index_digits_needed, nsubgraphs, subgraph_digits_needed)
            A.draw(output_filename)
