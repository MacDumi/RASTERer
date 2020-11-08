#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import h5py
import peakutils
import os, sys
import argparse as ap
greeting = """
#################################################################################
#################################################################################
#################################################################################
########██████╗##█████╗#███████╗████████╗███████╗██████╗#███████╗██████╗#########
########██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔════╝██╔══██╗########
########██████╔╝███████║███████╗###██║###█████╗##██████╔╝█████╗##██████╔╝########
########██╔══██╗██╔══██║╚════██║###██║###██╔══╝##██╔══██╗██╔══╝##██╔══██╗########
########██║##██║██║##██║███████║###██║###███████╗██║##██║███████╗██║##██║########
########╚═╝##╚═╝╚═╝##╚═╝╚══════╝###╚═╝###╚══════╝╚═╝##╚═╝╚══════╝╚═╝##╚═╝########
#################################################################################
#################################################################################
#################################################################################
"""
class RasterData:
    def __init__(self, file_name, mode):
        if not os.path.isfile(file_name):
            raise FileNotFoundError
        self.file_name = file_name
        self.mode = mode
        self.file = None
        self.tof_data = None
        self._mass = None
        self._time = None
        self._average = None
        self._x = None
        self._y = None

    def __enter__(self):
        #Create a class from a file
        self.file = h5py.File(self.file_name, self.mode)
        try:
            self.tof_data = self.file['tof_data']['spectra']
            self._average  = self.file['tof_data']['average']
            self.mass     = self.file['tof_data']['mass']
            self.time     = self.file['tof_data']['time']
            self.x        = self.file['coordinates']['x']
            self.y        = self.file['coordinates']['y']
            if len(self.x) != self.tof_data.shape[1]:
                raise ValueError('Shape Mismatch')
            return self
        except Exception as e:
            self.file.close()
            raise KeyError(e)

    def get_peaks(self, peaks, mass=True, intensity=True,
                       summed=True, mass_width=0.05, time_width=10):
        #Returns the intensity/area of one or several peaks
        if type(peaks) not in [tuple, list, set]:
            peaks = [peaks]
        out = {}
        x_axis = self.mass[:] if mass else self.time[:]
        width  = mass_width if mass else time_width
        for peak in peaks:
            start_idx = np.where(x_axis >= peak - width/2)[0][0]
            end_idx   = np.where(x_axis >= peak + width/2)[0][0]
            data = self.tof_data[start_idx:end_idx, :]
            if intensity:
                out[peak] = data.max(axis=0)
            else:
                out[peak] = data.sum(axis=0)
        if summed:
            return np.array([out[peak] for peak in peaks]).sum(axis=0)
        else:
            return out

    def get_region(self, regions, mass=True):
        #Returns the area of one or several regions
        if type(regions) not in [list, dict, set, tuple]:
            return
        if type(regions[0]) not in [list, dict, set, tuple]:
            regions = [regions]
        out = []
        x_axis = self.mass[:] if mass else self.time[:]
        for start, end in regions:
            start_idx = np.where(x_axis >= start)[0][0]
            end_idx   = np.where(x_axis >= end)[0][0]
            out.append(self.tof_data[start_idx:end_idx, :].sum(axis=0))
        return np.array(out).sum(axis=0)

    def save_image(self, image, label):
        if 'Images' not in self.file.keys():
            self.file.create_group('Images')
        images = self.file['Images']
        if label not in images.keys():
            images.create_dataset(label, shape=(1,1), maxshape=(None, None),
                    shuffle=True, compression=9)
        image_ds = images[label]
        image_ds.resize((image.shape[0], image.shape[1]))
        image_ds[:,:] = image
        self.file.flush()

    def generate_image(self, data):
        """
        Construct an image with the correct shape and normalize it
        """
        #Create a dataframe
        df = pd.DataFrame(np.column_stack((self.x, self.y, data)),
                                                          columns=['x','y','z'])
        #Create a pivot table with x in rows and y in columns
        image = df.pivot_table(values='z', index='x', columns='y')
        #Normalize the image
        # image = image - image.min().min()
        image = image / image.max().max() * 255
        return image.transpose().values[:,::-1]

    @property
    def average(self):
        #Returns the average mass spectrum (time, mass, intensity)
        return np.column_stack((self.time[:], self.mass[:], self._average[:]))

    @average.setter
    def average(self, average):
        self._average = average
        self.file.flush()

    @property
    def mass(self):
        #Returns the mass column
        return self._mass[:]

    @mass.setter
    def mass(self, mass):
        self._mass = mass
        self.file.flush()

    @property
    def time(self):
        #Returns the time column
        return self._time[:]

    @time.setter
    def time(self, time):
        self._time = time
        self.file.flush()

    @property
    def x(self):
        #Returns the x coordinate
        return self._x[:]

    @x.setter
    def x(self, x):
        self._x = x
        self.file.flush()

    @property
    def y(self):
        #Returns the y coordinate
        return self._y[:]

    @y.setter
    def y(self, y):
        self._y = y
        self.file.flush()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        #Properly close the hdf5 file
        self.file.close()



def plotSpectrum(data, mass=True, **kwargs):
    """
    Plot the averaged spectrum
    """
    print("[i] Calculating the average spectrum ...")
    mean = data[data.columns[2:]].mean(axis=1)
    mean.name = 'average'

    #Plot the spectrum
    print("[i] Plotting the average spectrum ...")
    if mass:
        plt.plot(data['mass'], mean)
        plt.xlabel('m/z')
        plt.xlim(10, data['mass'].iloc[-1])
    else:
        plt.plot(data['time'], mean)
        plt.xlabel('time of flight')
        plt.xlim(4000, data['time'].iloc[-1])
    plt.ylim(0, 1.05*mean.max())
    plt.ylabel('Intensity, counts')
    plt.tight_layout()
    plt.show()
    return pd.concat([data['time'], data['mass'], mean], axis=1)


def findPeak(x, y, pos, width=25, peak_width=10):
    """
    Find a single peak and get its intensity and area
    """
    ind = np.abs(x - pos).argmin()
    data_x = x[ind-width: ind+width].values
    data_y = y[ind-width: ind+width].values
    indexes = peakutils.indexes(data_y, thres=0.2, min_dist=30)
    if len(indexes) == 0:
        #if no peaks were found
        return {'intensity': 0, 'area':0}
    else:
        #get the highest peak
        intensity = max(data_y[indexes])

        #integrate the peak
        index = np.argwhere(data_y == intensity)[0][0]
        offset = int(peak_width / 2)
        area = np.sum(data_y[index-offset:index+offset])
        if area < 0:
            area = 0
        if intensity < 0:
            intensity = 0
        return {'intensity': intensity, 'area': round(area,2)}

def findRegion(x, y, start, end):
    """
    Find a region and get its area
    """
    if start < x.iloc[0]:
        start = x.iloc[0]
    if end > x.iloc[-1]:
        end = x.iloc[-1]
    ind_start = np.abs(x - start).argmin()
    ind_end = np.abs(x - end).argmin()
    data_y = y[ind_start: ind_end].values

    area = np.sum(data_y)
    if area < 0:
        area = 0
    return {'intensity': max(data_y), 'area': round(area,2)}

def findPeaks(x, y, peaks, **kwargs):
    """
    Find multiple peaks in the same spectrum
    """
    intensity, area = 0, 0
    if type(peaks) in [int, float]:
        return findPeak(x, y, peaks, **kwargs)
    else:
        for peak in peaks:
            result = findPeak(x, y, peak, **kwargs)
            intensity += result['intensity']
            area += result['area']
        return {'intensity': round(intensity, 2), 'area': round(area,2)}

def getPeaks(data, peaks, mass=True, **kwargs):
    """
    Get the signal of one or several peaks from all the spectra
    """
    columns = list(set(data.columns) - set(['time', 'mass']))
    out = []
    print(f"[i] Extracting the signal for peaks at {peaks} ... ")
    for c in tqdm(columns):
        if mass:
            out.append(findPeaks(data['mass'], data[c], peaks, **kwargs))
        else:
            out.append(findPeaks(data['time'], data[c], peaks, **kwargs))
    return out

def getRegion(data, start, end, mass=True, **kwargs):
    """
    Get the signal of a region from all the spectra
    """
    columns = list(set(data.columns) - set(['time', 'mass']))
    out = []
    print(f"[i] Extracting the signal for peaks from {start:.2f} to {end:.2f} ... ")
    for c in tqdm(columns):
        if mass:
            out.append(findRegion(data['mass'], data[c], start, end, **kwargs))
        else:
            out.append(findRegion(data['time'], data[c], start, end, **kwargs))
    return out




if __name__ == '__main__':
    """
    Will run when executed
        python raster.py <dataFile> -c <coordinates> --peaks <peak1> <peak2>...
    """
    print(greeting)
    parser = ap.ArgumentParser(
                description='Script for plotting chemical images',
                usage='%(prog)s [options] data -c coordinates')
    parser.add_argument('data', help="Data File")
    group_0= parser.add_mutually_exclusive_group(required=True)
    group_0.add_argument('-c', '--coords', help="Coordinates")
    group_0.add_argument('--average', action='store_true',
                    help='Plot the average spectrum')
    parser.add_argument('-a', '--area', action='store_true',
                    help='Plot the area of peaks')
    parser.add_argument('-s', '--save', action='store_true',
                    help='Save the data')
    parser.add_argument('-b', '--batch', action='store_true',
                    help='Batch for a list of peaks')
    parser.add_argument('--cmap', nargs='?', type=str, default='gray')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--peaks', nargs='+', help="Peaks to plot")
    group.add_argument('--region', nargs='+', help="Region to plot")
    args = vars(parser.parse_args())

    #Load the data
    data   = readData(args['data'])

    if args['average']:
        #Plot the average spectrum and exit
        out = plotSpectrum(data)

        if args['save']:
            name = os.path.splitext(args['data'])[0]
            name += "_Averaged_Spectrum.csv"
            out.to_csv(name, index=None)
            print("[i] Average spectrum saved")
        sys.exit()

    #Load the coordinates
    coords = readCoords(args['coords'])

    if args['peaks'] != None:
        #Get the peaks for each spectrum
        try:
            peaks = [float(p) for p in args['peaks']]
        except ValueError:
            print("[e] Peaks should be numbers")
            sys.exit()
        if args['batch']:
            signal = {peak:getPeaks(data, peak) for peak in peaks}
        else:
            signal = getPeaks(data, peaks)
    elif args['region'] != None:
        #Get the peaks for each spectrum
        try:
            region = [float(p) for p in args['region']]
        except ValueError:
            print("[e] Peaks should be numbers")
            sys.exit()
        if len(region) == 1:
            signal = getRegion(data, region[0], data['mass'].iloc[-1])
        else:
            signal = getRegion(data, region[0], region[1])
    else:
        print("[e] Please provide a list of peaks or a region to plot")
        sys.exit()

    #Generate Image
    if args['batch']:
        image = {peak: generateImage(coords, signal[peak], area=args['area'])
                            for peak in signal}
    else:
        image = generateImage(coords, signal, area=args['area'])

    if type(image) not in [pd.DataFrame, dict]:
        sys.exit()

    #Save the image
    if args['save']:
        name = os.path.splitext(args['data'])[0]
        if args['peaks'] != None:
            name += f"_PeakSignal({'_'.join(args['peaks'])}).csv"
        elif args['region'] != None:
            name += f"_PeakSignal({'_'.join(args['region'])}).csv"
        image.to_csv(name)
        plt.imsave(os.path.basename(name)+'.jpg', image, cmap=args['cmap'])
        print("[i] Image saved")
    #Plot the image
    if args['batch']:
        for peak in image:
            plt.imshow(image[peak], cmap=args['cmap'])
            plt.title(peak)
            plt.show()
    else:
        plt.imshow(np.flip(image.values, axis=1), cmap=args['cmap'])
            # extent=[coords['x'].min(), coords['x'].max(),
            #     coords['y'].min(), coords['y'].max()])
        plt.tight_layout()
        plt.show()

