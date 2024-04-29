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

def extract_text(html_content):
    """
    extracts text from html contents of a webpage
    @param html_content: full html code
    @return text: all natural text found in html from text snippets, paragraphs, headers, etc
    """
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text(separator=' ', strip=True)
    return text


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
    json_format = cfg['json_format']
    prompt = cfg['prompt_2']
    json_schema = cfg['json_schema']

    password = st.text_input("Enter Password:", type="password")

    if password == correct_password:

        st.title("Coworker Search App")
        option = sidebar()
        
        if option == "Upload PDF Resume":
            st.write("PDF Upload version not yet available")
            # uploaded_file = st.file_uploader("Upload PDF", type="pdf")
            # if uploaded_file is not None:
                # text = extract_text_from_pdf(uploaded_file)
                # st.write("Text extracted from PDF:")
                # st.write(text)

        elif option == "Paste Plain Text Resume":
            st.write("Paste Plain Text Resume version not yet available")
            # text_input = st.text_area("Paste plain text here:")
            # if st.button("Search"):
                # st.write("Text extracted from input:")
                # st.write(text_input)
        
        else:
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First name:")
            with col2:
                last_name = st.text_input("Last name:")
            num_option = st.selectbox("Number of input positions (job title/company):",
                                  ("",
                                   "Input One Position", 
                                   "Input Several Positions"))
            if num_option == "Input One Position":
                results = input_fields_single()
                system_message = cfg['single_position_system_message']
                # st.write(results)
                if st.button("Search", key=1):
                    if not results['workplace']:
                        st.warning("Please fill in all the required fields.")
                    else:
                        queries = build_queries(first_name, last_name, [results])
                        # st.write(queries)
                        google_results = make_requests(queries)
                        # st.write(google_results)
                        job_info = first_name + last_name + str(results)
                        input_prompt = build_prompt(prompt,
                                                    google_results,
                                                    first_name,
                                                    last_name,
                                                    json_format,
                                                    json_schema,
                                                    job_info)
                        # st.write(input_prompt)
                        # query chatgpt
                        with st.spinner(f"Querying GPT4 with information found on {first_name} {last_name}..."):
                            answers = query_openai(input_prompt, system_message, 10, True)
                            # display chatgpt response
                        st.markdown(f"#### {first_name} {last_name}'s Possible Coworkers:")
                        st.write(json.loads(answers.replace("'", '')))
                        st.markdown("---")
                        # st.markdown(f"#### Relevant Links for {first_name} {last_name}:")
                        # display person of interest links
                        # if the_org:
                        #     st.write(the_org)
                        # if signal_hire:
                        #     st.write(signal_hire)

            elif num_option == "Input Several Positions":
                results = input_fields_multiple()
                system_message = cfg['multiple_position_system_message']
                # st.write(results)
                if st.button("Search", key=3):
                    if not results[0]['workplace']:
                        st.warning("Please fill in all the required fields.")
                    else:
                        queries = build_queries(first_name, last_name, results)
                        # st.write(queries)
                        google_results = make_requests(queries)
                        # st.write(google_results)
                        job_info = first_name + last_name + str(results)
                        input_prompt = build_prompt(prompt,
                                                    google_results,
                                                    first_name,
                                                    last_name,
                                                    json_format,
                                                    json_schema,
                                                    job_info)
                        # st.write(input_prompt)
                        # query chatgpt
                        with st.spinner(f"Querying GPT4 with information found on {first_name} {last_name}..."):
                            answers = query_openai(input_prompt, system_message, 10, True)
                        # display chatgpt response
                        st.markdown(f"#### {first_name} {last_name}'s Possible Coworkers:")
                        st.write(json.loads(answers.replace("'", '')))
                        st.markdown("---")

    else:
        st.error("Incorrect password. Access denied.")

if __name__ == "__main__":
    main()