import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Configuration identique
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

st.set_page_config(page_title="Plateforme Examens", layout="wide", initial_sidebar_state="expanded")

# Design moderne et professionnel
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Raleway:wght@300;400;600;700;900&family=Montserrat:wght@400;600;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Raleway', sans-serif;
}

/* Arrière-plan avec dégradé moderne */
.main {
    background: linear-gradient(165deg, #0a0e27 0%, #1e3a5f 35%, #2c5f7c 100%);
    min-height: 100vh;
    padding: 3rem 2rem;
}

/* Section héro principale */
.hero-section {
    background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 50%, #c44569 100%);
    padding: 4rem 3rem;
    margin-bottom: 3rem;
    clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%);
    box-shadow: 0 25px 50px rgba(255, 107, 107, 0.3);
}

.hero-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 4rem;
    font-weight: 900;
    color: #fff;
    text-align: left;
    line-height: 1.2;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 3px;
}

.hero-description {
    font-size: 1.4rem;
    color: rgba(255,255,255,0.9);
    text-align: left;
    font-weight: 300;
    max-width: 600px;
}

.user-badge-horizontal {
    display: inline-flex;
    align-items: center;
    gap: 1.5rem;
    background: rgba(255,255,255,0.2);
    padding: 1.2rem 2.5rem;
    border-radius: 50px;
    margin-top: 2rem;
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255,255,255,0.3);
}

.user-badge-icon {
    font-size: 2.5rem;
}

.user-badge-text {
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
}

/* Statistiques horizontales */
.stats-horizontal {
    display: flex;
    gap: 1.5rem;
    margin: 2rem 0;
    flex-wrap: wrap;
}

.stat-box-horizontal {
    flex: 1;
    min-width: 200px;
    background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
    padding: 2rem;
    border-radius: 15px;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 210, 255, 0.3);
    transition: all 0.3s ease;
}

.stat-box-horizontal:hover {
    transform: scale(1.05) rotate(-2deg);
}

.stat-icon-large {
    font-size: 4rem;
    opacity: 0.9;
}

.stat-content-horizontal {
    flex: 1;
}

.stat-label-horizontal {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.8);
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

.stat-value-horizontal {
    font-size: 2.8rem;
    font-weight: 900;
    color: white;
}

/* Boîte de contenu */
.content-box {
    background: white;
    border-radius: 12px;
    padding: 2.5rem;
    margin: 2rem 0;
    box-shadow: 0 5px 25px rgba(0,0,0,0.15);
    border-left: 8px solid #ff6b6b;
}

/* Titre de section */
.section-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #2c3e50;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 4px solid #ff6b6b;
    text-transform: uppercase;
}

/* Boîtes de notification */
.notification-box {
    background: #fff3cd;
    border: 3px solid #ffc107;
    border-radius: 10px;
    padding: 2rem;
    margin: 1.5rem 0;
}

.notification-box.error {
    background: #f8d7da;
    border-color: #dc3545;
}

.notification-box.success {
    background: #d4edda;
    border-color: #28a745;
}

.notification-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
}

.notification-value {
    font-size: 3rem;
    font-weight: 900;
}

/* Carte d'examen horizontale */
.exam-horizontal-card {
    background: linear-gradient(to right, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 10px;
    padding: 1.8rem;
    margin: 1.2rem 0;
    display: flex;
    align-items: center;
    gap: 2rem;
    border: 2px solid #dee2e6;
    transition: all 0.3s ease;
}

.exam-horizontal-card:hover {
    background: linear-gradient(to right, #e3f2fd 0%, #bbdefb 100%);
    border-color: #2196f3;
    transform: translateY(-3px);
}

.exam-time-block {
    background: #ff6b6b;
    color: white;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    min-width: 120px;
}

.exam-time {
    font-size: 2rem;
    font-weight: 900;
}

.exam-date {
    font-size: 0.9rem;
    margin-top: 0.5rem;
}

.exam-details-flex {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.exam-title-horizontal {
    font-size: 1.6rem;
    font-weight: 700;
    color: #2c3e50;
}

.exam-meta {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
}

.exam-meta-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #495057;
    font-weight: 600;
}

/* Page de connexion avec design divisé */
.login-split-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
    min-height: 80vh;
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    margin: 2rem auto;
    max-width: 1200px;
}

.login-left-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 4rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: white;
}

.login-brand {
    font-size: 3.5rem;
    font-weight: 900;
    margin-bottom: 2rem;
}

.login-tagline {
    font-size: 1.4rem;
    line-height: 1.8;
    opacity: 0.95;
}

.login-right-panel {
    padding: 4rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.login-form-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #2c3e50;
    margin-bottom: 2rem;
}

/* Boutons modernes */
.stButton > button {
    background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 1.2rem 3rem;
    font-weight: 700;
    font-size: 1.1rem;
    box-shadow: 0 6px 20px rgba(17, 153, 142, 0.4);
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #38ef7d 0%, #11998e 100%);
    box-shadow: 0 8px 30px rgba(17, 153, 142, 0.6);
    transform: translateY(-2px);
}

/* Barre latérale */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
}

section[data-testid="stSidebar"] > div {
    background: transparent;
}

.sidebar-profile-box {
    background: rgba(255,255,255,0.1);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
    border: 2px solid rgba(255,255,255,0.2);
}

.sidebar-title {
    color: white;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.sidebar-role {
    background: #ff6b6b;
    color: white;
    padding: 1rem;
    border-radius: 8px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
}

.sidebar-name {
    color: white;
    font-size: 1.3rem;
    font-weight: 700;
    text-align: center;
}

/* En-tête de département */
.department-header {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 2rem 3rem;
    border-radius: 12px;
    margin: 2rem 0;
    box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
}

.department-name {
    font-size: 2.5rem;
    font-weight: 900;
    text-transform: uppercase;
}

/* En-tête de date */
.date-header-box {
    background: #2c3e50;
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 8px;
    margin: 2rem 0;
    font-size: 1.4rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Tableau de données */
.dataframe {
    border-radius: 10px !important;
    border: 2px solid #dee2e6 !important;
}

/* Barre de progression */
.stProgress > div > div {
    background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    height: 10px;
    border-radius: 5px;
}

/* Grille d'outils */
.tools-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin: 2rem 0;
}

.tool-card {
    background: white;
    border: 3px solid #e9ecef;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}

.tool-card:hover {
    border-color: #11998e;
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(17, 153, 142, 0.2);
}

.tool-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
}

.tool-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #2c3e50;
}

/* Conteneur de graphique */
.chart-container {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    margin: 2rem 0;
}

/* Métriques */
.metric-row {
    display: flex;
    gap: 2rem;
    margin: 2rem 0;
}

.metric-simple {
    flex: 1;
    background: white;
    padding: 2rem;
    border-radius: 10px;
    border-top: 5px solid #ff6b6b;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    text-align: center;
}

.metric-simple-label {
    font-size: 0.9rem;
    color: #6c757d;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.metric-simple-value {
    font-size: 3rem;
    font-weight: 900;
    color: #2c3e50;
}

/* Responsive pour petits écrans */
@media (max-width: 768px) {
    .login-split-container {
        grid-template-columns: 1fr;
    }
    
    .login-left-panel {
        display: none;
    }
    
    .stats-horizontal {
        flex-direction: column;
    }
    
    .tools-grid {
        grid-template-columns: 1fr;
    }
    
    .metric-row {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)

# Session State
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_dept_id" not in st.session_state:
    st.session_state.user_dept_id = None

# Fonctions de base de données
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
            params = tuple(int(p) if isinstance(p, np.integer) else float(p) if isinstance(p, np.floating) else p for p in params)
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"❌ Erreur requête : {e}")
        return pd.DataFrame()
    finally:
        conn.close()

@st.cache_data(ttl=300)
def get_departements():
    return execute_query("SELECT id, nom FROM departements ORDER BY nom")

@st.cache_data(ttl=300)
def get_formations_by_dept(dept_id=None):
    if dept_id:
        return execute_query("SELECT id, nom FROM formations WHERE dept_id = %s ORDER BY nom", params=(dept_id,))
    return execute_query("SELECT id, nom, dept_id FROM formations ORDER BY nom")

@st.cache_data(ttl=300)
def get_professeurs_by_dept(dept_id=None):
    if dept_id:
        return execute_query("SELECT id, nom FROM professeurs WHERE dept_id = %s ORDER BY nom", params=(dept_id,))
    return execute_query("SELECT id, nom, dept_id FROM professeurs ORDER BY nom")

@st.cache_data(ttl=60)
def load_edt_complete(dept_id=None, formation_id=None, date_filter=None):
    query = """SELECT e.id, m.nom AS module, f.nom AS formation, f.id AS formation_id, p.nom AS professeur, l.nom AS salle, l.capacite, e.date_heure, e.duree_minutes, COUNT(DISTINCT i.etudiant_id) AS nb_inscrits, d.nom AS departement, d.id AS departement_id
    FROM examens e JOIN modules m ON m.id = e.module_id JOIN formations f ON f.id = m.formation_id JOIN departements d ON d.id = f.dept_id JOIN professeurs p ON p.id = e.prof_id JOIN lieux_examen l ON l.id = e.lieu_id LEFT JOIN inscriptions i ON i.module_id = e.module_id WHERE 1=1"""
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
    query += " GROUP BY e.id, m.nom, f.nom, f.id, p.nom, l.nom, l.capacite, e.date_heure, e.duree_minutes, d.nom, d.id ORDER BY e.date_heure, f.nom"
    return execute_query(query, params=tuple(params) if params else None)

@st.cache_data(ttl=60)
def get_kpis_globaux():
    kpis = {}
    for key, query in {
        "nb_examens": "SELECT COUNT(*) as val FROM examens",
        "nb_salles": "SELECT COUNT(*) as val FROM lieux_examen",
        "nb_profs": "SELECT COUNT(*) as val FROM professeurs",
        "nb_etudiants": "SELECT COUNT(*) as val FROM etudiants"
    }.items():
        result = execute_query(query)
        kpis[key] = float(result.iloc[0, 0]) if not result.empty else 0
    return kpis

@st.cache_data(ttl=60)
def get_occupation_globale():
    return execute_query("""SELECT l.nom AS salle, l.capacite, COUNT(e.id) AS nb_examens, ROUND(AVG(CASE WHEN ins.nb_inscrits IS NOT NULL THEN (ins.nb_inscrits / l.capacite) * 100 ELSE 0 END), 1) AS taux_occupation FROM lieux_examen l LEFT JOIN examens e ON e.lieu_id = l.id LEFT JOIN (SELECT module_id, COUNT(etudiant_id) AS nb_inscrits FROM inscriptions GROUP BY module_id) ins ON ins.module_id = e.module_id GROUP BY l.id, l.nom, l.capacite ORDER BY taux_occupation DESC""")

@st.cache_data(ttl=60)
def get_stats_par_departement():
    return execute_query("""SELECT d.nom AS departement, COUNT(DISTINCT e.id) AS nb_examens, COUNT(DISTINCT m.id) AS nb_modules, COUNT(DISTINCT f.id) AS nb_formations FROM departements d LEFT JOIN formations f ON f.dept_id = d.id LEFT JOIN modules m ON m.formation_id = f.id LEFT JOIN examens e ON e.module_id = m.id GROUP BY d.id, d.nom ORDER BY nb_examens DESC""")

@st.cache_data(ttl=60)
def get_heures_enseignement():
    return execute_query("""SELECT p.nom AS professeur, d.nom AS departement, COUNT(e.id) AS nb_examens, SUM(e.duree_minutes) / 60 AS heures_totales, COUNT(s.examen_id) AS nb_surveillances FROM professeurs p JOIN departements d ON d.id = p.dept_id LEFT JOIN examens e ON e.prof_id = p.id LEFT JOIN surveillances s ON s.prof_id = p.id GROUP BY p.id, p.nom, d.nom ORDER BY heures_totales DESC""")

@st.cache_data(ttl=60)
def get_edt_etudiant(formation_id):
    return execute_query("""SELECT DISTINCT e.id, m.nom AS module, f.nom AS formation, f.id AS formation_id, p.nom AS professeur, l.nom AS salle, l.capacite, e.date_heure, e.duree_minutes, COUNT(DISTINCT i.etudiant_id) AS nb_inscrits, d.nom AS departement, d.id AS departement_id FROM examens e JOIN modules m ON m.id = e.module_id JOIN formations f ON f.id = m.formation_id JOIN departements d ON d.id = f.dept_id JOIN professeurs p ON p.id = e.prof_id JOIN lieux_examen l ON l.id = e.lieu_id LEFT JOIN inscriptions i ON i.module_id = e.module_id WHERE f.id = %s GROUP BY e.id, m.nom, f.nom, f.id, p.nom, l.nom, l.capacite, e.date_heure, e.duree_minutes, d.nom, d.id ORDER BY e.date_heure, f.nom""", params=(formation_id,))

def generer_edt_optimiser():
    conn = get_connection()
    if not conn:
        return 0, 0
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("DELETE FROM examens")
        conn.commit()
        cur.execute("""SELECT m.id AS module_id, m.nom AS module, f.id AS formation_id, f.dept_id AS dept_id, COALESCE(COUNT(DISTINCT i.etudiant_id), 1) AS nb_etudiants FROM modules m JOIN formations f ON f.id = m.formation_id LEFT JOIN inscriptions i ON i.module_id = m.id GROUP BY m.id, m.nom, f.id, f.dept_id ORDER BY nb_etudiants DESC""")
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
        formation_jour, salle_horaire, etudiant_jour, salles_occupees_par_slot = {}, {}, {}, {}
        prof_exams_count = {p["id"]: 0 for p in profs}
        success, failed, failed_modules, exams_to_insert = 0, 0, [], []
        for i, module in enumerate(modules):
            progress_bar.progress((i + 1) / len(modules))
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
                        exams_to_insert.append((module["module_id"], prof_trouve["id"], salle["id"], dt, DUREE_EXAM))
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
            cur.executemany("INSERT INTO examens (module_id, prof_id, lieu_id, date_heure, duree_minutes) VALUES (%s, %s, %s, %s, %s)", exams_to_insert)
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
        return 0, 0
    finally:
        conn.close()

# Page de connexion
def page_connexion():
    st.markdown('<div class="login-split-container">', unsafe_allow_html=True)
    
    # Panneau gauche
    st.markdown("""
        <div class="login-left-panel">
            <div class="login-brand">SYSTÈME EXAMENS</div>
            <div class="login-tagline">
                Plateforme avancée pour la gestion des examens universitaires<br>
                Système intelligent de planification et de suivi<br>
                Solutions numériques complètes
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Panneau droit
    col1, col2 = st.columns([1, 2])
    with col2:
        st.markdown('<div class="login-right-panel"><h2 class="login-form-title">Connexion</h2>', unsafe_allow_html=True)
        
        role = st.selectbox("Choisir le type de compte", list(ROLES.values()), key="role_select")
        
        if role == ROLES["vice_doyen"]:
            if st.button("Connexion Vice-Doyen", use_container_width=True, key="login_vd"):
                st.session_state.user_role, st.session_state.user_name = "vice_doyen", "Vice-Doyen"
                st.rerun()
        
        elif role == ROLES["admin_exams"]:
            if st.button("Connexion Administrateur", use_container_width=True, key="login_admin"):
                st.session_state.user_role, st.session_state.user_name = "admin_exams", "Administrateur"
                st
