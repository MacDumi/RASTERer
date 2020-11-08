#!/usr/bin/env python3
import sys, os
import pandas as pd
import numpy as np
import time
from datetime import datetime
from distutils.util import strtobool
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
from raster_hdf5 import RasterData
from layouts.ui_main import Ui_MainWindow
from image import *
from imports.zoom import *


class Rasterer(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Rasterer, self).__init__()
        self.setupUi(self)
        #Logging
        log_level = logging.INFO
        date = datetime.now().date()
        if not os.path.isdir('logs'):
            os.mkdir('logs')
        logging.basicConfig(filename=f'logs/{date}.log',
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=log_level)

        #Connect menu items
        self.dock_info.visibilityChanged.connect(self.actionInfo.setChecked)
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(
                                                self.table_item_right_clicked)
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(
                                                self.list_item_right_clicked)
        self.listWidget.doubleClicked.connect(self.plot_saved)
        self.plot_btn.clicked.connect(self.plot_image)
        self.plot_btn.setEnabled(False)
        self.img = []
        self.spectrum_plot = None

        self.readConfig()

        self.figure = plt.figure()
        self.figure.set_tight_layout(True)
        self.subplot = self.figure.add_subplot(111) #add a subfigure
        self.subplot.format_coord = lambda x, y: f'm/z={x:.2f}'
        #add widget
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFocusPolicy(Qt.ClickFocus )
        self.canvas.setFocus()
        self.zp = ZoomPan()
        figZoom = self.zp.zoom_factory(self.subplot, base_scale = 1.5)
        figPan = self.zp.pan_factory(self.subplot)

        self.toolbar = NavigationToolbar(self.canvas, self)
        #Delete all the actions
        for x in self.toolbar.actions():
            self.toolbar.removeAction(x)

        self.open_act = QAction(QIcon('media/open.png'), 'Open (Ctrl+O)', self.toolbar)
        self.open_act.setShortcut('Ctrl+O')
        self.save_act = QAction(QIcon('media/save.png'),
                                    'Save the average spectrum (Ctrl+S)', self.toolbar)
        self.save_act.setShortcut('Ctrl+S')
        self.save_act.setEnabled(False)
        self.save_act.triggered.connect(self.save_spectrum)
        self.info_act = QAction(QIcon('media/info.png'),
                                    'File info', self.toolbar, checkable=True)
        self.info_act.setChecked(True)
        self.info_act.triggered.connect(lambda: [self.dock_info.setVisible(
                        self.info_act.isChecked()), self.dock_info.raise_()])
        self.reset_act = QAction(QIcon("media/reset.png"),"Reset Image", self.toolbar)
        self.open_act.triggered.connect(self.open)
        self.reset_act.triggered.connect(self.plot)
        self.toolbar.addAction(self.open_act)
        self.toolbar.addAction(self.info_act)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.reset_act)
        self.toolbar.addAction(self.save_act)
        self.toolbar.addAction(x)

        self.gridLayout_2.addWidget(self.toolbar)
        self.gridLayout_2.addWidget(self.canvas)

        self.cursor = Cursor(self.subplot, horizOn=False, useblit=True,
                                color='red', linestyle='--', linewidth=1)
        self.span =SpanSelector(self.subplot, onselect=self.onselect,
                            direction='horizontal', minspan=0.02, useblit=True,
                            button=3, rectprops={'facecolor':'red', 'alpha':0.3})

        self.subplot.text(0.3, 0.5, 'NO DATA', fontsize=32, fontweight='bold')
        self.canvas.draw()



    def onselect(self, min_value, max_value):
        logging.info(f'Region selected ({min_value:.2f}, {max_value:.2f})')
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)
        self.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(f'{min_value:.2f}'))
        self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(f'{max_value:.2f}'))
        self.plot_btn.setEnabled(True)

    def table_item_right_clicked(self, QPos):
        self.listMenu= QtWidgets.QMenu()
        menu_item_0 = self.listMenu.addAction("Remove")
        self.listMenu.addSeparator()
        menu_item_1 = self.listMenu.addAction("Remove All")
        menu_item_0.triggered.connect(self.remove_item)
        menu_item_1.triggered.connect(self.clearTable)
        parentPosition = self.tableWidget.mapToGlobal(QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def list_item_right_clicked(self, QPos):
        self.listMenu= QtWidgets.QMenu()
        menu_item_0 = self.listMenu.addAction("Plot")
        menu_item_1 = self.listMenu.addAction("Remove")
        self.listMenu.addSeparator()
        menu_item_2 = self.listMenu.addAction("Refresh")
        menu_item_0.triggered.connect(self.plot_saved)
        menu_item_1.triggered.connect(self.remove_saved)
        menu_item_2.triggered.connect(self.show_saved)
        parentPosition = self.listWidget.mapToGlobal(QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def show_saved(self):
        self.listWidget.clear()
        with RasterData(self.fname, 'r') as f:
            if 'Images' in f.file.keys():
                images = f.file['Images'].keys()
                for img in images:
                    self.listWidget.addItem(QListWidgetItem(img))

    def remove_saved(self):
        #Remove the saved image
        label = self.listWidget.currentItem().text()
        with RasterData(self.fname, 'r+') as f:
            del f.file['Images'][label]
        self.show_saved()

    def plot_saved(self):
        label = self.listWidget.currentItem().text()
        with RasterData(self.fname, 'r') as f:
            img = f.file['Images'][label][()]
        self.show_image(img, disable_save=True, label=label)

    def remove_item(self):
        row = self.tableWidget.currentRow()
        self.tableWidget.removeRow(row)
        if self.tableWidget.rowCount() == 0:
            self.plot_btn.setEnabled(False)

    def clearTable(self):
        while self.tableWidget.rowCount():
            self.tableWidget.removeRow(0)
        self.plot_btn.setEnabled(False)

    def plot_image(self):
        regions = [(float(self.tableWidget.item(i, 0).text()),
                    float(self.tableWidget.item(i, 1).text())) for i in
                    range(self.tableWidget.rowCount())]
        with RasterData(self.fname, 'r') as f:
            data = f.get_region(regions)
            image = f.generate_image(data)
        self.show_image(image)
        self.clearTable()

    def show_image(self, image, **kwargs):
        self.img.append(Image(image, self.fname, **kwargs))
        self.img[-1].show()

    def open(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', self.path,
                                                        "HDF5 files (*.h5)")
        if not fname:
            return
        self.path = os.path.dirname(fname)
        self.fname = fname
        try:
            with RasterData(self.fname, 'r') as f:
                self.spectrum = f.average
                self.time = f.time
                comments = [f.file.attrs[a] for a in f.file.attrs.keys()
                            if a.startswith('comment')]
                self.show_saved()
            self.textEdit.setText('\n'.join(comments))
            self.plot()
            self.clearTable()
            self.save_act.setEnabled(True)
            self.setWindowTitle(f'RASTERer - {os.path.basename(fname)}')
            self.statusbar.showMessage(f'File {os.path.basename(fname)} loaded', 2000)
        except Exception as e:
            self.errorBox(f'Could not load the file\n{e}', 'I/O error')
            self.statusbar.showMessage("Error loading the file", 2000)

    def plot(self):
        #Plot the average spectrum
        self.subplot.clear()
        min_idx = np.where(self.spectrum[:,0]>10)[0][0]
        self.spectrum_plot = self.subplot.plot(self.spectrum[min_idx:,1],
                                                self.spectrum[min_idx:,2])
        self.subplot.set_title('Average spectrum', fontweight='bold')
        self.subplot.set_xlim(20, 1000)
        self.subplot.set_ylim(-1, 1.1*self.spectrum[min_idx:,1].max())
        self.subplot.set_xlabel('m/z', fontweight='bold')
        self.canvas.draw()

    def save_spectrum(self):
        #Save the average spectrum
        fname, ext = QFileDialog.getSaveFileName(self,
                'Save the average spectrum', self.path,
                'Text files (*.txt)')
        if fname != '':
            fname = f'{fname}.txt' if fname[-4:] != '.txt' else fname
            np.savetxt(fname, self.spectrum, delimiter='\t')

    def readConfig(self):
        self.settings = QSettings("Rasterer")
        self.restoreGeometry(self.settings.value('MainWindow/geometry',
                                                    self.saveGeometry()))
        self.restoreState(self.settings.value('MainWindow/state',
                                                        self.saveState()))
        self.actionInfo.setChecked(strtobool(
                        self.settings.value('MainWindow/info', 'true')))
        self.path = self.settings.value('MainWindow/path', './')
        logging.info("Config loaded")
        self.statusbar.showMessage('Config loaded', 2000)

    def errorBox(self, message, title="Error"):
        self.error = True
        self.statusbar.showMessage(message, 5000)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def closeEvent(self, event):
        self.settings.setValue('MainWindow/geometry', self.saveGeometry())
        self.settings.setValue('MainWindow/state', self.saveState())
        self.settings.setValue('MainWindow/info', self.actionInfo.isChecked())
        self.settings.setValue('MainWindow/path', self.path)
        event.accept()


if __name__ == '__main__':
    app = QApplication([sys.argv])
    application = Rasterer()
    application.show()
    app.exec()

