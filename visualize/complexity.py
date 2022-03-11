import os



import matplotlib
import matplotlib.pyplot as plt



import numpy as np


plt.style.use('seaborn')
plt.rcParams['font.family'] = 'monospace'



from subgraph_enumeration.evaluation.complexity import PrintRunningTimeStatistics
from subgraph_enumeration.data_structures.enumeration import MapVerticesToNeighborhoodSizes




def ComputationalComplexityPerVertex(input_filename, graph, motif_size):
    """
    Plot the computatjonal complexity for the given graph and motif size

    @param input_filename: the file location where the graph is stored
    @param graph: the actual graph to consider
    @param motif_size: the size of motifs to consider
    """
    # get the running time and the subgraphs for this graph and motif size
    running_times, subgraphs = PrintRunningTimeStatistics(graph, input_filename, motif_size, vertex_colored = False, edge_colored = False, community_based = False)
    neighborhood_sizes = MapVerticesToNeighborhoodSizes(graph, enumerated = True)

    # get summary statistics for these three attributes
    running_times_y = []
    subgraphs_xy = []
    neighborhood_sizes_x = []

    for vertex_index in sorted(running_times.keys()):
        running_times_y.append(running_times[vertex_index])
        subgraphs_xy.append(subgraphs[vertex_index] / (10 ** 9))
        neighborhood_sizes_x.append(neighborhood_sizes[vertex_index])


    # plot the two charts
    fig = plt.figure(figsize=(8, 5))
    # get the axis for this plot
    ax = fig.add_subplot(111)

    ax.set_title('Running Time and No. Subgraphs', fontsize=26)
    ax.set_xlabel('No. Subgraphs (Billions)', fontsize=22)
    ax.set_ylabel('Running Time (seconds)', fontsize=22)
    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)

    ax.scatter(subgraphs_xy, running_times_y, s = 100, color='#3d85c6', marker='o')

    # get the output filename and save
    output_directory = 'figures'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok = True)

    plt.tight_layout()

    output_filename = '{}/{}-subgraphs-running-time.png'.format(output_directory, graph.prefix)
    plt.savefig(output_filename)

    # clear the figure
    plt.clf()

    # plot the two charts
    fig = plt.figure(figsize=(8, 5))
    # get the axis for this plot
    ax = fig.add_subplot(111)

    ax.set_title('Neighborhood Size and No. Subgraphs', fontsize=26)
    ax.set_xlabel('Neighborhood Size', fontsize=22)
    ax.set_ylabel('No. Subgraphs(Billions)', fontsize=22)
    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)


    ax.scatter(neighborhood_sizes_x, subgraphs_xy, s = 100, color='#8e7cc3', marker='o')

    # get the output filename and save
    output_directory = 'figures'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok = True)

    plt.tight_layout()

    output_filename = '{}/{}-subgraphs-neighborhood-size.png'.format(output_directory, graph.prefix)
    plt.savefig(output_filename)

    # clear the figure
    plt.clf()

     # plot the two charts
    fig = plt.figure(figsize=(8, 5))
    # get the axis for this plot
    ax = fig.add_subplot(111)

    ax.set_title('Neighborhood Size and Running Time', fontsize=26)
    ax.set_xlabel('Neighborhood Size', fontsize=22)
    ax.set_ylabel('Running Time (seconds)', fontsize=22)
    ax.tick_params(axis='x', labelsize=18)
    ax.tick_params(axis='y', labelsize=18)


    ax.scatter(neighborhood_sizes_x, running_times_y, s = 100, color='#8e7cc3', marker='o')

    # get the output filename and save
    output_directory = 'figures'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok = True)

    plt.tight_layout()

    output_filename = '{}/{}-neighborhood-size-time.png'.format(output_directory, graph.prefix)
    plt.savefig(output_filename)

    # clear the figure
    plt.clf()