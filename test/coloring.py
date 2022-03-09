from addax.data_structures.graph import Graph
from addax.utilities.dataIO import WriteGraph



def CreateTestColoredExample():
    """
    Create a disconnected graph to produce known enumerations with specific colorings
    to test the coloring functionality of kavosh integrated with Nauty.
    """
    # test subgraph enumeration for known coloring permutations
    graph = Graph('coloring-test', directed = True, colored = True)

    # keep track of the vertex index through all of the created subgraphs
    vertex_index = 0

    # create 30 graphs (0 -> 1 -> 0)
    for _ in range(30):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 0)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 1)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 0)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)

        # update the vertex indices
        vertex_index += 3

    # create 35 graphs (0 -> 1 -> 1)
    for _ in range(35):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 0)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 1)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 1)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)

        # update the vertex indices
        vertex_index += 3

    # create 40 graphs (0 -> 0 -> 0)
    for _ in range(40):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 0)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 0)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 0)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)

        # update the vertex indices
        vertex_index += 3

    # create 45 graphs (1 -> 1 -> 1)
    for _ in range(45):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 1)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 1)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 1)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)

        # update the vertex indices
        vertex_index += 3

    # create 50 graphs (0 -> 2 -> 0)
    for _ in range(50):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 0)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 2)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 0)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)

        # update the vertex indices
        vertex_index += 3

    # create 55 graphs (0 <-> 1 -> 0)
    for _ in range(55):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 0)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 1)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 0)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)

        # update the vertex indices
        vertex_index += 3

    # create 60 graphs (1 <-> 1 -> 0)
    for _ in range(60):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 1)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 1)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 0)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)

        vertex_index += 3

    # create 65 graphs (1 <-> 1 <-> 0)
    for _ in range(65):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 1)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 1)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 0)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)
        graph.AddEdge(vertex_index + 2, vertex_index + 1)

        vertex_index += 3

    # create 70 graphs (0 <-> 0 <-> 1)
    for _ in range(70):
        # add the three vertices
        graph.AddVertex(vertex_index, vertex_index, community = -1, color = 0)
        graph.AddVertex(vertex_index + 1, vertex_index + 1, community = -1, color = 0)
        graph.AddVertex(vertex_index + 2, vertex_index + 2, community = -1, color = 1)

        # add the edges
        graph.AddEdge(vertex_index, vertex_index + 1)
        graph.AddEdge(vertex_index + 1, vertex_index)
        graph.AddEdge(vertex_index + 1, vertex_index + 2)
        graph.AddEdge(vertex_index + 2, vertex_index + 1)

        vertex_index += 3


    # write the graph to disk
    WriteGraph(graph, 'graphs/coloring-test.graph.bz2')
