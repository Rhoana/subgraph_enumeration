import struct



class Graph(object):
    def __init__(self, prefix, directed, vertex_colored, edge_colored):
        """
        Graph class defines the basic graph structure for addax used for clustering commmunities, motif discovery,
        and generating random examples

        @param prefix: a string to reference this graph by
        @param directed: indicates if the graph is directed or undirected
        @param vertex_colored: indicates if the vertices in the graph have color
        @param edge_colored: indicates if the edges in the graph have color
        """
        self.prefix = prefix
        self.directed = directed
        self.vertex_colored = vertex_colored
        self.edge_colored = edge_colored

        # vertices is a mapping from the vertex index to the vertex object
        self.vertices = {}
        # edges is a list of edges with sources, destinations, and weights
        self.edges = {}
        # get a mapping from vertex/edge colors to strings
        self.vertex_type_mapping = {}
        self.edge_type_mapping = {}

    def AddVertex(self, index, enumeration_index = -1, community = -1, color = -1):
        """
        Add a vertex to the graph

        @param index: the index for the vertex
        @param enumeration_index: an internal ordering system for enumeration speed up
        @param community: the community that the vertex belongs to (default = -1)
        @param color: the color that the vertex has (default = -1)
        """
        # vertices must have unique indices
        assert (not index in self.vertices)
        # make sure that the number of node colors is less than 256
        assert (color < 65536)

        # if there is no enumeration index, the index equals the number of vertices seen
        if enumeration_index == -1: enumeration_index = len(self.vertices)

        # create the vertex and add it to the mapping
        vertex = self.Vertex(self, index, enumeration_index, community, color)
        self.vertices[index] = vertex

    def AddEdge(self, source_index, destination_index, weight = 1, color = -1):
        """
        Add an edge to the graph

        @param source_index: the integer of the source index in the graph
        @param destination_index: the integer of the destination index in the graph
        @param weight: the weight of this edge where higher values indicate greater strength (default = 1)
        @param color: the color that the edge has (default = -1)
        """
        # the source and destination indices must actually belong to vertices
        assert (source_index in self.vertices)
        assert (destination_index in self.vertices)
        # make sure that the number of edge colors remains 8 or fewer
        assert (color < 7)

        # if the graph is undirected, make the source destination the smaller of the two indices
        if not self.directed and destination_index < source_index:
            tmp = destination_index
            destination_index = source_index
            source_index = tmp

        # create the edge and add it to the list of edges
        edge = self.Edge(self, source_index, destination_index, weight, color)

        # if the graph is undirected, add both directions to the dictionary
        self.edges[(source_index, destination_index)] = edge
        if not self.directed: self.edges[(destination_index, source_index)] = edge

        # add the edge to both vertices
        self.vertices[source_index].AddEdge(edge)
        self.vertices[destination_index].AddEdge(edge)

    def SetVertexTypeMapping(self, vertex_type_mapping):
        """
        Set the vertex type mapping

        @param vertex_type_mapping: the vertex mapping from indices to names
        """
        self.vertex_type_mapping = vertex_type_mapping

        for vertex in self.vertices.values():
            assert (vertex.color in self.vertex_type_mapping)

    def SetEdgeTypeMapping(self, edge_type_mapping):
        """
        Set the edge type mapping

        @param edge_type_mapping: the edge mapping from indices to names
        """
        self.edge_type_mapping = edge_type_mapping

        for edge in self.edges.values():
            assert (edge.color in self.edge_type_mapping)

    def NVertices(self):
        """
        Return the number of vertices in this graph
        """
        return len(self.vertices.keys())

    def NEdges(self):
        """
        Return the number of edges in this graph
        """
        if self.directed:
            return len(self.edges)
        else:
            return len(self.edges) // 2

    def Communities(self):
        """
        Return a mapping from vertex indices to communities
        """
        communities = {}

        for vertex in self.vertices.values():
            communities[vertex.index] = vertex.community

        return communities

    class Vertex(object):
        def __init__(self, graph, index, enumeration_index, community = -1, color = -1):
            """
            Vertex class defines the vertices in a graph that are labeled by the index

            @param graph: the larger graph that contains this vertex
            @param index: the integer index that corresponds to this vertex
            @param enumeration_index: an internal ordering system for enumeration speed up
            @param community: the community that the vertex belongs to (default = -1)
            @param color: the color that the vertex has (default = -1)
            """
            self.graph = graph
            self.index = index
            self.enumeration_index = enumeration_index
            self.community = community
            self.color = color

            # extra instance variables keep track of the ingoing and outgoing edges from the vertex
            self.incoming_edges = []
            self.outgoing_edges = []
            # keep track of incoming and outgoing neighbors
            self.incoming_neighbors = set()
            self.outgoing_neighbors = set()
            self.neighbors = set()

        def AddEdge(self, edge):
            """
            Add this edge to the set of edges for this vertex and ensure no edge parallelism

            @param edge: the edge that connects this vertex to another
            """
            # ensure that this is a valid edge for this vertex
            assert (edge.source_index == self.index or edge.destination_index == self.index)

            # if the graph is directed, add the incoming or outgoing edge
            if self.graph.directed:
                if edge.source_index == edge.destination_index:
                    self.incoming_neighbors.add(self.index)
                    self.outgoing_neighbors.add(self.index)
                    self.neighbors.add(self.index)
                elif edge.source_index == self.index:
                    self.outgoing_edges.append(edge)
                    assert (not edge.destination_index in self.outgoing_neighbors)
                    self.outgoing_neighbors.add(edge.destination_index)
                    self.neighbors.add(edge.destination_index)
                else:
                    self.incoming_edges.append(edge)
                    assert (not edge.source_index in self.incoming_neighbors)
                    self.incoming_neighbors.add(edge.source_index)
                    self.neighbors.add(edge.source_index)
            # if the graph is not directed, add the edge to both incoming and outgoing
            else:
                self.incoming_edges.append(edge)
                self.outgoing_edges.append(edge)

                if edge.source_index == edge.destination_index:
                    self.incoming_neighbors.add(self.index)
                    self.outgoing_neighbors.add(self.index)
                    self.neighbors.add(self.index)
                elif edge.source_index == self.index:
                    assert (not edge.destination_index in self.incoming_neighbors and not edge.destination_index in self.outgoing_neighbors)
                    self.incoming_neighbors.add(edge.destination_index)
                    self.outgoing_neighbors.add(edge.destination_index)
                    self.neighbors.add(edge.destination_index)
                else:
                    assert (not edge.source_index in self.incoming_neighbors and not edge.source_index in self.outgoing_neighbors)
                    self.incoming_neighbors.add(edge.source_index)
                    self.outgoing_neighbors.add(edge.source_index)
                    self.neighbors.add(edge.source_index)

        def IncomingNeighborIndices(self):
            """
            Returns the neighbors with edges going from
            """
            return self.incoming_neighbors

        def OutgoingNeighborIndices(self):
            """
            Returns the neighbors with an edge from this vertex to that neighbor
            """
            return self.outgoing_neighbors

        def NeighborIndices(self):
            """
            Return all neighbors from this vertex regardless of incoming and outgoing status
            """
            return self.neighbors

    class Edge(object):
        def __init__(self, graph, source_index, destiantion_index, weight = 1, color = -1):
            """
            Edge class defines the edges in a graph that connect the vertices

            @param graph: the larger graph that contains this edge
            @param source_index: the integer of the source index in the graph
            @param destination_index: the integer of the destination index in the graph
            @param weight: the weight of this edge where higher values indicate greater strength (default = 1)
            @param color: the color that the edge has (default = -1)
            """
            self.graph = graph
            self.source_index = source_index
            self.destination_index = destiantion_index
            self.weight = weight
            self.color = color
