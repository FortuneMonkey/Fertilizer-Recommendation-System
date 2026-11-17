"""Fertilizer Recommendation dashboard -- start with:  streamlit run app.py"""
import streamlit as st

import config
import nav
from core import ui
from views import database, overview, recommendations

st.set_page_config(page_title=config.APP_TITLE, page_icon=str(config.BASE_DIR / "static" / "favicon.png"),
                   layout="wide", initial_sidebar_state="collapsed")
ui.inject_css()

nav.PAGES.update({
    "overview": st.Page(overview.render, title="Overview", url_path="overview", default=True),
    "database": st.Page(database.render, title="Database", url_path="database"),
    "recommendations": st.Page(recommendations.render, title="Recommendations", url_path="recommendations"),
})
page = st.navigation(list(nav.PAGES.values()), position="hidden")
ui.top_bar(nav.PAGES)
page.run()
