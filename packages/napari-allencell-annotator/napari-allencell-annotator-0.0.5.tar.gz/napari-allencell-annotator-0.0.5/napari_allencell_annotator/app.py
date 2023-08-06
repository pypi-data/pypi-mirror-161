import sys

from qtpy.QtWidgets import QApplication

import napari
from napari_allencell_annotator.controller.main_controller import MainController


class App(QApplication):
    """
    A class used to initialize the image annotator controller.
    """

    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.viewer = napari.Viewer()
        self.main = MainController(self.viewer)
        self.viewer.window.add_dock_widget(self.main, area="right")


if __name__ == "__main__":
    app = App(sys.argv)

    sys.exit(app.exec_())
