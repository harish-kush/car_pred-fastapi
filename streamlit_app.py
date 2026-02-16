import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# Configure page with professional settings
st.set_page_config(
    page_title="Automotive Price Intelligence Platform",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Card styling */
    .prediction-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Data insights section */
    .insights-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    /* Progress bar */
    .progress-bar {
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://127.0.0.1:8000"

# Initialize session state
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []
if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None

def check_api_status():
    """Check if API is accessible"""
    try:
        response = requests.get(f"{API_URL}/", timeout=3)
        return response.status_code == 200
    except:
        return False

def calculate_depreciation(year, present_price):
    """Calculate expected depreciation"""
    current_year = datetime.now().year
    age = current_year - year
    depreciation_rate = 0.15  # 15% per year average
    expected_value = present_price * ((1 - depreciation_rate) ** age)
    return max(expected_value, present_price * 0.1)  # Minimum 10% of original

def get_market_insights(year, kms_driven, fuel_type):
    """Generate market insights based on inputs"""
    insights = []
    current_year = datetime.now().year
    age = current_year - year
    
    # Age analysis
    if age < 3:
        insights.append(("🟢", "Low Depreciation", "Vehicle is relatively new with minimal depreciation"))
    elif age < 7:
        insights.append(("🟡", "Moderate Age", "Good condition expected with reasonable depreciation"))
    else:
        insights.append(("🟠", "Higher Depreciation", "Older vehicle - expect higher depreciation"))
    
    # Mileage analysis
    avg_yearly_km = kms_driven / max(age, 1)
    if avg_yearly_km < 10000:
        insights.append(("🟢", "Low Usage", "Below average annual mileage - positive for resale"))
    elif avg_yearly_km < 15000:
        insights.append(("🟡", "Average Usage", "Normal usage pattern for this age"))
    else:
        insights.append(("🟠", "High Usage", "Above average mileage - may affect valuation"))
    
    # Fuel type insights
    fuel_insights = {
        "Diesel": ("🔵", "Diesel Engine", "Better fuel efficiency, higher resale in commercial segment"),
        "Petrol": ("🟢", "Petrol Engine", "Lower maintenance, preferred for city driving"),
        "CNG": ("🟡", "CNG Variant", "Economical fuel costs, environmental friendly")
    }
    insights.append(fuel_insights.get(fuel_type, fuel_insights["Petrol"]))
    
    return insights

def create_price_gauge(predicted_price, present_price):
    """Create a gauge chart for price prediction"""
    max_price = max(predicted_price, present_price) * 1.5
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = predicted_price,
        delta = {'reference': present_price, 'valueformat': '.2f'},
        title = {'text': "Predicted Price (₹ Lakhs)", 'font': {'size': 20, 'color': '#333'}},
        number = {'valueformat': '.2f', 'font': {'size': 36, 'color': '#667eea'}},
        gauge = {
            'axis': {'range': [None, max_price], 'tickformat': '.1f'},
            'bar': {'color': "#667eea"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, present_price * 0.7], 'color': '#ffebee'},
                {'range': [present_price * 0.7, present_price * 1.3], 'color': '#fff3e0'},
                {'range': [present_price * 1.3, max_price], 'color': '#e8f5e9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': present_price
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Arial, sans-serif"}
    )
    
    return fig

def create_comparison_chart(predicted_price, present_price, expected_depreciation):
    """Create a comparison bar chart"""
    fig = go.Figure()
    
    categories = ['Present Price', 'Predicted Price', 'Expected Value']
    values = [present_price, predicted_price, expected_depreciation]
    colors = ['#667eea', '#764ba2', '#f093fb']
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        text=[f'₹{v:.2f}L' for v in values],
        textposition='auto',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.2)', width=2)
        ),
        hovertemplate='<b>%{x}</b><br>₹%{y:.2f} Lakhs<extra></extra>'
    ))
    
    fig.update_layout(
        title='Price Comparison Analysis',
        yaxis_title='Price (₹ Lakhs)',
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': "Arial, sans-serif", 'size': 12},
        showlegend=False,
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)')
    )
    
    return fig

def main():
    # Header
    st.markdown("""
    <div class="app-header">
        <h1 style='margin:0; font-size: 2.5rem; font-weight: 700;'>🚗 Automotive Price Intelligence Platform</h1>
        <p style='margin:0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;'>Advanced ML-Powered Vehicle Valuation System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Status in sidebar
    with st.sidebar:
        st.markdown("### 🔌 System Status")
        api_status = check_api_status()
        
        if api_status:
            st.markdown("""
            <div style='background: #e8f5e9; padding: 1rem; border-radius: 8px; border-left: 4px solid #4caf50;'>
                <span class='status-indicator' style='background: #4caf50;'></span>
                <strong>API Connected</strong><br>
                <small style='color: #666;'>System operational</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: #ffebee; padding: 1rem; border-radius: 8px; border-left: 4px solid #f44336;'>
                <span class='status-indicator' style='background: #f44336;'></span>
                <strong>API Disconnected</strong><br>
                <small style='color: #666;'>Start server with:</small><br>
                <code>uvicorn main:app --reload</code>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Session Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Predictions", len(st.session_state.prediction_history))
        with col2:
            if st.session_state.prediction_history:
                avg_price = sum([p['predicted_price'] for p in st.session_state.prediction_history]) / len(st.session_state.prediction_history)
                st.metric("Avg Price", f"₹{avg_price:.1f}L")
            else:
                st.metric("Avg Price", "—")
        
        if st.button("Clear History", use_container_width=True):
            st.session_state.prediction_history = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        <small>
        This platform uses advanced machine learning algorithms to provide accurate vehicle valuations based on market data and vehicle characteristics.
        </small>
        """, unsafe_allow_html=True)
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Price Prediction", "📈 Analytics", "📜 History"])
    
    with tab1:
        # Two-column layout for input form
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            st.markdown("### 🚘 Vehicle Information")
            
            with st.container():
                car_name = st.text_input(
                    "Vehicle Model",
                    placeholder="e.g., Honda City, Maruti Swift, Hyundai Creta",
                    help="Enter the complete model name"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    year = st.number_input(
                        "Manufacturing Year",
                        min_value=1990,
                        max_value=datetime.now().year,
                        value=2020,
                        step=1
                    )
                with col2:
                    owner = st.selectbox(
                        "Ownership",
                        options=[0, 1, 2, 3],
                        format_func=lambda x: f"{'First' if x == 0 else 'Second' if x == 1 else 'Third' if x == 2 else 'Fourth+'} Owner"
                    )
                
                present_price = st.number_input(
                    "Current Market Price (₹ Lakhs)",
                    min_value=0.5,
                    max_value=150.0,
                    value=10.5,
                    step=0.5,
                    help="Current showroom or market price"
                )
                
                kms_driven = st.slider(
                    "Odometer Reading (Kilometers)",
                    min_value=0,
                    max_value=500000,
                    value=27000,
                    step=1000,
                    format="%d km"
                )
                
                st.markdown(f"**Approximate usage:** {kms_driven / max((datetime.now().year - year), 1):,.0f} km/year")
        
        with col_right:
            st.markdown("### ⚙️ Technical Specifications")
            
            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    fuel_type = st.selectbox(
                        "Fuel Type",
                        options=["Petrol", "Diesel", "CNG"],
                        help="Select primary fuel type"
                    )
                    
                    transmission = st.selectbox(
                        "Transmission",
                        options=["Manual", "Automatic"],
                        help="Gearbox type"
                    )
                
                with col2:
                    seller_type = st.selectbox(
                        "Seller Category",
                        options=["Dealer", "Individual"],
                        help="Purchase source"
                    )
                
                # Market insights preview
                st.markdown("---")
                st.markdown("### 🔍 Quick Insights")
                
                if car_name and year and kms_driven:
                    insights = get_market_insights(year, kms_driven, fuel_type)
                    
                    for icon, title, description in insights:
                        st.markdown(f"""
                        <div style='background: white; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #667eea;'>
                            <strong>{icon} {title}</strong><br>
                            <small style='color: #666;'>{description}</small>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Predict button (full width)
        st.markdown("<br>", unsafe_allow_html=True)
        predict_button = st.button("🎯 Generate Price Intelligence", use_container_width=True, type="primary")
        
        if predict_button:
            if not car_name:
                st.error("⚠️ Please enter a vehicle model name")
            elif not api_status:
                st.error("⚠️ API server is not accessible. Please start the backend service.")
            else:
                # Prepare payload
                payload = {
                    "Car_Name": car_name,
                    "Year": year,
                    "Present_Price": present_price,
                    "Kms_Driven": kms_driven,
                    "Fuel_Type": fuel_type,
                    "Seller_Type": seller_type,
                    "Transmission": transmission,
                    "Owner": owner
                }
                
                # Progress indicator
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔄 Connecting to prediction engine...")
                    progress_bar.progress(25)
                    time.sleep(0.3)
                    
                    status_text.text("🤖 Analyzing vehicle parameters...")
                    progress_bar.progress(50)
                    
                    # Make API request
                    response = requests.post(
                        f"{API_URL}/predict",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=15
                    )
                    
                    progress_bar.progress(75)
                    status_text.text("📊 Generating market insights...")
                    time.sleep(0.3)
                    
                    if response.status_code == 200:
                        result = response.json()
                        predicted_price = result.get("prediction_price", 0)
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Analysis complete!")
                        time.sleep(0.5)
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Store in session
                        st.session_state.last_prediction = {
                            'car_name': car_name,
                            'year': year,
                            'predicted_price': predicted_price,
                            'present_price': present_price,
                            'kms_driven': kms_driven,
                            'fuel_type': fuel_type,
                            'transmission': transmission,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.session_state.prediction_history.append(st.session_state.last_prediction)
                        
                        # Display results
                        st.markdown("---")
                        st.markdown("## 📊 Valuation Report")
                        
                        # Key metrics row
                        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                        
                        with metric_col1:
                            st.markdown("""
                            <div class='metric-card'>
                                <h4 style='color: #667eea; margin: 0;'>Predicted Price</h4>
                                <h2 style='margin: 0.5rem 0; color: #333;'>₹{:.2f}L</h2>
                            </div>
                            """.format(predicted_price), unsafe_allow_html=True)
                        
                        with metric_col2:
                            price_diff = predicted_price - present_price
                            diff_percent = (price_diff / present_price * 100) if present_price > 0 else 0
                            color = "#4caf50" if price_diff > 0 else "#f44336" if price_diff < 0 else "#ff9800"
                            arrow = "↑" if price_diff > 0 else "↓" if price_diff < 0 else "→"
                            
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h4 style='color: {color}; margin: 0;'>Price Variance</h4>
                                <h2 style='margin: 0.5rem 0; color: {color};'>{arrow} {abs(diff_percent):.1f}%</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with metric_col3:
                            expected_depreciation = calculate_depreciation(year, present_price)
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h4 style='color: #ff9800; margin: 0;'>Expected Value</h4>
                                <h2 style='margin: 0.5rem 0; color: #333;'>₹{expected_depreciation:.2f}L</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with metric_col4:
                            vehicle_age = datetime.now().year - year
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h4 style='color: #9c27b0; margin: 0;'>Vehicle Age</h4>
                                <h2 style='margin: 0.5rem 0; color: #333;'>{vehicle_age} years</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        # Visualizations
                        viz_col1, viz_col2 = st.columns([1, 1])
                        
                        with viz_col1:
                            gauge_fig = create_price_gauge(predicted_price, present_price)
                            st.plotly_chart(gauge_fig, use_container_width=True)
                        
                        with viz_col2:
                            comparison_fig = create_comparison_chart(predicted_price, present_price, expected_depreciation)
                            st.plotly_chart(comparison_fig, use_container_width=True)
                        
                        # Detailed analysis
                        st.markdown("### 📋 Detailed Analysis")
                        
                        analysis_col1, analysis_col2 = st.columns(2)
                        
                        with analysis_col1:
                            st.markdown("""
                            <div class='prediction-card'>
                                <h4>💰 Price Assessment</h4>
                            """, unsafe_allow_html=True)
                            
                            if abs(diff_percent) < 5:
                                st.success("✅ Predicted price aligns well with market value")
                            elif diff_percent > 5:
                                st.info(f"📈 Predicted price is {abs(diff_percent):.1f}% higher - indicating strong market demand or unique features")
                            else:
                                st.warning(f"📉 Predicted price is {abs(diff_percent):.1f}% lower - consider factors like mileage, condition, or market trends")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        with analysis_col2:
                            st.markdown("""
                            <div class='prediction-card'>
                                <h4>🎯 Recommendation</h4>
                            """, unsafe_allow_html=True)
                            
                            if predicted_price >= present_price * 0.95:
                                st.success("✅ Good value retention - Recommended for purchase/sale")
                            elif predicted_price >= present_price * 0.80:
                                st.info("ℹ️ Fair valuation - Reasonable deal within market range")
                            else:
                                st.warning("⚠️ Below average valuation - Review vehicle condition and market timing")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Export option
                        st.markdown("---")
                        report_data = {
                            "Vehicle": car_name,
                            "Year": year,
                            "Present_Price": f"₹{present_price:.2f}L",
                            "Predicted_Price": f"₹{predicted_price:.2f}L",
                            "Kilometers": f"{kms_driven:,} km",
                            "Fuel_Type": fuel_type,
                            "Transmission": transmission,
                            "Seller_Type": seller_type,
                            "Owner": owner,
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        st.download_button(
                            label="📄 Download Valuation Report (JSON)",
                            data=json.dumps(report_data, indent=2),
                            file_name=f"valuation_{car_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    else:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"❌ Prediction failed with status code: {response.status_code}")
                        try:
                            error_detail = response.json()
                            st.json(error_detail)
                        except:
                            st.text(response.text)
                
                except requests.exceptions.Timeout:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("⏱️ Request timeout - Please try again")
                
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.markdown("### 📈 Market Analytics Dashboard")
        
        if st.session_state.prediction_history:
            df = pd.DataFrame(st.session_state.prediction_history)
            
            # Summary statistics
            st.markdown("#### Key Statistics")
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("Total Predictions", len(df))
            with stat_col2:
                st.metric("Avg Predicted", f"₹{df['predicted_price'].mean():.2f}L")
            with stat_col3:
                st.metric("Max Value", f"₹{df['predicted_price'].max():.2f}L")
            with stat_col4:
                st.metric("Min Value", f"₹{df['predicted_price'].min():.2f}L")
            
            st.markdown("---")
            
            # Charts
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Price distribution
                fig = px.histogram(df, x='predicted_price', 
                                 title='Price Distribution',
                                 labels={'predicted_price': 'Predicted Price (₹ Lakhs)'},
                                 color_discrete_sequence=['#667eea'])
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with chart_col2:
                # Fuel type distribution
                fuel_counts = df['fuel_type'].value_counts()
                fig = px.pie(values=fuel_counts.values, names=fuel_counts.index,
                           title='Fuel Type Distribution',
                           color_discrete_sequence=px.colors.sequential.RdBu)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.markdown("#### Recent Predictions")
            display_df = df[['car_name', 'year', 'predicted_price', 'present_price', 'fuel_type', 'timestamp']].copy()
            display_df.columns = ['Model', 'Year', 'Predicted (₹L)', 'Market (₹L)', 'Fuel', 'Timestamp']
            st.dataframe(display_df.sort_values('Timestamp', ascending=False), use_container_width=True, hide_index=True)
        
        else:
            st.info("📊 No prediction data available yet. Make your first prediction to see analytics.")
    
    with tab3:
        st.markdown("### 📜 Prediction History")
        
        if st.session_state.prediction_history:
            for i, pred in enumerate(reversed(st.session_state.prediction_history[-10:])):
                with st.expander(f"🚗 {pred['car_name']} ({pred['year']}) - {pred['timestamp']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Predicted Price", f"₹{pred['predicted_price']:.2f}L")
                    with col2:
                        st.metric("Market Price", f"₹{pred['present_price']:.2f}L")
                    with col3:
                        diff = ((pred['predicted_price'] - pred['present_price']) / pred['present_price'] * 100)
                        st.metric("Variance", f"{diff:+.1f}%")
                    
                    st.markdown(f"""
                    **Specifications:**
                    - Kilometers: {pred['kms_driven']:,} km
                    - Fuel Type: {pred['fuel_type']}
                    - Transmission: {pred['transmission']}
                    """)
        else:
            st.info("📝 No prediction history available yet.")

if __name__ == "__main__":
    main()