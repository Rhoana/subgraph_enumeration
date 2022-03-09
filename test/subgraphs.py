import glob



from addax.kavosh.classify import ParseCertificate
from addax.utilities.dataIO import ReadGraph



def ValidateWrittenSubgraphs(input_filename, k, community_based = False):
    """
    Validate the correctness of the written subgraphs

    @param input_filename: the location for the graph file
    @param k: the size of the discovered motifs
    @param community_based: boolean flag for whether only subgraphs within communities were enumerated
    """
    # read the graph
    graph = ReadGraph(input_filename)

    # get the temporary directory
    if community_based: temp_directory = 'temp-community-based'
    else: temp_directory = 'temp'

    # get the subgraph filenames
    subgraph_filenames = sorted(glob.glob('{}/{}/subgraphs/*txt'.format(temp_directory, graph.prefix)))

    # iterate over all the subgraphs in each file
    for subgraph_filename in subgraph_filenames:
        with open(subgraph_filename, 'r') as fd:
            for subgraph in fd:
                certificate = subgraph.split(':')[0]
                vertices = [int(vertex) for vertex in subgraph.split(':')[1].strip().split()]

                # get the subgraph from the certificate
                subgraph = ParseCertificate(graph, k, certificate)

                for (out_index, in_index) in subgraph.edges:
                    out_vertex = vertices[out_index]
                    in_vertex = vertices[in_index]

                    assert ((out_vertex, in_vertex) in graph.edge_set)
