import math



import numpy as np


import matplotlib
import matplotlib.pyplot as plt



def PlotDegrees(degrees):
    """
    Plot the degree distribution.

    @param degrees: a list of degrees from the graph
    """
    # get the number of vertices in the grpah
    nvertices = len(degrees)
    # get the maximum degree
    max_degree = max(degrees)

    # construct a degree distribution
    degree_distribution = [0 for _ in range(max_degree + 1)]
    for degree in degrees:
        degree_distribution[degree] += 1

    # get the probability of each degree
    cdf = [1.0 - sum(degree_distribution[iv:]) / nvertices for iv in range(1, max_degree + 1)]

    plt.title('CDF of Degree Distribution')
    plt.xlabel('Vertex Degree')
    plt.ylabel('Probability')

    plt.plot(cdf)
    plt.show()




def ModelDegreeDistribution(graph):
    """
    Model the distribution of edge degrees for each vertex

    @param graph: the graph for which to analyze the edge distribution
    """
    # get a list of all degrees
    incoming_degrees = []
    outgoing_degrees = []
    degrees = []

    # iterate over all vertices in the graph
    for index, vertex in graph.vertices.items():
        incoming_degrees.append(len(vertex.incoming_neighbors))
        outgoing_degrees.append(len(vertex.outgoing_neighbors))
        degrees.append(len(vertex.neighbors))

    PlotDegrees(degrees)
    PlotDegrees(incoming_degrees)
    PlotDegrees(outgoing_degrees)



def PlotSynapseWeights(graph):
    """
    Plot the number of edges as a function of the synapse weights

    @param graph: the graph for which to analyze the edge distribution
    """
    # create an array of edge weights
    edge_weights = []
    for edge in graph.edges:
        edge_weights.append(int(round(edge.weight)))

    # sort the edge weights with the lowest number first
    edge_weights.sort()

    # get the minimum and maximum edge weights
    min_weight = edge_weights[0]
    max_weight = edge_weights[-1]

    # create an array for the number of edges greater than a given weight
    edges_over_weight = [0 for _ in range(max_weight + 1)]

    # iterate over the edge weights list
    edge_weight_index = 0
    for weight in range(max_weight + 1):
        # continually increment the edge weight index to
        # remove all edges less than this weight
        while edge_weights[edge_weight_index] < weight:
            edge_weight_index += 1

        # get the number of edges with weights greater than this
        edges_over_weight[weight] =len(edge_weights) - edge_weight_index

    plt.plot([math.log(iv, 10) for iv in range(min_weight, max_weight + 1)], edges_over_weight[1:])

    # plot figure titles/axes
    plt.title('Edge Weights')
    plt.xlabel('Synaptic Weight (Log Scale)')
    plt.ylabel('Edges with More Weight')

    plt.savefig('figures/{}/synaptic-weight.png'.format(graph.prefix.title().replace('-', '')))
