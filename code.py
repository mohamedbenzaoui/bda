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
    page_title="ExamPro - Gestion des Examens",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================== 
# NOUVEAU DESIGN CSS MODERNE
# ============================== 
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset et typographie */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fond principal avec gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Container principal */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin: 2rem auto;
    }
    
    /* Header moderne */
    .modern-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .modern-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .modern-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }
    
    /* Cards modernes */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card h3 {
        color: #667eea;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 0.5rem 0;
    }
    
    .metric-card .value {
        color: #2d3748;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-card .label {
        color: #718096;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
    
    /* Cartes d'alertes */
    .alert-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    }
    
    .success-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Boutons modernes */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Section headers */
    .section-header {
        color: #2d3748;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Exam card */
    .exam-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #667eea;
        transition: all 0.2s ease;
    }
    
    .exam-card:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transform: translateX(5px);
    }
    
    .exam-card h4 {
        color: #667eea;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .exam-info {
        color: #4a5568;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-primary {
        background: #667eea;
        color: white;
    }
    
    .badge-success {
        background: #48bb78;
        color: white;
    }
    
    .badge-warning {
        background: #ed8936;
        color: white;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    
    /* Login card */
    .login-card {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        max-width: 500px;
        margin: 4rem auto;
    }
    
    .login-card h2 {
        color: #667eea;
        text-align: center;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    
    /* Metrics container */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Status badge in sidebar */
    .sidebar-status {
        background: rgba(255, 255, 255, 0.2);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
</style>
""", unsafe_allow_html=True)

# ============================== 
# GESTION SESSION
# ============================== 
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_dept_id" not in st.session_state:
    st.session_state.user_dept_id = None

# ============================== 
# CONNEXION BDD
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
                float(p) if isinstance(p, np.floating) else p 
                for p in params
            )
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"❌ Erreur requête : {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# ============================== 
# REQUÊTES DONNÉES
# ============================== 
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
        SELECT e.id, m.nom AS module, f.nom AS formation, f.id AS formation_id,
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
        SELECT l.nom AS salle, l.capacite, COUNT(e.id) AS nb_examens,
               ROUND(AVG(CASE WHEN ins.nb_inscrits IS NOT NULL 
                              THEN (ins.nb_inscrits / l.capacite) * 100 
                              ELSE 0 END), 1) AS taux_occupation
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
        SELECT d.nom AS departement, COUNT(DISTINCT e.id) AS nb_examens,
               COUNT(DISTINCT m.id) AS nb_modules, COUNT(DISTINCT f.id) AS nb_formations
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
        SELECT p.nom AS professeur, d.nom AS departement, COUNT(e.id) AS nb_examens,
               SUM(e.duree_minutes) / 60 AS heures_totales, COUNT(s.examen_id) AS nb_surveillances
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
        SELECT DISTINCT e.id, m.nom AS module, f.nom AS formation, f.id AS formation_id,
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

# ============================== 
# GÉNÉRATION EDT
# ============================== 
def generer_edt_optimiser():
    conn = get_connection()
    if not conn:
        return 0, 0
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("DELETE FROM examens")
        conn.commit()
        
        cur.execute("""
            SELECT m.id AS module_id, m.nom AS module, f.id AS formation_id, 
                   f.dept_id AS dept_id, COALESCE(COUNT(DISTINCT i.etudiant_id), 1) AS nb_etudiants
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
            status_text.text(f"⏳ Planification: {module['module']} ({i+1}/{len(modules)})")
            
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
                            module["module_id"], prof_trouve["id"], salle["id"], dt, DUREE_EXAM
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
                    st.write(f"- {mod}")
                if failed > 20:
                    st.write(f"... et {failed - 20} autres")
        
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
# PAGE CONNEXION
# ============================== 
def page_connexion():
    st.markdown("""
    <div class="login-card">
        <h2>🎓 ExamPro</h2>
        <p style="text-align: center; color: #718096; margin-bottom: 2rem;">
            Plateforme de Gestion Intelligente des Examens
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        role = st.selectbox("Sélectionnez votre profil", list(ROLES.values()))
        
        if role == ROLES["vice_doyen"]:
            if st.button("🔐 Se connecter", use_container_width=True):
                st.session_state.user_role = "vice_doyen"
                st.session_state.user_name = "Vice-Doyen"
                st.rerun()
        
        elif role == ROLES["admin_exams"]:
            if st.button("🔐 Se connecter", use_container_width=True):
                st.session_state.user_role = "admin_exams"
                st.session_state.user_name = "Administrateur Examens"
                st.rerun()
        
        elif role == ROLES["chef_dept"]:
            depts = get_departements()
            if not depts.empty:
                dept_nom = st.selectbox("Département", depts["nom"].tolist())
                if st.button("🔐 Se connecter", use_container_width=True):
                    dept_id = depts[depts["nom"] == dept_nom]["id"].values[0]
                    st.session_state.user_role = "chef_dept"
                    st.session_state.user_name = f"Chef {dept_nom}"
                    st.session_state.user_dept_id = dept_id
                    st.rerun()
        
        elif role == ROLES["enseignant"]:
            profs = get_professeurs_by_dept()
            if not profs.empty:
                prof_nom = st.selectbox("Sélectionnez votre nom", profs["nom"].tolist())
                if st.button("🔐 Se connecter", use_container_width=True):
                    prof_data = profs[profs["nom"] == prof_nom].iloc[0]
                    st.session_state.user_role = "enseignant"
                    st.session_state.user_name = prof_nom
                    st.session_state.user_dept_id = prof_data["dept_id"]
                    st.rerun()
        
        elif role == ROLES["etudiant"]:
            formations = get_formations_by_dept()
            if not formations.empty:
                formation_nom = st.selectbox("Formation", formations["nom"].tolist())
                if st.button("🔐 Se connecter", use_container_width=True):
                    formation_data = formations[formations["nom"] == formation_nom].iloc[0]
                    st.session_state.user_role = "etudiant"
                    st.session_state.user_name = "Étudiant"
                    st.session_state.user_dept_id = formation_data["dept_id"]
                    st.rerun()

# ============================== 
# DASHBOARDS
# ============================== 
def dashboard_vice_doyen():
    st.markdown(f"""
    <div class="modern-header">
        <h1>📊 Tableau de Bord Stratégique</h1>
        <p>Vue d'ensemble globale - {st.session_state.user_name}</p>
    </div>
    """, unsafe_allow_html=True)
    
    kpis = get_kpis_globaux()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📘 Examens</h3>
            <p class="value">{int(kpis["nb_examens"])}</p>
            <p class="label">Planifiés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🏫 Salles</h3>
            <p class="value">{int(kpis["nb_salles"])}</p>
            <p class="label">Disponibles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👨‍🏫 Professeurs</h3>
            <p class="value">{int(kpis["nb_profs"])}</p>
            <p class="label">Actifs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎓 Étudiants</h3>
            <p class="value">13000</p>
            <p class="label">Inscrits</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if kpis["nb_conflits_salles"] > 0:
            st.markdown(f"""
            <div class="alert-card">
                <h3 style="margin:0;">⚠️ Conflits Salles</h3>
                <p class="value" style="font-size:2rem;">{int(kpis["nb_conflits_salles"])}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-card">
                <h3 style="margin:0;">✅ Conflits Salles</h3>
                <p class="value" style="font-size:2rem;">0</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if kpis["nb_conflits_profs"] > 0:
            st.markdown(f"""
            <div class="alert-card">
                <h3 style="margin:0;">⚠️ Conflits Professeurs</h3>
                <p class="value" style="font-size:2rem;">{int(kpis["nb_conflits_profs"])}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-card">
                <h3 style="margin:0;">✅ Conflits Professeurs</h3>
                <p class="value" style="font-size:2rem;">0</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">📊 Occupation des Salles</p>', unsafe_allow_html=True)
    
    occupation = get_occupation_globale()
    if not occupation.empty:
        fig = px.bar(
            occupation, x="salle", y="taux_occupation",
            color="taux_occupation", color_continuous_scale="Viridis",
            labels={"salle": "Salle", "taux_occupation": "Taux d'occupation (%)"}
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(occupation, use_container_width=True, height=300)
    
    st.markdown('<p class="section-header">🏢 Statistiques par Département</p>', unsafe_allow_html=True)
    
    stats_dept = get_stats_par_departement()
    if not stats_dept.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(stats_dept, x="departement", y="nb_examens", 
                        color="nb_examens", color_continuous_scale="Blues")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(stats_dept, use_container_width=True, height=400)

def dashboard_admin_examens():
    st.markdown(f"""
    <div class="modern-header">
        <h1>🛠️ Centre d'Administration</h1>
        <p>Gestion et planification - {st.session_state.user_name}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Générer EDT Complet", use_container_width=True):
            with st.spinner("⏳ Génération en cours..."):
                import time
                start = time.time()
                success, failed = generer_edt_optimiser()
                elapsed = time.time() - start
                total = success + failed
                taux = (success / total * 100) if total > 0 else 0
                st.success(f"✅ {success}/{total} modules planifiés ({taux:.1f}%) en {elapsed:.2f}s")
                if failed == 0:
                    st.balloons()
                st.cache_data.clear()
                st.rerun()
    
    with col2:
        if st.button("🔄 Actualiser Données", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Données actualisées")
            st.rerun()
    
    with col3:
        if st.button("🗑️ Réinitialiser EDT", use_container_width=True):
            conn = get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM examens")
                conn.commit()
                conn.close()
                st.success("✅ EDT réinitialisé")
                st.cache_data.clear()
                st.rerun()
    
    st.markdown('<p class="section-header">📋 Emploi du Temps Complet</p>', unsafe_allow_html=True)
    
    edt = load_edt_complete()
    if not edt.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Examens", len(edt))
        col2.metric("Départements", edt["departement"].nunique())
        col3.metric("Formations", edt["formation"].nunique())
        
        st.dataframe(edt, use_container_width=True, height=500)
        
        csv = edt.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger CSV", csv, "edt_complet.csv", "text/csv")
    else:
        st.info("Aucun examen planifié")

def dashboard_chef_dept():
    st.markdown(f"""
    <div class="modern-header">
        <h1>📂 Gestion Département</h1>
        <p>{st.session_state.user_name}</p>
    </div>
    """, unsafe_allow_html=True)
    
    dept_id = st.session_state.user_dept_id
    edt_dept = load_edt_complete(dept_id=dept_id)
    
    if not edt_dept.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("📘 Examens", len(edt_dept))
        col2.metric("📚 Formations", edt_dept["formation"].nunique())
        col3.metric("✅ Validés", len(edt_dept))
        
        st.markdown('<p class="section-header">📚 Examens par Formation</p>', unsafe_allow_html=True)
        
        for formation in edt_dept["formation"].unique():
            with st.expander(f"📖 {formation}", expanded=True):
                formation_data = edt_dept[edt_dept["formation"] == formation]
                for _, exam in formation_data.iterrows():
                    st.markdown(f"""
                    <div class="exam-card">
                        <h4>{exam['module']}</h4>
                        <div class="exam-info">
                            <span class="badge badge-primary">📅 {exam['date_heure']}</span>
                            <span class="badge badge-success">🏫 {exam['salle']}</span>
                            <span class="badge badge-warning">👨‍🏫 {exam['professeur']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Aucun examen planifié")

def dashboard_enseignant():
    st.markdown(f"""
    <div class="modern-header">
        <h1>👨‍🏫 Mon Planning</h1>
        <p>{st.session_state.user_name}</p>
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
        st.metric("📘 Mes Examens", len(mes_examens))
        
        st.markdown('<p class="section-header">📅 Mes Prochains Examens</p>', unsafe_allow_html=True)
        
        for _, exam in mes_examens.iterrows():
            st.markdown(f"""
            <div class="exam-card">
                <h4>📖 {exam['module']}</h4>
                <div class="exam-info">
                    <strong>Formation:</strong> {exam['formation']} ({exam['departement']})<br>
                    <span class="badge badge-primary">📅 {exam['date_heure']}</span>
                    <span class="badge badge-success">🏫 {exam['salle']}</span>
                    <span class="badge badge-warning">👥 {exam['nb_inscrits']} étudiants</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucun examen planifié")

def dashboard_etudiant():
    st.markdown(f"""
    <div class="modern-header">
        <h1>🎓 Mon Calendrier</h1>
        <p>Mes Examens</p>
    </div>
    """, unsafe_allow_html=True)
    
    formations = get_formations_by_dept(st.session_state.user_dept_id)
    if not formations.empty:
        formation_selected = st.selectbox("Ma Formation", formations["nom"].tolist())
        formation_id = formations[formations["nom"] == formation_selected]["id"].values[0]
        
        edt_formation = get_edt_etudiant(formation_id)
        
        if not edt_formation.empty:
            st.metric("📘 Mes Examens", len(edt_formation))
            
            st.markdown('<p class="section-header">📅 Calendrier</p>', unsafe_allow_html=True)
            
            edt_formation["date"] = pd.to_datetime(edt_formation["date_heure"]).dt.date
            for date in sorted(edt_formation["date"].unique()):
                st.markdown(f"#### 📅 {date.strftime('%A %d %B %Y')}")
                examens_jour = edt_formation[edt_formation["date"] == date]
                for _, exam in examens_jour.iterrows():
                    st.markdown(f"""
                    <div class="exam-card">
                        <h4>⏰ {exam['date_heure'].strftime('%H:%M')} - {exam['module']}</h4>
                        <div class="exam-info">
                            <span class="badge badge-success">🏫 {exam['salle']}</span>
                            <span class="badge badge-primary">👨‍🏫 {exam['professeur']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            csv = edt_formation.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger Mon Calendrier", csv, "mes_examens.csv")
        else:
            st.info("Aucun examen planifié")

# ============================== 
# NAVIGATION
# ============================== 
def main():
    with st.sidebar:
        if st.session_state.user_role:
            st.markdown(f"""
            <div class="sidebar-status">
                <h3 style="margin:0; font-size:1.1rem;">👤 Connecté</h3>
                <p style="margin:0.5rem 0 0 0; font-size:0.9rem;">{ROLES[st.session_state.user_role]}</p>
                <p style="margin:0.25rem 0 0 0; font-weight:600;">{st.session_state.user_name}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Déconnexion", use_container_width=True):
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
