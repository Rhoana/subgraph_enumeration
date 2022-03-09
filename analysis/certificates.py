import os



from addax.utilities.dataIO import ReadGraph
from addax.kavosh.enumerate import CreateDirectoryStructure



def ReadCertificates(input_filename, k, vertex_colored, edge_colored, community_based, ncertificates = -1):
    """
    Read the certificates for this graph from the subgraphs directory

    @param input_filename: location for the graph to enumerate
    @parak k: the motif subgraph size to find
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    @param ncertificates: how many certificates to read (default = all)
    """
    # get the temp directory
    temp_directory = CreateDirectoryStructure(input_filename, vertex_colored, edge_colored, community_based, False)

    # get the input directory
    input_directory = 'subgraphs/{}'.format('/'.join(temp_directory.split('/')[1:]))

    # read the combined enumerated subgraphs file
    subgraphs_filename = '{}/motif-size-{:03d}-certificates.txt'.format(input_directory, k)

    certificates = {}

    # keep track of the total subgraphs
    total_time = 0
    total_subgraphs = 0

    with open(subgraphs_filename, 'r') as fd:
        # read all of the certificates and enumerated subgraphs
        for index, certificate_info in enumerate(fd):
            if certificate_info.startswith('Found'): continue
            elif certificate_info.startswith('Enumerated'):
                total_subgraphs = int(certificate_info.split()[1])
                total_time = float(certificate_info.split()[-2])
            else:
                certificate = certificate_info.split(':')[0].strip()
                nsubgraphs = int(certificate_info.split(':')[1].strip())

                certificates[certificate] = nsubgraphs

            # skip if the number of certificates is specified
            if ncertificates > 0 and ncertificates == index: break

    # return the certificates and the number of subgraphs
    return certificates, total_subgraphs, total_time



def ReadSummaryStatistics(input_filename, k, vertex_colored, edge_colored, community_based):
    """
    Read the last line that gives the number of subgraphs and total running time

    @param input_filename: location for the graph to enumerate
    @parak k: the motif subgraph size to find
    @param vertex_colored: a boolean flag to allow for vertex colors
    @param edge_colored: a boolean flag to allow for edge colors
    @param community_based: a boolean flag to only enumerate subgraphs in the same community
    """
    # get the temp directory
    temp_directory = CreateDirectoryStructure(input_filename, vertex_colored, edge_colored, community_based, False)

    # get the input directory
    input_directory = 'subgraphs/{}'.format('/'.join(temp_directory.split('/')[1:]))

    # read the combined enumerated subgraphs file
    subgraphs_filename = '{}/motif-size-{:03d}-certificates.txt'.format(input_directory, k)

    # if this does not exist return -1
    if not os.path.exists(subgraphs_filename):
        return 0, 0

    with open(subgraphs_filename, 'rb') as fd:
        fd.seek(-2, os.SEEK_END)
        while (fd.read(1) != b'\n'):
            fd.seek(-2, os.SEEK_CUR)

        summary = fd.readline().decode()

        subgraphs = int(summary.split()[1])
        total_time = float(summary.split()[-2])

    return subgraphs, total_time
