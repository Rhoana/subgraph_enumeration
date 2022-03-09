#include "cpp-graph.h"



Vertex::Vertex(Graph *input_graph, long input_index, long input_enumeration_index, long input_community, int16_t input_color)
{
    /*
    Vertex class defines the vertices in a graph that are labeled by the index

    @param graph: the larger graph that contains this vertex
    @param index: the integer index that corresponds to this vertex
    @param enumeration_index: an internal ordering system for enumeration speed up
    @param community: the community that the vertex belongs to (default = -1)
    @param color: the color that the vertex has (default = -1)
    */
    graph = input_graph;
    index = input_index;
    enumeration_index = input_enumeration_index;
    community = input_community;
    color = input_color;

    // extra instance variables keep track of the ingoing and outgoing edges from the vertex
    incoming_edges = std::vector<Edge *>();
    outgoing_edges = std::vector<Edge *>();
    // keep track of incoming and outgoing neighbors
    incoming_neighbors = std::unordered_set<long>();
    outgoing_neighbors = std::unordered_set<long>();
    neighbors = std::unordered_set<long>();
}

Vertex::~Vertex(void)
{
    /*
    Destructor for eliminating vertex object
    */
}

void Vertex::AddEdge(Edge *edge)
{
    /*
    Add this edge to the set of edges for this vertex and ensure no edge parallelism

    @param edge: the edge that connects this vertex to another
    */

    // assert that this is a valid edge for this vertex
    assert (edge->source_index == index || edge->destination_index == index);

    // if the graph is directed, add the incoming or outgoing edge
    if (graph->directed) {
        if (edge->source_index == index) {
            outgoing_edges.push_back(edge);
            assert (outgoing_neighbors.find(edge->destination_index) == outgoing_neighbors.end());
            outgoing_neighbors.insert(edge->destination_index);
            neighbors.insert(edge->destination_index);
        }
        else {
            incoming_edges.push_back(edge);
            assert (incoming_neighbors.find(edge->source_index) == incoming_neighbors.end());
            incoming_neighbors.insert(edge->source_index);
            neighbors.insert(edge->source_index);
        }
    }
    // if the graph is not directed, add the edge to both incoming and outgoing
    else {
        incoming_edges.push_back(edge);
        outgoing_edges.push_back(edge);

        if (edge->source_index == index) {
            assert (incoming_neighbors.find(edge->destination_index) == incoming_neighbors.end());
            assert (outgoing_neighbors.find(edge->destination_index) == outgoing_neighbors.end());
            incoming_neighbors.insert(edge->destination_index);
            outgoing_neighbors.insert(edge->destination_index);
            neighbors.insert(edge->destination_index);
        }
        else {
            assert (incoming_neighbors.find(edge->source_index) == incoming_neighbors.end());
            assert (outgoing_neighbors.find(edge->source_index) == outgoing_neighbors.end());
            incoming_neighbors.insert(edge->source_index);
            outgoing_neighbors.insert(edge->source_index);
            neighbors.insert(edge->source_index);
        }
    }
}



Edge::Edge(Graph *input_graph, long input_source_index, long input_destination_index, double input_weight, int8_t input_color) :
graph(input_graph),
source_index(input_source_index),
destination_index(input_destination_index),
weight(input_weight),
color(input_color)
{
    /*
    Edge class defines the edges in a graph that connect the vertices

    @param graph: the larger graph that contains this edge
    @param source_index: the integer of the source index in the graph
    @param destination_index: the integer of the destination index in the graph
    @param weight: the weight of this edge where higher values indicate greater strength (default = 1)
    @param color: the color of the edge (default = -1)
    */
}


Edge::~Edge(void)
{
    /*
    Destructor for eliminating graph object
    */
}


Graph::Graph(const char input_prefix[128], bool input_directed, bool input_vertex_color, bool input_edge_colored)
{
    /*
    Graph class defines the basic graph structure for addax used for clustering commmunities, motif discovery,
    and generating random examples

    @param prefix: a string to reference this graph by
    @param directed: indicates if the graph is directed or undirected
    @param vertex_colored: indicates if the nodes in the graph have color
    @param edge_colored: indicates if the nodes in the graph have color
    */
    // force null terminating character by putting only 127 characters
    strncpy(prefix, input_prefix, 127);
    directed = input_directed;
    vertex_colored = input_vertex_color;
    edge_colored = input_edge_colored;

    vertices = std::map<long, Vertex *>();
    edges = std::map<std::pair<long, long>, Edge *>();
}

Graph::~Graph(void)
{
    /*
    Destructor for eliminating graph object
    */
    for (std::map<long, Vertex *>::iterator it = vertices.begin(); it != vertices.end(); ++it) {
        delete it->second;
    }

    for (std::map<std::pair<long, long>, Edge *>::iterator it = edges.begin(); it != edges.end(); ++it) {
        delete it->second;
    }
}

void Graph::AddVertex(long index, long enumeration_index, long community, int16_t color)
{
    /*
    Add a vertex to the graph

    @param index: the index for the vertex
    @param enumeration_index: an internal ordering system for enumeration speed up
    @param community: the community that the vertex belongs to (default = -1)
    @param color: the color that the vertex has (default = -1)
    */

    // vertices must have unique indices
    assert (vertices.find(index) == vertices.end());

    // create the vertex and add it to the mapping
    Vertex *vertex = new Vertex(this, index, enumeration_index, community, color);
    vertices[index] = vertex;
}

void Graph::AddEdge(long source_index, long destination_index, double weight, int8_t color)
{
    /*
    Add an edge to the graph

    @param source_index: the integer of the source index in the graph
    @param destination_index: the integer of the destination index in the graph
    @param weight: the weight of this edge where higher values indicate greater strength (default = 1)
    */

    // the source and destination indices must actually belong to vertices
    assert (vertices.find(source_index) != vertices.end());
    assert (vertices.find(destination_index) != vertices.end());

    // do not allow self loops
    assert (source_index != destination_index);

    // if the graph is undirected, make the source destination the smaller of the two indices
    if (!directed && destination_index < source_index) {
        long tmp = destination_index;
        destination_index = source_index;
        source_index = tmp;
    }

    // create the edge and add it to the list of edges
    Edge *edge = new Edge(this, source_index, destination_index, weight, color);

    // add to the set of edges in the graph for easier look up
    edges[std::pair<long, long>(source_index, destination_index)] = edge;
    if (not directed) {
        edges[std::pair<long, long>(destination_index, source_index)] = edge;
    }

    // add the edge to both vertices
    vertices[source_index]->AddEdge(edge);
    vertices[destination_index]->AddEdge(edge);
}

long Graph::NVertices(void)
{
    /*
    Return the number of vertices in this graph
    */
    return vertices.size();
}

long Graph::NEdges(void)
{
    /*
    Return the number of edges in this graph
    */
    return edges.size();
}


Graph *ReadGraph(const char input_filename[4096])
{
    // open file
    FILE *fp = fopen(input_filename, "rb");
    if (!fp) { fprintf(stderr, "Failed to open %s\n", input_filename); return NULL; }

    // read the basic attributes for the graph
    long nvertices, nedges;
    bool directed, vertex_colored, edge_colored;
    if (fread(&nvertices, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    if (fread(&nedges, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    if (fread(&directed, sizeof(bool), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    if (fread(&vertex_colored, sizeof(bool), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    if (fread(&edge_colored, sizeof(bool), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

    // read the prefix
    char prefix[128];
    if (fread(&prefix, sizeof(char), 128, fp) != 128) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

    // construct an empty graph
    Graph *graph = new Graph(prefix, directed, vertex_colored, edge_colored);

    // read all the vertices and add them to the graph
    for (long iv = 0; iv < nvertices; ++iv) {
        long index, enumeration_index, community, color;
        if (fread(&index, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        if (fread(&enumeration_index, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        if (fread(&community, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        if (fread(&color, sizeof(int16_t), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

        graph->AddVertex(index, enumeration_index, community, color);
    }

    // read all of the edges and add them to the graph
    for (long ie = 0; ie < nedges; ++ie) {
        long source_index, destination_index, color;
        double weight;
        if (fread(&source_index, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        if (fread(&destination_index, sizeof(long), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        if (fread(&weight, sizeof(double), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        if (fread(&color, sizeof(int8_t), 1, fp) != 1) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

        graph->AddEdge(source_index, destination_index, weight, color);
    }

    // close file
    fclose(fp);

    return graph;
}



Graph *ReadBZ2Graph(const char input_filename[4096])
{
    // open file
    FILE *fp = fopen(input_filename, "rb");
    if (!fp) { fprintf(stderr, "Failed to open %s\n", input_filename); return NULL; }

    // valuable local variables
    int bzerror;

    // open the BZ2 file
    BZFILE *bzfd = BZ2_bzReadOpen(&bzerror, fp, 0, 0, NULL, 0);
    if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

    // read the number of vertices and edges
    long nvertices, nedges;
    BZ2_bzRead(&bzerror, bzfd, &nvertices, sizeof(long));
    if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    BZ2_bzRead(&bzerror, bzfd, &nedges, sizeof(long));
    if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

    // read the graph attributes
    bool directed, vertex_colored, edge_colored;
    BZ2_bzRead(&bzerror, bzfd, &directed, sizeof(bool));
    if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    BZ2_bzRead(&bzerror, bzfd, &vertex_colored, sizeof(bool));
    if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    BZ2_bzRead(&bzerror, bzfd, &edge_colored, sizeof(bool));
    if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

    // read the prefix
    char prefix[128];
    BZ2_bzRead(&bzerror, bzfd, &prefix, sizeof(prefix));
    if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

    // construct an empty graph
    Graph *graph = new Graph(prefix, directed, vertex_colored, edge_colored);

    // read all the vertices and add them ot the graph
    for (long iv = 0; iv < nvertices; ++iv) {
        long index, enumeration_index, community;
        int16_t color;
        BZ2_bzRead(&bzerror, bzfd, &index, sizeof(long));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        BZ2_bzRead(&bzerror, bzfd, &enumeration_index, sizeof(long));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        BZ2_bzRead(&bzerror, bzfd, &community, sizeof(long));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        BZ2_bzRead(&bzerror, bzfd, &color, sizeof(int16_t));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

        graph->AddVertex(index, enumeration_index, community, color);
    }

    // read all of the edges and add them to the graph
    for (long ie = 0; ie < nedges; ++ie) {
        long source_index, destination_index;
        double weight;
        int8_t color;
        BZ2_bzRead(&bzerror, bzfd, &source_index, sizeof(long));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        BZ2_bzRead(&bzerror, bzfd, &destination_index, sizeof(long));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        BZ2_bzRead(&bzerror, bzfd, &weight, sizeof(double));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        BZ2_bzRead(&bzerror, bzfd, &color, sizeof(int8_t));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

        graph->AddEdge(source_index, destination_index, weight, color);
    }

    // read the neuron and edge types for file verification
    long nvertex_types;
    BZ2_bzRead(&bzerror, bzfd, &nvertex_types, sizeof(long));
    if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    assert (nvertex_types <= 65536);
    for (long iv = 0; iv < nvertex_types; ++iv) {
        long index;
        char dummy[128];
        BZ2_bzRead(&bzerror, bzfd, &index, sizeof(long));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        BZ2_bzRead(&bzerror, bzfd, &dummy, sizeof(dummy));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    }

    long nedge_types;
    BZ2_bzRead(&bzerror, bzfd, &nedge_types, sizeof(long));
    // if there are no edge types this is the end 
    if (bzerror != BZ_OK && bzerror != BZ_STREAM_END) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    assert (nedge_types <= 7);

    // update the graph with the number of edge types
    graph->nedge_types = nedge_types;

    for (long ie = 0; ie < nedge_types; ++ie) {
        long index;
        char dummy[128];
        BZ2_bzRead(&bzerror, bzfd, &index, sizeof(long));
        if (bzerror != BZ_OK) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
        BZ2_bzRead(&bzerror, bzfd, &dummy, sizeof(dummy));
        if (bzerror != BZ_OK && bzerror != BZ_STREAM_END) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }
    }

    // make sure the end is reached
    if (bzerror != BZ_STREAM_END) { fprintf(stderr, "Failed to read %s\n", input_filename); return NULL; }

    // close files
    BZ2_bzReadClose(&bzerror, bzfd);
    fclose(fp);

    return graph;
}
