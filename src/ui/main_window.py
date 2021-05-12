from PyQt5.QtWidgets import QWidget, QHBoxLayout

from . import tools
from .. import config
from .filter_widget import FilterWidget
from .scene_widget import SceneWidget

_cache = {}


class MainWindow(QWidget):
    def __init__(self, datasets: list):
        super(MainWindow, self).__init__()
        self.datasets = datasets

        # set current view data
        self.data = self.get_dataset(ds_idx=0, alg_idx=0)

        # precompute dataset and algorithms
        for ds_idx, alg_idx in zip(range(len(self.datasets)), range(len(config.ALGORITHMS))):
            self.get_dataset(ds_idx, alg_idx)

        # define window setup
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setMinimumSize(*config.SCENE_SIZE)

        # create widgets
        self.filter_widget = FilterWidget(
            self, submit_btn_cb=self.update_scene_callback,
            inverse_index_btn_cb=self.inverse_index_callback)
        self.viz_widget = SceneWidget(self, self.data, self.filter_widget)

        # create layout
        self.setLayout(
            tools.create_layout(QHBoxLayout, [self.filter_widget, self.viz_widget], parent=self))

        self.show()

    def get_dataset(self, ds_idx: int, alg_idx: int):
        assert ds_idx < len(self.datasets)
        assert alg_idx < len(config.ALGORITHMS)

        if (ds_idx, alg_idx) in _cache:
            adj_mat, node_type_map = _cache[(ds_idx, alg_idx)]
        else:
            # adjacency matrix
            adj_mat, node_type_map = self.datasets[ds_idx]
            alg = list(config.ALGORITHMS)[alg_idx]
            alg_fn = config.ALGORITHMS[alg]

            # apply reordering algorithm
            adj_mat = alg_fn(adj_mat)

            # store to cache
            _cache[(ds_idx, alg_idx)] = adj_mat, node_type_map

        return adj_mat, node_type_map

    def update_scene_callback(self, ds_idx: int, alg_idx: int):
        self.data = self.get_dataset(ds_idx, alg_idx)
        self.viz_widget.update_data(self.data)

    def inverse_index_callback(self):
        adj_mat, node_type_map = self.data
        adj_mat = adj_mat.loc[adj_mat.index[::-1], adj_mat.columns[::-1]]
        self.data = (adj_mat, node_type_map)
        self.viz_widget.update_data(self.data)
