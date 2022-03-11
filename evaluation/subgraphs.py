import os
import sys



import networkx as nx



import matplotlib
import matplotlib.pyplot as plt



plt.style.use('seaborn')
plt.rcParams['font.family'] = 'Ubuntu'


from subgraph_enumeration.analysis.certificates import ReadCertificates, ReadSummaryStatistics
from subgraph_enumeration.kavosh.classify import ParseCertificate
from subgraph_enumeration.utilities.dataIO import ReadGraph



def FindFrequentMotifs():
    """
    Find the top ten most frequent motifs for all of the datasets and draw them
    """
    # the datasets
    datasets = {
        'hemi-brain': [
            'graphs/hemi-brain-minimum.graph.bz2',
        ],
        'C-elegans-timelapsed': [
            'graphs/C-elegans-timelapsed-01-minimum.graph.bz2',
            'graphs/C-elegans-timelapsed-02-minimum.graph.bz2',
            'graphs/C-elegans-timelapsed-03-minimum.graph.bz2',
            'graphs/C-elegans-timelapsed-04-minimum.graph.bz2',
            'graphs/C-elegans-timelapsed-05-minimum.graph.bz2',
            'graphs/C-elegans-timelapsed-06-minimum.graph.bz2',
            'graphs/C-elegans-timelapsed-07-minimum.graph.bz2',
            'graphs/C-elegans-timelapsed-08-minimum.graph.bz2',
        ],
        'C-elegans-sex': [
            'graphs/C-elegans-sex-male-minimum.graph.bz2',
            'graphs/C-elegans-sex-hermaphrodite-minimum.graph.bz2',
        ],
    }

    # the number of motifs to consider per dataset
    nmotifs = 5

    # assumes only 8 different motifs (works for datasets described)
    colors = [
        '#6aa84f',
        '#6fa8dc',
        '#0a5394',
        '#c27ba1',
        '#8e7cc3',
        '#38761d',
        '#e69138',
        '#e69138',
    ]

    # go through each of the datasets
    for dataset, input_filenames in datasets.items():
        print (dataset)
        certificates_per_dataset = {}

        # go through each input filename
        for input_filename in input_filenames:
            graph = ReadGraph(input_filename, vertices_only = True)

            # create the output directory if it doesn't exist 
            output_directory = 'figures/{}'.format(graph.prefix)
            if not os.path.exists(output_directory):
                os.makedirs(output_directory, exist_ok = True)

            certificates_per_dataset[input_filename] = {}

            # only consider k values of 4 and 5 
            for k in [4, 5]:
                # no colors or community based
                certificates, _, _ = ReadCertificates(input_filename, k, False, False, False, nmotifs)

                certificates_per_dataset[input_filename][k] = certificates

        # only consider k values of 4 and 5
        for k in [4, 5]:
        
            # count the number of unique certificates of size k
            certificate_to_color = {}
        
            for input_filename in certificates_per_dataset.keys():
                # count the number of unique certificates 
                for certificate, _ in certificates_per_dataset[input_filename][k].items():
                    if not certificate in certificate_to_color:
                        certificate_to_color[certificate] = colors[len(certificate_to_color)]
            print ('{} {} - {}'.format(dataset, k, len(certificate_to_color)))
            
            # go through each input filename and save the motifs 
            for input_filename in certificates_per_dataset.keys():
                graph = ReadGraph(input_filename, vertices_only = True)

                certificates = certificates_per_dataset[input_filename][k]

                # create a new figure with one row of nmotifs 
                fig, ax = plt.subplots(1, nmotifs)

                ratio = 3
                fig.set_figheight(ratio)
                fig.set_figwidth(nmotifs * ratio)

                for iv, (certificate, _) in enumerate(sorted(certificates.items(), key = lambda x: x[1], reverse = True)):
                    # vertex and edges are not colored, graph is directed 
                    nx_graph = ParseCertificate(k, certificate, False, False, True)

                    # get the position for networkx 
                    pos = nx.circular_layout(nx_graph)

                    # draw the network to matplotlib 
                    nx.draw_networkx_nodes(nx_graph, pos, ax = ax[iv], node_size = 800, linewidths = 2, node_shape = 'o', node_color = certificate_to_color[certificate])
                    nx.draw_networkx_edges(nx_graph, pos, ax = ax[iv], edge_color = 'black', arrowsize = 50, width = 3)

                    ax[iv].axis('off')

                    # draw a boundary around the nodes 
                    ax[iv].collections[0].set_edgecolor('#666666')

                output_directory = 'figures/{}'.format(graph.prefix)
                output_filename = '{}/motifs-{:03d}.png'.format(output_directory, k)

                plt.tight_layout()

                plt.savefig(output_filename)

                plt.close()


def CountDatasetStatistics():
    """
    Count the subgraphs for the published datasets
    """
    # the datasets
    input_filenames = {
        'Hemi-Brain': 'graphs/hemi-brain-minimum.graph.bz2',
        'C. elegans D1': 'graphs/C-elegans-timelapsed-01-minimum.graph.bz2',
        'C. elegans D2': 'graphs/C-elegans-timelapsed-02-minimum.graph.bz2',
        'C. elegans D3': 'graphs/C-elegans-timelapsed-03-minimum.graph.bz2',
        'C. elegans D4': 'graphs/C-elegans-timelapsed-04-minimum.graph.bz2',
        'C. elegans D5': 'graphs/C-elegans-timelapsed-05-minimum.graph.bz2',
        'C. elegans D6': 'graphs/C-elegans-timelapsed-06-minimum.graph.bz2',
        'C. elegans D7': 'graphs/C-elegans-timelapsed-07-minimum.graph.bz2',
        'C. elegans D8': 'graphs/C-elegans-timelapsed-08-minimum.graph.bz2',
        'C. elegans SH': 'graphs/C-elegans-sex-hermaphrodite-minimum.graph.bz2',
        'C. elegans SM': 'graphs/C-elegans-sex-male-minimum.graph.bz2',
    }

    for dataset, input_filename in input_filenames.items():
        # write the dataset
        sys.stdout.write('{} '.format(dataset))

        # iterate over k
        for k in [3, 4, 5, 6, 7]:
            # go through all possibilities
            nsubgraphs, _ = ReadSummaryStatistics(input_filename, k, False, False, False)

            # skip if this doesn't exist
            if not nsubgraphs:
                sys.stdout.write('& N/A ')
            else:
                sys.stdout.write('& {} '.format(nsubgraphs))

        sys.stdout.write('\\\\ \n')



def PlotMotifs(filenames, legend, k, output_prefix):
    """
    Plot the three motifs for these filenames with the legend

    @param filenames: the files to show the motifs for
    @param legend: the titles for each line
    @param k: the subgraph size
    @param k: location to save the file
    """
    # create an empty figure
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot()

    # set the preliminary information
    ax.set_title('Proportion of Subgraphs of Size {}'.format(k), fontsize=28)
    ax.set_xlabel('Motif', fontsize=24)
    ax.set_ylabel('Proportion of Subgraphs', fontsize=24)
    ax.tick_params(axis='x', labelsize=0)
    ax.tick_params(axis='y', labelsize=16)

    certificates_per_filename = {}
    total_subgraphs_per_filename = {}

    # go through every file
    for filename in filenames:
        # set vertex and edge color, and communities to zero
        certificates, total_subgraphs, _ = ReadCertificates(filename, k, False, False, False)

        certificates_per_filename[filename] = certificates
        total_subgraphs_per_filename[filename] = total_subgraphs

    # create a set of ordered statistics
    ordered_certificates = set()
    for filename in filenames:
        for certificate in certificates_per_filename[filename]:
            ordered_certificates.add(certificate)

    ordered_certificates = sorted(list(ordered_certificates))

    # set the x limit
    ax.set_xlim(xmin = 0, xmax = len(ordered_certificates) - 1)

    # iterate through all files
    for iv, filename in enumerate(filenames):
        certificates = certificates_per_filename[filename]
        total_subgraphs = total_subgraphs_per_filename[filename]

        proportions = []

        # go through all of the certificates
        for certificate in ordered_certificates:
            if not certificate in certificates:
                proportions.append(0)
            else:
                proportions.append(certificates[certificate] / total_subgraphs)

        ax.plot(proportions, label = legend[iv], linewidth = 2)

    # save the figure
    plt.legend(fontsize=16)

    plt.tight_layout()
    plt.savefig('{}-motif-size-{:03d}.png'.format(output_prefix, k))

    plt.clf()
