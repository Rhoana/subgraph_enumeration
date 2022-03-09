#ifndef __CPP_ENUMERATE_H__
#define __CPP_ENUMERATE_H__


// set global flags
void CppSetVertexColored(bool input_vertex_colored);
void CppSetEdgeColored(bool input_edge_colored);
void CppSetCommunityBased(bool input_community_based);
void CppSetWriteSubgraphs(bool input_write_subgraphs);

// enumeration functions
void CppEnumerateSubgraphsSequentially(const char *input_filename, const char *temp_directory, short k);
void CppEnumerateSubgraphsFromNodes(const char *input_filename, const char *temp_directory, short k, long *nodes, long nnodes, long output_suffix);



#endif
