import streamlit as st
import PyPDF2
import requests
from bs4 import BeautifulSoup
import time
import yaml  # type: ignore
import openai
import json
import re
import random 
import string

# TODO: inquire about Signal Hire API
# TODO: alternative: query signal hires site -- fix signalhire employees page bug
# TODO: add functionality for pdf resume, extracting name work place from it?
# TODO: potentially add chatgpt query to infer job titles close to POI's job title

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
                # max_tokens=max_tokens,
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

def extract_text_from_pdf(uploaded_file):
    """
    extracts text from uploaded PDF version of resume
    @param uploaded_file: PDF uploaded to streamlit dashboard
    @return text: extracted text
    """
    text = ""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    num_pages = len(pdf_reader.pages)
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num] 
        text += page.extract_text()  
    return text

def extract_text(html_content):
    """
    extracts text from html contents of a webpage
    @param html_content: full html code
    @return text: all natural text found in html from text snippets, paragraphs, headers, etc
    """
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text(separator=' ', strip=True)
    return text

def query_name_workplace(query):
    """
    """
    output = ""
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        plain_text = extract_text(response.text)
        output += "RESULTS FROM GOOGLING NAME AND WORKPLACE:\n"
        output += plain_text
    return output

def query_name_workplace(query):
    """
    """
    output = ""
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        plain_text = extract_text(response.text)
        output += "RESULTS FROM GOOGLING NAME AND WORKPLACE:\n"
        output += plain_text
    return output

def sidebar():
    """
    """
    # option for input
    option = st.sidebar.selectbox(
        "Choose input method:",
        ("Input Info Manually", 
            "Upload PDF Resume", 
            "Paste Plain Text Resume")
            )
    # sidebar information
    st.sidebar.markdown("## README")
    st.sidebar.markdown("---")
    st.sidebar.write("- Current input formats supported: 'Input Info Manually ONLY'")
    st.sidebar.markdown("---")
    st.sidebar.write("- This version of the prototype uses Google queries based on first name, last name, current place of work, and current job title to gather information on the person of interest.")
    st.sidebar.write("- It also requests information from theOrg.com by attempting to find the relevant profile with the given information.")
    st.sidebar.write("- It takes the gathered information and uses it as input to ChatGPT to extract possible coworkers from the text.")
    
    return option

def input_fields_multiple():
    """
    """
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        workplace_a = st.text_input("Company:", key='1a')
    with col2:
        job_title_a = st.text_input("Job title:", key='2a')
    with col3:
        start_year_a = st.text_input("Start year:", key='3a')
    with col4:
        end_year_a = st.text_input("End year:", key='4a')
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        workplace_b = st.text_input("Company: (optional)", key='1b')
    with col2:
        job_title_b = st.text_input("Job title: (optional)", key='2b')
    with col3:
        start_year_b = st.text_input("Start year: (optional)", key='3b')
    with col4:
        end_year_b = st.text_input("End year: (optional)", key='4b')
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        workplace_c = st.text_input("Company: (optional)", key='1c')
    with col2:
        job_title_c = st.text_input("Job title: (optional)", key='2c')
    with col3:
        start_year_c = st.text_input("Start year: (optional)", key='3c')
    with col4:
        end_year_c = st.text_input("End year: (optional)", key='4c')
    
    return [{'workplace': workplace_a,
                           'job_title': job_title_a,
                           'start_year': start_year_a,
                           'end_year': end_year_a},
            {'workplace': workplace_b,
                           'job_title': job_title_b,
                           'start_year': start_year_b,
                           'end_year': end_year_b},
            {'workplace': workplace_c,
                           'job_title': job_title_c,
                           'start_year': start_year_c,
                           'end_year': end_year_c}]

def input_fields_single():
    """
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        workplace = st.text_input("Company:", key='1a')
    with col2:
        job_title = st.text_input("Job title:", key='2a')
    with col3:
        start_year = st.text_input("Start year:", key='3a')
    with col4:
        end_year = st.text_input("End year:", key='4a')
    
    return {'workplace': workplace,
            'job_title': job_title,
            'start_year': start_year,
            'end_year': end_year}

def build_queries(first_name, last_name, results):
    """
    """
    urls = []
    for pos in results:
        workplace = pos['workplace']
        job_title = pos['job_title']

        query_1 = f'"{first_name} {last_name}"+{workplace}"'
        url_1 = f"https://www.google.com/search?q={query_1}"

        query_2 = f'"{first_name} {last_name}"+"{workplace}"+{job_title}+Linkedin'
        url_2 = f"https://www.google.com/search?q={query_2.replace(' ', '+')}"

        if len(workplace.split()) > 1:
            workplace = workplace.replace(" ", "-")

        url_3 = f"https://theorg.com/org/{workplace.lower()}/org-chart/{first_name.lower()}-{last_name.lower()}"
        url_4 = f"https://www.signalhire.com/companies/{workplace.lower()}/employees"

        urls.append(url_1)
        urls.append(url_2)
        urls.append(url_3)
        urls.append(url_4)

    return urls

def make_requests(queries):
    """
    """
    google_results = ""
    for url in queries:
        if 'signalhire' in url:
            sig_headers  = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                }

            response = requests.get(url, headers=sig_headers)

        else:
            response = requests.get(url, headers=HEADERS)
        print('response.status_code', response.status_code)
        if response.status_code == 200:
            # extract text from html
            plain_text = extract_text(response.text)
            # add extracted text to google results
            google_results += f"RESULTS FROM {url}:\n"
            google_results += plain_text
    return google_results

def build_prompt(prompt, google_results, first_name, last_name,
                 json_format, json_schema, job_info):
    """
    """
    prompt = prompt.format(google_results=google_results,
                           first_name=first_name,
                           last_name=last_name,
                           json_format=json_format,
                           json_schema=json_schema,
                           job_info=job_info)
    return prompt


def main():

    with open('config.yaml') as f:
        cfg = yaml.safe_load(f)
    # system_message = cfg['system_message_option_2']
    # json_format = cfg['json_format']
    # prompt = cfg['prompt_2']
    # json_schema = cfg['json_schema']
    
    st.title("MedGenee")

if __name__ == "__main__":
    main()