"""Streamlit Community Cloud portfolio adapter for snake-game.

This does not replace the original implementation.
"""
from pathlib import Path

import streamlit as st

TITLE = "Neon Snake"
ICON = "🐍"
DESC = "Snake game implemented in Pygame, with a separate playable browser version."
CATEGORY = "Pygame / Web adaptation"
NOTICE = "Browser game below is a separate Vercel-hosted implementation embedded in Streamlit; the Pygame version is desktop-only."
GITHUB = "https://github.com/mohsinattasial/snake-game"
VERCEL = "https://mohsin-neon-snake.vercel.app"
LOCAL_COMMAND = "python snake_game.py"
FEATURES = ["Keyboard movement","Scoring and restart","Browser version"]

st.set_page_config(page_title=TITLE + " | Mohsin Atta", page_icon=ICON, layout="wide")
st.caption("Mohsin Atta · GitHub Portfolio · Streamlit Cloud edition")
st.title(ICON + " " + TITLE)
st.write(DESC)
st.caption(CATEGORY)

left, right = st.columns(2)
with left:
    st.link_button("GitHub source code", GITHUB, use_container_width=True)
with right:
    st.link_button("Existing browser version", VERCEL, use_container_width=True)

st.info(NOTICE)
with st.expander("Original project and features", expanded=False):
    for feature in FEATURES:
        st.write("• " + feature)
    st.code(LOCAL_COMMAND, language="bash")

st.subheader("Interactive browser edition")
st.caption("The following interactive view is embedded from the separate Vercel deployment.")
import streamlit.components.v1 as components
components.iframe(VERCEL, height=760, scrolling=True)

st.divider()
st.caption("© 2026 Mohsin Atta · Educational portfolio · MIT-licensed original code where applicable")
