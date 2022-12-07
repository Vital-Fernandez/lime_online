import streamlit as st


def run():

    # Side bar
    st.set_page_config(page_title="Intro")

    # Page structure
    st.sidebar.success("Switch between sections for different results")

    # Wording
    st.header('SMACs CEERS measurements')


if __name__ == "__main__":
    run()

