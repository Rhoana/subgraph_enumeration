#include "cpp-nauty.h"

/* Code modified from Peter Dobsan's pynauty repository.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.  This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

*/


// Nauty default options
// unfortunately, defined as macro in Nauty
//
static DEFAULTOPTIONS(default_options);



NyGraph::NyGraph(int no_vertices, bool colored)
{

    this->no_vertices = no_vertices;
    this->colored = colored;
    this->no_setwords = (no_vertices + WORDSIZE - 1) / WORDSIZE;

    // verify nauty parameters
    nauty_check(WORDSIZE, this->no_setwords, this->no_vertices, NAUTYVERSIONID);

    this->matrix = (setword *)malloc((size_t) this->no_setwords * (size_t) (this->no_vertices * sizeof(setword)));
    if (this->matrix == NULL) exit(-1);
    this->cmatrix = (setword *)malloc(this->no_setwords * this->no_vertices * WORDSIZE);
    if (this->cmatrix == NULL) exit(-1);
    this->lab = (int *)malloc(no_vertices * sizeof(int));
    if (this->lab == NULL) exit(-1);
    this->ptn = (int *)malloc(no_vertices * sizeof(int));
    if (this->ptn == NULL) exit(-1);
    this->orbits = (int *)malloc(no_vertices * sizeof(int));
    if (this->orbits == NULL) exit(-1);
    this->options = (optionblk *)malloc(sizeof(optionblk));
    if (this->options  == NULL) exit(-1);

    // get default options
    memcpy(this->options, &default_options, sizeof(optionblk));
    // update options for our purposes
    this->options->digraph = TRUE;
    this->options->getcanon = TRUE;
    // set to false for vertex colors
    if (this->colored) this->options->defaultptn = FALSE;
    else this->options->defaultptn = TRUE;
    this->options->writeautoms = FALSE;
    this->options->cartesian = TRUE;
    this->options->userautomproc = NULL;

    this->stats = (statsblk *)malloc(sizeof(statsblk));
    if (this->stats == NULL) exit(-1);
    this->worksize = WORKSPACE_FACTOR * this->no_setwords;
    this->workspace = (setword *)malloc(this->worksize * sizeof(setword));
    if (this->workspace == NULL) exit(-1);

    // clear the graph (malloc does not clear the memory space)
    EMPTYGRAPH(this->matrix, this->no_setwords, this->no_vertices);
}



NyGraph::~NyGraph(void)
{
    free(this->options);
    free(this->matrix);
    free(this->cmatrix);
    free(this->lab);
    free(this->ptn);
    free(this->orbits);
    free(this->stats);
    free(this->workspace);
}
