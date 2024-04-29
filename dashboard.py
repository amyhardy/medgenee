import streamlit as st
import time
import json
import requests

def query_openai(prompt, system_message, wait_time=60, prints_on=True):
    # Stub function for querying OpenAI; replace with your own API setup
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": f"Bearer YOUR_OPENAI_API_KEY",
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "model": "gpt-4-0125-preview",
        "prompt": prompt,
        "max_tokens": 150,
    })
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"]
    else:
        if prints_on:
            st.write(f'Error: {response.text}')
        time.sleep(wait_time)
        return None

# Streamlit dashboard setup
st.title('Medgenee: Gene Discovery Dashboard')

# User input for disease or topic
query_input = st.text_input("Enter a disease or topic to discover related genes:", "")

# Button to trigger the analysis
if st.button('Discover Genes'):
    if query_input:
        system_message = "Extract genes from biomedical literature related to specific diseases."
        prompt = f"Identify all gene names mentioned in this abstract related to {query_input} and summarize their roles."

        # Querying ChatGPT for gene discovery
        results = query_openai(prompt, system_message)

        # Display results
        if results:
            st.subheader("Gene Discovery Results:")
            st.write(results)
        else:
            st.error("Failed to retrieve results. Please try again.")
    else:
        st.error("Please enter a valid disease or topic.")

# Example of displaying visualization (Placeholder)
st.subheader("Gene Mention Frequency (Example Visualization)")
st.image("https://via.placeholder.com/500x300", caption="Frequency of gene mentions across studies.")

# Downloadable report (Placeholder)
if st.button('Download Report'):
    st.write("Download link would appear here.")

# Feedback mechanism
feedback = st.text_area("Feedback on the information provided:")
if st.button('Submit Feedback'):
    st.success("Thank you for your feedback!")
