import streamlit as st
import pandas as pd
import plotly.express as px

from crawler import run_crawler

# PAGE
st.set_page_config(
    page_title="SitePilot",
    page_icon="🚀",
    layout="wide"
)

# DARK UI
st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

.stMetric {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
}

.stButton>button {
    background-color: #22c55e;
    color: white;
    border-radius: 10px;
    height: 50px;
    width: 100%;
    border: none;
    font-size: 18px;
}

</style>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.title("🚀 SitePilot")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Reports",
        "SEO Issues",
        "Settings"
    ]
)

# SESSION STORAGE
if "data" not in st.session_state:
    st.session_state.data = None

# TITLE
st.title("🚀 SitePilot SEO Crawler")

st.write(
    "Professional Technical SEO Audit Tool"
)

# URL INPUT
url = st.text_input(
    "Enter Website URL",
    "https://example.com"
)

# START BUTTON
if st.button("Start Crawl"):

    with st.spinner(
        "Crawling website..."
    ):

        crawl_data = run_crawler(url)

        st.session_state.data = pd.DataFrame(crawl_data)

# GET DATA
df = st.session_state.data

# DASHBOARD
if df is not None:

    # OVERVIEW PAGE
    if page == "Overview":

        st.title("📊 Overview")

        total_urls = len(df)

        broken_urls = len(
            df[df["Status"] == 404]
        )

        missing_h1 = len(
            df[df["H1"] == "Missing"]
        )

        missing_meta = len(
            df[df["Meta Description"] == "Missing"]
        )

        # CARDS
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "URLs",
            total_urls
        )

        col2.metric(
            "404 Pages",
            broken_urls
        )

        col3.metric(
            "Missing H1",
            missing_h1
        )

        col4.metric(
            "Missing Meta",
            missing_meta
        )

        st.divider()

        # CHARTS
        col1, col2 = st.columns(2)

        with col1:

            fig = px.histogram(
                df,
                x="Status"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            issue_data = pd.DataFrame({

                "Issue": [
                    "Missing H1",
                    "Missing Meta"
                ],

                "Count": [
                    missing_h1,
                    missing_meta
                ]
            })

            fig2 = px.pie(
                issue_data,
                names="Issue",
                values="Count"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

        st.divider()

        st.subheader("Crawl Results")

        st.dataframe(
            df,
            use_container_width=True,
            height=500
        )

    # REPORTS PAGE
    elif page == "Reports":

        st.title("📁 Reports")

        st.write(
            "Download complete SEO audit report."
        )

        excel_file = "sitepilot_report.xlsx"

        df.to_excel(
            excel_file,
            index=False
        )

        with open(
            excel_file,
            "rb"
        ) as file:

            st.download_button(
                label="📥 Download Excel Report",
                data=file,
                file_name="sitepilot_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # SEO ISSUES PAGE
    elif page == "SEO Issues":

        st.title("⚠ SEO Issues")

        st.subheader(
            "Missing H1"
        )

        st.dataframe(
            df[df["H1"] == "Missing"],
            use_container_width=True
        )

        st.subheader(
            "Missing Meta Description"
        )

        st.dataframe(
            df[
                df["Meta Description"]
                == "Missing"
            ],
            use_container_width=True
        )

    # SETTINGS PAGE
    elif page == "Settings":

        st.title("⚙ Settings")

        st.write(
            "Crawler Settings"
        )

        crawl_limit = st.slider(
            "Max Crawl URLs",
            100,
            5000,
            500
        )

        st.selectbox(
            "User Agent",
            [
                "Googlebot",
                "Chrome",
                "Mozilla"
            ]
        )

        st.checkbox(
            "Enable JavaScript Rendering"
        )

        st.checkbox(
            "Respect robots.txt"
        )

        st.info(
            "More advanced settings coming soon."
        )