import csv
import itertools
from pathlib import Path

from qtpy.QtWidgets import QWidget, QVBoxLayout, QDialog

from napari_allencell_annotator.controller.images_controller import ImagesController

from napari_allencell_annotator.controller.annotator_controller import AnnotatorController
from napari_allencell_annotator.widgets.create_dialog import CreateDialog
import napari
from typing import List, Dict, Union


class MainController(QWidget):
    """
    A class used to combine/communicate between AnnotatorController and ViewController.

    Methods
    -------
    _start_annotating_clicked()
        Verifies that images are added and user wants to proceed, then opens a .csv file dialog.
    stop_annotating()
         Stops annotating in images and annotations views.
    _next_image_clicked()
        Moves to the next image for annotating.
    _prev_image_clicked()
        Moves to the previous image for annotating.
    """

    def __init__(self, napari_viewer: napari.Viewer):
        super().__init__()
        self.napari = napari_viewer
        self.layout = QVBoxLayout()
        self.images = ImagesController(self.napari)
        self.annots = AnnotatorController(self.napari)
        self.layout.addWidget(self.images.view, stretch=1)
        self.layout.addWidget(self.annots.view, stretch=2)
        self.setLayout(self.layout)
        self.show()

        self._connect_slots()
        self.csv_annotation_values: Dict[str, List] = None
        self.starting_row: int = -1
        self.has_new_shuffled_order = None

    def _connect_slots(self):
        """Connects annotator view buttons to slots"""
        self.annots.view.start_btn.clicked.connect(self._start_annotating_clicked)

        self.annots.view.next_btn.clicked.connect(self._next_image_clicked)
        self.annots.view.prev_btn.clicked.connect(self._prev_image_clicked)
        self.annots.view.csv_input.file_selected.connect(self._csv_write_selected_evt)
        self.annots.view.save_exit_btn.clicked.connect(self._save_and_exit_clicked)
        self.annots.view.import_btn.clicked.connect(self._import_annots_clicked)
        self.annots.view.annot_input.file_selected.connect(self._csv_json_import_selected_evt)
        self.annots.view.create_btn.clicked.connect(self._create_clicked)
        self.annots.view.save_json_btn.file_selected.connect(self._json_write_selected_evt)

    def _create_clicked(self):
        """Create dialog window for annotation creation and start viewing on accept event."""
        dlg = CreateDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.csv_annotation_values = None
            self.annots.set_annot_json_data(dlg.new_annot_dict)
            self.annots.start_viewing()

    def _json_write_selected_evt(self, file_list: List[str]):
        """
        Set json file name and write the annotations to the file.

        Ensure that all file names have .json extension and that a
        file name is selected. Disable save json button.

        Parameters
        ----------
        file_list : List[str]
            The list containing one file name.
        """

        if file_list is None or len(file_list) < 1:
            self.images.view.alert("No selection provided")
        else:
            file_path = file_list[0]
            extension = Path(file_path).suffix
            if extension != ".json":
                file_path = file_path + ".json"
            self.annots.view.save_json_btn.setEnabled(False)
            self.annots.write_json(file_path)

    def _csv_json_import_selected_evt(self, file_list: List[str]):
        """
        Read annotations from csv or json file. Read/Save csv images and annotation data if user chooses to.

        Parameters
        ----------
        file_list : List[str]
            The list containing one file name.
        """
        # todo bad file: json or csv --> send back to add
        self.csv_annotation_values = None
        self.has_new_shuffled_order = None
        if file_list is None or len(file_list) < 1:
            self.images.view.alert("No selection provided")
        else:
            file_path = file_list[0]
            if Path(file_path).suffix == ".json":
                self.annots.read_json(file_path)

            elif Path(file_path).suffix == ".csv":
                proceed: bool = self.annots.view.popup(
                    "Would you like to use the images from this csv in addition to the annotation list?\n "
                    "Any annotation values in the file written for these images will be used."
                    "\n Note: any currently listed images will be cleared."
                )
                file = open(file_path)

                reader = csv.reader(file)
                shuffled = next(reader)[1]
                shuffled = self.str_to_bool(shuffled)
                # annotation data header
                annts = next(reader)[1]
                # set the json dictionary of annotations
                self.annots.get_annotations_csv(annts)
                # skip actual header
                next(reader)
                self.starting_row = None
                if proceed:
                    self.has_new_shuffled_order = False

                    # get image/annotation data
                    # dictionary File Path -> [file name, fms, annt1, annt2...]
                    self.csv_annotation_values = {}

                    row_num: int = 0
                    for row in reader:
                        # for each line, add data to already annotated and check if there are null values
                        # if null, starting row for annotations is set
                        self.csv_annotation_values[row[0]] = row[1::]
                        if self.starting_row is None:
                            # if there is a none value for an annotation
                            if self.starting_row is None:
                                if self.has_none_annotation(row[3::]):
                                    self.starting_row = row_num
                            row_num = row_num + 1
                    if row_num == len(self.csv_annotation_values):
                        # all images have all annotations filled in, start annotating at last image
                        self.starting_row = row_num - 1
                    self.images.load_from_csv(self.csv_annotation_values.keys(), shuffled)
                    # keep track of if images are shuffled from now on:
                    self.images.view.shuffle.toggled.connect(self._shuffle_toggled)
                # start at row 0 if annotation data was not used from csv
                if self.starting_row is None:
                    self.starting_row = 0
                file.close()

            # move to view mode
            self.annots.start_viewing()

    def _shuffle_toggled(self, checked: bool):
        """
        Set has_new_shuffled_order to True if images are shuffled.

        Slot function used to record if csv imported image lists
        are given a new shuffle order before annotating. Slot disconnected once
        images have been shuffled once.

        Parameters
        ----------
        checked : bool
            True if shuffle button is pressed "Shuffle and Hide" mode. False if pressed in "Unhide" mode.
        """
        if checked:
            # images have been shuffled, have to adjust order
            self.has_new_shuffled_order = True
            self.images.view.shuffle.toggled.disconnect(self._shuffle_toggled)

    def str_to_bool(self, string) -> bool:
        """
        Convert a string to a bool.

        Parameters
        ----------
        string_ : str

        Returns
        -------
        boolean : bool
        """
        if string.lower() == "true":
            return True
        elif string.lower() == "false":
            return False
        else:
            raise ValueError("The value '{}' cannot be mapped to boolean.".format(string))

    def _import_annots_clicked(self):
        """Open file widget for importing csv/json."""
        self.annots.view.annot_input.simulate_click()

    def _csv_write_selected_evt(self, file_list: List[str]):
        """
        Set csv file name for writing annotations and call _setup_annotating.

        Ensure that all file names have .csv extension and that a
        file name is selected.

        Parameters
        ----------
        file_list : List[str]
            The list containing one file name.
        """
        if file_list is None or len(file_list) < 1:
            self.images.view.alert("No selection provided")
        else:
            file_path = file_list[0]
            extension = Path(file_path).suffix
            if extension != ".csv":
                file_path = file_path + ".csv"
            self.annots.set_csv_path(file_path)
            self._setup_annotating()

    def _start_annotating_clicked(self):
        """
        Verify that images are added and user wants to proceed, then
        open a .csv file dialog.

        Alert user if there are no files added.
        """
        if self.images.get_num_files() is None or self.images.get_num_files() < 1:
            self.images.view.alert("Can't Annotate Without Adding Images")
        else:
            proceed: bool = self.annots.view.popup(
                "Once annotating starts both the image set and annotations cannot be "
                "edited.\n Would "
                "you like to continue?"
            )
            if proceed:
                self.annots.view.csv_input.simulate_click()

    def _stop_annotating(self):
        """
        Stop annotating in images and annotations views.

        Display images and annots views.
        """
        if self.has_new_shuffled_order is not None and not self.has_new_shuffled_order:
            self.images.view.shuffle.toggled.disconnect(self._shuffle_toggled)
            self.has_new_shuffled_order = None
        if not self.images.view.file_widget.shuffled:
            self.images.view.file_widget.currentItemChanged.disconnect(self._image_selected)
        self.layout.addWidget(self.images.view, stretch=1)
        self.layout.addWidget(self.annots.view, stretch=2)
        self.images.view.show()
        self.annots.stop_annotating()
        self.images.stop_annotating()
        self.images.view.input_file.show()
        self.images.view.input_dir.show()
        self.images.view.shuffle.show()
        self.images.view.delete.show()

    def _setup_annotating(self):
        """
        Remove images view if shuffled/hidden annotating and start annotation.

        Pass in annotation values if there are any.
        """
        dct, shuffled = self.images.get_files_dict()
        # dct is a dictionary file path -> [filename, fms]
        if shuffled:
            # remove file list if blind annotation
            self.layout.removeWidget(self.images.view)
            self.images.view.hide()

        if self.csv_annotation_values is not None and len(self.csv_annotation_values) > 0:
            # if we are using csv annotation data
            # make sure csv_annotation_values reflects any changes made in view mode (add, delete, shuffle)
            self._fix_csv_annotations(dct)

            self.images.start_annotating(self.starting_row)

            self.annots.start_annotating(self.images.get_num_files(), self.csv_annotation_values, shuffled)

        else:
            # start annotating from beginning with just file info
            self.images.start_annotating()
            self.annots.start_annotating(self.images.get_num_files(), dct, shuffled)
        self.annots.set_curr_img(self.images.curr_img_dict())
        if not shuffled:
            # alter images view to fit annotation mode
            self.images.view.file_widget.currentItemChanged.connect(self._image_selected)
            self.images.view.input_dir.hide()
            self.images.view.input_file.hide()
            self.images.view.shuffle.hide()
            self.images.view.delete.hide()

    def _fix_csv_annotations(self, dct: Dict[str, List[str]]):
        """
        Change csv_annotation_values to reflect any edits to the image list.

        Image list could have been shuffled or had items added/deleted.

        Parameters
        ----------
        dct : Dict[str, List[str]]
            the image list dictionary file path -> [file name, fms]
        """
        dct_keys = dct.keys()
        alr_anntd_keys = self.csv_annotation_values.keys()
        # dct_keys is the dictionary from the images list. may have been edited
        # alr_anntd_keys was read in from csv. has not been edited
        if not dct_keys == alr_anntd_keys:
            # if dct .keys is not equal (order not considered) to aa.keys
            # means files were either added/deleted
            if self.has_new_shuffled_order:
                # if dct .keys is not equal (minus order ) to aa.keys. and SHUFFLED
                self._unequal_shuffled_fix_csv_annotations(dct)

            else:
                self._unequal_unshuffled_fix_csv_annotations(dct)
        else:
            # dct keys and aakeys are equal (except for order)
            if self.has_new_shuffled_order:
                self._equal_shuffled_fix_csv_annotations(dct)
            # if dct.keys == aakeys and NOT SHUFFLED then no changes

    def _unequal_unshuffled_fix_csv_annotations(self, dct: Dict[str, List[str]]):
        """
        Change csv_annotation_values to reflect any edits insertions/deletions to the image list.

        Find a new starting row if old starting row image was deleted or if new un-annotated images
        are the first un-annotated images.

        Parameters
        ----------
        dct : Dict[str, List[str]]
            the image list dictionary file path -> [file name, fms]
        """
        dct_keys = dct.keys()
        alr_anntd_keys = self.csv_annotation_values.keys()
        new_starting_row_found: bool = False
        new_csv_annotations = {}
        # order has not been changed/shuffled since upload
        # need to add/delete files from already annotated and get a new starting row in case the
        # file deleted or added is now the first file with a null annotation
        for old_file, row in zip(alr_anntd_keys, range(len(alr_anntd_keys))):
            if old_file in dct_keys:
                # old file wasn't removed from files
                new_csv_annotations[old_file] = self.csv_annotation_values[old_file]
                if not new_starting_row_found:
                    if row >= self.starting_row:
                        # every file at index before the original starting row was fully annotated
                        # if we are past that point in csv_annotation_values then we need to test if we
                        # have found a new none annotation value
                        if self.has_none_annotation(self.csv_annotation_values[old_file][2::]):
                            self.starting_row = len(new_csv_annotations) - 1
                            new_starting_row_found = True

            # if old_file not in dct_keys dont add it
        if len(new_csv_annotations) < len(dct):
            # items were added into dct that were not in already annotated
            if not new_starting_row_found:
                # start on first new item from dct which has not been annotated
                self.starting_row = len(new_csv_annotations)
                new_starting_row_found = True
            for file in list(dct_keys)[len(new_csv_annotations) : :]:
                new_csv_annotations[file] = dct[file]

        if not new_starting_row_found:
            self.starting_row = len(new_csv_annotations) - 1
        self.csv_annotation_values = new_csv_annotations

    def _unequal_shuffled_fix_csv_annotations(self, dct: Dict[str, List[str]]):
        """
        Change csv_annotation_values to reflect any edits insertions/deletions to the image list and shuffling.

        Find a new starting row if old starting row image was deleted or if new un-annotated images
        are the first un-annotated images.

        Reorder the csv_annotation_values keys so that the GUI will read/write
        the csv image list in this new shuffled order. This will help with saving progress
        when blindly annotating a large image set.

        Parameters
        ----------
        dct : Dict[str, List[str]]
            the image list dictionary file path -> [file name, fms]
        """
        # it has been either shuffled and is now blind or it was given a new shuffle order
        # want to save this order in case csv has unshuffled image order, annotation is supposed to be blind
        # and next time the csv is opened it will be in insertion order still
        dct_keys = dct.keys()
        alr_anntd_keys = self.csv_annotation_values.keys()
        new_starting_row_found: bool = False
        new_csv_annotations = {}
        for new_file, dct_index in zip(dct_keys, range(len(dct_keys))):

            if new_file not in alr_anntd_keys:
                # only possible to encounter a new file in middle when shuffling has happened
                # file added to dct
                new_csv_annotations[new_file] = dct[new_file]

                if not new_starting_row_found:
                    # just added a new, unannotated file
                    self.starting_row = dct_index
                    new_starting_row_found = True

            elif new_file in alr_anntd_keys:
                new_csv_annotations[new_file] = self.csv_annotation_values[new_file]
                if not new_starting_row_found:
                    # todo: could try an optimize this by storing csv_annotation_values indexes
                    if self.has_none_annotation(self.csv_annotation_values[new_file][2::]):
                        self.starting_row = dct_index
                        new_starting_row_found = True
        if not new_starting_row_found:
            self.starting_row = len(new_csv_annotations) - 1
        self.csv_annotation_values = new_csv_annotations

    def _equal_shuffled_fix_csv_annotations(self, dct: Dict[str, List[str]]):
        """
        Change csv_annotation_values to reflect shuffling.

        Parameters
        ----------
        dct : Dict[str, List[str]]
            the image list dictionary file path -> [file name, fms]
        """
        dct_keys = dct.keys()
        new_starting_row_found: bool = False
        new_csv_annotations = {}
        for new_file, dct_index in itertools.zip_longest(dct_keys, range(len(dct_keys))):
            new_csv_annotations[new_file] = self.csv_annotation_values[new_file]
            if not new_starting_row_found:
                if self.has_none_annotation(self.csv_annotation_values[new_file][2::]):
                    self.starting_row = dct_index
                    new_starting_row_found = True
        if not new_starting_row_found:
            self.starting_row = len(new_csv_annotations) - 1
        self.csv_annotation_values = new_csv_annotations

    def _next_image_clicked(self):
        """
        Move to the next image for annotating.

        If the last image is being annotated, write to csv. If the second
        image is being annotated, enable previous button.
        """
        self.annots.record_annotations(self.images.curr_img_dict()["File Path"])

        self.images.next_img()
        self.annots.set_curr_img(self.images.curr_img_dict())

    def _image_selected(self, current, previous):
        """
        Record the annotations for the previously selected image and set current image.

        Called only when annotating un-blind and users select an image from the list.
        """
        if previous:
            self.annots.record_annotations(previous.file_path)
        self.annots.set_curr_img(self.images.curr_img_dict())

    def _prev_image_clicked(self):
        """
        Move to the previous image for annotating.

        If the first image is being annotated, disable button.
        """
        self.annots.record_annotations(self.images.curr_img_dict()["File Path"])
        self.images.prev_img()
        self.annots.set_curr_img(self.images.curr_img_dict())

    def _save_and_exit_clicked(self):
        """Stop annotation if user confirms choice in popup."""
        proceed: bool = self.annots.view.popup("Close this session?")

        if proceed:
            self._stop_annotating()

    def has_none_annotation(self, lst: List[Union[str, int, bool]]) -> bool:
        """
        Test if the given list has any empty string or None values.
        Returns
        -------
        bool
            True if null values are in the list.
        """

        if len(lst) < len(self.annots.annot_json_data.keys()):
            return True
        else:
            for item in lst:
                if item is None or item == "":
                    return True
        return False
