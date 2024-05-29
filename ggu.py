import streamlit as st
import pandas as pd
import os
import openai

# Initialize the OpenAI client using environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.organization = os.getenv('OPENAI_ORGANIZATION')

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

    You are a HSE engineering working in refinery manufacturer, which include these element Oil pump, give the AMDEC method to analyze potential failure {element}

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
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo",
    )
    response = chat_completion.choices[0].message.content

    # Parse response to extract AMDEC-related information
    lines = response_content.split('\n')
    data = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()

    # Convert dictionary to DataFrame
    amdec_data = pd.DataFrame([data])
    return amdec_data

# Streamlit application starts here
st.title("FMECA Analysis Tool")

# Check if 'all_data' exists in session state, if not initialize it
if 'all_data' not in st.session_state:
    st.session_state.all_data = pd.DataFrame()

# Form to input new elements
with st.form("element_form"):
    element = st.text_input("Enter the element")
    detection = st.number_input("Enter Detection value", step=1)
    severity = st.number_input("Enter Severity value", step=1)
    occurrence = st.number_input("Enter Occurrence value", step=1)
    failure_mode = st.text_input("Enter Failure Mode")
    # Create the submit button
    submit_button = st.form_submit_button("Add Element")

    # Check if the submit button is clicked
    if submit_button:
        # Generate AMDEC information for the element
        amdec_data = generate_AMDEC_info(element, detection, severity, occurrence, failure_mode)

        # Add the data to the DataFrame in session state using concat
        st.session_state.all_data = pd.concat([st.session_state.all_data, amdec_data], ignore_index=True)

        # Ensure 'RPN' column is numeric
        if 'RPN' in st.session_state.all_data.columns:
            st.session_state.all_data['RPN'] = pd.to_numeric(st.session_state.all_data['RPN'], errors='coerce')

# Function to apply conditional formatting to the DataFrame
def color_rpns(val):
    if not pd.isna(val):
        if val < 4:
            color = 'background-color: green; color: black'
        elif val >= 4 and val <= 7:
            color = 'background-color: yellow; color: black'
        else:
            color = 'background-color: red; color: black'
        return color
    return None

# Display the collected AMDEC data with conditional formatting
if not st.session_state.all_data.empty:
    st.write("Collected AMDEC Information:")
    # Apply the style to the 'RPN' column
    styled_data = st.session_state.all_data.style.applymap(color_rpns, subset=['RPN'])
    st.dataframe(styled_data)  # Display the styled DataFrame in the Streamlit app

# Additional Streamlit code can go here for other features and functionalities
