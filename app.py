import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

load_dotenv()  # Load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    
    # Parse the JSON from the response
    parsed_response = json.loads(response.candidates[0]
                                 .content.parts[0].text)
    return parsed_response
    

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt_template = = """
  You are an AI bot designed to act as a professional for parsing resumes. You are given a resume, and your job is to extract the following information from the resume:
  1. langues
  2. email
  3. phone numbers
  4. langages de balisage
  5. programming languages
  6. databases
  7. skills
  8. status
  9. technologies
  10. APIs
  11. operating systems
  12. modeling languages
  13. methodologies
  14. design patterns
  15. architectures
  16. outils
  17. sexe: ["Male", "Female", "Other"]
  18. university
  19. adresse
  20. ans d'expérience
resume: {text}
I want the response in one single string with the structure:
{{"langues":"","email":"","phone numbers":"","langages de balisage":"","programming languages":"","databases":"","skills":"","status":"","technologies":"","APIs":"","operating systems":"","modeling languages":"","methodologies":"","design patterns":"","architectures":"","outils":"","sexe":"","university":"","adresse":"","ans d'expérience":""}}
"""

# Streamlit app
st.text("Data Scrapping")

uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        with st.spinner('Processing...'):
            text = input_pdf_text(uploaded_file)
            input_prompt = input_prompt_template.format(text=text)
            try:
                response = get_gemini_response(input_prompt)
                st.subheader("Parsed Resume Data")
                st.json(response)  # Display the parsed data as JSON
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload a resume before submitting.")


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
