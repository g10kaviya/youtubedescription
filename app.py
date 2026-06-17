import streamlit as st
import requests
import re

st.set_page_config(page_title="YouTube Title & Description Generator", page_icon="🎬")

st.title("🎬 YouTube Title & Description Generator")

video_script = st.text_area("Paste your video summary:", height=150)
col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox("Select tone:", ("Professional", "Casual", "Funny", "Inspirational"))
with col2:
    keywords = st.text_input("SEO Keywords (comma-separated):")

HF_TOKEN = st.secrets["HF_TOKEN"]
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

def generate_metadata(script, tone, keywords):
    prompt = f"""
You are a YouTube SEO expert. Generate:
1. One CATCHY title (under 60 characters)
2. SEO-optimized description (3 engaging paragraphs with keywords)

Video content: {script}
Tone: {tone}
Keywords: {keywords}

Format output as:
TITLE: [generated title]
DESCRIPTION: [generated description]
"""
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        st.error(f"API Error {response.status_code}: {response.text}")
        return ""
    result = response.json()
    return result["choices"][0]["message"]["content"]

def parse_output(result):
    title_match = re.search(r'TITLE:\s*["“]?(.*?)["”]?\s*DESCRIPTION:', result, re.DOTALL)
    desc_match = re.search(r'DESCRIPTION:\s*(.*)', result, re.DOTALL)
    title = title_match.group(1).strip() if title_match else "Title not found"
    desc = desc_match.group(1).strip() if desc_match else "Description not found"
    return title, desc

if st.button("Generate Metadata", use_container_width=True):
    if not video_script.strip():
        st.warning("Please enter video content")
    else:
        with st.spinner("Generating content (may take a few seconds)..."):
            result = generate_metadata(video_script, tone, keywords)
            if not result:
                st.stop()
            title, desc = parse_output(result)
            st.balloons()
            st.success("Generated!")
            st.subheader("Title:")
            st.markdown(f"### {title}")
            st.subheader("Description:")
            st.markdown(desc)
            st.download_button("Download as TXT", 
                              f"Title: {title}\n\nDescription:\n{desc}",
                              file_name="youtube_metadata.txt")

with st.sidebar:
    st.markdown("## About This App")
    st.write("Generate catchy YouTube titles and descriptions using AI.")
    st.divider()
    st.markdown("### How to use:")
    st.write("1. Enter video content")
    st.write("2. Select tone")
    st.write("3. Add SEO keywords")
    st.write("4. Click generate")
    st.markdown("---")
