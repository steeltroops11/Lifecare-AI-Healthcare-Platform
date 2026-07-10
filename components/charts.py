# Visualizations module using Plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

def _get_theme_colors():
    theme = st.session_state.get("theme", "Ethereal Silk (Light)")
    if theme not in ["Ethereal Silk (Light)", "Midnight Cosmic (Dark)"]:
        theme = "Ethereal Silk (Light)"
    is_dark = (theme == "Midnight Cosmic (Dark)")
    text_color = "#CBD5E1" if is_dark else "#0F172A"
    grid_color = "rgba(139, 92, 246, 0.15)" if is_dark else "#E2E8F0"
    return text_color, grid_color

def draw_risk_gauge(risk_percent, title="Risk Probability Indicator"):
    """Render a premium risk gauge indicator using Plotly."""
    text_color, grid_color = _get_theme_colors()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_percent,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20, 'color': text_color, 'family': 'Outfit, sans-serif'}},
        number={'suffix': "%", 'font': {'size': 36, 'color': text_color, 'family': 'Outfit, sans-serif'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': text_color},
            'bar': {'color': "#0F6E84"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': grid_color,
            'steps': [
                {'range': [0, 40], 'color': '#EAF9F1'},      # Low Risk Green
                {'range': [40, 70], 'color': '#FFFBEB'},     # Mod Risk Orange
                {'range': [70, 100], 'color': '#FEF2F2'}     # High Risk Red
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': risk_percent
            }
        }
    ))

    fig.update_layout(
        font=dict(color=text_color, family="Outfit, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def draw_disease_distribution(predictions):
    """Render a pie chart showing the distribution of diagnosed diseases."""
    text_color, grid_color = _get_theme_colors()
    if not predictions:
        # Fallback empty chart data
        df = pd.DataFrame({"Disease": ["No Data Available"], "Count": [1]})
    else:
        df = pd.DataFrame(predictions)
        df = df['disease'].value_counts().reset_index()
        df.columns = ['Disease', 'Count']

    fig = px.pie(
        df,
        values='Count',
        names='Disease',
        hole=0.4,
        color_discrete_sequence=['#0F6E84', '#1AA7C8', '#0F3D4F', '#5A7A86', '#88B0C0']
    )
    fig.update_layout(
        font=dict(color=text_color, family="Outfit, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(color=text_color)),
        margin=dict(l=10, r=10, t=10, b=40),
        height=300
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def draw_weekly_predictions(predictions):
    """Render a bar chart displaying weekly prediction activity counts."""
    text_color, grid_color = _get_theme_colors()
    # Build list of last 7 days
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    counts = {d: 0 for d in dates}

    for p in predictions:
        # Get YYYY-MM-DD from timestamp
        try:
            p_date = p["timestamp"].split(" ")[0]
            if p_date in counts:
                counts[p_date] += 1
        except Exception:
            continue

    df = pd.DataFrame({
        "Date": [datetime.strptime(d, "%Y-%m-%d").strftime("%a") for d in dates],
        "Predictions": [counts[d] for d in dates]
    })

    fig = px.bar(
        df,
        x='Date',
        y='Predictions',
        labels={'Predictions': 'Predictions Count'},
        color_discrete_sequence=['#0F6E84']
    )
    fig.update_layout(
        font=dict(color=text_color, family="Outfit, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=10, t=10, b=50),
        height=300,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=text_color),
            title=dict(text="Date", font=dict(color=text_color, size=13), standoff=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            dtick=1,
            tickfont=dict(color=text_color),
            title=dict(text="Predictions Count", font=dict(color=text_color, size=13), standoff=10),
        ),
    )
    return fig

def draw_monthly_trends(predictions):
    """Render a line chart displaying average risk level trends by month."""
    text_color, grid_color = _get_theme_colors()
    if not predictions:
        # Placeholder line
        df = pd.DataFrame({"Month": ["May", "Jun", "Jul"], "Avg Risk": [25.0, 30.0, 35.0]})
    else:
        df_all = pd.DataFrame(predictions)
        # Parse timestamp to Month Name
        df_all['Month'] = df_all['timestamp'].apply(lambda x: datetime.strptime(x.split(" ")[0], "%Y-%m-%d").strftime("%b") if len(x) > 10 else "Unknown")
        df_all['Risk %'] = df_all['risk'] * 100
        df = df_all.groupby('Month')['Risk %'].mean().reset_index()
        df.columns = ['Month', 'Avg Risk']
        # Order months logically
        months_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        df['Month'] = pd.Categorical(df['Month'], categories=months_order, ordered=True)
        df = df.sort_values('Month')

    fig = px.line(
        df,
        x='Month',
        y='Avg Risk',
        markers=True,
        labels={'Avg Risk': 'Average Risk (%)'},
        color_discrete_sequence=['#1AA7C8']
    )
    fig.update_layout(
        font=dict(color=text_color, family="Outfit, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=10, t=10, b=50),
        height=300,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color, size=13), standoff=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            range=[0, 100],
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color, size=13), standoff=10),
        ),
    )
    return fig

def draw_accuracy_overview():
    """Render a comparative bar chart indicating ML models accuracies."""
    text_color, grid_color = _get_theme_colors()
    df = pd.DataFrame({
        "Model Name": ["Diabetes", "Heart Disease", "Kidney Disease", "Readmission"],
        "Accuracy Score": [77.9, 78.7, 98.8, 66.3],
        "Metric": ["Pima Indians", "UCI Heart", "UCI CKD", "100k+ encounters"]
    })

    fig = px.bar(
        df,
        x='Accuracy Score',
        y='Model Name',
        orientation='h',
        color='Accuracy Score',
        color_continuous_scale=['#88B0C0', '#0F6E84'],
        text='Accuracy Score',
        labels={'Accuracy Score': 'Accuracy (%)'}
    )
    fig.update_layout(
        font=dict(color=text_color, family="Outfit, sans-serif"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=120, r=20, t=10, b=50),
        height=300,
        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            range=[0, 100],
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color, size=13), standoff=10),
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color=text_color, size=12),
            automargin=True,
        ),
        coloraxis_showscale=False
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
    return fig


def draw_xai_feature_contributions(disease, inputs):
    """Render a rule-based Explainable AI (XAI) feature contribution chart (Priority 4)."""
    contribs = []

    if disease == "Diabetes":
        glucose = inputs.get("glucose", 120)
        bmi = inputs.get("bmi", 25.0)
        age = inputs.get("age", 30)
        pregnancies = inputs.get("pregnancies", 1)
        bp = inputs.get("bp", 70)

        # Base rule-based contribution scores
        contribs.append({"Feature": "Plasma Glucose Concentration", "Contribution": 30 if glucose > 125 else (-15 if glucose < 90 else -5)})
        contribs.append({"Feature": "Body Mass Index (BMI)", "Contribution": 20 if bmi >= 30 else (-10 if bmi < 23 else 0)})
        contribs.append({"Feature": "Patient Age", "Contribution": 15 if age > 45 else -10})
        contribs.append({"Feature": "Pregnancies Count", "Contribution": 10 if pregnancies > 5 else -5})
        contribs.append({"Feature": "Diastolic Blood Pressure", "Contribution": 10 if bp > 90 else -5})

    elif disease == "Heart Disease":
        chol = inputs.get("chol", 200)
        bp = inputs.get("trestbps", 120)
        age = inputs.get("age", 50)
        cp = inputs.get("cp", 0)
        exang = inputs.get("exang", 0)

        contribs.append({"Feature": "Serum Cholesterol Level", "Contribution": 25 if chol > 240 else (-10 if chol < 190 else 0)})
        contribs.append({"Feature": "Resting Blood Pressure", "Contribution": 20 if bp > 140 else (-10 if bp < 120 else 0)})
        contribs.append({"Feature": "Patient Age Factor", "Contribution": 15 if age > 55 else -10})
        contribs.append({"Feature": "Chest Pain Type (cp)", "Contribution": 20 if cp > 1 else -15})
        contribs.append({"Feature": "Exercise Induced Angina", "Contribution": 15 if exang == 1 else -10})

    elif disease == "Kidney Disease":
        sc = inputs.get("sc", 1.2)
        hemo = inputs.get("hemo", 15.0)
        bp = inputs.get("bp", 80)
        al = inputs.get("al", 0)
        dm = inputs.get("dm", 0)

        contribs.append({"Feature": "Serum Creatinine Level", "Contribution": 35 if sc > 1.5 else -15})
        contribs.append({"Feature": "Hemoglobin Content", "Contribution": -20 if hemo > 13 else 25})
        contribs.append({"Feature": "Blood Pressure Level", "Contribution": 15 if bp > 90 else -5})
        contribs.append({"Feature": "Urine Albumin Level", "Contribution": 20 if al > 1 else -10})
        contribs.append({"Feature": "Diabetes Mellitus History", "Contribution": 15 if dm == 1 else -5})

    else:  # Readmission
        time = inputs.get("time_in_hospital", 4)
        meds = inputs.get("num_medications", 15)
        inpatient = inputs.get("number_inpatient", 0)
        emergency = inputs.get("number_emergency", 0)

        contribs.append({"Feature": "Length of Stay (days)", "Contribution": 15 if time > 6 else -5})
        contribs.append({"Feature": "Prescribed Medications Count", "Contribution": 10 if meds > 20 else -5})
        contribs.append({"Feature": "Inpatient Stays (past year)", "Contribution": 25 if inpatient > 1 else -10})
        contribs.append({"Feature": "Emergency Visits (past year)", "Contribution": 20 if emergency > 1 else -10})

    text_color, grid_color = _get_theme_colors()
    df = pd.DataFrame(contribs)
    df["Impact"] = df["Contribution"].apply(lambda val: "Increases Risk" if val > 0 else "Reduces Risk")

    fig = px.bar(
        df,
        x='Contribution',
        y='Feature',
        color='Impact',
        orientation='h',
        color_discrete_map={"Increases Risk": "#EF4444", "Reduces Risk": "#22C55E"},
        labels={'Contribution': 'Attribution Impact Score'},
        title="Explainable AI (XAI) Factor Contributions"
    )
    
    fig.update_layout(
        font=dict(color=text_color, family="Outfit, sans-serif"),
        title={'font': {'color': text_color, 'family': 'Outfit, sans-serif'}},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=20, t=50, b=50),
        height=320,
        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color, size=13), standoff=10),
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color=text_color, size=11),
            automargin=True,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(color=text_color))
    )
    return fig


def draw_biomarker_trends(predictions):
    """Parse historical inputs_json and render an interactive bio-marker trend timeline (Glucose, Cholesterol, Creatinine)."""
    import json
    text_color, grid_color = _get_theme_colors()

    data = []
    for p in predictions:
        try:
            inputs = json.loads(p["inputs_json"])
            timestamp = p["timestamp"]
            try:
                date_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
            except Exception:
                date_obj = datetime.now()

            if p["disease"] == "Diabetes" and "glucose" in inputs:
                data.append({
                    "Date": date_obj,
                    "Value": float(inputs["glucose"]),
                    "Bio-Marker": "Blood Glucose (mg/dL)"
                })
            elif p["disease"] == "Heart Disease" and "chol" in inputs:
                data.append({
                    "Date": date_obj,
                    "Value": float(inputs["chol"]),
                    "Bio-Marker": "Serum Cholesterol (mg/dL)"
                })
            elif p["disease"] == "Kidney Disease" and "sc" in inputs:
                data.append({
                    "Date": date_obj,
                    "Value": float(inputs["sc"]) * 100,
                    "Bio-Marker": "Serum Creatinine (mg/dL x 100)"
                })
        except Exception:
            continue

    if not data:
        fig = go.Figure()
        fig.add_annotation(text="Run diagnostic assessments to track historical vitals.", showarrow=False, font=dict(size=14, color=text_color))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig

    df = pd.DataFrame(data)
    df = df.sort_values("Date")
    df["Date Str"] = df["Date"].apply(lambda x: x.strftime("%b %d, %H:%M"))

    fig = px.line(
        df,
        x="Date Str",
        y="Value",
        color="Bio-Marker",
        markers=True,
        labels={"Value": "Laboratory Reading", "Date Str": "Timeline"},
        color_discrete_map={
            "Blood Glucose (mg/dL)": "var(--primary)",
            "Serum Cholesterol (mg/dL)": "var(--accent)",
            "Serum Creatinine (mg/dL x 100)": "var(--info)"
        }
    )

    fig.update_layout(
        font=dict(color=text_color, family="Plus Jakarta Sans, sans-serif"),
        title={'text': "📈 Patient Bio-Marker Vital Trends", 'font': {'color': text_color, 'family': 'Lora, serif', 'size': 18}},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=20, t=50, b=50),
        height=320,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color, size=13), standoff=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            tickfont=dict(color=text_color),
            title=dict(font=dict(color=text_color, size=13), standoff=10),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5, font=dict(color=text_color))
    )
    return fig
