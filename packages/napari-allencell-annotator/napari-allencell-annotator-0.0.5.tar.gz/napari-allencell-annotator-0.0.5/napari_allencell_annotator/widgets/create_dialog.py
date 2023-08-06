from typing import Dict

from qtpy import QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QScrollArea,
    QHBoxLayout,
)
from psygnal._signal import Signal

from napari_allencell_annotator.widgets.annotation_widget import AnnotationWidget


class CreateDialog(QDialog):
    """
    A class that creates up to 10 annotations in a popup dialog.

    Methods
    -------
    get_annots()
        Sets annotation dictionary and emits valid_annots_made signal if all annotations are valid.
    """

    # signal emitted when all annotations created are valid
    valid_annots_made = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Annotations")
        self.setMinimumSize(700, 500)

        self.list = AnnotationWidget()
        self.list.add_new_item()

        label = QLabel("Create Annotations")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 15))
        self.layout = QVBoxLayout()
        self.layout.addWidget(label)

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.list)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll, stretch=15)

        self.add = QPushButton("Add +")
        self.delete = QPushButton("Delete Selected")
        self.cancel = QPushButton("Cancel")
        self.apply = QPushButton("Apply")
        self.btns = QWidget()
        self.new_annot_dict: Dict[str, Dict] = None
        layout = QHBoxLayout()
        layout.addWidget(self.add)
        layout.addWidget(self.delete)
        sp_retain = QtWidgets.QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.delete.setSizePolicy(sp_retain)
        self.delete.hide()
        layout.addWidget(self.cancel)
        layout.addWidget(self.apply)

        self.btns.setLayout(layout)
        self.error = QLabel()
        self.error.setStyleSheet("color: red")
        self.layout.addWidget(self.error)
        self.layout.addWidget(self.btns)

        self.setLayout(self.layout)
        self.add.clicked.connect(self._add_clicked)
        self.cancel.clicked.connect(self.reject)
        self.apply.clicked.connect(self.get_annots)
        self.valid_annots_made.connect(self.accept)
        self.delete.clicked.connect(self._delete_clicked)
        self.list.annots_selected.connect(self._show_delete)

    def _show_delete(self, checked: bool):
        """
        Display the delete button

        Parameters
        ----------
        checked : bool
            True if delete is currently hidden.
        """
        if checked:
            self.delete.show()
        else:
            self.delete.hide()

    def _delete_clicked(self):
        """Delete checked items if there is at least one item checked"""
        if self.list.num_checked > 0:
            self.list.delete_checked()

    def _add_clicked(self):
        """Add a new item if there are less than 9. Hide add button otherwise"""
        self.list.add_new_item()
        if self.list.count() > 9:
            self.add.hide()

    def get_annots(self):
        """
        Set annotation dictionary to annotation data in list
        and emit valid_annots_made signal if all annotations are valid.

        """

        dct: Dict[str, Dict] = {}
        valid = True
        error = ""
        # grab all items from list of annotations
        items = [self.list.item(x) for x in range(self.list.count())]
        # if all items have been deleted annotations are invalid
        if len(items) < 1:
            valid = False
            error = " Must provide at least one annotation. "

        for i in items:
            item_valid, name, sub_dct, item_error = i.get_data()
            # sub_dct is annotation data (type,default, options)
            if name in dct.keys():
                valid = False
                i.highlight(i.name)
                error = error + " No duplicate names allowed. "
            dct[name] = sub_dct
            if not item_valid:
                valid = False
                error = error + " " + item_error
                break

        # if all values were valid emit signal and set new_annot_dict
        self.error.setText(error)
        if valid:
            self.new_annot_dict = dct
            self.valid_annots_made.emit()
        else:
            self.new_annot_dict = None
