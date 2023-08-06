from typing import Tuple, Dict
from qtpy import QtWidgets
from qtpy.QtWidgets import (
    QListWidgetItem,
    QListWidget,
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QLabel,
    QSpinBox,
    QGridLayout,
    QCheckBox,
)


class AnnotationItem(QListWidgetItem):
    """
    A class used to create custom annotation QListWidgetItems.
    """

    def __init__(self, parent: QListWidget):
        QListWidgetItem.__init__(self, parent)
        self.widget = QWidget()
        self.layout = QGridLayout()
        name_label = QLabel("Name:")
        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter name")

        type_label = QLabel("Type:")
        self.type = QComboBox()
        self.type.addItems(["text", "number", "checkbox", "dropdown"])
        self.name.setWhatsThis("name")
        self.type.setWhatsThis("type")
        self.name_widget = QWidget()
        name_layout = QHBoxLayout()
        self.check = QCheckBox()
        name_layout.addWidget(self.check)
        name_layout.addWidget(name_label)
        self.name_widget.setLayout(name_layout)
        self.layout.addWidget(self.name_widget, 0, 0, 1, 1)
        self.layout.addWidget(self.name, 0, 1, 1, 2)
        self.layout.addWidget(type_label, 0, 3, 1, 1)
        self.layout.addWidget(self.type, 0, 4, 1, 2)
        default_label = QLabel("Default:")
        self.default_text = QLineEdit()
        self.default_text.setPlaceholderText("Optional: Default Text")
        self.default_num = QSpinBox()
        self.default_num.setValue(2)
        self.default_check = QComboBox()
        self.default_check.addItems(["checked", "unchecked"])
        self.default_options_label = QLabel("Options:")
        self.default_options = QLineEdit()
        self.default_options.setPlaceholderText("Enter a comma separated list of options")

        self.default_options.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Preferred)
        self.default_options.setMinimumWidth(300)

        sp_retain = QtWidgets.QSizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.default_options.setSizePolicy(sp_retain)
        self.default_options_label.setSizePolicy(sp_retain)

        self.layout.addWidget(default_label, 0, 6, 1, 1)
        self.layout.addWidget(self.default_text, 0, 7, 1, 2)
        self.layout.addWidget(self.default_options_label, 1, 1, 1, 1)
        self.layout.addWidget(self.default_options, 1, 2, 1, 7)
        self.default_options.hide()
        self.default_options_label.hide()

        self.layout.setContentsMargins(5, 5, 5, 15)

        self.widget.setLayout(self.layout)
        self.setSizeHint(self.widget.sizeHint())
        if parent is not None:
            parent.setItemWidget(self, self.widget)

        self.type.currentTextChanged.connect(self._type_changed)

    def _type_changed(self, text: str):
        """
        Render the widgets which correspond to the new type

        Parameters
        ----------
        text : str
            the new type selected.
        """
        default_widget = self.layout.itemAtPosition(0, 7).widget()
        default_widget.setParent(None)
        self.layout.removeWidget(default_widget)

        if text == "text":
            self.default_options.hide()
            self.default_options_label.hide()
            self.layout.addWidget(self.default_text, 0, 7, 1, 2)

        elif text == "number":
            self.default_options.hide()
            self.default_options_label.hide()
            self.layout.addWidget(self.default_num, 0, 7, 1, 2)

        elif text == "checkbox":
            self.default_options.hide()
            self.default_options_label.hide()
            self.layout.addWidget(self.default_check, 0, 7, 1, 2)
        else:
            self.default_options.show()
            self.default_options_label.show()
            self.layout.addWidget(self.default_text, 0, 7, 1, 2)

    def get_data(self) -> Tuple[bool, str, Dict, str]:
        """
        Highlight any invalid entries and return the data.

        Return True if all data is valid along with str name and a dictionary
        of annotation data.
        Return False if data is invalid, highlight the incorrect entries, and return
        an incomplete dictionary.

        Returns
        ------
        Tuple[bool, str, Dict]
            bool : True if entries are valid.
            str: name of annotation item
            Dict: annotation item data (type, default, options)
            str: error msg if applicable
        """
        # bool valid if all annotation values are in the correct format
        error = ""
        valid: bool = True
        # test if annotation name is valid
        name: str = self.name.text()
        self._unhighlight(self.name)
        if name is None or name.isspace() or len(name) == 0:
            valid = False
            self.highlight(self.name)
            error = " Invalid Name. "

        type: str = self.type.currentText()
        # dictionary of annotation type, default, options
        dct: Dict = {}

        if type == "text" or type == "dropdown":
            # grab default text entry
            default = self.default_text.text()
            if default is None or len(default) == 0 or default.isspace():
                dct["default"] = ""
            else:
                default = default.strip()
                # default text exists
                dct["default"] = default
            if type == "text":
                dct["type"] = "string"
            else:
                # type is options
                # comma separate list of options
                txt2 = self.default_options.text()
                # unhighlight by default
                self._unhighlight(self.default_options)
                # if there is less than two options provided
                if txt2 is None or len(txt2.split(",")) < 2:
                    valid = False
                    self.highlight(self.default_options)
                    error = error + " Must provide two dropdown options. "
                else:
                    txt2 = [word.strip() for word in txt2.split(",")]
                    contained: bool = False
                    if dct["default"] == "":
                        contained = True
                    for item in txt2:
                        # check each item in options
                        if len(item) == 0:
                            valid = False
                            self.highlight(self.default_options)
                            error = error + " Invalid options for dropdown. "
                            break
                        else:
                            if not contained and item == dct["default"]:
                                contained = True
                    if not contained:
                        txt2.append(default)
                    dct["options"] = txt2
                    dct["type"] = "list"
        elif type == "number":
            # number defaults are required by spinbox, always valid
            dct["type"] = "number"
            dct["default"] = self.default_num.value()
        else:
            # checkbox type default required by the drop down, always valid
            dct["type"] = "bool"
            if self.default_check.currentText() == "checked":
                dct["default"] = True
            else:
                dct["default"] = False
        return valid, name, dct, error

    def highlight(self, objct: QWidget):
        objct.setStyleSheet("""QLineEdit{border: 1px solid red}""")

    def _unhighlight(self, objct: QWidget):
        objct.setStyleSheet("""QLineEdit{}""")
