import numpy as np
import math
from itertools import product

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsView, QWidget, QVBoxLayout,
                             QGraphicsRectItem, QGraphicsTextItem)
from PyQt5.QtGui import QPen, QBrush, QPainter, QFont

from . import tools, colors
from .. import config


class MatrixCellRect(QGraphicsRectItem):
    def __init__(self, x, y, size, is_one, is_diagonal, col_value, row_value):
        super(MatrixCellRect, self).__init__(x, y, size, size)
        self.col_value = col_value
        self.row_value = row_value

        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.ArrowCursor)

        self.pen = QPen(colors.COLORS[None])
        if is_one:
            self.brush_default = QBrush(colors.TAB10[0])
        elif is_diagonal:
            self.brush_default = QBrush(colors.COLORS['gray'])
        else:
            self.brush_default = QBrush(colors.COLORS['white'])
        self.brush_selected = QBrush(colors.TAB10[1])

        self.setPen(self.pen)
        self.setBrush(self.brush_default)

    def hoverEnterEvent(self, event):
        self.setBrush(self.brush_selected)
        self.setToolTip(f'{self.row_value} - {self.col_value}')

    def hoverLeaveEvent(self, event):
        self.setBrush(self.brush_default)
        self.setToolTip(None)


class MatrixColRowText(QGraphicsTextItem):
    def __init__(self, x, y, value, color, rotate=None):
        super(MatrixColRowText, self).__init__()
        self.value = value
        self.setPlainText(self.value[:20] + '...' if len(self.value) > 20 else self.value)
        self.setPos(x, y)
        self.setDefaultTextColor(color)
        # self.setTextWidth(width)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.ArrowCursor)

        # set bold font
        font = QFont()
        font.setBold(True)
        self.setFont(font)

        # rotate text
        if rotate is not None:
            self.setRotation(rotate)

    def hoverEnterEvent(self, event):
        self.setToolTip(self.value)

    def hoverLeaveEvent(self, event):
        self.setToolTip(None)


class GraphicsView(QGraphicsView):
    """Class that enables scrolling (for zooming) and dragging the view."""

    def __init__(self, scene, parent):
        super(GraphicsView, self).__init__(scene, parent)
        self.scene = scene

        self.start_x = 0.0
        self.start_y = 0.0
        self.distance = 0.0

        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def wheelEvent(self, event):
        zoom = 1 + event.angleDelta().y() * 0.001
        self.scale(zoom, zoom)

    def mousePressEvent(self, event):
        self.start_x = event.pos().x()
        self.start_y = event.pos().y()
        self.scene.was_dragg = False
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        end_x = event.pos().x()
        end_y = event.pos().y()
        delta_x = end_x - self.start_x
        delta_y = end_y - self.start_y
        distance = math.sqrt(delta_x*delta_x + delta_y*delta_y)
        if distance > 5:
            self.scene.was_dragg = True
        super().mouseReleaseEvent(event)


class SceneWidget(QWidget):
    def __init__(self, parent, data, filter_widget):
        super(SceneWidget, self).__init__(parent)
        self.filter_widget = filter_widget
        self.scene_size = config.SCENE_SIZE

        # create graphic view
        self.scene = QGraphicsScene()
        self.view = GraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, *self.scene_size)

        # create layout
        self.setLayout(tools.create_layout(QVBoxLayout, [self.view], parent=self))

        # draw scene and populate legend
        self.update_data(data)

    def update_data(self, data, init=False):
        self.scene.clear()
        self.map_data(data)

        node_type_colors = self.get_node_type_colors(data[1])
        self.filter_widget.update_legend(node_type_colors)

    def get_node_type_colors(self, node_type_map):
        unique_node_types = np.unique(list(node_type_map.values()))
        node_type_colors = {item: colors.TAB10[i] for i, item in enumerate(unique_node_types)}
        return node_type_colors

    def map_data(self, data):
        adj_mat, node_type_map = data
        n = len(adj_mat)

        # render columns and rows of adjacency matrix
        node_type_colors = self.get_node_type_colors(node_type_map)
        for i in range(n):  # row indexes
            node_name = adj_mat.index[i]
            node_type = node_type_map[node_name]
            self.scene.addItem(MatrixColRowText(
                x=0,
                y=config.COL_OFFSET + i * config.RECT_SIZE,
                value=node_name,
                color=node_type_colors[node_type]))

        for i in range(n):  # column names
            node_name = adj_mat.index[i]
            node_type = node_type_map[node_name]
            self.scene.addItem(MatrixColRowText(
                x=config.ROW_OFFSET + i * config.RECT_SIZE,
                y=0,
                value=node_name,
                color=node_type_colors[node_type],
                rotate=-90))

        # render body of adjacency matrix
        for i, j in product(range(n), range(n)):
            self.scene.addItem(MatrixCellRect(
                x=config.ROW_OFFSET + i * config.RECT_SIZE,
                y=config.COL_OFFSET + j * config.RECT_SIZE,
                size=config.RECT_SIZE - config.PAD,
                is_one=adj_mat.iloc[i, j] == 1,
                is_diagonal=i == j,
                col_value=adj_mat.index[i],
                row_value=adj_mat.index[j]))
