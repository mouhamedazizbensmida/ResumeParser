

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re

# Functions
def fetch_job_cards():
    job_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'jobs-search__results-list')))
    return job_list.find_elements(By.TAG_NAME, 'li')

def go_to_next_page():
    try:
        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Next")]')))
        next_button.click()
        return True
    except (NoSuchElementException, TimeoutException):
        return False

def scroll_down(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        try:
            show_more_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Voir plus offres d’emploi")]')
            if show_more_button.is_displayed():
                show_more_button.click()
                time.sleep(3)
                continue
        except NoSuchElementException:
            pass
        
        try:
            bottom_message = driver.find_element(By.XPATH, '//p[contains(text(), "Vous avez vu toutes les offres d’emploi de cette recherche")]')
            if bottom_message.is_displayed():
                print("Reached the bottom of the page.")
                break
        except NoSuchElementException:
            pass
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_element_text(element, class_names):
    if not isinstance(class_names, list):
        class_names = [class_names]

    for class_name in class_names:
        try:
            return element.find_element(By.CLASS_NAME, class_name).text.strip()
        except NoSuchElementException:
            continue

    return None

def extract_job_criteria():
    criteria_texts = None
    for _ in range(5):
        try:
            criteria_list = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.description__job-criteria-list')))
            criteria_items = criteria_list.find_elements(By.CSS_SELECTOR, 'li .description__job-criteria-text--criteria')
            criteria_texts = [item.text.strip() for item in criteria_items if item.text.strip() != '']
            if criteria_texts:
                break
        except TimeoutException:
            pass
    return criteria_texts

def extract_job_description():
    job_description_text = None
    for _ in range(3):
        try:
            job_description_section = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.show-more-less-html__markup')))
            job_description_html = job_description_section.get_attribute('outerHTML')
            soup = BeautifulSoup(job_description_html, 'html.parser')
            job_description_text = soup.get_text(separator='\n').strip()
            if job_description_text:
                break
        except TimeoutException:
            pass
    return job_description_text
def scrape_page():
    try:
        job_cards = fetch_job_cards()
        num_cards = len(job_cards)
        print(f"Number of job cards found: {num_cards}")

        for idx in range(num_cards):
            print(f"Scraping job {idx + 1} of {num_cards}")
            try:
                scrape_job_card(idx, job_cards)
            except StaleElementReferenceException:
                print("Stale element reference exception occurred. Retrying...")
                continue

    except Exception as e:
        print(f"An error occurred while scraping the page: {str(e)}")

def fetch_job_cards():
    job_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'jobs-search__results-list')))
    return job_list.find_elements(By.TAG_NAME, 'li')

def extract_element_text(element, class_names):
    if not isinstance(class_names, list):
        class_names = [class_names]

    for class_name in class_names:
        try:
            return element.find_element(By.CLASS_NAME, class_name).text.strip()
        except NoSuchElementException:
            continue

    return None

def navigate_and_retry(idx, job_cards):
    if idx != 0:
        prev = idx - 1
    else:
        prev = idx + 1

    while True:
        print("Job criteria not found, reloading details pane and continuing...")

        job_cards = fetch_job_cards()
        job_cards[prev].click()
        time.sleep(3)

        job_cards = fetch_job_cards()
        card = job_cards[idx]
        card.click()
        time.sleep(3)
        criteria_texts = extract_job_criteria()
        if criteria_texts:
            return criteria_texts

def check_url(base_url):
    return driver.current_url == base_url

def scrape_job_card(idx, job_cards):
    card = job_cards[idx]

    company_name = extract_element_text(card, 'base-search-card__subtitle')
    company_location = extract_element_text(card, 'job-search-card__location')
    company_title = extract_element_text(card, 'base-search-card__title')
    company_logo_link = card.find_element(By.CSS_SELECTOR, '.base-search-card__subtitle a').get_attribute('href') if card.find_elements(By.CSS_SELECTOR, '.base-search-card__info a') else None
    company_time_posted = extract_element_text(card, ["job-search-card__listdate--new", "job-search-card__listdate"])

    if not all([company_name, company_location, company_title, company_time_posted]):
        print(f"Missing critical information for job card {idx + 1}. Skipping...")
        return

    card.click()
    time.sleep(3)

    criteria_texts = extract_job_criteria()
    if not criteria_texts:
        criteria_texts = navigate_and_retry(idx, job_cards)

    job_description_text = extract_job_description()

    offre_details_link = None
    try:
        profile_link_element = driver.find_element(By.CSS_SELECTOR, 'a.topcard__link[data-tracking-control-name="public_jobs_topcard-title"]')
        offre_details_link = profile_link_element.get_attribute('href') if profile_link_element else None
    except NoSuchElementException:
        print(f"Profile link not found for job card {idx + 1}")

    if start_button_Profondeur :
        st.write("youor job should be  here")
    table.append({
        'Company Name': company_name,
        'Location': company_location,
        'Job Title': company_title,
        'Date Posted': datetime.now().strftime("%Y-%m-%d"),
        'Posted Time': company_time_posted,
        'Link To Profile': company_logo_link,
        'Offre_details_link': offre_details_link,
        'Job Criteria': criteria_texts,
        'Job Description': job_description_text
    })
    print(f"Scraped job details for {company_name, company_logo_link, offre_details_link}")

def construct_url(base_url, position, driver):
    current_job_id = None
    if 'currentJobId=' in driver.current_url:
        current_job_id = re.search(r'currentJobId=(\d+)', driver.current_url).group(1)
    return base_url.format(position, current_job_id)

def load_page(url):
    driver.get(url)
    time.sleep(5)

def process_pages(base_url):
    position = 0
    try:
        while True:
            url = construct_url(base_url, position, driver)
            load_page(url)
            while not check_url(base_url):
                url = construct_url(base_url, position, driver)
                load_page(url)
                time.sleep(5)

            scroll_down(driver)
            scrape_page()
            if not go_to_next_page():
                break
            position += 1
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        driver.quit()


def Search_Profondeur(table):
    st.write(table)
# Streamlit UI
st.title("LinkedIn Job Scraper")
base_url = st.text_input("Enter the base URL", "Put the LinkedIn URL to extract the jobs")
start_button_Simple = st.button("Start Scraping Simple")
start_button_Profondeur = st.button("Start Scraping En Profondeur")
@st.cache_data
def convert_df(data):
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

if start_button_Simple or start_button_Profondeur:
    service = Service(r'C:\\Users\\Azizb\\Desktop\\Softwares\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    table = []
    process_pages(base_url)

    # Convert DataFrame to CSV
    csv = convert_df(table)
    
    # Instructions for the user
    st.write("""
    After clicking the download button, your browser will prompt you to save the file. 
    If you want to choose the location where the file should be saved, make sure your browser is configured to ask you where to save each file before downloading. 
    Here's how you can do it for popular browsers:
    - **Chrome:** Go to Settings > Advanced > Downloads, and turn on "Ask where to save each file before downloading".
    - **Firefox:** Go to Options > General, and under "Files and Applications", select "Always ask you where to save files".
    - **Edge:** Go to Settings > Downloads, and turn on "Ask me what to do with each download".
    """)

    # Download button with dynamic file name
    st.download_button(
        label="Press to Download",
        data=csv,
        file_name=f"file_name.csv",
        mime="text/csv",
        key='download-csv'
    )
if start_button_Profondeur:
    Search_Profondeur("Yoo Hello")

###################################################################################################
Resume Parser
#import streamlit as st
# import google.generativeai as genai
# import os
# import PyPDF2 as pdf
# from dotenv import load_dotenv
# import json

# load_dotenv()  # Load all our environment variables

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def get_gemini_response(input):
#     model = genai.GenerativeModel('gemini-pro')
#     response = model.generate_content(input)
    
#     # Parse the JSON from the response
#     parsed_response = json.loads(response.candidates[0]
#                                  .content.parts[0].text)
#     return parsed_response
    

# def input_pdf_text(uploaded_file):
#     reader = pdf.PdfReader(uploaded_file)
#     text = ""
#     for page in range(len(reader.pages)):
#         page = reader.pages[page]
#         text += str(page.extract_text())
#     return text

# # Prompt Template
# input_prompt_template = """
#   You are an AI bot designed to act as a professional for parsing resumes. You are given a resume, and your job is to extract the following information from the resume:
#   . langues
#   . email
#   . phone numbers
#   . langages de balisage
#   . programming languages
#   . databases
#   . status
#   . technologies
#   . APIs
#   . operating systems
#   . modeling languages
#   . methodologies
#   . design patterns
#   . architectures
#   . outils
#   . sexe: ["Male", "Female", "Other"]
#   . university
#   . adresse
#   . ans d'expérience
#   if an attribute hasn't information a null value is affected to this attribute
# resume: {text}
# I want the response in one single string with the structure:
# {{"langues":"","email":"","phone numbers":"","langages de balisage":"","programming languages":"","databases":"","skills":"","status":"","technologies":"","APIs":"","operating systems":"","modeling languages":"","methodologies":"","design patterns":"","architectures":"","outils":"","sexe":"","university":"","adresse":"","ans d'expérience":""}}
# """

# # Streamlit app
# st.text("Data Scrapping")

# uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

# submit = st.button("Submit")

# if submit:
#     if uploaded_file is not None:
#         with st.spinner('Processing...'):
#             text = input_pdf_text(uploaded_file)
#             input_prompt = input_prompt_template.format(text=text)
#             try:
#                 response = get_gemini_response(input_prompt)
#                 st.subheader("Parsed Resume Data")
#                 st.json(response)  # Display the parsed data as JSON
#             except Exception as e:
#                 st.error(f"An error occurred: {e}")
#     else:
#         st.warning("Please upload a resume before submitting.")

###########################################################################################



# import os
# import google.generativeai as genai
# import streamlit as st
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configure GenerativeAI API
# API_KEY = os.getenv('GEMINI_API_KEY')
# genai.configure(api_key=API_KEY)

# # Initialize GenerativeModel
# model = genai.GenerativeModel('gemini-pro') 
# chat = model.start_chat(history=[])

# # Instruction text (not shown in Streamlit)
# instruction = (
#     "ask the question from this resume: {text}"
# )

# # Streamlit app
# def main():
#     st.title('Preliminary School Chatbot')

#     # Display user input widget
#     question = st.text_input("You:")

#     if question.strip():
#         # Send message to GenerativeAI model
#         response = chat.send_message(instruction + question)

#         # Display response
#         st.text_area("Bot:", value=response.text, height=150)

# if __name__ == "__main__":
#     main()
