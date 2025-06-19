import streamlit as st
import openai
import pandas as pd
import json
from io import StringIO

# OpenAI API Key
openai.api_key = "YOUR_API_KEY"

st.set_page_config(page_title="Web Content Extractor", layout="centered")
st.title("🧠 Web Content to Table (AI Extractor)")

# Input text area
raw_text = st.text_area("Paste the unstructured webpage content here:", height=300)

# Desired output format
output_format = st.selectbox("Select download format:", ["CSV", "JSON"])

if st.button("Extract Information"):
    if not raw_text.strip():
        st.warning("Please paste some content.")
    else:
        with st.spinner("Extracting data using GPT..."):
            prompt = f"""
            Extract all structured information from the following text and return it as a JSON array of objects (list of dictionaries).
            Try to identify fields like title, product, price, date, brand, color, model, etc.

            Example input:
            \"\"\"{raw_text}\"\"\"
            """

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                content = response.choices[0].message["content"]

                # Try parsing the response to JSON
                json_data = json.loads(content)
                df = pd.DataFrame(json_data)

                st.success("Data extracted successfully!")
                st.dataframe(df)

                if output_format == "CSV":
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="extracted_data.csv",
                        mime="text/csv"
                    )
                else:
                    json_output = df.to_json(orient="records", indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_output,
                        file_name="extracted_data.json",
                        mime="application/json"
                    )

            except json.JSONDecodeError:
                st.error("⚠️ OpenAI response was not valid JSON.")
                st.text_area("Raw Output from OpenAI:", value=content, height=200)
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
