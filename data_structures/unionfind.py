class UnionFindElement:
    def __init__(self, label):
        """
        Union-Find class that implements an algorithm for joining together a set of objects

        @param label: a unique label to identify this given element in the union-find data structure

        Additional instance variables parent and rank define the trees in the union-find data structure
        """
        self.label = label
        # all elements initially are their own parents
        self.parent = self
        # initially all elements start as their own tree with rank (distance to root) of zero
        self.rank = 0

    def Label(self):
        """
        Returns the label for this element
        """
        return self.label

    def Parent(self):
        """
        Returns the parent of this element
        """
        return self.parent

    def Rank(self):
        """
        Returns the rank of this element (i.e., how far the element is from a root)
        """
        return self.rank



def Find(element):
    """
    Recursively find the parent element to the given element by climbing up the tree

    @param element: the element for which to find the root

    Returns a reference to the root of the tree to which this element belongs
    """
    if (element.parent != element):
        element.parent = Find(element.parent)
    return element.parent



def Union(element_one, element_two):
    """
    Combine these two elements in the data structure by linking their trees together

    @param element_one, element_two: the two elements to link together
    """
    # find the roots for both trees
    root_one = Find(element_one)
    root_two = Find(element_two)

    # if already linked, continue
    if (root_one == root_two): return

    # link the smaller ranked tree to the larger one, if equal ranks, update the first parent's rank
    # note we do not care about the ranks of the non roots since they are never used in the algorithm
    if (root_one.rank < root_two.rank):
        root_one.parent = root_two
    elif (root_one.rank > root_two.rank):
        root_two.parent = root_one
    else:
        root_two.parent = root_one
        root_one.rank = root_one.rank + 1
