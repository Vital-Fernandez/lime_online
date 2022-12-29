from matplotlib import pyplot as plt
from matplotlib import colors
from bokeh.plotting import figure, show
from bokeh.transform import linear_cmap
from bokeh.models import LinearColorMapper, LogColorMapper, TeX
from bokeh.layouts import column
from lime.tools import UNITS_LATEX_DICT, latex_science_float
from astropy.visualization import ZScaleInterval
import streamlit as st

Z_FUNC_CMAP = ZScaleInterval()


def inter_spectrum_labelling_spec(data, wave, hdr, obj_label):

    # 2D figure image
    # im_fig = figure(width=900, height=300, tooltips=[("x", "Dispersion"), ("y", "Flux"), ("Flux", "@image")])
    im_fig = figure(width=900, aspect_ratio=4, tooltips=[("x", "Dispersion"), ("y", "Flux")],
                    tools="pan,wheel_zoom,ybox_select,reset, box_edit", active_drag="ybox_select")
    im_fig.x_range.range_padding = im_fig.y_range.range_padding = 0

    # Color scale
    z1, z2 = Z_FUNC_CMAP.get_limits(data)
    l_mapper = LinearColorMapper(palette="Inferno256", low=z1, high=z2) # Oranges256

    im_fig.image(image=[data], x=0, y=0, dw=data.shape[1], dh=data.shape[0], color_mapper=l_mapper, level="image")

    # 1D spectrum
    spec_fig = figure(width=900, aspect_ratio=4, tooltips=[("x", "Wavelength"), ("y", "Flux")], y_axis_type="linear")

    flux_1d = data.sum(axis=0)
    spec_fig.step(wave, flux_1d)

    # Formatting
    im_fig.x_range.range_padding = im_fig.y_range.range_padding = 0
    im_fig.grid.grid_line_width = 0.25

    # Display figure
    show(column(im_fig, spec_fig))

    return


def plot_nirspec_2D(data, wave, in_fig=None):

    if in_fig is None:
        fig, ax = plt.subplots()
    else:
        fig = in_fig
        ax = in_fig.add_subplot()

    z1, z2 = Z_FUNC_CMAP.get_limits(data)

    ax.imshow(data, cmap='gist_heat', vmin=z1, vmax=z2, aspect=10)


    if in_fig is None:
        plt.show()

    return fig


def plot_spectrum(spec):

    fig = figure(width=600, height=300, tools="pan,xwheel_pan,xzoom_in,xzoom_out,wheel_zoom,reset")
    # im_fig.x_range.range_padding = im_fig.y_range.range_padding = 0
    fig.step(x=spec.wave, y=spec.flux, mode="center")

    units_wave = UNITS_LATEX_DICT[spec.units_wave].replace(r"\AA", "Å")
    units_flux = UNITS_LATEX_DICT[spec.units_flux].replace(r"\AA", "Å")
    norm_label = r' \,/\,{}'.format(latex_science_float(spec.norm_flux)) if spec.norm_flux != 1.0 else ''

    # fig.xaxis.axis_label = f'wavelength (Å)' if spec.units_wave == 'A' else f'$${UNITS_LATEX_DICT[spec.units_wave]}$$'
    fig.xaxis.axis_label = r'$$\text{Wavelength }' + f'({units_wave}\,\,\,)$$'
    fig.yaxis.axis_label = r'$$\text{Flux }' + f'({units_flux})' + f'{norm_label}$$'

    return fig


def plot_spectrum(spec):

    fig = figure(width=600, height=300, tools="pan,xwheel_pan,xzoom_in,xzoom_out,wheel_zoom,reset")
    # im_fig.x_range.range_padding = im_fig.y_range.range_padding = 0

    fig.step(x=spec.wave, y=spec.flux, mode="center")

    units_wave = UNITS_LATEX_DICT[spec.units_wave].replace(r"\AA", "Å")
    units_flux = UNITS_LATEX_DICT[spec.units_flux].replace(r"\AA", "Å")
    norm_label = r' \,/\,{}'.format(latex_science_float(spec.norm_flux)) if spec.norm_flux != 1.0 else ''

    # fig.xaxis.axis_label = f'wavelength (Å)' if spec.units_wave == 'A' else f'$${UNITS_LATEX_DICT[spec.units_wave]}$$'
    fig.xaxis.axis_label = r'$$\text{Wavelength }' + f'({units_wave}\,\,\,)$$'
    fig.yaxis.axis_label = r'$$\text{Flux }' + f'({units_flux})' + f'{norm_label}$$'

    return fig


def plot_fits_2d(flux_image, wave):

    # Create the image
    fig_cfg = {'width': 600, 'aspect_ratio': 3, 'tools': "hover,wheel_zoom,reset,pan,xzoom_in,xzoom_out",
               'toolbar_location':"below", 'tooltips': [("x", "$x"), ("y", "$y")]}

    # TOOLTIPS = [
    #     ('name', "$name"),
    #     ('index', "$index"),
    #     ('pattern', '@pattern'),
    #     ("x", "$x"),
    #     ("y", "$y"),
    #     ("value", "@image"),
    #     ('squared', '@squared')
    # ]

    fig = figure(**fig_cfg)
    fig.x_range.range_padding = fig.y_range.range_padding = 0

    # Color map for the plot
    z1, z2 = Z_FUNC_CMAP.get_limits(flux_image)
    l_mapper = LinearColorMapper(palette="Inferno256", low=z1, high=z2)  # Oranges256

    # Plotting the image
    im_cfg = {'image': [flux_image],
              'x': wave[0], 'y': 0,
              'dw': wave[-1]-wave[0], 'dh': flux_image.shape[0],
              'color_mapper': l_mapper, 'level': "image"}
    fig.image(**im_cfg)
    fig.xaxis.axis_label = r'$$\text{Wavelength }' + f'(Å\,\,\,)$$'
    fig.yaxis.axis_label = r'$$\text{Pixel y coordinate}$$'


    return fig

def pdf_display(pdf_render):

    pdf_display = F'<embed src="data:application/pdf;base64,{pdf_render}" width="650" height="500" type="application/pdf">'

    return pdf_display