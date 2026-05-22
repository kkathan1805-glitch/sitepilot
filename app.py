import streamlit as st
import pandas as pd
import plotly.express as px

from crawler import crawl, results
from urllib.parse import urlparse

st.set_page_config(
    page_title="SitePilot",
    layout="wide"
)

st.sidebar.title("🚀 SitePilot")

st.title("SitePilot SEO Crawler")

url = st.text_input(
    "Enter Website URL",
    "https://example.com"
)

if st.button("Start Crawl"):

    results.clear()

    domain = urlparse(url).netloc

    crawl(url, domain)

    df = pd.DataFrame(results)

    if df.empty:

        st.error(
            "No pages crawled."
        )

    else:

        st.success(
            "Crawl Completed!"
        )

        total_urls = len(df)

        broken = len(
            df[df["Status"] == 404]
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Total URLs",
            total_urls
        )

        col2.metric(
            "Broken URLs",
            broken
        )

        st.subheader(
            "Status Codes"
        )

        fig = px.histogram(
            df,
            x="Status"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader(
            "Crawl Results"
        )

        st.dataframe(df)

        csv = df.to_csv(
            index=False
        ).encode()

        st.download_button(
            "Download CSV",
            csv,
            "sitepilot_report.csv",
            "text/csv"
        )