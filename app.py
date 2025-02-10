import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Apartment Rent Calculator",
    layout="wide"
)

# Load the models and encoders
@st.cache_resource
def load_models():
    return {
        'model': joblib.load('rent_model.joblib'),
        'conformal_model': joblib.load('conformal_model.joblib'),
        'le_floor': joblib.load('le_floor.joblib'),
        'le_style': joblib.load('le_style.joblib')
    }

models = load_models()

# Main title and description
st.title('🏢 Apartment Rent Calculator')
st.markdown("""
This calculator estimates monthly rent with 95% confidence intervals using advanced statistical methods.
The prediction range shows where we expect the true rent value to fall with 95% confidence.
""")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Basic Information")
    rooms = st.number_input('Number of Rooms', min_value=1, max_value=5, value=2)
    bathrooms = st.number_input('Number of Bathrooms', min_value=1, max_value=3, value=1)
    total_surface = st.number_input('Total Surface (m²)', min_value=30, max_value=200, value=80)

with col2:
    st.subheader("🏗️ Property Details")
    building_age = st.number_input('Building Age (years)', min_value=0, max_value=50, value=10)
    floor_material = st.selectbox('Floor Material', options=models['le_floor'].classes_)
    style = st.selectbox('Architectural Style', options=models['le_style'].classes_)

# Calculate button with custom styling
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0066cc;
    color: white;
    padding: 0.5rem 2rem;
    font-size: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# Add input validation
if total_surface < rooms * 15:  # Minimum 15m² per room
    st.warning("⚠️ The total surface seems too small for the number of rooms.")

if bathrooms > rooms:
    st.warning("⚠️ The number of bathrooms is unusually high for the number of rooms.")

calculate = st.button('Calculate Rent Estimate')

if calculate:
    st.session_state.last_prediction = {
        'rooms': rooms,
        'bathrooms': bathrooms,
        'total_surface': total_surface,
        'building_age': building_age,
        'floor_material': floor_material,
        'style': style
    }
    # Prepare input data
    features = ['rooms', 'bathrooms', 'total_surface', 'building_age', 
                'floor_material_encoded', 'style_encoded']
    
    input_data = pd.DataFrame({
        'rooms': [rooms],
        'bathrooms': [bathrooms],
        'total_surface': [total_surface],
        'building_age': [building_age],
        'floor_material_encoded': [models['le_floor'].transform([floor_material])[0]],
        'style_encoded': [models['le_style'].transform([style])[0]]
    })
    
    # Ensure columns are in the correct order
    input_data = input_data[features]
    
    # Make prediction with confidence intervals
    try:
        prediction, prediction_intervals = models['conformal_model'].predict(input_data, alpha=0.05)
        
        # Add debug information in expander
        with st.expander("🔍 Debug Information"):
            st.write("Input Features:", input_data.to_dict('records')[0])
            st.write("Feature Names:", features)
            st.write("Prediction Shape:", prediction.shape)
            st.write("Intervals Shape:", prediction_intervals.shape)
    except Exception as e:
        st.error(f"Prediction Error: {str(e)}")
        st.write("Input Data:", input_data)
        raise e
    
    # Create three columns for results
    res_col1, res_col2, res_col3 = st.columns(3)
    
    lower_bound = prediction_intervals[0, 0, 0]
    upper_bound = prediction_intervals[0, 1, 0]
    point_estimate = prediction[0]
    
    with res_col1:
        st.metric(
            "Lower Bound",
            f"${lower_bound:,.2f}",
            delta=f"${lower_bound - point_estimate:,.2f}",
            delta_color="off"
        )
    
    with res_col2:
        st.metric(
            "Best Estimate",
            f"${point_estimate:,.2f}"
        )
    
    with res_col3:
        st.metric(
            "Upper Bound",
            f"${upper_bound:,.2f}",
            delta=f"${upper_bound - point_estimate:,.2f}",
            delta_color="off"
        )

    # Create a visual representation of the prediction interval using a box plot
    fig = go.Figure()

    # Add the prediction interval as a box plot
    fig.add_trace(go.Box(
        q1=[lower_bound],
        median=[point_estimate],
        q3=[upper_bound],
        lowerfence=[lower_bound],
        upperfence=[upper_bound],
        mean=[point_estimate],
        name="Prediction Range",
        boxpoints=False,
        fillcolor="rgba(0,102,204,0.5)",
        line=dict(color="#0066cc"),
    ))

    # Update layout
    fig.update_layout(
        title="Rent Prediction Range",
        yaxis=dict(
            title="Monthly Rent ($)",
            tickformat="$,.0f",  # Format y-axis as currency
            range=[
                lower_bound - (upper_bound - lower_bound) * 0.1,  # Add 10% padding
                upper_bound + (upper_bound - lower_bound) * 0.1
            ]
        ),
        showlegend=False,
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='white',
        xaxis=dict(
            showticklabels=False,
            zeroline=False,
            showgrid=False
        )
    )

    # Show the plot
    st.plotly_chart(fig, use_container_width=True)

    # Additional information
    with st.expander("📊 Detailed Analysis"):
        st.markdown(f"""
        ### Prediction Details
        - **Point Estimate**: ${point_estimate:,.2f}
        - **95% Confidence Interval**: ${lower_bound:,.2f} to ${upper_bound:,.2f}
        - **Interval Width**: ${upper_bound - lower_bound:,.2f}
        
        ### Interpretation
        This means we are 95% confident that the true market rent for an apartment with these 
        characteristics would fall between ${lower_bound:,.2f} and ${upper_bound:,.2f}.
        """)

# Footer
st.markdown("""
---
Made with ❤️, using Memex, Streamlit and Conformal Predictions
""")
