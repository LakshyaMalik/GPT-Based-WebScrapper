import streamlit as st
import pandas as pd
import json
import re
import google.generativeai as genai
from secret import gemini

genai.configure(api_key=gemini)
model = genai.GenerativeModel("gemini-2.0-flash-lite")

st.set_page_config(page_title="Web Content Extractor", layout="centered")
st.title("🧠 Web Content to Table")

raw_text = st.text_area("Paste the unstructured webpage content here:", height=300)
output_format = st.selectbox("Select download format:", ["CSV", "JSON"])

if st.button("Extract Information"):
    if not raw_text.strip():
        st.warning("Please paste some content.")
    else:
        with st.spinner("Extracting using Gemini..."):
            prompt = f"""
            Extract structured data from the following text and return ONLY a valid JSON array as if done by a professional Web Scrapper - data entry work (no explanations or formatting like markdown/code blocks).
            Look for fields like name, product, email, contacts, socials, key features,price, date, brand, model, etc.
            Avoid giving long paras or descriptions. Stay to the point.

            Web Article Content:
            {raw_text}
            """

            try:
                response = model.generate_content(prompt)
                content = response.text.strip()

                # Optional: strip markdown ```json blocks if present
                match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if match:
                    content = match.group(1)
                else:
                    content = re.search(r'(\[.*\])', content, re.DOTALL).group(1)

                json_data = json.loads(content)
                df = pd.DataFrame(json_data)

                st.success("✅ Data extracted successfully!")
                st.dataframe(df)

                if output_format == "CSV":
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download CSV", csv, "data.csv", "text/csv")
                else:
                    json_out = df.to_json(orient="records", indent=2).encode("utf-8")
                    st.download_button("📥 Download JSON", json_out, "data.json", "application/json")

            except json.JSONDecodeError:
                st.error("⚠️ Gemini response was not valid JSON.")
                st.code(content)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
