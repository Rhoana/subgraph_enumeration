import os
import sys
import glob
import time



import numpy as np



cimport cython
cimport numpy as np
import ctypes
from libcpp cimport bool



from subgraph_enumeration.utilities.dataIO import ReadGraph, ReadPrefix



cdef extern from 'cpp-enumerate.h':
    void CppSetVertexColored(bool vertex_colored)
    void CppSetEdgeColored(bool edge_colored)
    void CppSetCommunityBased(bool community_based)
    void CppSetWriteSubgraphs(bool write_subgraphs)
    void CppEnumerateSubgraphsSequentially(const char *input_filename, const char *temp_directory, short k)
    void CppEnumerateSubgraphsFromNodes(const char *input_filename, const char *temp_directory, short k, long *nodes, long nnodes, long output_suffix)



def CreateDirectoryStructure(input_filename, vertex_colored, edge_colored, community_based, write_subgraphs):
    """
    Create the directory structure for enumeration. Return the tmp directory name.

    @param input_filename: location for the graph to enumerate
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    @param write_subgraphs: a boolean flag to write all enumerated subgraphs to disk
    """
    # make sure that both vertex and edge colors are not both on
    assert (not vertex_colored or not edge_colored)

    # is this enumeration community based
    if community_based: community_suffix = 'local'
    else: community_suffix = 'global'

    # are there colors associated with this graph
    if vertex_colored: color_suffix = 'vertex-colored'
    elif edge_colored: color_suffix = 'edge-colored'
    else: color_suffix = 'colorless'

    # get the prefix for the dataset
    prefix = ReadPrefix(input_filename)

    temp_directory = 'temp/{}-{}-{}'.format(prefix, community_suffix, color_suffix)

    # create the certificate and subgraph directory
    certificate_directory = '{}/certificates'.format(temp_directory)
    if not os.path.exists(certificate_directory):
        os.makedirs(certificate_directory, exist_ok = True)

    if write_subgraphs:
        subgraphs_directory = '{}/subgraphs'.format(temp_directory)
        if not os.path.exists(subgraphs_directory):
            os.makedirs(subgraphs_directory, exist_ok = True)

    return temp_directory



def EnumerateSubgraphsSequentially(input_filename, k, vertex_colored = False, edge_colored = False, community_based = False, write_subgraphs = False):
    """
    Enumerate all subgraphs in the graph specified by input_filename

    @param input_filename: location for the graph to enumerate
    @parak k: the motif subgraph size to find
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    @param write_subgraphs: a boolean flag to write all enumerated subgraphs to disk
    """
    # make sure that if coloring is request, the graph is colored
    graph = ReadGraph(input_filename, header_only = True)

    if vertex_colored: assert (graph.vertex_colored)
    if edge_colored: assert (graph.edge_colored)

    # the graph cannot be both vertex and edge colored
    assert (not vertex_colored or not edge_colored)

    # create the temp directory if it does not exist
    temp_directory = CreateDirectoryStructure(input_filename, vertex_colored, edge_colored, community_based, write_subgraphs)

    # set the vertex color flag
    CppSetVertexColored(vertex_colored)
    # set the edge color flag
    CppSetEdgeColored(edge_colored)
    # set the community based flag
    CppSetCommunityBased(community_based)
    # set the write subgraphs flag
    CppSetWriteSubgraphs(write_subgraphs)

    # enumerate the subgraph, cast the string into a character array
    CppEnumerateSubgraphsSequentially(input_filename.encode('utf-8'), temp_directory.encode('utf-8'), k)



def EnumerateSubgraphsFromNodes(input_filename, k, nodes, output_suffix, vertex_colored = False, edge_colored = False, community_based = False, write_subgraphs = False):
    """
    Enumerate all subgraphs in the graph starting at the nodes array

    @param input_filename: location for the graph to enumerate
    @parak k: the motif subgraph size to find
    @param nodes: an array of nodes to enumerate starting at
    @param output_suffix: a integer identifying a unique file to which to save the results
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    @param write_subgraphs: a boolean flag to write all enumerated subgraphs to disk
    """
    # make sure that if coloring is request, the graph is colored
    graph = ReadGraph(input_filename, header_only = True)

    if vertex_colored: assert (graph.vertex_colored)
    if edge_colored: assert (graph.edge_colored)

    # the graph cannot be both vertex and edge colored
    assert (not vertex_colored or not edge_colored)

    # create the temp directory if it does not exist
    temp_directory = CreateDirectoryStructure(input_filename, vertex_colored, edge_colored, community_based, write_subgraphs)

    # set the vertex color flag
    CppSetVertexColored(vertex_colored)
    # set the edge color flag
    CppSetEdgeColored(edge_colored)
    # set the community based flag
    CppSetCommunityBased(community_based)
    # set the write subgraphs flag
    CppSetWriteSubgraphs(write_subgraphs)

    # convert the array of nodes into a c array
    nnodes = len(nodes)
    cdef np.ndarray[long, ndim=1, mode='c'] cpp_nodes = np.ascontiguousarray(nodes, dtype=ctypes.c_int64)

    # enumerate the subgraph, cast the string into a character array
    CppEnumerateSubgraphsFromNodes(input_filename.encode('utf-8'), temp_directory.encode('utf-8'), k, &(cpp_nodes[0]), nnodes, output_suffix)

    # free memory
    del cpp_nodes



def CombineEnumeratedSubgraphs(input_filename, k, vertex_colored = False, edge_colored = False, community_based = False):
    """
    Combine all of the enumerated subgraphs for a given file and motif size.

    @param input_filename: location for the graph to enumerate
    @parak k: the motif subgraph size to find
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    """
    # the graph cannot be both vertex and edge colored
    assert (not vertex_colored or not edge_colored)

    # read the graph (only vertices)
    graph = ReadGraph(input_filename, vertices_only = True)

    # create the list of vertices
    vertices = set(list(graph.vertices.keys()))

    # get the temp directory
    temp_directory = CreateDirectoryStructure(input_filename, vertex_colored, edge_colored, community_based, False)

    # get a list of all the input filenames for this motif size
    input_filenames = sorted(glob.glob('{}/certificates/motif-size-{:03d}-*.txt'.format(temp_directory, k)))

    # create a dictionary of certificates
    certificates = {}

    # set initial counter variables
    total_nsubgraphs, total_time = 0, 0

    # iterate over all the input files
    for input_filename in input_filenames:
        start_time = time.time()
        sys.stdout.write('Reading {}...'.format(input_filename))
        sys.stdout.flush()

        # open the output file
        with open(input_filename, 'r') as fd:
            for certificate_line in fd:
                segments = certificate_line.split()

                # update the mode that currently exists
                if segments[0] == 'Enumerated':
                    nsubgraphs, vertex, vertex_time = int(segments[1]), int(segments[5]), float(segments[7])

                    # update the counter variables that verify correctness
                    total_nsubgraphs += nsubgraphs
                    total_time += vertex_time
                    vertices.remove(vertex)

                    certificate_mode = False
                else:
                    certificate, nsubgraphs = segments[0].strip(':'), int(segments[1])

                    # update the certificate information
                    if not certificate in certificates: certificates[certificate] = nsubgraphs
                    else: certificates[certificate] += nsubgraphs

                    certificate_mode = True

        assert (not certificate_mode)

        sys.stdout.write('done in {:0.2f} seconds\n'.format(time.time() - start_time))
        sys.stdout.flush()

    # all vertices are found
    assert (not len(vertices))
    # the number of output subgraphs is correctly tabulated
    assert (sum(certificates.values()) == total_nsubgraphs)

    # create the output directory if it does not exist
    output_directory = 'subgraphs/{}'.format('/'.join(temp_directory.split('/')[1:]))

    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok = True)

    output_filename = '{}/motif-size-{:03d}-certificates.txt'.format(output_directory, k)
    with open(output_filename, 'w') as fd:

        # write starting statistics
        fd.write('Found {} unique subgraphs.\n'.format(len(certificates)))
        print ('Found {} unique subgraphs'.format(len(certificates)))

        # enumerate over all the certificates in descending order of occurrences
        for certificate, nsubgraphs in sorted(certificates.items(), key = lambda x: x[1], reverse = True):
            fd.write('{}: {}\n'.format(certificate, nsubgraphs))
            print ('{}: {}'.format(certificate, nsubgraphs))

        # write statistics
        fd.write('Enumerated {} subgraphs in {:0.2f} seconds.'.format(total_nsubgraphs, total_time))
        print ('Enumerated {} subgraphs in {:0.2f} seconds.'.format(total_nsubgraphs, total_time))
