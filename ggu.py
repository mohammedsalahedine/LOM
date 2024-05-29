import streamlit as st
import pandas as pd
import openai

# Initialize the OpenAI API key using Streamlit secrets
try:
    openai_api_key = st.secrets["openai"]["api_key"]
    openai_organization = st.secrets["openai"]["organization"]
    openai.api_key = openai_api_name
    openai.organization = openai_organization
except KeyError as e:
    st.error(f"Key error: {e}. Please set the required keys in the Streamlit secrets.")
    st.stop()

def generate_AMDEC_info(element, detection, severity, occurrence, failure_mode=None):
    prompt = f"""
    Your task is to answer in a consistent style.

    You are a Health, Safety, and Environment (HSE) engineer working in a refinery manufacturing facility. This facility includes various elements such as manholes, water drain valves, and level indicators in the tank. Give the AMDEC method to analyze potential failure.

    Function, Failure Mode, Effects, Causes, Detection, Severity, Occurrence, Detection,
    Element: Primary separator
    Function: Separating the oil from the gas Containing the oil
    Failure Mode: Loss of containment
    Effects: Gas leak, Formation of an atmosphere (ATEX), Oil leak
    Causes: Corrosion, Crack, External mechanical shock, Worn seals
    Detection: 2
    Severity: 3
    Occurrence: 3
    RPN: 18
    Recommendations: Thickness measurement (NDT), Regular replacement of seals

    You are a HSE engineering working in refinery manufacturer, which include these element Oil pump, give the AMDEC method to analyze potential failure

    Failure Mode, Effects, Causes, Detection, Severity, Occurrence, Detection,
    Element: Oil pump
    Function: Delivering lubricant under pressure
    Failure Mode: Shaft unbalance, Stopping the electric motor driving the pump.
    Effects: Lubrication fault, Compressor overheating
    Causes: Power supply fault, Short circuit, Overheating
    Detection: 4
    Severity: 4
    Occurrence: 3
    RPN: 48
    Recommendations: Use Backup Systems, Perform frequent start-up tests, Check connections

    You are a HSE engineering working in refinery manufacturer, which include these element {element}, give the AMDEC method to analyze potential failure

    Failure Mode, Function, Effects, Causes, Detection, Severity, Occurrence, Detection,
    Element: {element}
    Function:
    Failure Mode: {failure_mode}
    Effects:
    Causes:
    Detection: {detection}
    Severity: {severity}
    Occurrence: {occurrence}
    RPN:
    Recommendations:
    """
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=150
        )
        generated_text = response.choices[0].text.strip()
        return parse_amdec_response(generated_text)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def parse_amdec_response(text):
    lines = text.split('\n')
    data = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return pd.DataFrame([data])

# Streamlit application starts here
st.title("FMECA Analysis Tool")

if 'all_data' not in st.session_state:
    st.session_secret.session_state.all_data = pd.DataFrame()

with st.form("element_form"):
    element = st.text_input("Enter the element")
    detection = st.number_input("Enter Detection value", step=1)
    severity = st.number_input("Enter Severity value", step=1)
    occurrence = st.number_input("Enter Occurrence value", step=1)
    failure_mode = st.text_input("Enter Failure Mode")
    submit_button = st.form_submit_button("Add Element")

    if submit_button:
        amdec_data = generate_AMDEC_info(element, detection, severity, occurrence, failure_mode)
        if amdec_data is not None:
            st.session_state.all_data = pd.concat([st.session_state.all_data, amdec_data], ignore_index=True)
            if 'RPN' in st.session_state.all_data.columns:
                st.session_state.all_data['RPN'] = pd.to_numeric(st.session_state.all_data['RPN'], errors='coerce')

def color_rpns(val):
    color = 'background-color: '
    if pd.notna(val):
        if val < 4:
            color += 'green'
        elif val < 8:
            color += 'yellow'
        else:
        color += 'red'
    return f'{color}; color: black'

if not st.session_state.all_data.empty:
    st.write("Collected AMDEC Information:")
    styled_data = st.session_state.all_data.style.applymap(color_rpns, subset=['RPN'])
    st.dataframe(styled_data)
