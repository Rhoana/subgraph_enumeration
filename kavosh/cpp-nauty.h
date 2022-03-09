#ifndef __CPP_NAUTY_H__
#define __CPP_NAUTY_H__

/* Code modified from Peter Dobsan's pynauty repository.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.  This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

*/

#define WORKSPACE_FACTOR    66

#include <nauty.h>

class NyGraph {
public:
    NyGraph(int no_vertices, bool colored);
    ~NyGraph(void);

    // options for nauty algorithm
    optionblk *options;

    int no_vertices;
    bool colored;
    int no_setwords;
    // adjacency matrix as a bit array
    setword *matrix;
    // adjacency matrix for the canonical graph
    setword *cmatrix;
    // coloring: represented as 0-level partition of vertices
    int *lab;
    int *ptn;
    // orbits under Autgrp
    int *orbits;

    statsblk *stats;
    int worksize;
    setword *workspace;
};

#endif
