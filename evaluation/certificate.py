import math
import numpy as np



def TotalVariationalDistance(certificate_one, certificate_two):
    """
    Calculate the total variational distance between two vectors of certificates

    @param certificate_one: certificates for vector one
    @param certificate_two: certificates for vector two
    """

    return max(np.abs(certificate_one - certificate_two))


def L1(certificate_one, certificate_two):
    """
    Calculate the L1 distance between the two certificates

    @param certificate_one: certificates for vector one
    @param certificate_two: certificates for vector two
    """

    return sum(np.abs(certificate_one - certificate_two))



def CosineSimilarity(certificate_one, certificate_two):
    """
    Calculate the cosine similiarity between two vectors of certificates

    @param certificate_one: certificates for vector one
    @param certificate_two: certificates for vector two
    """
    # make sure that the certificates are 64-bits
    assert (certificate_one.dtype == np.float64)
    assert (certificate_two.dtype == np.float64)

    return (np.dot(certificate_one, certificate_two) / (np.linalg.norm(certificate_one) * np.linalg.norm(certificate_two)))
