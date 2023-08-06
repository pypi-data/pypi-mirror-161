from enum import Enum
from typing import Dict, List, Optional, Any, Union

from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QListWidget,
    QScrollArea,
    QListWidgetItem,
    QPushButton,
    QAbstractScrollArea,
    QMessageBox,
    QVBoxLayout,
    QSizePolicy,
)
from napari import Viewer
from napari_allencell_annotator.widgets.file_input import (
    FileInput,
    FileInputMode,
)


class AnnotatorViewMode(Enum):
    """
    Mode for view.

    ADD is used when there is not an annotation set selected
    VIEW is used when an annotation set has been made/selected, but annotating has not started.
    ANNOTATE is used when the image set is finalized and annotating has started.
    """

    ADD = "add"
    VIEW = "view"
    ANNOTATE = "annotate"


class AnnotatorView(QWidget):
    """
    A class used to create a view for annotations.

    Inputs
    ----------
    viewer : napari.Viewer
        a napari viewer where the plugin will be used
    mode : AnnotatorViewMode
        a mode for the view

    Methods
    -------
    mode() -> AnnotatorViewMode

    set_mode(mode: AnnotatorViewMode)

    set_num_images(num: int)
        Sets the total images to be annotated.

    set_curr_index(num: int)
        Sets the index of the currently selected image.

    reset_annotations()
        Resets annotation data to empty.

    render_default_values()
        Sets annotation widget values to default.

    render_values(vals: List):
        Sets the values of the annotation widgets to vals.

    get_curr_annots() -> List
        Returns the current annotation values in a list form.

    toggle_annots_editable()
        Enables the annotations for editing.

    render_annotations(data : Dict[str,Dict]))
        Renders GUI elements from the dictionary of annotations.

    popup(text:str) -> bool
        Pop up dialog that asks the user a question. Returns True if 'Yes' False if 'No'.
    """

    def __init__(
        self,
        viewer: Viewer,
        mode: AnnotatorViewMode = AnnotatorViewMode.ADD,
    ):
        super().__init__()
        self._mode = mode
        label = QLabel("Annotations")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 15))
        self.layout = QVBoxLayout()
        self.layout.addWidget(label)

        self.annot_list = QListWidget()
        self.annot_list.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.annot_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.annot_list)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.scroll.setStyleSheet(
            """QScrollBar:vertical {
            width:10px;    
            margin: 0px 0px 0px 0px;
        }"""
        )
        style = """QScrollBar::handle:vertical {border: 0px solid red; border-radius: 
        2px;} """
        self.scroll.setStyleSheet(self.scroll.styleSheet() + style)
        self.layout.addWidget(self.scroll)

        self.num_images: int = None
        self.curr_index: int = None

        # Add widget visible in ADD mode
        self.add_widget = QWidget()
        add_layout = QHBoxLayout()
        self.create_btn = QPushButton("Create New Annotation Template")
        self.create_btn.setEnabled(True)
        self.import_btn = QPushButton("Import Existing Annotation Template (.csv or .json)")
        self.import_btn.setEnabled(True)
        self.annot_input = FileInput(mode=FileInputMode.JSONCSV, placeholder_text="Start Annotating")
        self.annot_input.toggle(False)

        add_layout.addWidget(self.create_btn, stretch=2)
        add_layout.addWidget(self.import_btn, stretch=2)
        self.add_widget.setLayout(add_layout)
        self.layout.addWidget(self.add_widget)

        # view widget visible in VIEW mode
        self.view_widget = QWidget()
        view_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.start_btn = QPushButton("Start Annotating")
        self.csv_input = FileInput(mode=FileInputMode.CSV)
        self.csv_input.toggle(False)
        self.save_json_btn = FileInput(mode=FileInputMode.JSON, placeholder_text="Save to JSON")
        self.save_json_btn.toggle(True)
        self.start_btn.setEnabled(True)

        view_layout.addWidget(self.cancel_btn, stretch=1)
        view_layout.addWidget(self.save_json_btn, stretch=1)
        view_layout.addWidget(self.start_btn, stretch=1)
        self.view_widget.setLayout(view_layout)

        # annot widget visible in ANNOTATE mode
        self.annot_widget = QWidget()
        annot_layout = QGridLayout()
        self.save_exit_btn = QPushButton("Save + Exit")

        self.prev_btn = QPushButton("< Previous")
        self.next_btn = QPushButton("Next >")
        self.next_btn.setEnabled(True)
        self.progress_bar = QLabel()
        annot_layout.addWidget(self.progress_bar, 0, 1, 1, 2)
        annot_layout.addWidget(self.save_exit_btn, 1, 0, 1, 2)
        annot_layout.addWidget(self.prev_btn, 1, 2, 1, 1)
        annot_layout.addWidget(self.next_btn, 1, 3, 1, 1)
        self.annot_widget.setLayout(annot_layout)

        self._display_mode()
        self.annotation_item_widgets: List[QWidget] = []
        self.annots_order: List[str] = []
        self.default_vals: List[str] = []
        self.setLayout(self.layout)
        self.viewer: Viewer = viewer

    @property
    def mode(self) -> AnnotatorViewMode:
        return self._mode

    def set_mode(self, mode: AnnotatorViewMode):
        """
        Set current mode.

        Parameters
        ----------
        mode: AnnotatorViewMode
        """
        self._mode = mode
        self._display_mode()

    def set_num_images(self, num: Optional[int] = None):
        """
        Set the total number of images to be annotated

        Parameters
        ----------
        num : Optional[int]
            number of images, set to None if not provided.
        """
        self.num_images = num

    def set_curr_index(self, num: Optional[int] = None):
        """
        Set the index of the currently selected image and display it on progress bar.

        Parameters
        ----------
        num : Optional[int]
            row of the current image.
        """
        if num is not None:
            self.curr_index = num
            self.progress_bar.setText("{} of {} Images".format(self.curr_index + 1, self.num_images))

    def _reset_annotations(self):
        """Reset annotation data to empty."""
        self.annot_list.clear()
        # todo: make size policy, remove this line
        self.annot_list.setMaximumHeight(600)
        self.annotation_item_widgets: List[QWidget] = []
        self.annots_order: List[str] = []
        self.default_vals: List[str] = []

    def render_default_values(self):
        """Set annotation widget values to default."""
        # for curr index if annots exist fill else fill with default
        self.render_values(self.default_vals)

    def render_values(self, vals: List[str]):
        """
        Set the values of the annotation widgets.

        Parameters
        ----------
        vals:List[str]
            the values for the annotations.
        """
        for (widget, val, default) in zip(self.annotation_item_widgets, vals, self.default_vals):
            if val is None or val == "":
                val = default
            if isinstance(widget, QLineEdit):
                widget.setText(val)
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(val))
            elif isinstance(widget, QCheckBox):
                if isinstance(val, str):
                    # val is a str from previous annotation
                    widget.setChecked(eval(val))
                else:
                    # val is bool from default vals
                    widget.setChecked(val)
            elif isinstance(widget, QComboBox):
                widget.setCurrentText(val)

    def get_curr_annots(self) -> List[Union[str, bool, int]]:
        """
        Return the current annotation values in a list.

        Returns
        ----------
        List
            a list of annotation values.
        """
        annots = []
        for i in self.annotation_item_widgets:
            value = ""
            if isinstance(i, QLineEdit):
                value = i.text()
            elif isinstance(i, QSpinBox):
                value = i.value()
            elif isinstance(i, QCheckBox):
                value = i.isChecked()
            elif isinstance(i, QComboBox):
                value = i.currentText()
            annots.append(value)
        return annots

    def toggle_annots_editable(self, editable: bool):
        """Enable the annotation widgets for editing."""
        for i in self.annotation_item_widgets:
            i.setEnabled(editable)

    def _display_mode(self):
        """Render GUI buttons visible depending on the mode."""
        item = self.layout.itemAt(self.layout.count() - 1)
        item.widget().hide()
        self.layout.removeItem(item)
        if self._mode == AnnotatorViewMode.ADD:
            self.add_widget.show()
            self._reset_annotations()
            self.layout.addWidget(self.add_widget)
        elif self._mode == AnnotatorViewMode.VIEW:
            self.save_json_btn.setEnabled(True)
            self.view_widget.show()
            self.layout.addWidget(self.view_widget)
        elif self._mode == AnnotatorViewMode.ANNOTATE:
            self.annot_widget.show()
            self.layout.addWidget(self.annot_widget)
            self.prev_btn.setEnabled(False)

    def render_annotations(self, data: Dict[str, Dict[str, Any]]):
        """
        Read annotation dictionary into individual annotations.

        Parameters
        ----------
        data : Dict[str, Dict[str, Any]]
            The dictionary of annotation names -> a dictionary of types, defaults, and options.
        """
        self.annotation_item_widgets = []

        for name in data.keys():
            self._create_annot(name, data[name])
            # todo fix: doesnt work if certain widgets are first leaves blank spot on bottom
        self.annot_list.setMaximumHeight(self.annot_list.item(0).sizeHint().height() * len(data))

    def _create_annot(self, name: str, dictn: Dict[str, Any]):
        """
        Create annotation widgets from dictionary entries.

        Parameters
        ----------
        name : str
            annotation name.
        dictn : Dict[str, Any]
            annotation type, default, and options.
        """
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel(name)
        self.annots_order.append(name)

        layout.addWidget(label)
        annot_type: str = dictn["type"]
        if annot_type == "string":
            item = QLineEdit(dictn["default"])
        elif annot_type == "number":
            item = QSpinBox()
            item.setValue(dictn["default"])
        elif annot_type == "bool":
            item = QCheckBox()
            if dictn["default"]:
                item.setChecked(True)
        elif annot_type == "list":
            item = QComboBox()
            for opt in dictn["options"]:
                item.addItem(opt)
            item.setCurrentText(dictn["default"])
        layout.addWidget(item)
        self.default_vals.append(dictn["default"])
        self.annotation_item_widgets.append(item)
        item.setEnabled(True)
        layout.setContentsMargins(2, 12, 8, 12)
        layout.setSpacing(2)
        widget.setLayout(layout)
        list_item = QListWidgetItem(self.annot_list)
        list_item.setSizeHint(widget.minimumSizeHint())
        self.annot_list.setItemWidget(list_item, widget)

    def popup(self, text: str) -> bool:
        """
        Pop up dialog to ask the user yes or no.

        Parameters
        ----------
        text : str
            question for the message box.

        Returns
        ----------
        bool
            user input, true if 'Yes' false if 'No'

        """
        msg_box = QMessageBox()
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        return_value = msg_box.exec()
        if return_value == QMessageBox.Yes:
            return True
        else:
            return False
