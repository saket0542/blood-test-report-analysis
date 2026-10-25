import hashlib
import pandas as pd
import streamlit as st
from parser import extract_text, parse_results, fallback_text
from llm import analyze

st.set_page_config(page_title="Health Analysis", page_icon="🩺")
st.title("🩺 Blood Test Health Analysis")
st.caption("Upload a text-based blood test PDF to get a summary and an Indian diet plan.")

diet = st.sidebar.radio("Diet preference", ["Vegetarian", "Non-vegetarian", "Eggetarian", "Vegan"])
file = st.file_uploader("Blood test report (PDF)", type="pdf")


@st.cache_data(show_spinner=False)
def run(payload: str, diet: str):
    return analyze(payload, diet)


if file and st.button("Analyze", type="primary"):
    try:
        text = extract_text(file.getvalue())
    except Exception as e:
        st.error(f"Could not read PDF: {e}")
        st.stop()
    if not text.strip():
        st.error("No text found. This looks like a scanned PDF, which isn't supported.")
        st.stop()

    rows = parse_results(text)
    abnormal = [r for r in rows if r["status"] != "Normal"]
    normal = [r["test"] for r in rows if r["status"] == "Normal"]

    if len(rows) >= 3:
        payload = "Abnormal:\n" + (
            "\n".join(f"{r['test']}: {r['value']} {r['unit']} ({r['status']}, ref {r['range']})" for r in abnormal)
            or "none"
        ) + "\nNormal tests: " + ", ".join(normal)
    else:
        payload = "Report excerpt:\n" + fallback_text(text)

    with st.expander(f"Parsed {len(rows)} results, {len(abnormal)} abnormal"):
        if rows:
            st.dataframe(pd.DataFrame(rows), width="stretch")

    try:
        with st.spinner("Analyzing..."):
            result, usage = run(payload, diet)
    except Exception as e:
        st.error(f"LLM error: {e}")
        st.stop()

    st.subheader("Summary")
    st.write(result.get("summary", ""))
    if result.get("abnormal"):
        st.subheader("Abnormal findings")
        st.table(pd.DataFrame(result["abnormal"]))
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("✅ Eat")
        for i in result.get("eat", []):
            st.markdown(f"- **{i['food']}**: {i['why']}")
    with c2:
        st.subheader("❌ Avoid")
        for i in result.get("avoid", []):
            st.markdown(f"- **{i['food']}**: {i['why']}")
    if result.get("tips"):
        st.subheader("Lifestyle tips")
        for t in result["tips"]:
            st.markdown(f"- {t}")
    st.caption(f"Tokens: {usage['prompt']} in / {usage['completion']} out")
    st.info("General guidance only, not medical advice. Consult a doctor.")
