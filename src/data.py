import numpy as np
import pandas as pd
from copy import deepcopy


def get_graph(graph_dict):
    def process_node_edge(node_edge, archetypes, attr_types):
        out = deepcopy(node_edge)
        if 'subedgeInfo' in out:
            out.update(out['subedgeInfo'][0])

        out['archetype'] = archetypes[out['archetype']]['name']
        if isinstance(out['attributes'], dict):
            out['attributes'] = {attr_types[int(k)]['name']: v
                                 for k, v in out['attributes'].items()}
        elif isinstance(out['attributes'], list):
            out['attributes'] = {item[0]: item[1] for item in out['attributes']}
        return out

    def expand_attributes_in_df(df):
        return pd.concat([df, df['attributes'].apply(pd.Series)],
                         axis=1).drop(columns=['attributes'])

    # get node, edge data
    nodes = graph_dict['vertices']
    edges = graph_dict['edges']

    # get metadata
    attr_types = graph_dict['attributeTypes']
    node_archetypes = graph_dict['vertexArchetypes']
    edge_archetypes = graph_dict['edgeArchetypes']

    nodes = [process_node_edge(item, node_archetypes, attr_types) for item in nodes]
    edges = [process_node_edge(item, edge_archetypes, attr_types) for item in edges]

    # convert to DataFrames
    nodes_df = expand_attributes_in_df(pd.DataFrame(nodes))
    edges_df = expand_attributes_in_df(pd.DataFrame(edges))

    return nodes_df, edges_df


def create_adj_mat(nodes_df, edges_df, name_col):
    name_id_map = nodes_df[['id', name_col]].set_index('id')[name_col].to_dict()

    # create pivot table
    adj_mat = pd.crosstab(edges_df['from'], edges_df['to'])

    # add missing rows / columns
    for item in nodes_df['id']:
        if item not in adj_mat.columns:
            adj_mat.loc[:, item] = 0

        if item not in adj_mat.index:
            adj_mat.loc[item] = 0

    assert adj_mat.shape[0] == adj_mat.shape[1] == len(nodes_df)

    # postprocess matrix
    adj_mat = np.sign(adj_mat)
    adj_mat = adj_mat.rename(name_id_map).rename(columns=name_id_map)

    # make symmetric
    x_idx, y_idx = np.where(adj_mat != 0)
    adj_mat_np = adj_mat.values
    adj_mat_np[y_idx, x_idx] = 1
    adj_mat[:] = adj_mat_np
    assert np.allclose(adj_mat, adj_mat.T), 'Adj matrix is not symmetric, there is an error in code'

    return adj_mat
