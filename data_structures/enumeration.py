import time



import numpy as np



from addax.utilities.dataIO import WriteGraph



def PrintNeighborhoodStatistics(graph, enumerated = False):
    """
    Print statistics for the neighborhoods of the vertices.

    @param graph: an input graph
    @param enumerated: only consider neighbors with a higher enumeration index
    """
    neighborhoods = list(MapVerticesToNeighborhoodSizes(graph, enumerated).values())

    print ('Neighborhood Sizes')
    print ('  Median: {}'.format(int(round(np.median(neighborhoods)))))
    print ('  Maximum: {}'.format(np.max(neighborhoods)))
    print ('  Std Dev: {:0.2f}'.format(np.std(neighborhoods)))



def MapVerticesToNeighborhoodSizes(graph, enumerated = False):
    """
    Return a mapping from vertices to the number of neighbors

    @param graph: an input graph
    @param enumerated: only consider neighbors with a higher enumeration index
    """
    # create a mapping from vertex indices to neighborhood sizes
    vertex_to_neighborhood_size = {}

    # iterate over all vertices in the graph
    for vertex_index, vertex in graph.vertices.items():
        # get the neighborhood around this vertex
        # copy the set to keep original immutable
        neighborhood = set(vertex.neighbors)

        # if enumerated, only consider neighbors with a higher enumeration index
        if enumerated:
            # anything with a higher enueration index will belong to the group of subgraphs explorable from vertex_index
            neighborhood = [neighbor_index for neighbor_index in neighborhood if graph.vertices[neighbor_index].enumeration_index > graph.vertices[vertex_index].enumeration_index]

        vertex_to_neighborhood_size[vertex_index] = len(neighborhood)

    return vertex_to_neighborhood_size



def SaveGraphWithUpdatedEnumeration(graph, method):
    """
    Calculate the enumeration index in an ascending fashion

    @param graph: an input graph to determine the enumeration indices
    @param method: the method for determining enumeration order
    """
    # update the prefix for this graph
    previous_prefix = graph.prefix
    graph.prefix = '{}-{}'.format(graph.prefix, method)

    # save this graph
    output_filename = 'graphs/{}.graph.bz2'.format(graph.prefix, method)
    WriteGraph(graph, output_filename)

    # reset the graph prefix
    graph.prefix = previous_prefix

    # reset the enumeration indices to allow for subsequent calls of the same data
    for enumeration_index, vertex_index in enumerate(sorted(graph.vertices.keys())):
        graph.vertices[vertex_index].enumeration_index = enumeration_index

    # verify graph turned back to original state
    for enumeration_index, vertex_index in enumerate(sorted(graph.vertices.keys())):
        assert (graph.vertices[vertex_index].enumeration_index == enumeration_index)



def CalculateAscendingEnumerationIndex(graph, method):
    """
    Calculate the enumeration index in an ascending fashion

    @param graph: an input graph to determine the enumeration indices
    @param method: the method for determining enumeration order
    """
    # create a mapping from vertex indices to the neighborhood size
    vertex_to_neighborhood_size = MapVerticesToNeighborhoodSizes(graph, enumerated = False)

    # begin with no enumerated vertices
    unenumerated_vertices = set(graph.vertices.keys())
    # no enumerated vertices so first selected as index 0
    enumeration_index = 0

    # add vertices one-by-one to the ordered enumeration list
    while len(unenumerated_vertices):
        # the vertex depends on the method
        if method == 'minimum':
            vertex_index = min(vertex_to_neighborhood_size.keys(), key=vertex_to_neighborhood_size.get)
        elif method == 'median':
            # get the vertex with the smallest neighborhood
            vertices_sorted_by_neighborhood_size = sorted(vertex_to_neighborhood_size.keys(), key=vertex_to_neighborhood_size.get)
            vertex_index = vertices_sorted_by_neighborhood_size[len(vertices_sorted_by_neighborhood_size) // 2]
        else:
            raise Exception('Unrecognized method: {}'.format(method))

        # update all of the neighbors of this vertex
        # since they will no longer traverse this one
        for neighbor_index in set(graph.vertices[vertex_index].neighbors):
            # only neighbors that have yet to be traversed need updates
            if neighbor_index in unenumerated_vertices:
                # decrement the neighborhood size for the neighbor since
                # it will no longer go to this vertex
                vertex_to_neighborhood_size[neighbor_index] -= 1

        # remove this key from the potential future indices
        del vertex_to_neighborhood_size[vertex_index]
        # update the enumeration index for this vertex
        graph.vertices[vertex_index].enumeration_index = enumeration_index
        # increment the enumeration index by one
        enumeration_index += 1
        # remove this vertex from the group of ones yet to traverse
        unenumerated_vertices.remove(vertex_index)

    # print statistics
    print ('Enumeration Method: {}'.format(method.title()))
    PrintNeighborhoodStatistics(graph, enumerated = True)

    # save the graph with updated enumerations
    SaveGraphWithUpdatedEnumeration(graph, method)



def CalculateDescendingEnumerationIndex(graph, method):
    """
    Calculate the enumeration index in an ascending fashion

    @param graph: an input graph to determine the enumeration indices
    @param method: the method for determining enumeration order
    """
    # create a mapping from vertex indices to the neighborhood size
    vertex_to_neighborhood_size = MapVerticesToNeighborhoodSizes(graph, enumerated = False)

    # begin with no enumerated vertices
    enumerated_vertices = set(graph.vertices.keys())
    # no enumerated vertices so first selected as index 0
    enumeration_index = len(graph.vertices.keys()) - 1

    # add vertices one-by-one to the ordered enumeration list
    while len(enumerated_vertices):
        # the vertex depends on the method
        if method == 'maximum':
            vertex_index = max(vertex_to_neighborhood_size.keys(), key=vertex_to_neighborhood_size.get)
        else:
            raise Exception('Unrecognized method: {}'.format(method))

        # remove this key from the potential future indices
        del vertex_to_neighborhood_size[vertex_index]
        # update the enumeration index for this vertex
        graph.vertices[vertex_index].enumeration_index = enumeration_index
        # increment the enumeration index by one
        enumeration_index -= 1
        # remove this vertex from the group of ones yet to traverse
        enumerated_vertices.remove(vertex_index)

    # print statistics
    print ('Enumeration Method: {}'.format(method.title()))
    PrintNeighborhoodStatistics(graph, enumerated = True)

    # save the graph with updated enumerations
    SaveGraphWithUpdatedEnumeration(graph, method)
