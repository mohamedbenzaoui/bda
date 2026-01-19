import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ==============================
# CONFIGURATION
# ==============================
DUREE_EXAM = 90
CRENEAUX = ["08:30", "11:00", "14:00"]
DATE_DEBUT = datetime(2026, 1, 10)
DATE_FIN = datetime(2026, 1, 25)
MAX_SALLES_PER_SLOT = 50

ROLES = {
    "vice_doyen": "Vice-Doyen / Doyen",
    "admin_exams": "Administrateur Examens",
    "chef_dept": "Chef de Département",
    "enseignant": "Enseignant",
    "etudiant": "Étudiant"
}

st.set_page_config(
    page_title="ExamFlow Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# REDESIGNED CSS
# ==============================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Background */
    .main {
        background: linear-gradient(to bottom right, #e0f2fe 0%, #ddd6fe 50%, #fae8ff 100%);
        padding: 1.5rem;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Top Navigation Bar */
    .top-nav {
        background: white;
        border: 2px solid #e0e7ff;
        border-radius: 20px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
    }
    
    .brand-logo {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }
    
    .nav-title {
        color: #1e1b4b;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .nav-subtitle {
        color: #6366f1;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }
    
    /* Role Pill */
    .role-pill {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 0.6rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Glass Card */
    .glass-card {
        background: white;
        border: 2px solid #e0e7ff;
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
    }
    
    /* Metric Box */
    .metric-box {
        background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
        border: 2px solid #c7d2fe;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-8px);
        border-color: #6366f1;
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.25);
        background: linear-gradient(135deg, #bfdbfe 0%, #c7d2fe 100%);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 8px rgba(99, 102, 241, 0.3));
    }
    
    .metric-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .metric-text {
        color: #4f46e5;
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Alert Box */
    .alert-box {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        border: 2px solid #f87171;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .alert-box.success {
        background: linear-gradient(135deg, #bbf7d0 0%, #86efac 100%);
        border-color: #4ade80;
    }
    
    .alert-box.warning {
        background: linear-gradient(135deg, #fed7aa 0%, #fdba74 100%);
        border-color: #fb923c;
    }
    
    .alert-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e1b4b;
        margin: 0.5rem 0;
    }
    
    .alert-label {
        color: #312e81;
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Section Title */
    .section-title {
        color: #1e1b4b;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-title::before {
        content: '';
        width: 4px;
        height: 32px;
        background: linear-gradient(to bottom, #6366f1, #8b5cf6);
        border-radius: 4px;
    }
    
    /* Exam Timeline Card */
    .exam-timeline-card {
        background: white;
        border-left: 4px solid #6366f1;
        border: 2px solid #e0e7ff;
        border-left: 4px solid #6366f1;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .exam-timeline-card:hover {
        background: #f5f3ff;
        border-left-color: #8b5cf6;
        transform: translateX(8px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
    }
    
    .exam-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #1e1b4b;
        margin-bottom: 1rem;
    }
    
    .exam-info {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .exam-info-item {
        color: #6366f1;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .exam-info-item strong {
        color: #1e1b4b;
    }
    
    /* Login Container */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    
    .login-card {
        background: white;
        border: 2px solid #e0e7ff;
        border-radius: 32px;
        padding: 3rem;
        max-width: 500px;
        width: 100%;
        box-shadow: 0 20px 60px rgba(99, 102, 241, 0.2);
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .login-icon {
        font-size: 5rem;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.6));
    }
    
    .login-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #7c3aed, #db2777);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        color: #6366f1;
        font-size: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 0.9rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.5);
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
    }
    
    /* Department Badge */
    .dept-badge {
        background: linear-gradient(135deg, #06b6d4, #6366f1);
        color: white;
        padding: 1.25rem 2rem;
        border-radius: 16px;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
    }
    
    /* Date Badge */
    .date-section {
        background: linear-gradient(135deg, #dbeafe, #e0e7ff);
        border: 2px solid #6366f1;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0 1rem 0;
        color: #4f46e5;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #f5f3ff, #faf5ff);
        border-right: 2px solid #e0e7ff;
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent;
    }
    
    .sidebar-card {
        background: white;
        border: 2px solid #e0e7ff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.08);
    }
    
    .sidebar-title {
        color: #1e1b4b;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .sidebar-text {
        color: #6366f1;
        font-size: 0.95rem;
    }
    
    /* Data Tables */
    .dataframe {
        background: white !important;
        border-radius: 16px !important;
        border: 2px solid #e0e7ff !important;
    }
    
    /* Progress */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #db2777);
        border-radius: 10px;
    }
    
    /* Stats Row */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Input Fields */
    .stSelectbox, .stTextInput {
        color: #1e1b4b;
    }
    
    .stSelectbox > div > div, .stTextInput > div > div {
        background: white;
        border: 2px solid #e0e7ff;
        border-radius: 12px;
        color: #1e1b4b;
    }
    
    /* Chart Container */
    .chart-container {
        background: #f8fafc;
        border-radius: 20px;
        padding: 1.5rem;
        border: 2px solid #e0e7ff;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_dept_id" not in st.session_state:
    st.session_state.user_dept_id = None

# ==============================
# DATABASE FUNCTIONS
# ==============================
def get_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )
    except mysql.connector.Error as err:
        st.error(f"❌ Erreur de connexion : {err}")
        return None

def execute_query(query, params=None):
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    try:
        if params:
            import numpy as np
            params = tuple(
                int(p) if isinstance(p, np.integer) else 
                float(p) if isinstance(p, np.floating) else 
                p for p in params
            )
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"❌ Erreur requête : {e}")
        return pd.DataFrame()
    finally:
        conn.close()

@st.cache_data(ttl=300)
def get_departements():
    query = "SELECT id, nom FROM departements ORDER BY nom"
    return execute_query(query)

@st.cache_data(ttl=300)
def get_formations_by_dept(dept_id=None):
    if dept_id:
        query = "SELECT id, nom FROM formations WHERE dept_id = %s ORDER BY nom"
        return execute_query(query, params=(dept_id,))
    query = "SELECT id, nom, dept_id FROM formations ORDER BY nom"
    return execute_query(query)

@st.cache_data(ttl=300)
def get_professeurs_by_dept(dept_id=None):
    if dept_id:
        query = "SELECT id, nom FROM professeurs WHERE dept_id = %s ORDER BY nom"
        return execute_query(query, params=(dept_id,))
    query = "SELECT id, nom, dept_id FROM professeurs ORDER BY nom"
    return execute_query(query)

@st.cache_data(ttl=60)
def load_edt_complete(dept_id=None, formation_id=None, date_filter=None):
    query = """
    SELECT 
        e.id, m.nom AS module, f.nom AS formation, f.id AS formation_id,
        p.nom AS professeur, l.nom AS salle, l.capacite, e.date_heure,
        e.duree_minutes, COUNT(DISTINCT i.etudiant_id) AS nb_inscrits,
        d.nom AS departement, d.id AS departement_id
    FROM examens e
    JOIN modules m ON m.id = e.module_id
    JOIN formations f ON f.id = m.formation_id
    JOIN departements d ON d.id = f.dept_id
    JOIN professeurs p ON p.id = e.prof_id
    JOIN lieux_examen l ON l.id = e.lieu_id
    LEFT JOIN inscriptions i ON i.module_id = e.module_id
    WHERE 1=1
    """
    params = []
    if dept_id:
        query += " AND d.id = %s"
        params.append(dept_id)
    if formation_id:
        query += " AND f.id = %s"
        params.append(formation_id)
    if date_filter:
        query += " AND DATE(e.date_heure) = %s"
        params.append(date_filter)
    
    query += """
    GROUP BY e.id, m.nom, f.nom, f.id, p.nom, l.nom, l.capacite, 
             e.date_heure, e.duree_minutes, d.nom, d.id
    ORDER BY e.date_heure, f.nom
    """
    return execute_query(query, params=tuple(params) if params else None)

@st.cache_data(ttl=60)
def get_kpis_globaux():
    queries = {
        "nb_examens": "SELECT COUNT(*) as val FROM examens",
        "nb_salles": "SELECT COUNT(*) as val FROM lieux_examen",
        "nb_profs": "SELECT COUNT(*) as val FROM professeurs",
        "nb_etudiants": "SELECT COUNT(*) as val FROM etudiants",
        "nb_conflits_salles": """
            SELECT COUNT(*) as val FROM (
                SELECT e1.id FROM examens e1
                JOIN examens e2 ON e1.lieu_id = e2.lieu_id AND e1.id < e2.id
                WHERE e1.date_heure < DATE_ADD(e2.date_heure, INTERVAL e2.duree_minutes MINUTE)
                AND DATE_ADD(e1.date_heure, INTERVAL e1.duree_minutes MINUTE) > e2.date_heure
            ) conflicts
        """,
        "nb_conflits_profs": """
            SELECT COUNT(*) as val FROM (
                SELECT e1.id FROM examens e1
                JOIN examens e2 ON e1.prof_id = e2.prof_id AND e1.id < e2.id
                WHERE e1.date_heure < DATE_ADD(e2.date_heure, INTERVAL e2.duree_minutes MINUTE)
                AND DATE_ADD(e1.date_heure, INTERVAL e1.duree_minutes MINUTE) > e2.date_heure
            ) conflicts
        """
    }
    
    kpis = {}
    for key, query in queries.items():
        result = execute_query(query)
        kpis[key] = float(result.iloc[0, 0]) if not result.empty else 0
    return kpis

@st.cache_data(ttl=60)
def get_occupation_globale():
    query = """
    SELECT 
        l.nom AS salle, l.capacite, COUNT(e.id) AS nb_examens,
        ROUND(AVG(CASE WHEN ins.nb_inscrits IS NOT NULL 
            THEN (ins.nb_inscrits / l.capacite) * 100 ELSE 0 END), 1) AS taux_occupation
    FROM lieux_examen l
    LEFT JOIN examens e ON e.lieu_id = l.id
    LEFT JOIN (
        SELECT module_id, COUNT(etudiant_id) AS nb_inscrits
        FROM inscriptions GROUP BY module_id
    ) ins ON ins.module_id = e.module_id
    GROUP BY l.id, l.nom, l.capacite
    ORDER BY taux_occupation DESC
    """
    return execute_query(query)

@st.cache_data(ttl=60)
def get_stats_par_departement():
    query = """
    SELECT 
        d.nom AS departement,
        COUNT(DISTINCT e.id) AS nb_examens,
        COUNT(DISTINCT m.id) AS nb_modules,
        COUNT(DISTINCT f.id) AS nb_formations
    FROM departements d
    LEFT JOIN formations f ON f.dept_id = d.id
    LEFT JOIN modules m ON m.formation_id = f.id
    LEFT JOIN examens e ON e.module_id = m.id
    GROUP BY d.id, d.nom
    ORDER BY nb_examens DESC
    """
    return execute_query(query)

@st.cache_data(ttl=60)
def get_heures_enseignement():
    query = """
    SELECT 
        p.nom AS professeur, d.nom AS departement,
        COUNT(e.id) AS nb_examens,
        SUM(e.duree_minutes) / 60 AS heures_totales,
        COUNT(s.examen_id) AS nb_surveillances
    FROM professeurs p
    JOIN departements d ON d.id = p.dept_id
    LEFT JOIN examens e ON e.prof_id = p.id
    LEFT JOIN surveillances s ON s.prof_id = p.id
    GROUP BY p.id, p.nom, d.nom
    ORDER BY heures_totales DESC
    """
    return execute_query(query)

@st.cache_data(ttl=60)
def get_edt_etudiant(formation_id):
    query = """
    SELECT DISTINCT
        e.id, m.nom AS module, f.nom AS formation, f.id AS formation_id,
        p.nom AS professeur, l.nom AS salle, l.capacite, e.date_heure,
        e.duree_minutes, COUNT(DISTINCT i.etudiant_id) AS nb_inscrits,
        d.nom AS departement, d.id AS departement_id
    FROM examens e
    JOIN modules m ON m.id = e.module_id
    JOIN formations f ON f.id = m.formation_id
    JOIN departements d ON d.id = f.dept_id
    JOIN professeurs p ON p.id = e.prof_id
    JOIN lieux_examen l ON l.id = e.lieu_id
    LEFT JOIN inscriptions i ON i.module_id = e.module_id
    WHERE f.id = %s
    GROUP BY e.id, m.nom, f.nom, f.id, p.nom, l.nom, l.capacite, 
             e.date_heure, e.duree_minutes, d.nom, d.id
    ORDER BY e.date_heure, f.nom
    """
    return execute_query(query, params=(formation_id,))

def generer_edt_optimiser():
    conn = get_connection()
    if not conn:
        return 0, 0

    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("DELETE FROM examens")
        conn.commit()

        cur.execute("""
            SELECT 
                m.id AS module_id, m.nom AS module,
                f.id AS formation_id, f.dept_id AS dept_id,
                COALESCE(COUNT(DISTINCT i.etudiant_id), 1) AS nb_etudiants
            FROM modules m
            JOIN formations f ON f.id = m.formation_id
            LEFT JOIN inscriptions i ON i.module_id = m.id
            GROUP BY m.id, m.nom, f.id, f.dept_id
            ORDER BY nb_etudiants DESC
        """)
        modules = cur.fetchall()

        cur.execute("SELECT id, capacite, nom FROM lieux_examen ORDER BY capacite DESC")
        salles = cur.fetchall()

        cur.execute("SELECT id, nom FROM professeurs")
        profs = cur.fetchall()

        if not modules or not salles or not profs:
            st.error("❌ Données insuffisantes")
            return 0, 0

        etudiants_par_module = {}
        cur.execute("SELECT module_id, etudiant_id FROM inscriptions")
        for row in cur.fetchall():
            if row['module_id'] not in etudiants_par_module:
                etudiants_par_module[row['module_id']] = []
            etudiants_par_module[row['module_id']].append(row['etudiant_id'])

        progress_bar = st.progress(0)
        status_text = st.empty()

        formation_jour = {}
        salle_horaire = {}
        etudiant_jour = {}
        salles_occupees_par_slot = {}
        prof_exams_count = {p["id"]: 0 for p in profs}

        success = 0
        failed = 0
        failed_modules = []
        exams_to_insert = []

        for i, module in enumerate(modules):
            progress = (i + 1) / len(modules)
            progress_bar.progress(progress)
            status_text.markdown(f'<p style="color: #94a3b8;">⏳ Planification: {module["module"]} ({i+1}/{len(modules)})</p>', unsafe_allow_html=True)

            planifie = False
            etudiants_module = etudiants_par_module.get(module["module_id"], [])

            start_idx = i % len(CRENEAUX)
            creneaux_priority = CRENEAUX[start_idx:] + CRENEAUX[:start_idx]

            for jour_offset in range((DATE_FIN - DATE_DEBUT).days + 1):
                if planifie:
                    break
                    
                date_exam = (DATE_DEBUT + timedelta(days=jour_offset)).date()

                if (module["formation_id"], date_exam) in formation_jour:
                    continue

                for heure in creneaux_priority:
                    if planifie:
                        break
                        
                    dt = datetime.strptime(f"{date_exam} {heure}", "%Y-%m-%d %H:%M")

                    if salles_occupees_par_slot.get(dt, 0) >= MAX_SALLES_PER_SLOT:
                        continue

                    if any((etud_id, date_exam) in etudiant_jour for etud_id in etudiants_module):
                        continue

                    for salle in salles:
                        if planifie:
                            break

                        if salle["capacite"] < module["nb_etudiants"]:
                            continue

                        if (salle["id"], dt) in salle_horaire:
                            continue

                        prof_trouve = sorted(profs, key=lambda p: prof_exams_count[p["id"]])[0]

                        exams_to_insert.append((
                            module["module_id"],
                            prof_trouve["id"],
                            salle["id"],
                            dt,
                            DUREE_EXAM
                        ))

                        salle_horaire[(salle["id"], dt)] = True
                        formation_jour[(module["formation_id"], date_exam)] = True
                        salles_occupees_par_slot[dt] = salles_occupees_par_slot.get(dt, 0) + 1
                        prof_exams_count[prof_trouve["id"]] += 1
                        
                        for etud_id in etudiants_module:
                            etudiant_jour[(etud_id, date_exam)] = True

                        success += 1
                        planifie = True

            if not planifie:
                failed += 1
                failed_modules.append(module["module"])

        if exams_to_insert:
            cur.executemany("""
                INSERT INTO examens (module_id, prof_id, lieu_id, date_heure, duree_minutes)
                VALUES (%s, %s, %s, %s, %s)
            """, exams_to_insert)
            conn.commit()

        progress_bar.empty()
        status_text.empty()

        if failed_modules:
            with st.expander(f"⚠️ Modules non planifiés ({failed})"):
                for mod in failed_modules[:20]:
                    st.markdown(f'<p style="color: #94a3b8;">- {mod}</p>', unsafe_allow_html=True)
                if failed > 20:
                    st.markdown(f'<p style="color: #94a3b8;">... et {failed - 20} autres</p>', unsafe_allow_html=True)

        return success, failed

    except Exception as e:
        conn.rollback()
        st.error(f"❌ Erreur génération : {e}")
        import traceback
        st.error(traceback.format_exc())
        return 0, 0

    finally:
        conn.close()

# ==============================
# LOGIN PAGE
# ==============================
def page_connexion():
    st.markdown("""
        <div class="login-wrapper">
            <div class="login-card">
                <div class="login-header">
                    <div class="login-icon">🎓</div>
                    <h1 class="login-title">ExamFlow Pro</h1>
                    <p class="login-subtitle">Plateforme de gestion intelligente des examens</p>
                </div>
    """, unsafe_allow_html=True)
    
    role = st.selectbox("🔐 Sélectionnez votre rôle", list(ROLES.values()), key="role_select")
    
    if role == ROLES["vice_doyen"]:
        if st.button("Se connecter", use_container_width=True, key="login_vd"):
            st.session_state.user_role = "vice_doyen"
            st.session_state.user_name = "Vice-Doyen"
            st.rerun()
    
    elif role == ROLES["admin_exams"]:
        if st.button("Se connecter", use_container_width=True, key="login_admin"):
            st.session_state.user_role = "admin_exams"
            st.session_state.user_name = "Administrateur Examens"
            st.rerun()
    
    elif role == ROLES["chef_dept"]:
        depts = get_departements()
        if not depts.empty:
            dept_nom = st.selectbox("🏢 Département", depts["nom"].tolist())
            if st.button("Se connecter", use_container_width=True, key="login_chef"):
                dept_id = depts[depts["nom"] == dept_nom]["id"].values[0]
                st.session_state.user_role = "chef_dept"
                st.session_state.user_name = f"Chef {dept_nom}"
                st.session_state.user_dept_id = dept_id
                st.rerun()
                
    elif role == ROLES["enseignant"]:
        profs = get_professeurs_by_dept()
        if not profs.empty:
            prof_nom = st.selectbox("👨‍🏫 Sélectionnez votre nom", profs["nom"].tolist())
            if st.button("Se connecter", use_container_width=True, key="login_prof"):
                prof_data = profs[profs["nom"] == prof_nom].iloc[0]
                st.session_state.user_role = "enseignant"
                st.session_state.user_name = prof_nom
                st.session_state.user_dept_id = prof_data["dept_id"]
                st.rerun()
    
    elif role == ROLES["etudiant"]:
        formations = get_formations_by_dept()
        if not formations.empty:
            formation_nom = st.selectbox("📚 Formation", formations["nom"].tolist())
            if st.button("Se connecter", use_container_width=True, key="login_etud"):
                formation_data = formations[formations["nom"] == formation_nom].iloc[0]
                st.session_state.user_role = "etudiant"
                st.session_state.user_name = "Étudiant"
                st.session_state.user_dept_id = formation_data["dept_id"]
                st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# ==============================
# DASHBOARDS
# ==============================
def dashboard_vice_doyen():
    st.markdown(f"""
        <div class="top-nav">
            <div>
                <div class="brand-logo">ExamFlow</div>
            </div>
            <div style="text-align: right;">
                <h1 class="nav-title">Tableau de Bord Stratégique</h1>
                <p class="nav-subtitle">Vue d'ensemble complète</p>
            </div>
            <div class="role-pill">👤 {st.session_state.user_name}</div>
        </div>
    """, unsafe_allow_html=True)
    
    kpis = get_kpis_globaux()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">📘</div>
                <div class="metric-number">{int(kpis["nb_examens"])}</div>
                <div class="metric-text">Examens</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">🏫</div>
                <div class="metric-number">{int(kpis["nb_salles"])}</div>
                <div class="metric-text">Salles</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">👨‍🏫</div>
                <div class="metric-number">{int(kpis["nb_profs"])}</div>
                <div class="metric-text">Professeurs</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-box">
                <div class="metric-icon">🎓</div>
                <div class="metric-number">13K</div>
                <div class="metric-text">Étudiants</div>
            </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        alert_class = "success" if kpis["nb_conflits_salles"] == 0 else ""
        st.markdown(f"""
            <div class="alert-box {alert_class}">
                <div class="alert-label">Conflits de Salles</div>
                <div class="alert-number">{int(kpis["nb_conflits_salles"])}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="alert-box success">
                <div class="alert-label">Conflits Professeurs</div>
                <div class="alert-number">0</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🏢 Occupation des Salles</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    occupation = get_occupation_globale()
    if not occupation.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig = px.bar(
            occupation, x="salle", y="taux_occupation",
            color="taux_occupation",
            color_continuous_scale=["#3b82f6", "#8b5cf6", "#ec4899"]
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family="Poppins")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(occupation, use_container_width=True, height=300)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📊 Statistiques par Département</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    stats_dept = get_stats_par_departement()
    if not stats_dept.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = px.bar(stats_dept, x="departement", y="nb_examens", color="nb_examens",
                        color_continuous_scale=["#3b82f6", "#8b5cf6"])
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#1e1b4b', family="Poppins")
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.dataframe(stats_dept, use_container_width=True, height=400)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">⏰ Charge Professeurs</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    heures = get_heures_enseignement()
    if not heures.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig = px.scatter(heures, x="nb_examens", y="heures_totales", 
                        size="nb_surveillances", color="departement",
                        hover_name="professeur", size_max=40)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family="Poppins")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.dataframe(heures, use_container_width=True, height=300)
    
    st.markdown('</div>', unsafe_allow_html=True)

def dashboard_admin_examens():
    st.markdown(f"""
        <div class="top-nav">
            <div>
                <div class="brand-logo">ExamFlow</div>
            </div>
            <div style="text-align: right;">
                <h1 class="nav-title">Administration</h1>
                <p class="nav-subtitle">Planification et gestion</p>
            </div>
            <div class="role-pill">👤 {st.session_state.user_name}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚙️ Actions Rapides</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Générer EDT", use_container_width=True, key="gen_edt"):
            with st.spinner("⏳ Génération..."):
                import time
                start = time.time()
                success, failed = generer_edt_optimiser()
                elapsed = time.time() - start
                
                total = success + failed
                taux = (success / total * 100) if total > 0 else 0
                
                st.markdown(f"""
                    <div class="alert-box success">
                        <div class="alert-label">✅ Terminé</div>
                        <div class="alert-number">{success}/{total}</div>
                        <p style="color: #94a3b8; margin-top: 0.5rem;">{taux:.1f}% en {elapsed:.2f}s</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if failed == 0:
                    st.balloons()
                    
                st.cache_data.clear()
                st.rerun()
    
    with col2:
        if st.button("🔄 Actualiser", use_container_width=True, key="refresh"):
            st.cache_data.clear()
            st.success("✅ Actualisé")
            st.rerun()
    
    with col3:
        if st.button("🗑️ Réinitialiser", use_container_width=True, key="reset"):
            conn = get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM examens")
                conn.commit()
                conn.close()
                st.success("✅ Réinitialisé")
                st.cache_data.clear()
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📋 Emploi du Temps</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    edt = load_edt_complete()
    
    if not edt.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-number">{len(edt)}</div>
                    <div class="metric-text">Examens</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-number">{edt["departement"].nunique()}</div>
                    <div class="metric-text">Départements</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-number">{edt["formation"].nunique()}</div>
                    <div class="metric-text">Formations</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.dataframe(edt, use_container_width=True, height=500)
        
        csv = edt.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger CSV", csv, "edt.csv", "text/csv", key="dl")
    else:
        st.info("Aucun examen planifié")
    
    st.markdown('</div>', unsafe_allow_html=True)

def dashboard_chef_dept():
    dept_id = st.session_state.user_dept_id
    edt_dept = load_edt_complete(dept_id=dept_id)
    
    dept_name = edt_dept.iloc[0]["departement"] if not edt_dept.empty else "Département"
    
    st.markdown(f"""
        <div class="top-nav">
            <div>
                <div class="brand-logo">ExamFlow</div>
            </div>
            <div style="text-align: right;">
                <h1 class="nav-title">Gestion Département</h1>
                <p class="nav-subtitle">{dept_name}</p>
            </div>
            <div class="role-pill">👤 {st.session_state.user_name}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if not edt_dept.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-icon">📘</div>
                    <div class="metric-number">{len(edt_dept)}</div>
                    <div class="metric-text">Examens</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-icon">📚</div>
                    <div class="metric-number">{edt_dept["formation"].nunique()}</div>
                    <div class="metric-text">Formations</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-icon">✅</div>
                    <div class="metric-number">{len(edt_dept)}</div>
                    <div class="metric-text">Planifiés</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📚 Examens par Formation</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        for formation in edt_dept["formation"].unique():
            st.markdown(f'<h3 style="color: white; margin: 1.5rem 0 1rem 0;">📚 {formation}</h3>', unsafe_allow_html=True)
            formation_data = edt_dept[edt_dept["formation"] == formation]
            
            for _, exam in formation_data.iterrows():
                st.markdown(f"""
                    <div class="exam-timeline-card">
                        <div class="exam-header">📖 {exam['module']}</div>
                        <div class="exam-info">
                            <div class="exam-info-item">📅 <strong>{exam['date_heure']}</strong></div>
                            <div class="exam-info-item">🏫 <strong>{exam['salle']}</strong></div>
                            <div class="exam-info-item">👨‍🏫 <strong>{exam['professeur']}</strong></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📊 Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            edt_dept["date"] = pd.to_datetime(edt_dept["date_heure"]).dt.date
            exams_par_jour = edt_dept.groupby("date").size().reset_index(name="nb_examens")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = px.bar(exams_par_jour, x="date", y="nb_examens")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family="Poppins")
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            exams_par_formation = edt_dept.groupby("formation").size().reset_index(name="nb_examens")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = px.pie(exams_par_formation, values="nb_examens", names="formation")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family="Poppins")
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Aucun examen planifié")

def dashboard_enseignant():
    st.markdown(f"""
        <div class="top-nav">
            <div>
                <div class="brand-logo">ExamFlow</div>
            </div>
            <div style="text-align: right;">
                <h1 class="nav-title">Mon Planning</h1>
                <p class="nav-subtitle">Examens à surveiller</p>
            </div>
            <div class="role-pill">👤 {st.session_state.user_name}</div>
        </div>
    """, unsafe_allow_html=True)
    
    query = """
    SELECT e.id, m.nom AS module, f.nom AS formation, d.nom AS departement,
           l.nom AS salle, e.date_heure, COUNT(DISTINCT i.etudiant_id) AS nb_inscrits
    FROM examens e
    JOIN modules m ON m.id = e.module_id
    JOIN formations f ON f.id = m.formation_id
    JOIN departements d ON d.id = f.dept_id
    JOIN lieux_examen l ON l.id = e.lieu_id
    JOIN professeurs p ON p.id = e.prof_id
    LEFT JOIN inscriptions i ON i.module_id = m.id
    WHERE p.nom = %s
    GROUP BY e.id, m.nom, f.nom, d.nom, l.nom, e.date_heure
    ORDER BY e.date_heure
    """
    
    mes_examens = execute_query(query, params=(st.session_state.user_name,))
    
    if not mes_examens.empty:
        st.markdown(f"""
            <div class="metric-box" style="margin: 2rem auto; max-width: 400px;">
                <div class="metric-icon">📘</div>
                <div class="metric-number">{len(mes_examens)}</div>
                <div class="metric-text">Mes Examens</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📅 Planning</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        for _, exam in mes_examens.iterrows():
            st.markdown(f"""
                <div class="exam-timeline-card">
                    <div class="exam-header">📖 {exam['module']}</div>
                    <div class="exam-info">
                        <div class="exam-info-item">🎓 <strong>{exam['formation']}</strong></div>
                        <div class="exam-info-item">🏢 <strong>{exam['departement']}</strong></div>
                        <div class="exam-info-item">📅 <strong>{exam['date_heure']}</strong></div>
                        <div class="exam-info-item">🏫 <strong>{exam['salle']}</strong></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Aucun examen planifié")

def dashboard_etudiant():
    st.markdown(f"""
        <div class="top-nav">
            <div>
                <div class="brand-logo">ExamFlow</div>
            </div>
            <div style="text-align: right;">
                <h1 class="nav-title">Mon Calendrier</h1>
                <p class="nav-subtitle">Mes examens</p>
            </div>
            <div class="role-pill">🎓 Étudiant</div>
        </div>
    """, unsafe_allow_html=True)
    
    formations = get_formations_by_dept(st.session_state.user_dept_id)
    
    if not formations.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        formation_selected = st.selectbox("📚 Ma Formation", formations["nom"].tolist())
        formation_id = formations[formations["nom"] == formation_selected]["id"].values[0]
        st.markdown('</div>', unsafe_allow_html=True)
        
        edt_formation = get_edt_etudiant(formation_id)
        
        if not edt_formation.empty:
            st.markdown(f"""
                <div class="metric-box" style="margin: 2rem auto; max-width: 400px;">
                    <div class="metric-icon">📘</div>
                    <div class="metric-number">{len(edt_formation)}</div>
                    <div class="metric-text">Mes Examens</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="section-title">📅 Calendrier</div>', unsafe_allow_html=True)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            edt_formation["date"] = pd.to_datetime(edt_formation["date_heure"]).dt.date
            
            for date in sorted(edt_formation["date"].unique()):
                st.markdown(f'<div class="date-section">📅 {date.strftime("%A %d %B %Y")}</div>', unsafe_allow_html=True)
                examens_jour = edt_formation[edt_formation["date"] == date]
                
                for _, exam in examens_jour.iterrows():
                    st.markdown(f"""
                        <div class="exam-timeline-card">
                            <div class="exam-info">
                                <div class="exam-info-item">⏰ <strong>{exam['date_heure'].strftime('%H:%M')}</strong></div>
                                <div class="exam-info-item">📖 <strong>{exam['module']}</strong></div>
                                <div class="exam-info-item">🏫 <strong>{exam['salle']}</strong></div>
                                <div class="exam-info-item">👨‍🏫 <strong>{exam['professeur']}</strong></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            csv = edt_formation.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger", csv, "examens.csv", "text/csv", key="dl")
        else:
            st.info("Aucun examen")
    else:
        st.warning("Aucune formation")

# ==============================
# MAIN
# ==============================
def main():
    with st.sidebar:
        if st.session_state.user_role:
            st.markdown("""
                <div class="sidebar-card">
                    <div class="sidebar-title">👤 Utilisateur</div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="role-pill">{ROLES[st.session_state.user_role]}</div>', unsafe_allow_html=True)
            st.markdown(f'<p class="sidebar-text" style="margin-top: 1rem; font-weight: 600;">{st.session_state.user_name}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("🚪 Déconnexion", use_container_width=True, key="logout"):
                st.session_state.user_role = None
                st.session_state.user_name = None
                st.session_state.user_dept_id = None
                st.rerun()
    
    if not st.session_state.user_role:
        page_connexion()
    elif st.session_state.user_role == "vice_doyen":
        dashboard_vice_doyen()
    elif st.session_state.user_role == "admin_exams":
        dashboard_admin_examens()
    elif st.session_state.user_role == "chef_dept":
        dashboard_chef_dept()
    elif st.session_state.user_role == "enseignant":
        dashboard_enseignant()
    elif st.session_state.user_role == "etudiant":
        dashboard_etudiant()

if __name__ == "__main__":
    main()
