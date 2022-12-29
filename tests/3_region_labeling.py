import base64
from PIL import Image

import streamlit as st

from pathlib import Path
from tools import load_nirspec_fits, hdr_to_df, encrypt_file, decrypt_file
from streamlit import session_state as st_state
from astropy.visualization import ZScaleInterval
from bokeh.plotting import figure, output_file, show
from bokeh.models import BoxEditTool, ColumnDataSource, LinearColorMapper, LogColorMapper


def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf_out = base64.b64encode(f.read()).decode('utf-8')

    return base64_pdf_out


def myCallBack(attr, old, new):
    print('Hi')
    return


if st_state['auth_status']:

    image_file = Path(r'/tests/page0.png')
    image_pickle = Path(r'/tests/page0.pkl')
    image = Image.open(image_file)


    encrypt_file(image_pickle, st.secrets.calibration.key, image)
    image_d = decrypt_file(image_pickle, st.secrets.calibration.key)
    st.image(image_d, caption='Sunrise by the mountains')
    # file_address = Path(r'/data/CEERs_2022-12/bio_plots/00686_bio.pdf')
    # # base64_pdf = displayPDF(file_address)
    #
    # file_encry_address = file_address.parent/'test_pdf_encrypt.pkl'
    # # encrypt_file(file_encry_address, st.secrets.calibration.key, base64_pdf)
    # base64_pdf_d = decrypt_file(file_encry_address, st.secrets.calibration.key)
    #
    # # Embedding PDF in HTML
    # pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf_d}" width="650" height="500" type="application/pdf">'
    #
    # # Displaying File
    # st.markdown(pdf_display, unsafe_allow_html=True)


    # file_address = Path('D:/Downloads/p4_PRISM_1027_s01027_x1d.fits')
    # wave_array, flux_array, err_array, header = load_nirspec_fits(file_address.as_posix())
    #
    # fig_cfg = {'width': 600,
    #            'tools': "reset,pan"}
    #
    # im_fig = figure(**fig_cfg)
    # im_fig.x_range.range_padding = im_fig.y_range.range_padding = 0
    #
    # # Plotting the image
    # im_cfg = {'x': wave_array, 'y': flux_array}
    # im_fig.step(**im_cfg)
    #
    # st.bokeh_chart(im_fig)






    # Z_FUNC_CMAP = ZScaleInterval()
    #
    # file_address = Path('D:/Downloads/p4_PRISM_1027_s01027_s2d.fits')
    # wave_array, flux_array, err_array, header = load_nirspec_fits(file_address.as_posix())
    #
    # fig_cfg = {'width': 600,
    #            'aspect_ratio': 4,
    #            'tools': "reset,pan,ybox_select"}
    #
    # im_fig = figure(**fig_cfg)
    # im_fig.x_range.range_padding = im_fig.y_range.range_padding = 0
    #
    # # Color scale
    # z1, z2 = Z_FUNC_CMAP.get_limits(flux_array)
    # l_mapper = LinearColorMapper(palette="Inferno256", low=z1, high=z2)  # Oranges256
    #
    # # Plotting the image
    # im_cfg = {'image': [flux_array],
    #           'x': 0,
    #           'y': 0,
    #           'dw': flux_array.shape[1],
    #           'dh': flux_array.shape[0],
    #           'color_mapper': l_mapper,
    #           'level': "image"}
    # im_fig.image(**im_cfg)
    #
    # st.bokeh_chart(im_fig)
    #
    # # Display the header
    # st.markdown(f'### header data')
    # tab1, tab2 = st.tabs(['Extension 0', 'Extension 1'])
    #
    # with tab1:
    #     hdr_df = hdr_to_df(header[0])
    #     st.dataframe(hdr_df, width=800)
    #
    # with tab2:
    #     hdr_df = hdr_to_df(header[1])
    #     st.dataframe(hdr_df, width=800)


    # file_address = Path('S:/Astro_data/Observations/SMACS_Nirspec_v8/S2_out_clean_custom_pl_v2.0/G235M/Visit_1/8506/jw02736007001_03101_00002_nrs1_s2d.fits')
    # wave_array, flux_array, err_array, header = load_nirspec_fits(file_address.as_posix())
    #
    # fig_cfg = {'width': 600,
    #            'aspect_ratio': 4,
    #            'tools': "reset,pan,ybox_select"}
    #
    # im_fig = figure(**fig_cfg)
    # im_fig.x_range.range_padding = im_fig.y_range.range_padding = 0
    #
    # # Color scale
    # z1, z2 = Z_FUNC_CMAP.get_limits(flux_array)
    # l_mapper = LinearColorMapper(palette="Inferno256", low=z1, high=z2)  # Oranges256
    #
    # # Plotting the image
    # im_cfg = {'image': [flux_array],
    #           'x': 0,
    #           'y': 0,
    #           'dw': flux_array.shape[1],
    #           'dh': flux_array.shape[0],
    #           'color_mapper': l_mapper,
    #           'level': "image"}
    # im_fig.image(**im_cfg)
    #
    # # Data container for the selections
    # source_cfg = {'x': [400, 200, 800], 'y': [5, 7, 8], 'width': [100, 200, 200], 'height': [2, 5, 10],
    #               'alpha': [0.5, 0.5, 0.5]}
    # src = ColumnDataSource(source_cfg)
    # renderer = im_fig.rect('x', 'y', 'width', 'height', source=src, alpha='alpha')
    #
    # draw_tool = BoxEditTool(renderers=[renderer], empty_value=1)
    # draw_tool.on_change('renderers', myCallBack)
    # st.markdown(f'Aqui: {draw_tool.renderers[0].data_source.data["x"]}')
    #
    # im_fig.add_tools(draw_tool)
    # im_fig.toolbar.active_drag = draw_tool
    # st.bokeh_chart(im_fig)
