import json

from napari_allencell_annotator.view.annotator_view import (
    AnnotatorView,
    AnnotatorViewMode,
)
import napari

from typing import Dict, List, Optional, Any
import csv


class AnnotatorController:
    """
    A class used to control the model and view for annotations.

    Inputs
    ----------
    viewer : napari.Viewer
        a napari viewer where the plugin will be used

    Methods
    -------
    set_annot_json_data(dct : dct: Dict[str, Dict[str, Any]])
        Sets annotation data dictionary.

    set_csv_path(path : str)
        Sets csv file name for writing.

    start_viewing()
        Changes view to VIEW mode and render annotations.

    stop_viewing()
        Changes view to ADD mode, resets annotations, and clears annotation json data.

    start_annotating(num_images: int, dct: Dict[str, List[str]])
        Changes annotation view to annotating mode.

    stop_annotating()
        Resets values from annotating and changes mode to VIEW.

    set_curr_img(curr_img_dict : Dict[str, str])
        Sets the current image and adds the image to annotations_dict.

    record_annotations(prev_img: str)
        Adds the outgoing image's annotation values to the files_and_annots.

    read_json(file_path : str)
        Reads a json file into a dictionary and sets annot_json_data.

    read_csv(file_path : str)
        Reads the first line of a csv file into a dictionary and sets annot_json_data.

    write_to_csv()
        Writes header and annotations to the csv file.
    """

    def __init__(self, viewer: napari.Viewer):

        # dictionary of json info:
        self.annot_json_data: Dict[str, Dict[str, Any]] = None
        # open in view mode
        self.view: AnnotatorView = AnnotatorView(viewer)

        self.view.show()
        # {'File Path' : path, 'Row' : str(row)}
        self.curr_img_dict: Dict[str, str] = None
        self.csv_path: str = None
        # annotation dictionary maps file paths -> [file name, FMS, annot1val, annot2val, ...]
        self.files_and_annots: Dict[str, List[str]] = {}

        self.view.cancel_btn.clicked.connect(self.stop_viewing)

        self.shuffled: bool = None

    def set_annot_json_data(self, dct: Dict[str, Dict[str, Any]]):
        """
        Set annotation data dictionary.

        Parameters
        ------
        dct : Dict[str, Dict]
            a dictionary of annotation data. name -> {type -> str,  options -> List[str], default -> bool, int, or str}
        """
        self.annot_json_data = dct

    def set_csv_path(self, path: Optional[str] = None):
        """
        Set csv file path for writing.

        Parameters
        ----------
        path: Optional[str] = None
            file path of csv. set to none if not provided.
        """
        self.csv_path = path

    def write_json(self, file_path: str):
        """
        Write annotation dictionary to a file.

        file_path : str
            file path for json file to write to.
        """
        if self.annot_json_data is not None:
            json.dump(self.annot_json_data, open(file_path, "w"), indent=4)

    def start_viewing(self):
        """Change view to VIEW mode and render annotations."""
        self.view.set_mode(mode=AnnotatorViewMode.VIEW)
        self.view.render_annotations(self.annot_json_data)

    def stop_viewing(self):
        """Change view to ADD mode, reset annotations, and clear annotation json data."""
        self.view.set_mode(mode=AnnotatorViewMode.ADD)
        self.annot_json_data = None

    def start_annotating(self, num_images: int, dct: Dict[str, List[str]], shuffled: bool):
        """
        Change annotation view to annotating mode and create files_and_annots with files.

        Parameters
        ----------
        num_images : int
            The total number of images to be annotated.
        dct : Dict[str, List[str]]
            The files to be used. path -> [name, FMS]
        """
        self.files_and_annots = dct
        self.view.set_num_images(num_images)
        self.view.set_mode(mode=AnnotatorViewMode.ANNOTATE)
        self.shuffled = shuffled

    def stop_annotating(self):
        """Reset values from annotating and change mode to ADD."""
        self.record_annotations(self.curr_img_dict["File Path"])
        self.write_csv()
        self.view.set_curr_index()
        self.files_and_annots = {}
        self.view.set_num_images()
        self.view.set_mode(mode=AnnotatorViewMode.ADD)
        self.view.render_default_values()
        self.set_curr_img()
        self.set_csv_path()

    def set_curr_img(self, curr_img: Optional[Dict[str, str]] = None):
        """
        Set the current image and add the image to annotations_dict.

        Changes next button if annotating the last image.

        Parameters
        ----------
        curr_img : Dict[str, str]
            The current image {'File Path' : 'path', 'Row' : str(rownum)}
        """
        self.curr_img_dict = curr_img
        if curr_img is not None:
            path: str = curr_img["File Path"]
            # files_and_annots values are lists File Path ->[File Name, FMS, annot1val, annot2val ...]
            # if the file has not been annotated the list is just length 2 [File Name, FMS]
            if len(self.files_and_annots[path]) < 3:
                # if the image is un-annotated render the default values

                self.view.render_default_values()
            else:
                # if the image has been annotated render the values that were entered
                # dictionary list [2::] is [annot1val, annot2val, ...]
                self.view.render_values(self.files_and_annots[path][2::])
            # convert row to int
            self.view.set_curr_index(int(curr_img["Row"]))
            # if at the end disable next
            if int(curr_img["Row"]) == self.view.num_images - 1:
                self.view.next_btn.setEnabled(False)
            else:
                self.view.next_btn.setEnabled(True)
            if int(curr_img["Row"]) == 0:
                self.view.prev_btn.setEnabled(False)
            else:
                self.view.prev_btn.setEnabled(True)

    def record_annotations(self, prev_img: str):
        """
        Add the outgoing image's annotation values to the files_and_annots.

        Parameters
        ----------
        prev_img : str
            The previous image file path.
        """
        lst: List = self.view.get_curr_annots()
        self.files_and_annots[prev_img] = self.files_and_annots[prev_img][:2:] + lst

    def read_json(self, file_path: str):
        """
        Read a json file into a dictionary and set annot_json_data.

        Parameters
        ----------
        file_path : str
            file path to json file to read from
        """
        # todo file not found
        with open(file_path, "r") as f:
            self.annot_json_data: Dict[str, Dict] = json.loads(f.read())

    def get_annotations_csv(self, annotations: str):
        """
        Read the first line of a csv file into a dictionary and set annot_json_data.

        Parameters
        ----------
        annotations: str
            a string of annotation dictionary data from the csv
        """

        self.annot_json_data = json.loads(annotations)

    def write_csv(self):
        """write headers and file info"""
        file = open(self.csv_path, "w")
        writer = csv.writer(file)
        writer.writerow(["Shuffled:", self.shuffled])
        header: List[str] = ["Annotations:", json.dumps(self.annot_json_data)]
        writer.writerow(header)

        header = ["File Name", "File Path", "FMS"]
        for name in self.view.annots_order:
            header.append(name)
        writer.writerow(header)
        for name, lst in self.files_and_annots.items():
            writer.writerow([name] + lst)
        file.close()
