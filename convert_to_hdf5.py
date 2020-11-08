#!/usr/bin/env python3
import sys, os
import pandas as pd
import numpy as np
import h5py
import time
import argparse as ap
from tqdm import tqdm
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import layouts.convert_main as ui_main

class WorkerThread(QThread):
    error = pyqtSignal(str, name='error')
    finished = pyqtSignal()
    canceled = pyqtSignal()
    progress = pyqtSignal(int, name='progress')

    def __init__(self, data_file, coords, save_file,
                comments, compression=4, chunksize=500):
        QThread.__init__(self)
        self.data_file = data_file
        self.save_file = save_file
        self.compression = compression
        self.chunksize = chunksize
        self.coords_file = coords
        self.comment = comments
        self.cancel = False
    def abort(self):
        self.cancel = True

    def run(self):
        f = None
        try:
            f = h5py.File(self.save_file, 'w')
            data_group = f.create_group('tof_data')
            columns, rows = self.get_file_info()
            time    = data_group.create_dataset('time', (1,), maxshape=(None,),
                                    compression=self.compression, shuffle=True)
            mass    = data_group.create_dataset('mass', (1,), maxshape=(None,),
                                    compression=self.compression, shuffle=True)
            average = data_group.create_dataset('average', (1,), maxshape=(None,),
                                    compression=self.compression, shuffle=True)
            spectra = data_group.create_dataset('spectra',
                                    (1,columns-2), compression=self.compression,
                                       shuffle=True, maxshape=(None,columns-2))
            #Read the file in chunks
            chunks = pd.read_csv(self.data_file, sep='\t', skiprows=20, header=None,
                                                            chunksize=self.chunksize)
            nr_chunks = int(rows / self.chunksize) + (rows % self.chunksize > 0)
            for i, chunk in enumerate(chunks):
                if self.cancel:
                    break
                value = int(100 * i / nr_chunks)
                self.progress.emit(value)
                rows = chunk.shape[0]
                spectra.resize((spectra.shape[0]+rows, columns-2))
                time.resize((time.shape[0]+rows, ))
                mass.resize((mass.shape[0]+rows, ))
                average.resize((average.shape[0]+rows, ))
                spectra[spectra.shape[0]-rows-1:
                        spectra.shape[0]-1,:] = chunk.values[:,2:-1]
                time[time.shape[0]-rows-1:time.shape[0]-1] = chunk.values[:,0]
                mass[mass.shape[0]-rows-1:mass.shape[0]-1] = chunk.values[:,1]
                average[average.shape[0]-rows-1:average.shape[0]-1] = chunk.values[
                                :,2:-1].mean(axis=1)
                del chunk
            self.progress.emit(100)
            time.resize((time.shape[0]-1,))
            mass.resize((mass.shape[0]-1,))
            average.resize((average.shape[0]-1,))
            spectra.resize((spectra.shape[0]-1,spectra.shape[1]))

            #Add the coordinates
            coords = np.loadtxt(self.coords_file)
            coords_group = f.create_group('coordinates')
            n_points = coords.shape[0]
            z = coords_group.create_dataset('z', (n_points,),
                                            compression=self.compression, shuffle=True)
            y = coords_group.create_dataset('y', (n_points,),
                                            compression=self.compression, shuffle=True)
            x = coords_group.create_dataset('x', (n_points,),
                                            compression=self.compression, shuffle=True)
            z[:] = coords[:,1]
            y[:] = coords[:,2]
            x[:] = coords[:,3]

            #add comments
            for i, c in enumerate(self.comment):
                f.attrs.create(f'comment_{i}', c)
            f.flush()
            if not self.cancel:
                self.finished.emit()
        except OSError:
            self.canceled.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            if f is not None:
                f.close()

    def get_file_info(self, header=20, sep='\t'):
        #Get the number of columns
        with open(self.data_file, 'r') as f:
            lines = [next(f) for x in range(header+1)]
        columns = len(lines[-1].strip().split(sep))
        rows    = sum(1 for i in open(self.data_file, 'rb')) - header
        return columns, rows


class Main(QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self, data, coords, save):
        super(Main, self).__init__()
        self.setupUi(self)
        self.setFixedSize(600, 640)
        self.readConfig()
        self.reset()

        if save is not None:
            self.save_file = save
            self.out_lbl.setText(save)

        if data is not None:
            self.data_file = data
            self.data_lbl.setText(os.path.basename(data))
            if self.save_file is None:
                self.save_file = os.path.splitext(data)[0]+'.h5'
                self.out_lbl.setText(os.path.basename(self.save_file))

        if coords is not None:
            self.coords_file = coords
            self.coords_lbl.setText(os.path.basename(coords))
            if self.data_file is not None:
                self.convert_btn.setEnabled(True)

        #Connect to UI elements
        self.data_btn.clicked.connect(self.browse_data)
        self.coords_btn.clicked.connect(self.browse_coords)
        self.out_btn.clicked.connect(self.browse_out)

    def reset(self):
        self.coords_file, self.data_file, self.save_file = None, None, None
        self.data_lbl.setText('Data file')
        self.coords_lbl.setText('Coordinates file')
        self.out_lbl.setText('Output file')
        self.progressBar.setEnabled(False)
        self.convert_btn.clicked.connect(self.convert)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText('Convert')
        self.data_btn.setEnabled(True)
        self.out_btn.setEnabled(True)
        self.coords_btn.setEnabled(True)
        self.comment_txt.setEnabled(True)
        self.compression_slider.setEnabled(True)
        self.worker = None

    def browse_data(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Select data file',
                         self.path, "Text files (*.txt *.csv);;All files (*.*)")
        if fname != '':
            self.data_lbl.setText(os.path.basename(fname))
            self.path = os.path.dirname(fname)
            self.data_file = fname
            self.save_file = f'{os.path.splitext(fname)[0]}.h5'
            self.out_lbl.setText(os.path.basename(self.save_file))
            if self.coords_file is not None:
                self.convert_btn.setEnabled(True)

    def browse_coords(self):
        fname, _ = QFileDialog.getOpenFileName(self,
                                       'Select the coordinates file', self.path,
                                    "Coordinates files (*.coords);;All files (*.*)")
        if fname != '':
            self.coords_lbl.setText(os.path.basename(fname))
            self.coords_file = fname
            if self.data_file is not None:
                self.convert_btn.setEnabled(True)

    def browse_out(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Output file', self.save_file,
                            "HDF5 files (*.h5)")
        if fname != '':
            self.out_lbl.setText(os.path.basename(fname))
            self.save_file = fname

    def convert(self):
        comments = self.comment_txt.toPlainText().split('\n')
        self.progressBar.setEnabled(True)
        self.convert_btn.setText('Cancel')
        self.out_btn.setEnabled(False)
        self.coords_btn.setEnabled(False)
        self.comment_txt.setEnabled(False)
        self.compression_slider.setEnabled(False)

        self.worker = WorkerThread(self.data_file, self.coords_file, self.save_file, comments,
                                                    compression=self.compression_slider.value())

        self.worker.progress.connect(self.progressBar.setValue)
        self.worker.finished.connect(self.finished)
        self.worker.error.connect(self.error)
        self.worker.canceled.connect(self.canceled)
        self.convert_btn.clicked.connect(self.worker.abort)
        self.data_btn.setEnabled(False)
        self.worker.start()

    def canceled(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Task canceled")
        msg.setWindowTitle("Canceled")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        self.reset()

    def error(self, error):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Something went wrong\n{error}")
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def finished(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"All done!\nFile saved at: {self.save_file}")
        msg.setWindowTitle("Success")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        self.reset()

    def readConfig(self):
        self.settings = QSettings("ConvertToHDF5")
        self.restoreGeometry(self.settings.value('MainWindow/geometry',
                                                    self.saveGeometry()))
        self.restoreState(self.settings.value('MainWindow/state',
                                                        self.saveState()))
        self.path = self.settings.value('path', './')
        self.compression_slider.setValue(
                                    int(self.settings.value('compression', 4)))

    def closeEvent(self, event):
        if self.worker is not None:
            self.worker.abort()
        self.settings.setValue('MainWindow/geometry', self.saveGeometry())
        self.settings.setValue('MainWindow/state', self.saveState())
        self.settings.setValue('path', self.path)
        self.settings.setValue('compression', self.compression_slider.value())
        event.accept()



if __name__ == '__main__':
    parser = ap.ArgumentParser(
                          description='Script to convert MS txt files to hdf5',
                                   usage='%(prog)s [options] data coordinates')
    parser.add_argument('-d', '--data', help="Data File")
    parser.add_argument('-c', '--coords', help="Coordinates File")
    parser.add_argument('-z', '--compression', type=int, default=4,
                                                     help="Coompression level")
    parser.add_argument('-s', '--save', type=str, help='Output file')
    args = vars(parser.parse_args())

    app = QApplication([sys.argv])
    application = Main(args['data'], args['coords'], args['save'])
    application.show()
    app.exec()

