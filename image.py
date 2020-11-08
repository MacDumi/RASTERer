#!/usr/bin/env python3
import sys, os
import numpy as np
import time
from datetime import datetime
import logging
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor, SpanSelector
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from layouts.ui_label import Ui_Dialog
from raster_hdf5 import RasterData

class LabelDiag(QDialog, Ui_Dialog):
    def __init__(self):
        super(LabelDiag, self).__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint |
                                        Qt.WindowMinMaxButtonsHint);

    def getData(self):
        return self.lineEdit_lbl.text().strip()

class Image(QWidget):
    def __init__(self, image, fname, disable_save=False, label=None):
        super().__init__()
        self.layout = QGridLayout()
        self.image = image
        self.original_image = np.array(image)
        self.fname = fname
        title = 'Image' if label is None else f'Image - {label}'
        self.cbar = None
        self.cmap_cl = 'gray'

        save_hdf = QAction(QIcon("media/save_to.png"),"Save to HDF5", self)
        save     = QAction(QIcon("media/save.png"),"Save Image", self)
        reset    = QAction(QIcon("media/reset.png"),"Reset Image", self)
        rotate_right  = QAction(QIcon("media/rotate_right.png"),
                                                    "Rotate 90° clockwise", self)
        rotate_left   = QAction(QIcon("media/rotate_left.png"),
                                            "Rotate 90° counter-clockwise", self)
        flip_hor  = QAction(QIcon("media/flip_hor.png"),
                                                       "Flip horizontally", self)
        flip_ver  = QAction(QIcon("media/flip_ver.png"),
                                                       "Flip vertically", self)
        c_0 = QAction(QIcon("media/gray.png"), 'Gray', self)
        c_1 = QAction(QIcon("media/binary.png"), 'Binary', self)
        c_2 = QAction(QIcon("media/copper.png"), 'Copper', self)
        c_3 = QAction(QIcon("media/bone.png"), 'Bone', self)
        c_4 = QAction(QIcon("media/hot.png"), 'Hot', self)
        c_5 = QAction(QIcon("media/heat.png"), 'Gist Heat', self)
        c_6 = QAction(QIcon("media/spectral.png"), 'Spectral', self)
        c_7 = QAction(QIcon("media/seismic.png"), 'Seismic', self)
        c_8 = QAction(QIcon("media/coolwarm.png"), 'Coolwarm', self)
        menu = QMenu(self)
        menu.addAction(c_0)
        menu.addAction(c_1)
        menu.addAction(c_2)
        menu.addAction(c_3)
        menu.addAction(c_4)
        menu.addAction(c_5)
        menu.addAction(c_6)
        menu.addAction(c_7)
        menu.addAction(c_8)

        cmap = QToolButton()
        cmap.setPopupMode(QToolButton.InstantPopup)
        cmap.setToolTip('Colormap')
        cmap.setIcon(QIcon("media/cmap.png"))
        cmap.setMenu(menu)

        self.toolbar = QToolBar("tools")
        if not disable_save:
            self.toolbar.addAction(save_hdf)
            save_hdf.triggered.connect(self.save_to_hdf)
        self.toolbar.addAction(save)
        self.toolbar.addAction(reset)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(cmap)
        self.toolbar.addAction(rotate_right)
        self.toolbar.addAction(rotate_left)
        self.toolbar.addAction(flip_hor)
        self.toolbar.addAction(flip_ver)
        self.layout.addWidget(self.toolbar, 0, 0, 1, 6)

        c_0.triggered.connect(lambda: self.plot_image(cmap='gray'))
        c_1.triggered.connect(lambda: self.plot_image(cmap='binary'))
        c_2.triggered.connect(lambda: self.plot_image(cmap='copper'))
        c_3.triggered.connect(lambda: self.plot_image(cmap='bone'))
        c_4.triggered.connect(lambda: self.plot_image(cmap='hot'))
        c_5.triggered.connect(lambda: self.plot_image(cmap='gist_heat'))
        c_6.triggered.connect(lambda: self.plot_image(cmap='Spectral'))
        c_7.triggered.connect(lambda: self.plot_image(cmap='seismic'))
        c_8.triggered.connect(lambda: self.plot_image(cmap='coolwarm'))
        save.triggered.connect(self.save_txt)
        reset.triggered.connect(self.image_reset)
        rotate_left.triggered.connect(lambda: self.transform_image(rotate='left'))
        rotate_right.triggered.connect(lambda: self.transform_image(rotate='right'))
        flip_hor.triggered.connect(lambda: self.transform_image(flip='hor'))
        flip_ver.triggered.connect(lambda: self.transform_image(flip='ver'))

        self.figure = plt.figure()
        self.figure.set_tight_layout(True)
        self.subplot = self.figure.add_subplot(111) #add a subfigure
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas, 1, 0, 2, 6)

        icon = QIcon()
        icon.addPixmap(QPixmap("media/icon.png"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.brightness_slider = QSlider()
        self.brightness_slider.setMinimum(-127)
        self.brightness_slider.setMaximum(127)
        self.brightness_slider.setProperty("value", 0)
        self.brightness_slider.setOrientation(Qt.Horizontal)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)

        self.contrast_slider = QSlider()
        self.contrast_slider.setMinimum(-30)
        self.contrast_slider.setMaximum(230)
        self.contrast_slider.setProperty("value", 0)
        self.contrast_slider.setOrientation(Qt.Horizontal)
        self.contrast_slider.setTickPosition(QSlider.TicksBelow)
        self.gamma_slider = QSlider()
        self.gamma_slider.setMinimum(-130)
        self.gamma_slider.setMaximum(130)
        self.gamma_slider.setProperty("value", 0)
        self.gamma_slider.setOrientation(Qt.Horizontal)
        self.gamma_slider.setTickPosition(QSlider.TicksBelow)
        self.label_1 = QLabel()
        self.label_2 = QLabel()
        self.label_3 = QLabel()
        self.label_1.setText('Brightness (α)')
        self.label_2.setText('Contrast (β)')
        self.label_3.setText('Gamma (γ)')
        self.layout.addWidget(self.label_1, 3, 0, 1, 1)
        self.layout.addWidget(self.label_2, 4, 0, 1, 1)
        self.layout.addWidget(self.label_3, 5, 0, 1, 1)
        self.layout.addWidget(self.brightness_slider, 3, 1, 1, 5)
        self.layout.addWidget(self.contrast_slider, 4, 1, 1, 5)
        self.layout.addWidget(self.gamma_slider, 5, 1, 1, 5)
        self.contrast_slider.valueChanged.connect(self.plot_image)
        self.brightness_slider.valueChanged.connect(self.plot_image)
        self.gamma_slider.valueChanged.connect(self.plot_image)
        self.setWindowTitle(title)

        self.setLayout(self.layout)
        self.plot_image()

    def save_to_hdf(self):
        dialog = LabelDiag()
        result = dialog.exec_()
        label = dialog.getData()
        if result == QtWidgets.QDialog.Accepted:
            if label == '':
                label = 'Image_' + datetime.now()
            with RasterData(self.fname, 'r+') as f:
                f.save_image(self.image, label)
            logging.info(f'Image saved with the label: {label}')

    def save_txt(self):
        extensions = ['Text files (*.txt)',
                 'Portable Network Graphics (*.png)',
                 'Encapsulated Postscript (*.eps)']
        path = os.path.dirname(self.fname)
        fname, ext = QFileDialog.getSaveFileName(self, 'Save image', path,
                ';;'.join(extensions))
        if fname != '':
            if ext == extensions[0]:
                fname = f'{fname}.txt' if fname[-4:]!='.txt' else fname
                np.savetxt(fname, self.image)
            elif ext in extensions[1:]:
                fname = f'{fname}.png' if fname[-4:] not in ['.png', '.eps'] else fname
                self.figure.savefig(fname)

    def plot_image(self, cmap=None):
        cmap = self.cmap_cl if cmap is None else cmap
        self.subplot.clear()
        alpha = 10**(self.contrast_slider.value() / 100)
        beta  = self.brightness_slider.value()
        gamma = 10**(self.gamma_slider.value() / 100)
        self.image = self.original_image * alpha + beta
        self.image = np.clip(self.image, 0, self.image.max())
        self.image = np.clip(255.0 * np.power(
                            self.image / 255.0, gamma), 0, 255)
        try:
            img = self.subplot.imshow(self.image, cmap=cmap)
            self.subplot.set_xticks([])
            self.subplot.set_yticks([])
            if self.cbar is not None:
                self.cbar.remove()
            self.cbar = self.figure.colorbar(img, ax=self.subplot)
            self.canvas.draw()
            self.cmap_cl = cmap
        except ValueError:
            self.plot_image(cmap=self.cmap_cl)

    def image_reset(self):
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.gamma_slider.setValue(0)
        self.plot_image()

    def transform_image(self, rotate=None, flip=None):
        if rotate == 'right':
            self.original_image = np.rot90(self.original_image, 3)
        elif rotate == 'left':
            self.original_image = np.rot90(self.original_image)

        if flip == 'hor':
            self.original_image = self.original_image[:,::-1]
        elif flip == 'ver':
            self.original_image = self.original_image[::-1, :]

        self.plot_image()
