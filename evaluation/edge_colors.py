import sys



from subgraph_enumeration.analysis.certificates import ReadSummaryStatistics



def EdgeColorComputationTimes():
    """
    Calculate the increased computation time for edges
    """
    #the values of k to compare
    ks = [3, 4, 5, 6]

    datasets = {
        'Hemi-Brain': 'graphs/hemi-brain-minimum.graph.bz2',
        'C. elegans Hermaphrodite': 'graphs/C-elegans-sex-hermaphrodite-minimum.graph.bz2',
        'C. elegans Male': 'graphs/C-elegans-sex-male-minimum.graph.bz2'
        }

    # iterate over all datasets
    for dataset, input_filename in datasets.items():
        # write the first columnn
        sys.stdout.write('\\textbf{{{}}} '.format(dataset))

        # iterate over all values of k
        for k in ks:
            # the hemi-brain dataset does not have much higher motifs
            if dataset == 'Hemi-Brain' and k >= 5:
                sys.stdout.write('& N/A ')
                continue

            # read the statistics with edge coloring off
            _, colorless_time = ReadSummaryStatistics(input_filename, k, False, False, False)

            # read the statistics with edge coloring on
            _, edge_colored_time = ReadSummaryStatistics(input_filename, k, False, True, False)

            # get the increased time
            increased_time = 100 * (edge_colored_time - colorless_time) / colorless_time

            # determine if we need seconds, hours, or days
            if edge_colored_time < 3600:
                sys.stdout.write('& {:0.2f}/{:0.2f} sec ({:0.0f}\\%) '.format(colorless_time, edge_colored_time, increased_time))
            elif edge_colored_time < 86400:
                sys.stdout.write('& {:0.2f}/{:0.2f} hr ({:0.0f}\\%) '.format(colorless_time / 3600, edge_colored_time / 3600, increased_time))
            elif edge_colored_time < 31557600:
                sys.stdout.write('& {:0.2f}/{:0.2f} d ({:0.0f}\\%) '.format(colorless_time / 86400, edge_colored_time / 86400, increased_time))
            else:
                sys.stdout.write('& {:0.2f}/{:0.2f} yr ({:0.0f}\\%) '.format(colorless_time / 31557600, edge_colored_time / 31557600, increased_time))

        sys.stdout.write('\\\\\n')
