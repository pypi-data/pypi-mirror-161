from qtpy.QtWidgets import QListWidget, QAbstractItemView
from typing import Set, List, Optional, Dict

from qtpy.QtCore import Signal

from napari_allencell_annotator.widgets.file_item import FileItem


class FilesWidget(QListWidget):
    """
    A class used to create a QListWidget for files.

    Attributes
    ----------
    shuffled : bool
        a boolean, True if list is currently shuffled
    checked : Set[FileItem]
        a set of items that are currently checked
    files_dict : Dict[str , List[str]]
        a dictionary of file path -> [File Name, FMS]
        stores file order in insertion order of keys

    Methods
    -------
    set_shuffled(shuffled : bool)
        Sets the list shuffled property.
    clear_all()
        Clears all image data.
    clear_for_shuff() -> List[str]
        Clears the list display and returns the file_order.
    get_curr_row() -> int
        Returns current image row.
    add_new_item(file:str)
        Adds a new file to the list and file_order.
    add_item(file: str, hidden: bool)
        Adds a file to the list, but not to the file_order.
    remove_item(item: ListItem)
        Removes the item from all attributes.
    delete_checked()
        Removes all items in checked.
    """

    files_selected = Signal(bool)
    files_added = Signal(bool)

    def __init__(self):
        QListWidget.__init__(self)
        self.checked: Set[FileItem] = set()
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        # files_dict holds all image info file path -> [file name, FMS]
        # also holds the original insertion order in .keys()
        self.files_dict: Dict[str, List[str]] = {}
        self.setCurrentItem(None)
        self._shuffled: bool = False

    @property
    def shuffled(self) -> bool:
        """
        Current shuffle state of the list.

        Returns
        -------
        bool
            the shuffled property.
        """
        return self._shuffled

    def set_shuffled(self, shuffled: bool):
        """
        Set the shuffled property to shuffled or unshuffled.

        Parameters
        ----------
        shuffled : bool
        """
        self._shuffled = shuffled

    def unhide_all(self):
        """Display the file names on all files in the list."""
        for i in range(self.count()):
            self.item(i).unhide()

    def get_curr_row(self) -> int:
        """
        Get the row of the currently selected image

        Returns
        -------
        int
            the current row.
        """
        if self.currentItem() is not None:
            return self.row(self.currentItem())
        else:
            return -1

    def clear_all(self):
        """Clear all image data."""
        self._shuffled = False
        self.checked = set()
        self.files_dict = {}

        self.setCurrentItem(None)
        self.clear()

    def clear_for_shuff(self) -> Dict[str, List[str]]:
        """
        Clear the list display and return the files_dict.

        This function clears all displayed, checked, and current items, but keeps the files_dict.

        Returns
        -------
         Dict[str, List[str]]
            file dictionary file path -> [filen name, fms].
        """
        self._shuffled = True
        self.setCurrentItem(None)
        self.checked = set()
        self.clear()
        return self.files_dict

    def add_new_item(self, file: str, hidden: Optional[bool] = False):
        """
        Adds a new file to the list and files_dict.

        This function emits a files_added signal when this is the first file added.

        Params
        -------
        file: str
            a file path.
        hidden : Optional[bool]
            a boolean if true file path hidden in list.
        """
        if file not in self.files_dict.keys():
            item = FileItem(file, self, hidden)
            item.check.stateChanged.connect(lambda: self._check_evt(item))
            self.files_dict[file] = [item.get_name(), ""]
            if len(self.files_dict) == 1:
                self.files_added.emit(True)

    def add_item(self, file: str, hidden: bool = False):
        """
        Add a file to the list, but not to the files_dict.

        Optional hidden parameter toggles file name visibility.

        Params
        -------
        file: str
            a file path.
        hidden: bool
            file name visibility.
        """
        item = FileItem(file, self, hidden)
        item.check.stateChanged.connect(lambda: self._check_evt(item))

    def remove_item(self, item: FileItem):
        """
        Remove the item from all attributes.

        This function emits a files_added signal when the item to remove is the only item.

        Params
        -------
        item: FileItem
            an item to remove.
        """
        if item.file_path in self.files_dict.keys():
            if item == self.currentItem():
                self.setCurrentItem(None)
            self.takeItem(self.row(item))
            del self.files_dict[item.file_path]
            if len(self.files_dict) == 0:
                self.files_added.emit(False)

    def delete_checked(self):
        """
        Delete the checked items.

        This function emits a files_selected signal.
        """
        for item in self.checked:
            self.remove_item(item)
        self.checked.clear()
        self.files_selected.emit(False)

    def _check_evt(self, item: FileItem):
        """
        Update checked set and emit files_selected signal.

        Params
        -------
        item: FileItem
            the item that has been checked or unchecked.
        """
        if item.check.isChecked() and item not in self.checked:
            self.checked.add(item)
            if len(self.checked) == 1:
                self.files_selected.emit(True)
        elif not item.check.isChecked() and item in self.checked:
            self.checked.remove(item)
            if len(self.checked) == 0:
                self.files_selected.emit(False)
