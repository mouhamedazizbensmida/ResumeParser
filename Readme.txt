% Install Dependencies
conda create -p venv python==3.10 -y
conda activate venv/      
pip install -r requirements.txt
% To run the app :
streamlit run app.py