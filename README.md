# RASTERer

Tools for creating chemical images from mass spectra

### Dependencies

Before running this script, please make sure that you have __Python3.6__ or higher installed on your system. 
Make sure that all the required libraries are installed by running:

    $ pip install -r requirements.txt

### Usage

Before using the tool, mass spectrometric data has to be converted to an HDF5 file with the following internal structure. 

<p align="center">
    <img src="/screenshots/file_structure.png">
</p>

The __Images__ dataset is not mandatory but will be created automatically when a new image is added.
For convenience, a tool for converting text files to HDF5 is included:

    $ python convert_to_hdf5.py

<p align="center">
    <img src="/screenshots/convert_script.png">
</p>

The input text file should have the following structure:

    time mass spectrum_0 spectrum_1 ... spectrum_n
    ...  ...     ...        ...            ...

The coordinates file should contain the __x__, __y__, and __z__ coordinates for each of the recorded spectra.

After converting the data to HDF5 you can run the __RASTERer__ tool:

    $ python rasterer.py

<p align="center">
    <img src="/screenshots/rasterer.png">
</p>

After loading a file (__Ctrl+O__) you will see the average mass spectrum.
Al the comments and saved images will be displayed in the __File Info__ docked widget.
You can plot a saved image by either double clicking on it or from the contextual menu.
To plot a new image, select one or several regions on the average mass spectrum and click __Plot Image__.
The obtained picture will appear in a separate window.

<p align="center">
    <img src="/screenshots/image.png">
</p>

In the __image__ window you are able to apply several transformations (α, β, γ, rotation, and mirroring) to the obtained figure and change the color map.
The image can be then saved to HDF5, text or image file.



