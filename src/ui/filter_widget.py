from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QComboBox, QVBoxLayout, QPushButton, QLabel

from . import tools
from .. import config


class FilterWidget(QWidget):
    def __init__(self, parent, submit_btn_cb, inverse_index_btn_cb):
        super(QWidget, self).__init__(parent)

        self.setFixedWidth(config.FILTER_WIDGET_WIDTH)

        # create individual groups
        self.create_filter_group(submit_btn_cb)
        self.create_inverse_index_btn(inverse_index_btn_cb)
        self.create_legend_group()

        # create layout
        self.layout = tools.create_layout(
            QVBoxLayout, [self.filter_group, self.inverse_index_btn, self.legend_group],
            alignment=Qt.AlignTop, parent=self)
        self.setLayout(self.layout)

    def create_filter_group(self, submit_btn_cb):
        # create form items
        self.datasets_dropdown = tools.create_widget(
            QComboBox, items=config.DATASETS.keys(), parent=self)
        self.algorithms_dropdown = tools.create_widget(
            QComboBox, items=config.ALGORITHMS.keys(), parent=self)

        # create button
        submit_btn = tools.create_widget(QPushButton, 'Submit', parent=self)
        submit_btn.clicked.connect(
            lambda: submit_btn_cb(self.datasets_dropdown.currentIndex(),
                                  self.algorithms_dropdown.currentIndex()))

        # group all items into groupbox
        self.filter_group = tools.create_form_group('Visualization Parameters', [
            (QLabel('Dataset:'), self.datasets_dropdown),
            (QLabel('Algorithm:'), self.algorithms_dropdown),
            submit_btn])

    def create_inverse_index_btn(self, inverse_index_btn_cb):
        self.inverse_index_btn = tools.create_widget(
            QPushButton, 'Inverse Rows and Columns', parent=self)
        self.inverse_index_btn.clicked.connect(inverse_index_btn_cb)

    def create_legend_group(self):
        def create_blank_label():
            label = QLabel(parent=self)
            label.setVisible(False)
            return label

        # create 10 invisible labels (not all of them will be used)
        self.labels = [create_blank_label() for _ in range(6)]
        self.legend_group = tools.create_form_group('Legend', self.labels)

    def update_legend(self, node_type_colors):
        for i, (text, color) in enumerate(node_type_colors.items()):
            label = self.labels[i]
            label.setText(text)
            color_str = 'rgb({}, {}, {})'.format(*color.getRgb()[:3])
            label.setStyleSheet(f'color: {color_str}')
            label.setVisible(True)

        # make remaining labels invisible
        for label in self.labels[len(node_type_colors):]:
            label.setVisible(False)
