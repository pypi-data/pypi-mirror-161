
import numpy as np
from scipy.spatial.distance import pdist, squareform


class Lattice2D:
    # PBC enabled
    # bonds are sequential
    def __init__(self, n_beads):
        self._n_beads = n_beads

    # This isn't right...
    def permutations(self):
        """

        3 - 2
        4 - 5
        5 - 11?

        12345
        *****

        1234*
        ***5*

        123**
        **45*

        123**
        **4**
        **5**

        123**
        *54**

        12***
        *345*

        12***
        *3***
        *45**

        12***
        *3***
        *4***
        *5***

        12***
        *3***
        54***

        12***
        43***
        5****

        *12**
        453**

        541**
         32

        Returns
        -------

        """
        n_beads = self._n_beads
        from itertools import combinations_with_replacement
        xy = list(combinations_with_replacement(range(n_beads), r=2))
        for _ in combinations_with_replacement(xy, r=n_beads):
            if all(np.diag(squareform(pdist(_)), k=1) == 1):
                yield _

    def draw_permutations(self):
        n_beads = self._n_beads
        permutations = self.permutations()
        for permutation in permutations:
            a = np.empty((n_beads, n_beads), dtype='str')
            a[:] = ' '
            for x, y in permutation:
                a[x, y] = '*'
            yield a



"""
xx1xx
xx23x
xxx4x
"""


if __name__ == '__main__':
    lattice = Lattice2D(4)
    p = lattice.draw_permutations()




