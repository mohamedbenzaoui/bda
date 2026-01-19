import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# ────────────────────────────────────────────────
# إعدادات عامة
# ────────────────────────────────────────────────
DUREE_EXAM = 90
CRENEAUX = ["08:30", "11:00", "14:00"]
DATE_DEBUT = datetime(2026, 1, 10)
DATE_FIN   = datetime(2026, 1, 25)
MAX_SALLES_PER_SLOT = 50

ROLES = {
    "vice_doyen": "Vice-Doyen",
    "admin_exams": "Administrateur Examens",
    "chef_dept": "Chef de Département",
    "enseignant": "Enseignant",
    "etudiant": "Étudiant"
}

st.set_page_config(
    page_title="Gestion des Examens 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────
# تصميم CSS جديد – ثيم أزرق-رمادي-أبيض نظيف
# ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg: #f8fafc;
        --card: #ffffff;
        --text: #1e293b;
        --primary: #3b82f6;
        --primary-dark: #2563eb;
        --border: #e2e8f0;
        --muted: #64748b;
    }

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background-color: var(--bg);
    }

    .main-header {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid var(--border);
    }

    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: var(--primary-dark);
        margin: 0;
    }

    .main-subtitle {
        color: var(--muted);
        font-size: 1.15rem;
        margin-top: 0.75rem;
    }

    .card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text);
        margin: 1.8rem 0 1.2rem;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid var(--primary);
        display: inline-block;
    }

    .stButton > button {
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.65rem 1.4rem;
        font-weight: 500;
    }

    .stButton > button:hover {
        background-color: var(--primary-dark);
    }

    .metric-card {
        background: linear-gradient(145deg, #f0f9ff, #e0f2fe);
        border-radius: 12px;
        padding: 1.4rem;
        text-align: center;
        border: 1px solid #bae6fd;
    }

    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--primary-dark);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.95rem;
        margin-top: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# تهيئة الـ Session State
# ────────────────────────────────────────────────
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_dept_id" not in st.session_state:
    st.session_state.user_dept_id = None

# ────────────────────────────────────────────────
# دوال قاعدة البيانات (يفترض أنها موجودة وتعمل)
# ────────────────────────────────────────────────
# يجب نسخ دوال get_connection, execute_query, get_departements, ...
# get_formations_by_dept, get_professeurs_by_dept, load_edt_complete,
# get_kpis_globaux, generer_edt_optimiser, ... من الكود الأصلي

# للاختصار هنا، نفترض أنها معرفة مسبقاً

# ────────────────────────────────────────────────
# صفحة تسجيل الدخول (ترتيب جديد + تصميم نظيف)
# ────────────────────────────────────────────────
def page_login():
    st.markdown('<div class="main-header"><h1 class="main-title">نظام إدارة الامتحانات</h1><p class="main-subtitle">الجامعة – جانفي 2026</p></div>', unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("تسجيل الدخول")

            role_display = st.selectbox(
                "اختر نوع الحساب",
                options=list(ROLES.values()),
                index=None,
                placeholder="→ اختر دورك ←"
            )

            if role_display:
                role_key = next(k for k, v in ROLES.items() if v == role_display)

                if role_key == "vice_doyen":
                    if st.button("الدخول كـ Vice-Doyen", use_container_width=True):
                        st.session_state.user_role = role_key
                        st.session_state.user_name = "Vice-Doyen"
                        st.rerun()

                elif role_key == "admin_exams":
                    if st.button("الدخول كـ Administrateur", use_container_width=True):
                        st.session_state.user_role = role_key
                        st.session_state.user_name = "Administrateur Examens"
                        st.rerun()

                elif role_key == "chef_dept":
                    depts = get_departements()
                    if not depts.empty:
                        dept_name = st.selectbox("القسم", depts["nom"].tolist())
                        if st.button("تأكيد", use_container_width=True):
                            dept_id = depts[depts["nom"] == dept_name]["id"].iloc[0]
                            st.session_state.user_role = role_key
                            st.session_state.user_name = f"Chef {dept_name}"
                            st.session_state.user_dept_id = dept_id
                            st.rerun()

                elif role_key == "enseignant":
                    profs = get_professeurs_by_dept()
                    if not profs.empty:
                        prof_name = st.selectbox("الأستاذ", profs["nom"].tolist())
                        if st.button("الدخول", use_container_width=True):
                            row = profs[profs["nom"] == prof_name].iloc[0]
                            st.session_state.user_role = role_key
                            st.session_state.user_name = prof_name
                            st.session_state.user_dept_id = row["dept_id"]
                            st.rerun()

                elif role_key == "etudiant":
                    forms = get_formations_by_dept()
                    if not forms.empty:
                        form_name = st.selectbox("التخصص", forms["nom"].tolist())
                        if st.button("عرض الرزنامة", use_container_width=True):
                            row = forms[forms["nom"] == form_name].iloc[0]
                            st.session_state.user_role = role_key
                            st.session_state.user_name = "طالب"
                            st.session_state.user_dept_id = row["dept_id"]
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
# الصفحة الرئيسية بعد الدخول (مثال – يمكن توسيعها)
# ────────────────────────────────────────────────
def main_dashboard():
    st.markdown('<div class="main-header"><h1 class="main-title">مرحباً بك</h1></div>', unsafe_allow_html=True)
    st.markdown(f'<h3>أنت مسجل كـ : **{ROLES[st.session_state.user_role]}**</h3>', unsafe_allow_html=True)

    if st.session_state.user_role == "vice_doyen":
        kpis = get_kpis_globaux()
        cols = st.columns(4)
        for col, (key, icon, label) in zip(cols, [
            ("nb_examens", "📝", "عدد الامتحانات"),
            ("nb_salles", "🏛️", "عدد القاعات"),
            ("nb_profs", "👨‍🏫", "عدد الأساتذة"),
            ("nb_etudiants", "🎓", "عدد الطلبة")
        ]):
            with col:
                st.markdown(f'''
                <div class="metric-card">
                    <div style="font-size:2.2rem;">{icon}</div>
                    <div class="metric-value">{int(kpis.get(key, 0))}</div>
                    <div class="metric-label">{label}</div>
                </div>
                ''', unsafe_allow_html=True)

    # باقي الـ dashboards يمكن إضافتها بنفس الأسلوب...

# ────────────────────────────────────────────────
# الشريط الجانبي + التوجيه الرئيسي
# ────────────────────────────────────────────────
with st.sidebar:
    if st.session_state.user_role:
        st.markdown(f"**المستخدم الحالي**  \n**{ROLES[st.session_state.user_role]}**")
        st.markdown(f"_{st.session_state.user_name}_")
        if st.button("تسجيل الخروج", use_container_width=True):
            st.session_state.clear()
            st.rerun()

if not st.session_state.user_role:
    page_login()
else:
    main_dashboard()
    # يمكن هنا استدعاء dashboard خاص بكل دور
    # مثال: if st.session_state.user_role == "admin_exams": dashboard_admin()

if __name__ == "__main__":
    # يجب وضع باقي الدوال (قاعدة البيانات، generer_edt_optimiser، إلخ) قبل هذا السطر
    pass
