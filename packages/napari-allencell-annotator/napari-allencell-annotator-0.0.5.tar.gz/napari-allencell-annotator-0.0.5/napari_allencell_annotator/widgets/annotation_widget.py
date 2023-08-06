from qtpy.QtWidgets import QListWidget, QAbstractItemView
from psygnal._signal import Signal

from napari_allencell_annotator.widgets.annotation_item import AnnotationItem


class AnnotationWidget(QListWidget):
    """
    A class used to create a QListWidget for annotations that are created.

    """

    # signal emitted when annotation check boxes are selected
    annots_selected = Signal(bool)

    def __init__(self):
        QListWidget.__init__(self)
        self.num_checked: int = 0
        # allow drag and drop rearrangement
        self.setDragDropMode(QAbstractItemView.InternalMove)

        # TODO: styling https://blog.actorsfit.com/a?ID=01450-929cf741-2d80-418c-8a55-a52395053369

    def clear_all(self):
        """Clear all image data."""
        self.num_checked = 0
        self.clear()

    def add_new_item(self):
        """
        Adds a new Annotation Item to the list. .

        Only allows 10 items to be added.
        """
        if self.count() < 10:
            item = AnnotationItem(self)
            item.check.stateChanged.connect(lambda: self._check_evt(item))
            h = item.sizeHint().height()
            self.setMaximumHeight(h * self.count())

    def remove_item(self, item: AnnotationItem):
        """
        Remove the item.

        Params
        -------
        item: AnnotationItem
            an item to remove.
        """
        h = item.sizeHint().height()
        self.takeItem(self.row(item))
        self.setMaximumHeight(h * self.count())

    def delete_checked(self):
        """
        Delete the checked items.

        This function emits a annots_selected signal.
        """
        lst = []
        for x in range(self.count()):
            if self.item(x).check.isChecked():
                lst.append(self.item(x))
        for item in lst:
            self.remove_item(item)
        self.num_checked = 0
        self.annots_selected.emit(False)

    def _check_evt(self, item: AnnotationItem):
        """
        Update checked count and emit files_selected signal.

        Params
        -------
        item: AnnotationItem
            the item that has been checked or unchecked.
        """
        if item.check.isChecked():
            self.num_checked = self.num_checked + 1
            if self.num_checked == 1:
                self.annots_selected.emit(True)
        elif not item.check.isChecked():
            self.num_checked = self.num_checked - 1
            if self.num_checked == 0:
                self.annots_selected.emit(False)
