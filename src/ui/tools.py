from PyQt5.QtWidgets import QLayout, QFormLayout, QGroupBox


def create_widget(widget_cls, *args, items=None, **kwargs):
    widget = widget_cls(*args, **kwargs)
    if items is not None and hasattr(widget, 'addItems'):
        widget.addItems(items)
    return widget


def create_layout(layout_cls, widgets, *, alignment=None, parent=None):
    layout = layout_cls(parent)
    for widget in widgets:
        if isinstance(widget, QLayout):
            layout.addLayout(widget)
        else:
            layout.addWidget(widget)
    if alignment is not None:
        layout.setAlignment(alignment)
    return layout


def create_form_group(name, widgets):
    form_group = QGroupBox(name)
    layout = QFormLayout()
    for widget in widgets:
        if isinstance(widget, (tuple, list)):
            layout.addRow(*widget)
        else:
            layout.addRow(widget)
    form_group.setLayout(layout)
    return form_group
