import streamlit as st
import openai
import os
import time
import requests
from bs4 import BeautifulSoup
import yaml  # type: ignore
import json

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
                st.write(f'Received error from OpenAI: {e}. Pausing for {wait_time}s.')
                if "context_length_exceeded" in str(e):
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
        json_format_opt = True
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
            pulling relevant abstracts from scientific research articles in real time and using LLMs to \
            extract important gene information from them.")
    
    st.sidebar.write("Please enter a topic of interest.")
    st.sidebar.write("Examples include 'alzheimer's disease', \
                     'sickle cell disease', 'cystic fibrosis', etc.")
    
    st.title('MedGenee')

    st.markdown("---")

    with open('config.yaml') as f:
        cfg = yaml.safe_load(f)
    json_format = cfg['json_format']
    none_return = cfg['none_return']
    topic = st.text_input("Disease, disorder, or topic here:")
    input_prompt = f"Analyze the above scientific research paper abstract. Please return the output in the following JSON format: {json_format}"
    input_prompt += f"If no genes are found in the abstracts, return {none_return}"
    system_message = "You are a bioinformatics expert."
    st.write(1)
    if st.button("Start Gene Analysis"):
        with st.spinner(f"Generating Gene Analysis on {topic}..."):
            format_topic = topic.lower().replace("'", '%27').replace(' ', '+')
            url = f"https://pubmed.ncbi.nlm.nih.gov/?term={format_topic}%5BTitle%2FAbstract%5D+gene%5BTitle%2FAbstract%5D&filter=dates.2023%2F1%2F1-3000%2F12%2F12"
            # url = f"https://pubmed.ncbi.nlm.nih.gov/?term={format_topic}%5BTitle%2FAbstract%5D&filter=dates.2023%2F1%2F1-3000%2F12%2F12"
            response = requests.get(url, headers=HEADERS)
            st.write(2)
            if response.status_code == 200:
                st.write(3)
                soup = BeautifulSoup(response.text, "html.parser")
                # Find the label with class 'of-total-pages' and extract its text
                pages = soup.find("label", class_="of-total-pages")
                st.write(4)
                if pages:
                    st.write(5)
                    # extract the text and split it to get the number of pages
                    total_pages_text = pages.get_text()
                    total_pages = total_pages_text.split()[-1].replace(",", "")  # Extracting the number and removing comma
                    total_pages = 2
                    st.write(6)
                    st.write("Total number of pages:", total_pages)
                    progress_bar = st.progress(0, "Gathering abstracts...")
                    max_pages = 10
                    st.write(7)
                    num_pages = min(max_pages, total_pages)
                    for i in range(1, num_pages):
                        page_url = url + f"&page={i}"
                        response = requests.get(page_url, headers=HEADERS)
                        if response.status_code == 200:
                            # html_document = response.text
                            soup_page = BeautifulSoup(response.text, "html.parser")
                            links = soup_page.find_all("a", class_="docsum-title")
                            link_urls = [link['href'] for link in links]
                            link_abstracts = []
                            for link in link_urls:
                                url = f'https://pubmed.ncbi.nlm.nih.gov/{link}'
                                res = requests.get(url, headers=HEADERS)
                                if response.status_code == 200:
                                    html_text = res.text
                                    link_soup = BeautifulSoup(html_text, 'html.parser')
                                    abstract = link_soup.find("div", class_="abstract-content selected")
                                    if abstract:
                                        abstract_text = abstract.get_text(separator=' ', strip=True)
                                        link_abstracts.append((link, abstract_text))
                                else:
                                    continue
                        else:
                            continue  
                        # Update the progress bar
                        progress_bar.progress(i / total_pages, "Gathering abstracts...")                 
                    st.write(f"Found {len(link_abstracts)} abstracts about {topic}.")
                    jsons = []
                    for abstract in link_abstracts:
                        answers = query_openai(input_prompt, system_message, 10, True)
                        genes = json.loads(answers)
                        if 'genes' in genes:
                            jsons.append({'genes': genes,
                                          'abstract': abstract[1]})
                        # jsons.append(answers)
                    st.write(jsons)

                else:
                    st.write("Num pages not found. Check if the page structure has changed or your query didn't return results.")
            else:
                st.write("Page cannot be found.")
if __name__ == "__main__":
    main()
