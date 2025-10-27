import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import time

# Initialize session state for predictions
if 'predictions' not in st.session_state:
    st.session_state.predictions = {}
if 'last_prediction_time' not in st.session_state:
    st.session_state.last_prediction_time = {}

# Set page configuration
st.set_page_config(
    page_title="Health Assistant",
    layout="wide",
    page_icon="🧑‍⚕️",
    initial_sidebar_state="expanded"
)

# Modern UI CSS
st.markdown("""
    <style>
    /* Main page styling */
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #2d2d2d;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3498db !important;
        box-shadow: 0 0 0 1px #3498db !important;
    }
    .stTextInput > label {
        color: #b3b3b3 !important;
        font-size: 14px !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white !important;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        margin-top: 20px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }
    
    /* Header styling */
    .section-header {
        text-align: center;
        padding: 24px 0;
        margin-bottom: 32px;
        background: linear-gradient(90deg, #2d2d2d, #1e1e1e);
        border-radius: 12px;
        border: 1px solid #404040;
    }
    .section-header h1 {
        color: #3498db !important;
        font-size: 2.2rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* Input group styling */
    .input-group {
        background-color: #2d2d2d;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #404040;
    }
    
    /* Result box styling */
    .result-box {
        background: linear-gradient(135deg, #2d2d2d, #1e1e1e);
        border-radius: 12px;
        padding: 24px;
        margin: 24px 0;
        text-align: center;
        border: 1px solid #404040;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .result-box.error {
        border-left: 5px solid #e74c3c;
    }
    .result-box.success {
        border-left: 5px solid #2ecc71;
    }
    .result-box h3 {
        color: #ffffff;
        font-size: 20px;
        margin: 0;
    }

    /* Remove unwanted boxes */
    .block-container > div:nth-child(1) > div:nth-child(2),
    .block-container > div:nth-child(1) > div:nth-child(3) {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Optimize model loading
@st.cache_resource(ttl=3600)
def load_model(model_name):
    working_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = f'{working_dir}/saved_models/{model_name}.sav'
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return pickle.load(open(model_path, 'rb'))

# Initialize models dictionary
models = {}

def get_model(model_name):
    if model_name not in models:
        models[model_name] = load_model(model_name)
    return models[model_name]

def make_prediction(model_name, user_input):
    try:
        input_key = str(user_input)
        current_time = time.time()
        
        if (model_name in st.session_state.predictions and 
            input_key in st.session_state.predictions[model_name] and
            current_time - st.session_state.last_prediction_time.get(model_name, 0) < 300):
            return st.session_state.predictions[model_name][input_key]
        
        model = get_model(model_name)
        input_array = np.array([user_input])
        prediction = model.predict(input_array)[0]
        
        if model_name not in st.session_state.predictions:
            st.session_state.predictions[model_name] = {}
        st.session_state.predictions[model_name][input_key] = prediction
        st.session_state.last_prediction_time[model_name] = current_time
        
        return prediction
    except Exception as e:
        raise Exception(f"Prediction error: {str(e)}")

# Simplified input validation
def validate_inputs(inputs, model_type):
    try:
        inputs_array = np.array([float(x) for x in inputs])
        return np.all((inputs_array >= 0) & (inputs_array <= 1000)), "Values should be between 0 and 1000"
    except ValueError:
        return False, "Please enter valid numeric values"

# Sidebar navigation with improved styling
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem;'>
            <h1 style='color: #3498db; margin: 0;'>Health Assistant</h1>
            <p style='color: #b3b3b3; margin: 8px 0 0 0; font-size: 14px;'>Disease Prediction System</p>
        </div>
    """, unsafe_allow_html=True)
    
    selected = option_menu('',
                          ['Diabetes Prediction',
                           'Heart Disease Prediction',
                           'Parkinsons Prediction'],
                          icons=['activity', 'heart', 'person'],
                          menu_icon='hospital-fill',
                          default_index=0,
                          styles={
                              "container": {"padding": "0!important", "background-color": "transparent"},
                              "icon": {"color": "#3498db", "font-size": "20px"},
                              "nav-link": {
                                  "font-size": "16px",
                                  "text-align": "left",
                                  "margin": "8px 0",
                                  "padding": "12px 20px",
                                  "border-radius": "8px",
                                  "background-color": "#2d2d2d",
                                  "color": "#ffffff"
                              },
                              "nav-link-selected": {
                                  "background-color": "#3498db",
                                  "color": "#ffffff",
                                  "font-weight": "600"
                              },
                          })

# Diabetes Prediction Page
if selected == 'Diabetes Prediction':
    st.header('Diabetes Prediction')
    
    col1, col2 = st.columns(2)
    
    with col1:
        pregnancies = st.text_input('Number of Pregnancies (0-17)', key='pregnancies')
        glucose = st.text_input('Glucose Level (70-200 mg/dL)', key='glucose')
        blood_pressure = st.text_input('Blood Pressure (60-140 mm Hg)', key='bp')
        skin_thickness = st.text_input('Skin Thickness (0-100 mm)', key='skin')
    
    with col2:
        insulin = st.text_input('Insulin Level (0-850 mu U/ml)', key='insulin')
        bmi = st.text_input('BMI (18.5-40)', key='bmi')
        pedigree = st.text_input('Diabetes Pedigree Function (0.0-2.5)', key='pedigree')
        age = st.text_input('Age (21-90)', key='age')

    if st.button('Predict Diabetes Risk'):
        user_input = [pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, pedigree, age]
        
        is_valid, error_message = validate_inputs(user_input, 'diabetes')
        if not is_valid:
            st.error(error_message)
        else:
            try:
                with st.spinner('Analyzing...'):
                    user_input = [float(x) for x in user_input]
                    prediction = make_prediction('diabetes_model', user_input)
                    result = 'The person is at risk of diabetes' if prediction == 1 else 'The person is not at risk of diabetes'
                    
                    insights_risk = """<li>Monitor blood glucose levels regularly</li>
                    <li>Maintain a balanced diet rich in fiber and low in refined carbohydrates</li>
                    <li>Engage in regular physical activity (150 minutes/week)</li>
                    <li>Maintain a healthy BMI (18.5-24.9)</li>
                    <li>Consider consulting an endocrinologist</li>"""
                    
                    insights_healthy = """<li>Continue maintaining a healthy lifestyle</li>
                    <li>Regular exercise (30 minutes daily)</li>
                    <li>Balanced nutrition with whole grains</li>
                    <li>Regular health check-ups</li>
                    <li>Adequate sleep (7-9 hours)</li>"""
                    
                    st.markdown(f"""<div class='result-box {"error" if prediction == 1 else "success"}'>
                        <h3>{result}</h3>
                        <div style='margin-top: 20px; text-align: left;'>
                            <h4 style='color: #ffffff; margin-bottom: 10px;'>Key Insights & Recommendations:</h4>
                            <ul style='color: #b3b3b3; margin: 0; padding-left: 20px;'>
                                {insights_risk if prediction == 1 else insights_healthy}
                            </ul>
                        </div>
                    </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Heart Disease Prediction Page
if selected == 'Heart Disease Prediction':
    st.header('Heart Disease Prediction')
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.text_input('Age (20-95)', key='heart_age')
        sex = st.text_input('Sex (1=male, 0=female)', key='heart_sex')
        cp = st.text_input('Chest Pain Type (0-3)', key='heart_cp')
        trestbps = st.text_input('Resting Blood Pressure (90-200 mm Hg)', key='heart_bp')
        chol = st.text_input('Cholesterol (100-600 mg/dl)', key='heart_chol')
        fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl (1=true, 0=false)', key='heart_fbs')
    
    with col2:
        restecg = st.text_input('Resting ECG Results (0-2)', key='heart_ecg')
        thalach = st.text_input('Maximum Heart Rate (60-220 bpm)', key='heart_rate')
        exang = st.text_input('Exercise Induced Angina (1=yes, 0=no)', key='heart_exang')
        oldpeak = st.text_input('ST Depression (0.0-6.0)', key='heart_st')
        slope = st.text_input('ST Slope (0-2)', key='heart_slope')
        ca = st.text_input('Number of Major Vessels (0-4)', key='heart_vessels')
        thal = st.text_input('Thalassemia (0=normal, 1=fixed defect, 2=reversible defect)', key='heart_thal')

    if st.button('Predict Heart Disease Risk'):
        user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
        
        is_valid, error_message = validate_inputs(user_input, 'heart')
        if not is_valid:
            st.error(error_message)
        else:
            try:
                with st.spinner('Analyzing...'):
                    user_input = [float(x) for x in user_input]
                    prediction = make_prediction('heart_disease_model', user_input)
                    result = 'The person is at risk of heart disease' if prediction == 1 else 'The person is not at risk of heart disease'
                    
                    insights_risk = """<li>Monitor blood pressure and cholesterol levels</li>
                    <li>Follow a heart-healthy diet (Mediterranean diet recommended)</li>
                    <li>Regular cardiovascular exercise (at least 30 minutes daily)</li>
                    <li>Stress management through relaxation techniques</li>
                    <li>Consider consulting a cardiologist</li>
                    <li>Quit smoking and limit alcohol intake</li>"""
                    
                    insights_healthy = """<li>Maintain heart-healthy lifestyle</li>
                    <li>Regular blood pressure monitoring</li>
                    <li>Stay physically active</li>
                    <li>Annual cardiac check-ups</li>
                    <li>Maintain healthy weight</li>"""
                    
                    st.markdown(f"""<div class='result-box {"error" if prediction == 1 else "success"}'>
                        <h3>{result}</h3>
                        <div style='margin-top: 20px; text-align: left;'>
                            <h4 style='color: #ffffff; margin-bottom: 10px;'>Key Insights & Recommendations:</h4>
                            <ul style='color: #b3b3b3; margin: 0; padding-left: 20px;'>
                                {insights_risk if prediction == 1 else insights_healthy}
                            </ul>
                        </div>
                    </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Parkinson's Prediction Page
if selected == "Parkinsons Prediction":
    st.header("Parkinson's Disease Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fo = st.text_input('MDVP:Fo(Hz) (80-260 Hz)', key='park_fo')
        fhi = st.text_input('MDVP:Fhi(Hz) (100-280 Hz)', key='park_fhi')
        flo = st.text_input('MDVP:Flo(Hz) (60-240 Hz)', key='park_flo')
        jitter_percent = st.text_input('Jitter(%) (0.0-5.0%)', key='park_jitter_p')
        jitter_abs = st.text_input('Jitter(Abs) (0.0-1.0)', key='park_jitter_a')
        rap = st.text_input('RAP - Relative Amplitude Perturbation (0.0-1.0)', key='park_rap')
        ppq = st.text_input('PPQ - Period Perturbation Quotient (0.0-1.0)', key='park_ppq')
        ddp = st.text_input('DDP - Average Differences (0.0-1.0)', key='park_ddp')
        shimmer = st.text_input('Shimmer Local (0.0-1.0)', key='park_shimmer')
        shimmer_db = st.text_input('Shimmer(dB) (0.0-2.0)', key='park_shimmer_db')
        apq3 = st.text_input('APQ3 - Amplitude Perturbation (0.0-1.0)', key='park_apq3')
    
    with col2:
        apq5 = st.text_input('APQ5 - Amplitude Perturbation (0.0-1.0)', key='park_apq5')
        apq = st.text_input('APQ - Amplitude Perturbation Quotient (0.0-1.0)', key='park_apq')
        dda = st.text_input('DDA - Directional Differences (0.0-1.0)', key='park_dda')
        nhr = st.text_input('NHR - Noise to Harmonic Ratio (0.0-1.0)', key='park_nhr')
        hnr = st.text_input('HNR - Harmonic to Noise Ratio (0-40 dB)', key='park_hnr')
        rpde = st.text_input('RPDE - Recurrence Period Density Entropy (0.0-1.0)', key='park_rpde')
        dfa = st.text_input('DFA - Detrended Fluctuation Analysis (0.0-1.0)', key='park_dfa')
        spread1 = st.text_input('Spread1 (0.0-1.0)', key='park_spread1')
        spread2 = st.text_input('Spread2 (0.0-1.0)', key='park_spread2')
        d2 = st.text_input('D2 - Correlation Dimension (0.0-5.0)', key='park_d2')
        ppe = st.text_input('PPE - Pitch Period Entropy (0.0-1.0)', key='park_ppe')

    if st.button("Predict Parkinson's Disease Risk"):
        user_input = [fo, fhi, flo, jitter_percent, jitter_abs, rap, ppq, ddp, shimmer, shimmer_db,
                     apq3, apq5, apq, dda, nhr, hnr, rpde, dfa, spread1, spread2, d2, ppe]
        
        is_valid, error_message = validate_inputs(user_input, 'parkinsons')
        if not is_valid:
            st.error(error_message)
        else:
            try:
                with st.spinner('Analyzing...'):
                    user_input = [float(x) for x in user_input]
                    prediction = make_prediction('parkinsons_model', user_input)
                    result = "The person is at risk of Parkinson's disease" if prediction == 1 else "The person is not at risk of Parkinson's disease"
                    
                    insights_risk = """<li>Consult a neurologist for detailed evaluation</li>
                    <li>Consider physical therapy for mobility</li>
                    <li>Engage in regular exercise (tai chi, yoga recommended)</li>
                    <li>Speech therapy may be beneficial</li>
                    <li>Focus on balance and coordination exercises</li>
                    <li>Maintain a consistent sleep schedule</li>"""
                    
                    insights_healthy = """<li>Regular physical activity</li>
                    <li>Brain-stimulating activities</li>
                    <li>Balanced nutrition with antioxidants</li>
                    <li>Regular medical check-ups</li>
                    <li>Maintain social connections</li>"""
                    
                    st.markdown(f"""<div class='result-box {"error" if prediction == 1 else "success"}'>
                        <h3>{result}</h3>
                        <div style='margin-top: 20px; text-align: left;'>
                            <h4 style='color: #ffffff; margin-bottom: 10px;'>Key Insights & Recommendations:</h4>
                            <ul style='color: #b3b3b3; margin: 0; padding-left: 20px;'>
                                {insights_risk if prediction == 1 else insights_healthy}
                            </ul>
                        </div>
                    </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

