import streamlit as st
import openai
import os
import time
import requests
from bs4 import BeautifulSoup

openai.api_key = os.environ.get('OPENAI_API_KEY')


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def query_openai(prompt, system_message, wait_time, prints_on):
    """
    hits OPENAI API to generate sample, waits in case of error,
    calls sample_generator.generate to get one response
    @param prompt: prompt to pass to the model
    @param sample_generator: generator class
    @param wait_time: time to wait in the event of an API request error
    @param prints_on: whether or not to print outputs
    @returns: text output from the model
    """
    # generate chatgpt response, keep trying if error received
    while True:
        try:
            return generate(prompt, system_message)
        except Exception as e:
            if prints_on:
                print(f'Received error from OpenAI: {e}. Pausing for {wait_time}s.')
                st.write(f'Received error from OpenAI: {e}. Pausing for {wait_time}s.')
                if "context_length_exceeded" in str(e):
                    print('ChatGPT context window exceeded, skipping this sample')
                    st.write('ChatGPT context window exceeded, skipping this sample')
                    return None
            time.sleep(wait_time)

def generate(prompt, system_message):
        """
        Generates sample based on set of GPT related parameters
        @param prompt: input prompt used
        @param system_message: chatgpt system message
        @returns: GPT output
        """
        json_format_opt = False
        model_str = 'gpt-4-0125-preview'
        temperature = 1.0
        max_tokens = 1500
        top_p = 1.0
        frequency_penalty = 0
        presence_penalty = 0

        if json_format_opt:
            response_format = {"type": "json_object"}
        else:
            response_format = None

        if model_str != 'text-davinci-003':
            sample = openai.chat.completions.create(
                response_format=response_format,
                model=model_str,
                messages=[
                    {'role': "system", 'content': system_message},
                    {'role': "user", 'content': prompt}
                ],
                temperature=temperature,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            return sample.choices[0].message.content

        else:
            sample = openai.completions.create(
                model=model_str,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            return sample.choices[0].text

def extract_text(html_content):
    """
    extracts text from html contents of a webpage
    @param html_content: full html code
    @return text: all natural text found in html from text snippets, paragraphs, headers, etc
    """
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text(separator=' ', strip=True)
    return text

def main():

    st.sidebar.subheader("MedGenee: A GPT-4 Powered Gene Analysis App")
    st.sidebar.markdown('---')
    st.sidebar.write("MedGenee allows users to jumpstart their gene analysis exploration journey by \
            pulling relevant abstracts from scientific research articles and using LLMs to \
            extract important gene information from them.")
    st.sidebar.write("Please enter a topic of interest. Examples include 'alzheimer's disease', \
            'sickle cell disease', 'cystic fibrosis', etc.")
    
    st.title('MedGenee')

    st.markdown("---")
    topic = st.text_input("Disease, disorder, or topic here:")
    input_prompt = "Hi, how are you?"
    system_message = "You are nice."

    format_topic = topic.lower().replace("'", '%27').replace(' ', '+')
    url = "https://pubmed.ncbi.nlm.nih.gov/?term={format_topic}%5BTitle%2FAbstract%5D&filter=dates.2023%2F1%2F1-3000%2F12%2F12"
    response = requests.get(url, headers=HEADERS)
    # plain_text = extract_text(response.text)
    # st.write(plain_text)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the label with class 'of-total-pages' and extract its text
    label = soup.find("label", class_="of-total-pages")
    if label:
        # Extract the text and split it to get the number of pages
        total_pages_text = label.get_text()
        total_pages = total_pages_text.split()[-1].replace(",", "")  # Extracting the number and removing comma
        st.write("Total number of pages:", total_pages)
    else:
        st.write("Label not found. Check if the page structure has changed or your query didn't return results.")


    if st.button("Start Gene Analysis"):
        with st.spinner(f"Generating Gene Analysis on {topic}..."):
            answers = query_openai(input_prompt, system_message, 10, True)

if __name__ == "__main__":
    main()
