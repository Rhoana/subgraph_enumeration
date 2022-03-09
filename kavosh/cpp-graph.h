#ifndef __CPP_GRAPH_H__
#define __cpp_graph_H__

#include <assert.h>
#include <vector>
#include <stdlib.h>
#include <cstring>
#include <unordered_set>
#include <map>
#include <bzlib.h>



class Vertex;
class Edge;
class Graph;



// I/O functions for raeding a graph
Graph *ReadGraph(const char input_filename[4096]);
Graph *ReadBZ2Graph(const char input_filename[4096]);



class Vertex {
public:
    // constructors/destructors
    Vertex(Graph *graph, long index, long enumeration_index, long community, int16_t color);
    ~Vertex();

    // modifying functions
    void AddEdge(Edge *edge);

    // instance variables
    Graph *graph;
    long index;
    long enumeration_index;
    long community;
    int16_t color;


    // extra instance variables keep track of the ingoing and outgoing edges from the vertex
    std::vector<Edge *> incoming_edges;
    std::vector<Edge *> outgoing_edges;
    // keep track of incoming and outgoing neighbors
    std::unordered_set<long> incoming_neighbors;
    std::unordered_set<long> outgoing_neighbors;
    std::unordered_set<long> neighbors;
};



class Edge {
public:
    // constructors/destructors
    Edge(Graph *graph, long source_index, long destination_index, double weight, int8_t color);
    ~Edge();

    // instance variables
    Graph *graph;
    long source_index;
    long destination_index;
    double weight;
    int8_t color;
};




class Graph {
public:
    // constructors/destructors
    Graph(const char input_prefix[128], bool input_directed, bool input_vertex_colored, bool input_edge_colored);
    ~Graph();

    // modifying functions
    void AddVertex(long index, long enumeration_index, long community = -1, int16_t color = -1);
    void AddEdge(long source_index, long destination_index, double weight = -1, int8_t color = -1);

    // attribute functions
    long NVertices(void);
    long NEdges(void);

    // instance variables
    char prefix[128];
    bool directed;
    bool vertex_colored;
    bool edge_colored;
    std::map<long, Vertex *> vertices;
    std::map<std::pair<long, long>, Edge *> edges;
    long nedge_types;
};



#endif
