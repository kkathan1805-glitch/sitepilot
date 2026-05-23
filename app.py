import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
from streamlit_option_menu import option_menu

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="SitePilot",
    page_icon="🚀",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

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
    text-align: center;
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

div[data-baseweb="select"] {
    color: black;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    selected = option_menu(

        menu_title="🚀 SitePilot",

        options=[
            "Overview",
            "Crawl Results",
            "SEO Issues",
            "Reports",
            "Settings"
        ],

        icons=[
            "speedometer2",
            "globe",
            "exclamation-triangle",
            "file-earmark",
            "gear"
        ],

        menu_icon="rocket",

        default_index=0
    )

# ---------------------------------------------------
# SESSION
# ---------------------------------------------------

if "crawl_data" not in st.session_state:
    st.session_state.crawl_data = None

# ---------------------------------------------------
# CRAWLER SETTINGS
# ---------------------------------------------------

MAX_URLS = 500

# ---------------------------------------------------
# URL NORMALIZER
# ---------------------------------------------------

def normalize_url(url):

    parsed = urlparse(url)

    return (
        parsed.scheme +
        "://" +
        parsed.netloc +
        parsed.path.rstrip("/")
    )

# ---------------------------------------------------
# CRAWLER
# ---------------------------------------------------

def run_crawler(start_url):

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    visited = set()

    queue = deque()

    results = []

    start_url = normalize_url(start_url)

    domain = urlparse(start_url).netloc

    queue.append(start_url)

    session = requests.Session()

    progress_bar = st.progress(0)

    status_text = st.empty()

    while queue and len(visited) < MAX_URLS:

        current_url = queue.popleft()

        current_url = normalize_url(current_url)

        if current_url in visited:
            continue

        visited.add(current_url)

        progress = len(visited) / MAX_URLS

        progress_bar.progress(progress)

        status_text.text(
            f"Crawled {len(visited)} pages"
        )

        try:

            response = session.get(
                current_url,
                headers=headers,
                timeout=15,
                allow_redirects=True
            )

            status = response.status_code

            content_type = response.headers.get(
                "Content-Type",
                ""
            )

            if "text/html" not in content_type:
                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # TITLE

            title = "Missing"

            if soup.title and soup.title.text:

                title = soup.title.text.strip()

            # META DESCRIPTION

            meta_description = "Missing"

            meta = soup.find(
                "meta",
                attrs={"name":"description"}
            )

            if meta and meta.get("content"):

                meta_description = (
                    meta.get("content").strip()
                )

            # H1

            h1_tags = soup.find_all("h1")

            if len(h1_tags) == 0:

                h1 = "Missing"

            elif len(h1_tags) > 1:

                h1 = "Multiple H1"

            else:

                h1 = h1_tags[0].get_text().strip()

            # CANONICAL

            canonical = "Missing"

            canonical_tag = soup.find(
                "link",
                rel="canonical"
            )

            if canonical_tag and canonical_tag.get("href"):

                canonical = canonical_tag.get("href")

            # WORD COUNT

            text = soup.get_text(
                separator=" ",
                strip=True
            )

            word_count = len(
                text.split()
            )

            # IMAGES

            images = soup.find_all("img")

            image_count = len(images)

            missing_alt = 0

            for img in images:

                alt = img.get("alt")

                if not alt or alt.strip() == "":

                    missing_alt += 1

            # LINKS

            internal_links = 0

            external_links = 0

            links = soup.find_all(
                "a",
                href=True
            )

            for link in links:

                href = link.get("href")

                if not href:
                    continue

                if href.startswith("#"):
                    continue

                if href.startswith("mailto:"):
                    continue

                if href.startswith("tel:"):
                    continue

                full_url = urljoin(
                    current_url,
                    href
                )

                parsed = urlparse(full_url)

                clean_url = normalize_url(
                    full_url
                )

                if parsed.netloc == domain:

                    internal_links += 1

                    if clean_url not in visited:

                        queue.append(clean_url)

                else:

                    external_links += 1

            # SAVE DATA

            results.append({

                "URL": current_url,

                "Status": status,

                "Title": title,

                "Title Length": len(title),

                "Meta Description": meta_description,

                "Meta Length": len(meta_description),

                "H1": h1,

                "Canonical": canonical,

                "Word Count": word_count,

                "Images": image_count,

                "Missing Alt": missing_alt,

                "Internal Links": internal_links,

                "External Links": external_links
            })

        except Exception as e:

            print("ERROR:", current_url, e)

    return results

# ---------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------

st.title("🚀 SitePilot SEO Auditor")

st.write(
    "Professional Technical SEO Audit Tool"
)

# ---------------------------------------------------
# URL INPUT
# ---------------------------------------------------

url = st.text_input(
    "Enter Website URL",
    "https://example.com"
)

# ---------------------------------------------------
# START BUTTON
# ---------------------------------------------------

if st.button("Start Crawl"):

    with st.spinner(
        "Crawling website..."
    ):

        crawl_data = run_crawler(
            url.strip()
        )

        st.session_state.crawl_data = pd.DataFrame(
            crawl_data
        )

# ---------------------------------------------------
# DATA
# ---------------------------------------------------

df = st.session_state.crawl_data

# ---------------------------------------------------
# IF NO DATA
# ---------------------------------------------------

if df is None:

    st.warning(
        "Start a crawl to see audit data."
    )

    st.stop()

if df.empty:

    st.warning(
        "No pages found."
    )

    st.stop()

# ---------------------------------------------------
# SEO AUDITS
# ---------------------------------------------------

df["Title Audit"] = df["Title Length"].apply(

    lambda x:
    "Good"
    if 50 <= x <= 55
    else "Bad"
)

df["Meta Audit"] = df["Meta Length"].apply(

    lambda x:
    "Good"
    if 150 <= x <= 155
    else "Bad"
)

df["Canonical Audit"] = df["Canonical"].apply(

    lambda x:
    "Present"
    if x != "Missing"
    else "Missing"
)

df["Word Audit"] = df["Word Count"].apply(

    lambda x:
    "Good"
    if x >= 300
    else "Thin Content"
)

df["Alt Audit"] = df["Missing Alt"].apply(

    lambda x:
    "Good"
    if x == 0
    else "Missing Alt"
)

df["Duplicate Title"] = df.duplicated(
    subset=["Title"],
    keep=False
)

df["Duplicate Meta"] = df.duplicated(
    subset=["Meta Description"],
    keep=False
)

# ---------------------------------------------------
# OVERVIEW PAGE
# ---------------------------------------------------

if selected == "Overview":

    st.subheader("📊 Crawl Overview")

    total_urls = len(df)

    missing_h1 = len(
        df[df["H1"] == "Missing"]
    )

    multiple_h1 = len(
        df[df["H1"] == "Multiple H1"]
    )

    missing_meta = len(
        df[
            df["Meta Description"]
            == "Missing"
        ]
    )

    broken_pages = len(
        df[df["Status"] == 404]
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "URLs",
        total_urls
    )

    col2.metric(
        "404 Pages",
        broken_pages
    )

    col3.metric(
        "Missing H1",
        missing_h1
    )

    col4.metric(
        "Multiple H1",
        multiple_h1
    )

    col5.metric(
        "Missing Meta",
        missing_meta
    )

    st.divider()

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

        issue_chart = pd.DataFrame({

            "Issue": [
                "Missing H1",
                "Multiple H1",
                "Missing Meta",
                "404"
            ],

            "Count": [
                missing_h1,
                multiple_h1,
                missing_meta,
                broken_pages
            ]
        })

        fig2 = px.pie(
            issue_chart,
            names="Issue",
            values="Count"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

# ---------------------------------------------------
# CRAWL RESULTS
# ---------------------------------------------------

elif selected == "Crawl Results":

    st.subheader("🌐 Crawl Results")

    search = st.text_input(
        "Search URL"
    )

    filtered_df = df

    if search:

        filtered_df = df[
            df["URL"].str.contains(
                search,
                case=False
            )
        ]

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=700
    )

# ---------------------------------------------------
# SEO ISSUES
# ---------------------------------------------------

elif selected == "SEO Issues":

    st.subheader("⚠ SEO Issues")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([

        "Titles",
        "Meta",
        "H1",
        "Images",
        "Content"
    ])

    # TITLES

    with tab1:

        st.write("### Bad Title Length")

        st.dataframe(

            df[
                df["Title Audit"]
                == "Bad"
            ][[
                "URL",
                "Title",
                "Title Length"
            ]],

            use_container_width=True
        )

        st.write("### Duplicate Titles")

        st.dataframe(

            df[
                df["Duplicate Title"]
                == True
            ][[
                "URL",
                "Title"
            ]],

            use_container_width=True
        )

    # META

    with tab2:

        st.write(
            "### Bad Meta Descriptions"
        )

        st.dataframe(

            df[
                df["Meta Audit"]
                == "Bad"
            ][[
                "URL",
                "Meta Description",
                "Meta Length"
            ]],

            use_container_width=True
        )

        st.write(
            "### Duplicate Meta"
        )

        st.dataframe(

            df[
                df["Duplicate Meta"]
                == True
            ][[
                "URL",
                "Meta Description"
            ]],

            use_container_width=True
        )

    # H1

    with tab3:

        st.write("### Missing H1")

        st.dataframe(

            df[
                df["H1"] == "Missing"
            ][[
                "URL",
                "H1"
            ]],

            use_container_width=True
        )

        st.write("### Multiple H1")

        st.dataframe(

            df[
                df["H1"] == "Multiple H1"
            ][[
                "URL",
                "H1"
            ]],

            use_container_width=True
        )

    # IMAGES

    with tab4:

        st.write(
            "### Missing Alt Text"
        )

        st.dataframe(

            df[
                df["Alt Audit"]
                == "Missing Alt"
            ][[
                "URL",
                "Missing Alt"
            ]],

            use_container_width=True
        )

    # CONTENT

    with tab5:

        st.write(
            "### Thin Content"
        )

        st.dataframe(

            df[
                df["Word Audit"]
                == "Thin Content"
            ][[
                "URL",
                "Word Count"
            ]],

            use_container_width=True
        )

# ---------------------------------------------------
# REPORTS
# ---------------------------------------------------

elif selected == "Reports":

    st.subheader("📁 Export Reports")

    excel_file = "sitepilot_report.xlsx"

    with pd.ExcelWriter(
        excel_file,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="All URLs",
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

# ---------------------------------------------------
# SETTINGS
# ---------------------------------------------------

elif selected == "Settings":

    st.subheader("⚙ Settings")

    st.slider(
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
        "Respect robots.txt"
    )

    st.checkbox(
        "Enable JavaScript Rendering"
    )

    st.info(
        "Advanced features coming soon."
    )