import numpy as np



from addax.analysis.certificates import ReadCertificates
from addax.evaluation.certificate import CosineSimilarity, L1, TotalVariationalDistance



def EvaluateCommunities(k, edge_colored):
    """
    Evaluate the results of the METIS communities

    @param k: the size of the motifs to read
    @param edge_colored: a boolean flag to allow for edge colors
    """

    # create dictionaries
    metis_certificates = {}
    metis_total_subgraphs = {}
    metis_total_time = {}

    # read the global information
    input_filename = 'graphs/hemi-brain-minimum.graph.bz2'

    # get the ceertificates
    certificates, total_subgraphs, total_time = ReadCertificates(input_filename, k, False, edge_colored, False)

    # update dictionary entries
    metis_certificates[1] = certificates
    metis_total_subgraphs[1] = total_subgraphs
    metis_total_time[1] = total_time

    # iterate over all communities
    communities = [5, 10, 15, 20, 25, 30]
    for community in communities:
        # read the graph for this file
        input_filename = 'graphs/hemi-brain-minimum-metis-{:02d}.graph.bz2'.format(community)

        # get the certificates (vertex_colored is False and community_based is True)
        certificates, total_subgraphs, total_time = ReadCertificates(input_filename, k, False, edge_colored, True)

        metis_certificates[community] = certificates
        metis_total_subgraphs[community] = total_subgraphs
        metis_total_time[community] = total_time

    # create vectors for the certificates
    unique_certificates = set()
    # the values are certificates
    for certificates in metis_certificates.values():
        for certificate in certificates:
            unique_certificates.add(certificate)
    ncertificates = len(unique_certificates)
    unique_certificates = sorted(list(unique_certificates))

    # create vectors
    metis_vectors = {}

    # create vectors for each community
    for community, certificates in metis_certificates.items():
        metis_vectors[community] = np.zeros(ncertificates, dtype=np.float64)

        for iv, unique_certificate in enumerate(unique_certificates):
            if unique_certificate in metis_certificates[community]:
                metis_vectors[community][iv] = metis_certificates[community][unique_certificate] / metis_total_subgraphs[community]
            else:
                metis_vectors[community][iv] = 0

    # print out the latex table
    print ('\\textbf{No. Communities} & \\textbf{No. Subgraphs} & \\textbf{Total Time} & \\textbf{Cosine Similarity} \\\\ \hline')
    for community in sorted(metis_certificates.keys()):
        if k == 3: print ('{} & {} & \\SI{{{:0.2f}}}{{\sec}} & {:0.4f} \\\\'.format(community, metis_total_subgraphs[community], metis_total_time[community], TotalVariationalDistance(metis_vectors[1], metis_vectors[community])))
        elif k == 4: print ('{} & {} & \\SI{{{:0.2f}}}{{\hour}} & {:0.4f} \\\\'.format(community, metis_total_subgraphs[community], metis_total_time[community] / (3600), TotalVariationalDistance(metis_vectors[1], metis_vectors[community])))
        else: print ('{} & {} & \\SI{{{:0.2f}}}{{\year}} & {:0.4f} \\\\'.format(community, metis_total_subgraphs[community], metis_total_time[community] / 31557600, TotalVariationalDistance(metis_vectors[1], metis_vectors[community])))
