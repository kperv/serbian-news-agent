import streamlit as st
from src.parse_news import prepare_article
from src.news_analysis import init_model, analyze_article
from src.context_agent import search_entities_sync

st.set_page_config(page_title="Serbian News Guide", page_icon="🇷🇸", layout="wide")

st.title("🇷🇸 Serbian News Helper")
st.write("Fetch latest news and generate language study notes.")


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "entity_context" not in st.session_state:
    st.session_state.entity_context = None


# 2. Now your functions and UI will work safely
def reset_article_state():
    st.session_state.analysis_result = None
    st.session_state.entity_context = None


with st.sidebar:
    st.header("Controls")
    if st.button("Fetch & Analyze Latest News", type="primary"):
        reset_article_state()
        with st.spinner("Scraping and Analyzing..."):
            try:
                # Scrape
                article_info = prepare_article()
                if not article_info:
                    st.error("No article found.")
                else:
                    # Analyze
                    model = init_model()
                    analysis = analyze_article(model, article_info["text"])

                    # SAVE TO STATE (This prevents the white screen on rerun)
                    st.session_state.analysis_result = {
                        "title": article_info["title"],
                        "url": article_info["url"],
                        "text": article_info["text"],
                        "summary": analysis.summary,
                        "entities": analysis.entities,
                        "vocab": analysis.study_lemmas,
                    }
            except Exception as e:
                st.error(f"Analysis failed: {e}")

    if st.button("Clear Results"):
        st.session_state.analysis_result = None
        st.rerun()

if st.session_state.analysis_result:
    res = st.session_state.analysis_result

    st.header(res["title"])
    st.caption(f"Source: {res['url']}")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Summary (Russian)")
        st.info(res["summary"])

        with st.expander("Show Original Serbian Text"):
            st.write(res["text"])

        st.subheader("📚 Study Lemmas")
        # Display as a bulleted list for readability
        for word in res["vocab"]:
            st.markdown(f"- {word}")

    with col2:
        st.subheader("🔍 Key Entities")
        # Displaying as pretty badges
        st.write(" ".join([f"`{e}`" for e in res["entities"]]))

        st.divider()
        st.subheader("🕵️ Entity Deep Dive")

        # Check if we already have context for these entities
        if "entity_context" not in st.session_state:
            st.session_state.entity_context = None

        if st.button("Research These Entities", icon="🌐"):
            with st.spinner("Searching Wikipedia & Web..."):
                # Call your new async logic through the sync wrapper
                context_map = search_entities_sync(res["entities"])
                st.session_state.entity_context = context_map
                st.rerun()

        if st.session_state.entity_context:
            # Display the descriptions nicely in a grid or list
            for entity, desc in st.session_state.entity_context.items():
                with st.container(border=True):
                    st.markdown(f"**{entity}**")
                    st.write(desc)


else:
    st.info("Click the button in the sidebar to fetch today's news.")
