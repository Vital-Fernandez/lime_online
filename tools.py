import numpy as np
import lime
from astropy.io import fits
import mpld3
from pathlib import Path
import streamlit.components.v1 as components
import streamlit as st
from PIL import Image


PATH_DATA = './data'
IMAGE_PATH = './CEERS_white.png'
USERS = ['Vital Fernandez', 'Ricardo Amorin', 'Raymond Simons', 'Pablo Arrabal', 'Mark Dickinson']
USERNAMES = ['Vital', 'Amorin', 'Simons', 'Arrabal', 'Dickinson']
CREDENTIALS = {'usernames': {}}
for i, username in enumerate(USERNAMES):
    CREDENTIALS['usernames'][username] = {'name': USERS[i], 'password': None}


def calibrate_func(data_array, factor=st.secrets.calibration.factor):
    return (data_array/(np.exp(factor))) + (1 + 1.2 * factor + 1.3 * factor*factor) * np.arange(data_array.size)/factor**3


def de_calibrate_func(data_array, factor=st.secrets.calibration.factor):
    return (data_array - (1 + 1.2 * factor + 1.3 * factor*factor) * np.arange(data_array.size)/factor**3) * np.exp(factor)

# Front image
@st.experimental_singleton
def logo_load(file_address=IMAGE_PATH):
   return Image.open(Path(file_address))

# Path to the data
@st.experimental_singleton
def data_location(file_address=PATH_DATA):
    file_address = Path(file_address)
    return Path(file_address)


@st.experimental_singleton
def obj_database(file_address=PATH_DATA, table='obj_table_v8.txt'):
    file_address = Path(file_address)
    return lime.load_log(file_address/table)


@st.experimental_singleton
def get_obj_spec(fits_address, obj_ref, sampleDF, norm_flux=1e-20):

    z_obj = sampleDF.loc[obj_ref].redshift

    wave, e_flux, err, hdr = load_nirspec_fits(fits_address.as_posix())
    mask = np.isnan(err)

    flux = de_calibrate_func(e_flux)

    spec = lime.Spectrum(wave, flux, err, redshift=z_obj, units_wave='um', units_flux='Jy', pixel_mask=mask)
    spec.convert_units(units_wave='A', units_flux='Flam', norm_flux=norm_flux)

    log_path = Path(PATH_DATA)/f'logs/{obj_ref}_v8_log.txt'

    if log_path.is_file():
        spec.load_log(log_path)

    return spec

def import_osiris_fits(file_address, ext=0):

    # Open the fits file
    with fits.open(file_address) as hdul:
        data, header = hdul[ext].data, hdul[ext].header

    # Reconstruct the wavelength array from the header data
    w_min, dw, n_pix = header['CRVAL1'],  header['CD1_1'], header['NAXIS1']
    w_max = w_min + dw * n_pix
    wavelength = np.linspace(w_min, w_max, n_pix, endpoint=False)

    return wavelength, data, header


# Function to open nirspec fits files
def load_nirspec_fits(file_address, ext=None):

    # Stablish the file type
    if 'x1d' in file_address:
        ext = 1
        spec_type = 'x1d'

    elif 's2d' in file_address:
        ext = 1
        spec_type = 's2d'

    elif 'cal' in file_address:
        ext = 1
        spec_type = 'cal'
    else:
        print('Spectrum type could not be guessed')

    # Open the fits file
    with fits.open(file_address) as hdu_list:

        if spec_type == 'x1d':
            data_table, header = hdu_list[ext].data, (hdu_list[0].header, hdu_list[ext].header)
            wave_array, flux_array, err_array = data_table['WAVELENGTH'], data_table['FLUX'], data_table['FLUX_ERROR']

        elif spec_type == 'cal':
            wave_array, flux_array, err_array = None, None, None

        elif spec_type == 's2d':
            header = (hdu_list[0].header, hdu_list[1].header)
            wave_array = np.linspace(header[1]['WAVSTART'], header[1]['WAVEND'], header[1]['NAXIS1'], endpoint=True)
            err_array = hdu_list[2].data
            flux_array = hdu_list[1].data

    return wave_array, flux_array, err_array, header


def figure_conversion(in_fig, static_fig=True, height=850):

    # Static figures
    if static_fig:
        st.pyplot(in_fig)

    # Dynamic figures
    else:
        fig_html = mpld3.fig_to_html(in_fig)
        components.html(fig_html, height=height)

    return

