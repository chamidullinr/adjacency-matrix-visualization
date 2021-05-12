import sys

from PyQt5.QtWidgets import QApplication

from src import io, data, ui, config


def get_adj_mat(filename):
    # load data
    data_dict = io.load_json(filename)

    # convert to dfs
    nodes_df, edges_df = data.get_graph(data_dict)

    name_col = 'title' if 'title' in nodes_df else 'name'
    type_col = 'archetype'

    # create adjacency matrix
    adj_mat = data.create_adj_mat(nodes_df, edges_df, name_col)

    # define note types map for heterogeneous graph
    node_type_map = nodes_df.set_index(name_col)[type_col].to_dict()

    return adj_mat, node_type_map


if __name__ == "__main__":
    # load adjacency matrix of several datasets
    data = [get_adj_mat(filename) for filename in config.DATASETS.values()]

    # create PyQt application
    app = QApplication(sys.argv)
    ex = ui.MainWindow(data)
    sys.exit(app.exec_())
