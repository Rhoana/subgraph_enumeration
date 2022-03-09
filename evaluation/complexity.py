import glob



import matplotlib
import matplotlib.pyplot as plt



plt.style.use('seaborn')



import numpy as np



from addax.kavosh.enumerate import CreateDirectoryStructure
from addax.utilities.dataIO import ReadGraph



def PrintRunningTimeStatistics(graph, input_filename, motif_size, vertex_colored = False, edge_colored = False, community_based = False):
    """
    Print statistics for the running times for each vertex in the graph

    @param: graph: the input graph to evaluate
    @param input_filename: location for the graph that was enumerated
    @parak motif_size: the motif subgraph size to find
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    """
    # get the temp directory
    temp_directory = CreateDirectoryStructure(input_filename, vertex_colored, edge_colored, community_based, False)

    # get a list of all the input filenames for this motif size
    filenames = sorted(glob.glob('{}/certificates/motif-size-{:03d}-*.txt'.format(temp_directory, motif_size)))

    # create a dictionary of running times
    running_times = {}
    subgraphs = {}

    # keep track of the cpu time for each job
    cpu_times = []

    # read all of the filenames corresponding to enumeration data
    for filename in filenames:
        # keep track of the processor time
        cpu_time = 0.0

        # open the file
        with open(filename, 'r') as fd:
            # only worry about the lines with Enumerated summaries
            for line in fd.readlines():
                if not line.startswith('Enumerated'): continue

                # get the relevant stats from this line
                segments = line.split()
                nsubgraphs, vertex_index, time = int(segments[1]), int(segments[5]), float(segments[7])

                # add to the mapping of running times
                running_times[vertex_index] = time
                subgraphs[vertex_index] = nsubgraphs

                # update the time with this subgraph
                cpu_time += time

        # append to the list of job times
        cpu_times.append(cpu_time)

    wall_time = max(cpu_times)
    idle_cpu_time = 0.0
    for cpu_time in cpu_times:
        idle_cpu_time += (wall_time - cpu_time)

    # make sure that every vertex is accounted for
    assert (sorted(list(running_times.keys())) == sorted(list(graph.vertices.keys())))

    print ('Running Time Statistics for {} Motif Size {}'.format(graph.prefix, motif_size))
    print ('  Mean Time: {:0.2f} seconds'.format(np.mean(list(running_times.values()))))
    print ('  Median Time: {:0.2f} seconds'.format(np.median(list(running_times.values()))))
    print ('  Maximum Time: {:0.2f} seconds'.format(np.max(list(running_times.values()))))
    print ('  Std Dev: {:0.2f} seconds'.format(np.std(list(running_times.values()))))
    print ('  95th Percentile: {:0.2f} seconds'.format(np.percentile(list(running_times.values()), 95)))
    print ('  Wall Time: {:0.2f} minutes'.format(wall_time / 60))
    print ('  Idle CPU Time: {:0.2f} hours'.format(idle_cpu_time / 3600))
    print ('  Total Time: {:0.2f} seconds'.format(sum(list(running_times.values()))))

    return running_times, subgraphs



def EvaluateRunningTimes(input_filename, motif_size, vertex_colored = False, edge_colored = False, community_based = False):
    """
    Print statistics for the running times for each vertex in the graph

    @param input_filename: location for the graph that was enumerated
    @parak motif_size: the motif subgraph size to find
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    """
    # read the input graph
    graph = ReadGraph(input_filename, vertices_only = True)

    running_times, subgraphs = PrintRunningTimeStatistics(graph, input_filename, motif_size, vertex_colored = False, edge_colored = False, community_based = False)

    # create a figure for this statistic
    fig = plt.figure(figsize=(10, 5))

    # create the x and y variables
    x = []
    y = []

    # iterate over all variables
    for vertex_index in running_times.keys():
        x.append(subgraphs[vertex_index])
        y.append(running_times[vertex_index])


    # create an axis for the figure
    ax = fig.add_subplot(111)

    # plot the attribute
    ax.scatter(x, y)

    # set the titles
    ax.set_title('Running Times and No. Subgraphs', fontsize=20)
    ax.set_xlabel('No. Subgraphs', fontsize=18)
    ax.set_ylabel('Time (s)', fontsize=18)

    fig.tight_layout()

    plt.show()

    plt.clf()
