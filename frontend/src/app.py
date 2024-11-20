import logging
from datetime import datetime

import streamlit as st


logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs/frontend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)


def main() -> None:

    st.write("Hello, world!")


if __name__ == "__main__":
    st.set_page_config(
        page_title="DnD Chatbot",
        page_icon="🎲",
        layout="wide",
        initial_sidebar_state="auto",
    )
    main()
