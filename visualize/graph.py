import networkx as nx



def VisualizeGraph(graph, output_filename):
    """
    Visualize the graph using networkx and output the result in a .dot file

    @param graph: the graph data structure to visualize
    @param output_filename: the file to save the visualized results
    """
    # different visualizations for directed and undirected graphs
    if graph.directed:
        viz_graph = nx.DiGraph()
    else:
        viz_graph = nx.Graph()

    # iterate over the keys for the ids
    for index in graph.vertices.keys():
        viz_graph.add_node(index)

    # iterate over all edges in the graph
    for edge in graph.edges.values():
        # get the source and destination for each edge in the graph
        viz_graph.add_edge(edge.source_index, edge.destination_index)

    # create the graph drawing structue
    A = nx.nx_agraph.to_agraph(viz_graph)
    A.layout(prog='dot')

    A.draw(output_filename)
