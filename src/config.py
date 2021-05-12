from src import core


# data and algorithms definitions
DATA_DIR = 'data/'
DATASETS = {'Dataset 1': DATA_DIR + 'histrocal-data.json',
            'Dataset 2': DATA_DIR + 'raw.json',
            'Dataset 3': DATA_DIR + 'SW-eng-anonymized-demo-graph.json'}
ALGORITHMS = {'Raw data': lambda x: x,
              'Count based (naive)': core.count_perm,
              'Similarity based': core.nearest_neigbor_perm,
              'Reverse Cuthill-McKee': core.rcm_perm,
              'Hierarchical Clustering': core.hierarchical_clustering_perm}


# UI configuration
WINDOW_TITLE = 'Adjacency Matrix Visualization'

# scene and widget sizes
SCENE_SIZE = (800, 600)
FILTER_WIDGET_WIDTH = 240

# visualization sizes
RECT_SIZE = 16
PAD = 0
ROW_OFFSET = 160
COL_OFFSET = 0  # not needed because of rotation -90
