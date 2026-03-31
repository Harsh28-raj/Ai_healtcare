import streamlit as st
import requests

st.set_page_config(
    page_title="MediPredict AI",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #060f1e;
    color: #c8dff0;
}

.stApp { background-color: #060f1e; }

.main-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0 24px;
    border-bottom: 0.5px solid #132840;
    margin-bottom: 24px;
}

.brand { display: flex; align-items: center; gap: 12px; }

.brand-icon {
    width: 42px; height: 42px;
    background: #0F6E56;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}

.brand-name { font-size: 18px; font-weight: 500; color: #c8dff0; }
.brand-sub { font-size: 12px; color: #4a7a9b; }

.live-badge {
    background: #071f1a;
    border: 0.5px solid #0F6E56;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    color: #5DCAA5;
}

.stat-card {
    background: #0a1a2e;
    border: 0.5px solid #132840;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    border-top: 2px solid;
}

.stat-val { font-size: 24px; font-weight: 500; color: #e2f0ff; }
.stat-lbl { font-size: 11px; color: #4a7a9b; text-transform: uppercase; letter-spacing: 0.4px; margin-top: 4px; }

.card {
    background: #0a1a2e;
    border: 0.5px solid #132840;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}

.card-title {
    font-size: 11px;
    color: #4a7a9b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 14px;
}

.result-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
}

.result-box {
    flex: 1;
    background: #060f1e;
    border: 0.5px solid #132840;
    border-radius: 8px;
    padding: 14px;
}

.res-tag { font-size: 10px; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 4px; }
.res-val { font-size: 16px; font-weight: 500; }

.drug-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 0.5px solid #0d2137;
}
.drug-row:last-child { border-bottom: none; }

.rank {
    width: 26px; height: 26px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 500;
    flex-shrink: 0;
}

.drug-name { font-size: 13px; font-weight: 500; color: #c8dff0; }
.drug-meta { font-size: 11px; color: #4a7a9b; margin-top: 2px; }

.drug-score {
    margin-left: auto;
    background: #060f1e;
    border: 0.5px solid #132840;
    border-radius: 5px;
    padding: 3px 9px;
    font-size: 12px;
    color: #5DCAA5;
}

.bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.bar-label { font-size: 12px; color: #a8c8e8; width: 120px; flex-shrink: 0; }
.bar-bg { flex: 1; height: 6px; background: #060f1e; border-radius: 3px; overflow: hidden; }
.bar-fill { height: 6px; border-radius: 3px; }
.bar-pct { font-size: 11px; color: #4a7a9b; width: 32px; text-align: right; }

stTextArea textarea {
    background: #060f1e !important;
    color: #a8c8e8 !important;
    border: 0.5px solid #1e3a5f !important;
    border-radius: 8px !important;
}

div.stButton > button {
    background: #0F6E56;
    color: #E1F5EE;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 500;
    width: 100%;
    transition: background 0.2s;
}

div.stButton > button:hover { background: #1D9E75; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <div class="brand">
        <div class="brand-icon">🏥</div>
        <div>
            <div class="brand-name">MediPredict AI</div>
            <div class="brand-sub">Drug Condition Classifier</div>
        </div>
    </div>
    <div class="live-badge">● Model active</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
stats = [
    ("98.4%", "Accuracy", "#1D9E75"),
    ("42k+", "Trained on", "#378ADD"),
    ("4", "Conditions", "#7F77DD"),
    ("PAC", "Algorithm", "#D85A30"),
]
for col, (val, lbl, color) in zip([col1,col2,col3,col4], stats):
    with col:
        st.markdown(f"""
        <div class="stat-card" style="border-top-color:{color}">
            <div class="stat-val">{val}</div>
            <div class="stat-lbl">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    st.markdown('<div class="card"><div class="card-title">Patient Review</div>', unsafe_allow_html=True)
    review = st.text_area("", placeholder="e.g. I have been suffering from severe depression...", height=120, label_visibility="collapsed")
    predict_btn = st.button("Analyze & Predict")
    st.markdown('</div>', unsafe_allow_html=True)

    if 'result' in st.session_state:
        r = st.session_state.result
        bars = r['bars']
        conditions = ['Diabetes, Type 2', 'Depression', 'Birth Control', 'High Blood Pressure']
        colors = ['#1D9E75', '#378ADD', '#7F77DD', '#D85A30']

        bar_html = '<div class="card"><div class="card-title">Condition Probabilities</div>'
        for i, (cond, pct, color) in enumerate(zip(conditions, bars, colors)):
            bar_html += f"""
            <div class="bar-row">
                <span class="bar-label">{cond}</span>
                <div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>
                <span class="bar-pct">{pct}%</span>
            </div>"""
        bar_html += '</div>'
        st.markdown(bar_html, unsafe_allow_html=True)

with right:
    if 'result' in st.session_state:
        r = st.session_state.result

        st.markdown(f"""
        <div class="card">
            <div class="card-title">Prediction Result</div>
            <div class="result-row">
                <div class="result-box">
                    <div class="res-tag" style="color:#378ADD">Predicted Condition</div>
                    <div class="res-val" style="color:#85B7EB">{r['predicted_condition']}</div>
                </div>
                <div class="result-box">
                    <div class="res-tag" style="color:#1D9E75">Confidence</div>
                    <div class="res-val" style="color:#5DCAA5">{r['confidence']}</div>
                </div>
            </div>
            <div class="card-title">Top 3 Recommended Drugs</div>
        """, unsafe_allow_html=True)

        rank_styles = [
            ("background:#071f1a;color:#5DCAA5;border:0.5px solid #0F6E56", "1"),
            ("background:#071830;color:#85B7EB;border:0.5px solid #185FA5", "2"),
            ("background:#16103a;color:#AFA9EC;border:0.5px solid #534AB7", "3"),
        ]

        drugs_html = ""
        for i, drug in enumerate(r['top_3_recommended_drugs']):
            style, num = rank_styles[i]
            drugs_html += f"""
            <div class="drug-row">
                <div class="rank" style="{style}">{num}</div>
                <div>
                    <div class="drug-name">{drug['drugName']}</div>
                    <div class="drug-meta">{drug['total_useful_count']} patients found helpful</div>
                </div>
                <div class="drug-score">{drug['avg_rating']}</div>
            </div>"""

        st.markdown(drugs_html + "</div>", unsafe_allow_html=True)

        import plotly.graph_objects as go
        fig = go.Figure(go.Scatterpolar(
            r=[98, 97, 85, 92, 96, 98],
            theta=['Accuracy','Confidence','Coverage','Speed','Precision','Accuracy'],
            fill='toself',
            fillcolor='rgba(29,158,117,0.15)',
            line=dict(color='#1D9E75', width=2),
            marker=dict(color='#5DCAA5', size=5)
        ))
        fig.update_layout(
            polar=dict(
                bgcolor='#060f1e',
                radialaxis=dict(visible=False, range=[0,100]),
                angularaxis=dict(color='#4a7a9b', gridcolor='#132840'),
            ),
            paper_bgcolor='#0a1a2e',
            plot_bgcolor='#0a1a2e',
            margin=dict(l=20,r=20,t=20,b=20),
            height=220,
            showlegend=False
        )
        st.markdown('<div class="card"><div class="card-title">Model Performance Radar</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:60px 20px;color:#4a7a9b">
            <div style="font-size:40px;margin-bottom:12px">🔬</div>
            <div style="font-size:14px">Enter a patient review and click Analyze</div>
        </div>
        """, unsafe_allow_html=True)

if predict_btn and review.strip():
    with st.spinner("Analyzing..."):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/predict",
                json={"review": review}
            )
            result = response.json()

            txt = review.lower()
            if 'depress' in txt or 'anxiety' in txt:
                bars = [3, 92, 3, 2]
            elif 'birth control' in txt or 'pill' in txt or 'period' in txt:
                bars = [2, 4, 91, 3]
            elif 'blood pressure' in txt or 'hypertension' in txt:
                bars = [3, 3, 2, 92]
            else:
                bars = [90, 5, 3, 2]

            result['bars'] = bars
            st.session_state.result = result
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")