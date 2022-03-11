import bz2
import pickle
import struct



from subgraph_enumeration.data_structures.graph import Graph



def ReadGraph(input_filename, header_only = False, vertices_only = False):
    """
    Read a graph data structure from disk

    @param input_filename: the filename where the graph data is stored
    @param vertices_only: boolean flag that determines if edges are read
    """
    assert (input_filename.endswith('.graph.bz2'))

    data = bz2.decompress(open(input_filename, 'rb').read())

    byte_index = 0

    # read the basic attributes for the graph
    nvertices, nedges, directed, vertex_colored, edge_colored = struct.unpack('qq???', data[byte_index:byte_index + 19])
    byte_index += 19

    # read the prefix
    prefix, = struct.unpack('128s', data[byte_index:byte_index + 128])
    byte_index += 128

    prefix = prefix.decode().strip('\0')

    graph = Graph(prefix, directed, vertex_colored, edge_colored)

    if header_only: return graph

    # read all the vertices and add them to the graph
    for _ in range(nvertices):
        index, enumeration_index, community, color, = struct.unpack('qqqh', data[byte_index:byte_index + 26])
        byte_index += 26

        graph.AddVertex(index, enumeration_index, community, color)

    # if the flag to read only vertices is on, avoid reading edges
    if vertices_only: return graph

    # read all of the edges and add them to the graph
    for _ in range(nedges):
        source_index, destination_index, weight, color, = struct.unpack('qqdb', data[byte_index:byte_index + 25])
        byte_index += 25

        graph.AddEdge(source_index, destination_index, weight, color)

    # read the vertex type mappings
    nvertex_types, = struct.unpack('q', data[byte_index:byte_index + 8])
    assert (nvertex_types <= 65536)
    byte_index += 8

    vertex_type_mapping = {}
    for _ in range(nvertex_types):
        index, = struct.unpack('q', data[byte_index:byte_index + 8])
        byte_index += 8

        vertex_type, = struct.unpack('128s', data[byte_index:byte_index + 128])
        byte_index += 128

        vertex_type_mapping[index] = vertex_type.decode().strip('\0')

    if graph.vertex_colored: graph.SetVertexTypeMapping(vertex_type_mapping)

    # read the edge type mappings
    nedge_types, = struct.unpack('q', data[byte_index:byte_index + 8])
    assert (nedge_types <= 7)
    byte_index += 8

    edge_type_mapping = {}
    for _ in range(nedge_types):
        index, = struct.unpack('q', data[byte_index:byte_index + 8])
        byte_index += 8

        edge_type, = struct.unpack('128s', data[byte_index:byte_index + 128])
        byte_index += 128

        edge_type_mapping[index] = edge_type.decode().strip('\0')

    if graph.edge_colored: graph.SetEdgeTypeMapping(edge_type_mapping)

    return graph



def ReadPrefix(input_filename):
    """
    Read the prefix of a graph data structure from disk

    @param input_filename: the filename where the graph data is stored
    """
    assert (input_filename.endswith('.graph.bz2'))

    data = bz2.decompress(open(input_filename, 'rb').read())

    byte_index = 0

    # read the basic attributes for the graph
    nvertices, nedges, directed, vertex_colored, edge_colored = struct.unpack('qq???', data[byte_index:byte_index + 19])
    byte_index += 19

    # read the prefix
    prefix, = struct.unpack('128s', data[byte_index:byte_index + 128])
    byte_index += 128

    prefix = prefix.decode().strip('\0')

    return prefix



def WriteGraph(graph, output_filename):
    """
    Write a graph to disk for later I/O access

    @param graph: the graph data structure to save to disk
    @param output_filename: the location to save the graph data structure
    """
    assert (output_filename.endswith('.graph.bz2'))

    # create a new compression object
    compressor = bz2.BZ2Compressor()

    # write the basic attributes for the graph to disk
    nvertices = graph.NVertices()
    nedges = graph.NEdges()
    directed = graph.directed
    vertex_colored = graph.vertex_colored
    edge_colored = graph.edge_colored
    prefix = graph.prefix

    # create an empty byte array which we will concatenate later
    compressed_graph = []

    compressed_graph.append(compressor.compress(struct.pack('qq???', nvertices, nedges, directed, vertex_colored, edge_colored)))
    compressed_graph.append(compressor.compress(struct.pack('128s', prefix.encode())))

    # write all of the vertices and their attributes
    for vertex in graph.vertices.values():
        compressed_graph.append(compressor.compress(struct.pack('qqqh', vertex.index, vertex.enumeration_index, vertex.community, vertex.color)))

    # write all of the edges and their attributes
    for edge in graph.edges.values():
        compressed_graph.append(compressor.compress(struct.pack('qqdb', edge.source_index, edge.destination_index, edge.weight, edge.color)))

    # write the vertex types
    nvertex_types = len(graph.vertex_type_mapping)
    compressed_graph.append(compressor.compress(struct.pack('q', nvertex_types)))
    for index, vertex_type in graph.vertex_type_mapping.items():
        compressed_graph.append(compressor.compress(struct.pack('q128s', index, vertex_type.encode())))

    # write the edge types
    nedge_types = len(graph.edge_type_mapping)
    compressed_graph.append(compressor.compress(struct.pack('q', nedge_types)))
    for index, edge_type in graph.edge_type_mapping.items():
        compressed_graph.append(compressor.compress(struct.pack('q128s', index, edge_type.encode())))

    # flush the data
    compressed_graph.append(compressor.flush())

    # convert the array into a binary string - faster than native implementation
    compressed_graph = b''.join(compressed_graph)

    # write the compressed string to file
    with open(output_filename, 'wb') as fd:
        fd.write(compressed_graph)



def PickleData(data, filename):
    """
    Pickle the data and write to disk

    @param data: the data to pickle
    @param filename: the location to save the pickled data
    """
    with open(filename, 'wb') as fd:
        pickle.dump(data, fd)



def ReadPickledData(filename):
    """
    Read pickled data from disk and return object

    @param filename: the location of the saved pickled data
    """
    with open(filename, 'rb') as fd:
        return pickle.load(fd)
