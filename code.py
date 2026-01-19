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

# NOUVEAU DESIGN CSS COMPLET
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.main { background: linear-gradient(125deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); padding: 1.5rem; }
.glass-card { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border: 2px solid rgba(255, 255, 255, 0.3); border-radius: 25px; padding: 2.5rem; box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3); margin-bottom: 2rem; }
.main-header { text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); border-radius: 30px; box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4); margin-bottom: 3rem; }
.main-title { font-size: 3.5rem; font-weight: 800; color: white; text-shadow: 2px 4px 10px rgba(0, 0, 0, 0.3); margin: 0; letter-spacing: 1px; }
.main-subtitle { color: rgba(255, 255, 255, 0.95); font-size: 1.3rem; margin-top: 1rem; font-weight: 300; }
.floating-role-badge { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1rem 2.5rem; border-radius: 100px; font-weight: 700; font-size: 1.1rem; box-shadow: 0 10px 40px rgba(245, 87, 108, 0.5); display: inline-block; margin-top: 1.5rem; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
.neon-stat-card { background: linear-gradient(145deg, #1e3c72, #2a5298); border-radius: 20px; padding: 2rem; border: 2px solid rgba(94, 114, 228, 0.5); box-shadow: 0 0 30px rgba(94, 114, 228, 0.3); transition: all 0.4s ease; }
.neon-stat-card:hover { transform: translateY(-10px) scale(1.03); box-shadow: 0 0 50px rgba(94, 114, 228, 0.6); }
.stat-icon { font-size: 3rem; margin-bottom: 1rem; }
.stat-number { font-size: 3rem; font-weight: 800; color: white; margin: 1rem 0; }
.stat-description { color: rgba(255, 255, 255, 0.85); font-size: 1rem; font-weight: 500; text-transform: uppercase; letter-spacing: 2px; }
.modern-alert { background: rgba(255, 193, 7, 0.15); border-left: 5px solid #ffc107; border-radius: 15px; padding: 2rem; margin: 1.5rem 0; box-shadow: 0 8px 25px rgba(255, 193, 7, 0.2); }
.modern-alert.success { background: rgba(76, 175, 80, 0.15); border-left-color: #4caf50; box-shadow: 0 8px 25px rgba(76, 175, 80, 0.2); }
.modern-alert.danger { background: rgba(244, 67, 54, 0.15); border-left-color: #f44336; box-shadow: 0 8px 25px rgba(244, 67, 54, 0.2); }
.alert-title { font-size: 1.5rem; font-weight: 700; margin: 0 0 0.5rem 0; }
.alert-value { font-size: 2.5rem; font-weight: 800; margin-top: 1rem; }
.advanced-exam-card { background: white; border-radius: 20px; padding: 2rem; margin: 1.5rem 0; border: 2px solid #e8eaf6; box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08); transition: all 0.4s ease; position: relative; }
.advanced-exam-card:hover { transform: translateX(10px); box-shadow: 0 15px 40px rgba(102, 126, 234, 0.25); border-color: #667eea; }
.exam-header { font-size: 1.5rem; font-weight: 700; color: #1a237e; margin-bottom: 1.5rem; }
.exam-info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-top: 1.5rem; }
.info-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; background: #f5f7fa; border-radius: 12px; font-weight: 500; color: #37474f; }
.login-3d-container { background: white; border-radius: 30px; padding: 4rem 3rem; box-shadow: 0 30px 80px rgba(0, 0, 0, 0.3); max-width: 550px; margin: 4rem auto; }
.login-emoji { font-size: 5rem; margin-bottom: 1.5rem; }
.login-heading { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.75rem; text-align: center; }
.login-text { color: #546e7a; font-size: 1.1rem; font-weight: 400; text-align: center; }
.stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 15px; padding: 1rem 2.5rem; font-weight: 700; font-size: 1.1rem; box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4); }
.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6); }
.animated-section-header { font-size: 2rem; font-weight: 800; color: #1a237e; margin: 3rem 0 2rem 0; padding-bottom: 1rem; border-bottom: 4px solid; border-image: linear-gradient(90deg, #667eea, #764ba2, #f093fb) 1; }
.elegant-dept-badge { background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%); color: white; padding: 1.5rem 2.5rem; border-radius: 20px; font-weight: 700; font-size: 1.3rem; text-align: center; margin: 2rem 0; box-shadow: 0 10px 40px rgba(0, 114, 255, 0.4); }
.modern-date-badge { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); color: #263238; padding: 1rem 2rem; border-radius: 15px; font-weight: 700; font-size: 1.1rem; display: inline-block; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# Session State
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_dept_id" not in st.session_state:
    st.session_state.user_dept_id = None

# Fonctions Database (INCHANGÉES)
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

# PAGE CONNEXION
def page_connexion():
    st.markdown('<div class="main-header"><div class="login-emoji">🎓</div><h1 class="main-title">Système de Gestion des Examens</h1><p class="main-subtitle">Plateforme intelligente de planification et suivi</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-3d-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="login-heading">Authentification</h2><p class="login-text">Sélectionnez votre profil pour continuer</p>', unsafe_allow_html=True)
    role = st.selectbox("🔐 Profil utilisateur", list(ROLES.values()), key="role_select")
    if role == ROLES["vice_doyen"]:
        if st.button("Accéder au tableau de bord", use_container_width=True, key="login_vd"):
            st.session_state.user_role, st.session_state.user_name = "vice_doyen", "Vice-Doyen"
            st.rerun()
    elif role == ROLES["admin_exams"]:
        if st.button("Accéder au panneau admin", use_container_width=True, key="login_admin"):
            st.session_state.user_role, st.session_state.user_name = "admin_exams", "Administrateur Examens"
            st.rerun()
    elif role == ROLES["chef_dept"]:
        depts = get_departements()
        if not depts.empty:
            dept_nom = st.selectbox("🏢 Choisir département", depts["nom"].tolist())
            if st.button("Se connecter", use_container_width=True, key="login_chef"):
                dept_id = depts[depts["nom"] == dept_nom]["id"].values[0]
                st.session_state.user_role, st.session_state.user_name, st.session_state.user_dept_id = "chef_dept", f"Chef {dept_nom}", dept_id
                st.rerun()
    elif role == ROLES["enseignant"]:
        profs = get_professeurs_by_dept()
        if not profs.empty:
            prof_nom = st.selectbox("👨‍🏫 Votre nom", profs["nom"].tolist())
            if st.button("Accéder à mon espace", use_container_width=True, key="login_prof"):
                prof_data = profs[profs["nom"] == prof_nom].iloc[0]
                st.session_state.user_role, st.session_state.user_name, st.session_state.user_dept_id = "enseignant", prof_nom, prof_data["dept_id"]
                st.rerun()
    elif role == ROLES["etudiant"]:
        formations = get_formations_by_dept()
        if not formations.empty:
            formation_nom = st.selectbox("📚 Votre formation", formations["nom"].tolist())
            if st.button("Voir mon calendrier", use_container_width=True, key="login_etud"):
                formation_data = formations[formations["nom"] == formation_nom].iloc[0]
                st.session_state.user_role, st.session_state.user_name, st.session_state.user_dept_id = "etudiant", "Étudiant", formation_data["dept_id"]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# DASHBOARDS
def dashboard_vice_doyen():
    st.markdown(f'<div class="main-header"><h1 class="main-title">Tableau de Bord Exécutif</h1><p class="main-subtitle">Analyse complète et indicateurs clés</p><div class="floating-role-badge">👤 {st.session_state.user_name}</div></div>', unsafe_allow_html=True)
    kpis = get_kpis_globaux()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="neon-stat-card"><div class="stat-icon">📘</div><div class="stat-number">{int(kpis["nb_examens"])}</div><div class="stat-description">Examens Total</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="neon-stat-card"><div class="stat-icon">🏫</div><div class="stat-number">{int(kpis["nb_salles"])}</div><div class="stat-description">Salles Actives</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="neon-stat-card"><div class="stat-icon">👨‍🏫</div><div class="stat-number">{int(kpis["nb_profs"])}</div><div class="stat-description">Enseignants</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="neon-stat-card"><div class="stat-icon">🎓</div><div class="stat-number">13,000</div><div class="stat-description">Étudiants</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><h2 class="animated-section-header">📊 Occupation des Espaces</h2>', unsafe_allow_html=True)
    occupation = get_occupation_globale()
    if not occupation.empty:
        fig = px.bar(occupation, x="salle", y="taux_occupation", color="taux_occupation", color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins"))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(occupation, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><h2 class="animated-section-header">🏢 Performance Départements</h2>', unsafe_allow_html=True)
    stats_dept = get_stats_par_departement()
    if not stats_dept.empty:
        fig = px.bar(stats_dept, x="departement", y="nb_examens", color="nb_examens", color_continuous_scale="Purples")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(stats_dept, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def dashboard_admin_examens():
    st.markdown(f'<div class="main-header"><h1 class="main-title">Centre de Contrôle</h1><p class="main-subtitle">Administration et planification globale</p><div class="floating-role-badge">👤 {st.session_state.user_name}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><h2 class="animated-section-header">⚙️ Outils de Gestion</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Lancer génération automatique", use_container_width=True, key="gen_edt"):
            with st.spinner("Traitement en cours..."):
                import time
                start = time.time()
                success, failed = generer_edt_optimiser()
                elapsed = time.time() - start
                total = success + failed
                taux = (success / total * 100) if total > 0 else 0
                st.markdown(f'<div class="modern-alert success"><h3 class="alert-title">✅ Processus terminé</h3><p>{success}/{total} modules ({taux:.1f}%) en {elapsed:.2f}s</p></div>', unsafe_allow_html=True)
                if failed == 0:
                    st.balloons()
                st.cache_data.clear()
                st.rerun()
    with col2:
        if st.button("🔄 Rafraîchir système", use_container_width=True, key="refresh"):
            st.cache_data.clear()
            st.success("✅ Système mis à jour")
            st.rerun()
    with col3:
        if st.button("🗑️ Effacer planning", use_container_width=True, key="reset"):
            conn = get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM examens")
                conn.commit()
                conn.close()
                st.success("✅ Planning réinitialisé")
                st.cache_data.clear()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><h2 class="animated-section-header">📋 Vue d\'ensemble du planning</h2>', unsafe_allow_html=True)
    edt = load_edt_complete()
    if not edt.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("📘 Examens", len(edt))
        col2.metric("🏢 Départements", edt["departement"].nunique())
        col3.metric("📚 Formations", edt["formation"].nunique())
        st.dataframe(edt, use_container_width=True, height=400)
        csv = edt.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter données", csv, "planning_complet.csv", "text/csv", key="dl_csv")
    else:
        st.info("Aucune donnée planifiée")
    st.markdown('</div>', unsafe_allow_html=True)

def dashboard_chef_dept():
    st.markdown(f'<div class="main-header"><h1 class="main-title">Espace Département</h1><p class="main-subtitle">Supervision et validation</p><div class="floating-role-badge">👤 {st.session_state.user_name}</div></div>', unsafe_allow_html=True)
    dept_id = st.session_state.user_dept_id
    edt_dept = load_edt_complete(dept_id=dept_id)
    if not edt_dept.empty:
        st.markdown(f'<div class="elegant-dept-badge">🏢 {edt_dept.iloc[0]["departement"]}</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="neon-stat-card"><div class="stat-icon">📘</div><div class="stat-number">{len(edt_dept)}</div><div class="stat-description">Examens</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="neon-stat-card"><div class="stat-icon">📚</div><div class="stat-number">{edt_dept["formation"].nunique()}</div><div class="stat-description">Formations</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="neon-stat-card"><div class="stat-icon">✅</div><div class="stat-number">{len(edt_dept)}</div><div class="stat-description">Validés</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card"><h2 class="animated-section-header">📚 Examens par formation</h2>', unsafe_allow_html=True)
        for formation in edt_dept["formation"].unique():
            st.markdown(f"### 📖 {formation}")
            formation_data = edt_dept[edt_dept["formation"] == formation]
            for _, exam in formation_data.iterrows():
                st.markdown(f'''<div class="advanced-exam-card"><div class="exam-header">📖 {exam['module']}</div><div class="exam-info-grid"><div class="info-item"><span class="info-icon">📅</span><span>{exam['date_heure']}</span></div><div class="info-item"><span class="info-icon">🏫</span><span>{exam['salle']}</span></div><div class="info-item"><span class="info-icon">👨‍🏫</span><span>{exam['professeur']}</span></div><div class="info-item"><span class="info-icon">👥</span><span>{exam['nb_inscrits']} étudiants</span></div></div></div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card"><h2 class="animated-section-header">📊 Analyses statistiques</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            edt_dept["date"] = pd.to_datetime(edt_dept["date_heure"]).dt.date
            exams_par_jour = edt_dept.groupby("date").size().reset_index(name="nb_examens")
            fig = px.bar(exams_par_jour, x="date", y="nb_examens", title="Distribution temporelle")
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins"))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            exams_par_formation = edt_dept.groupby("formation").size().reset_index(name="nb_examens")
            fig = px.pie(exams_par_formation, values="nb_examens", names="formation", title="Répartition formations")
            fig.update_layout(font=dict(family="Poppins"))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Aucune donnée pour ce département")

def dashboard_enseignant():
    st.markdown(f'<div class="main-header"><h1 class="main-title">Espace Enseignant</h1><p class="main-subtitle">Mes surveillances et responsabilités</p><div class="floating-role-badge">👤 {st.session_state.user_name}</div></div>', unsafe_allow_html=True)
    query = """SELECT e.id, m.nom AS module, f.nom AS formation, d.nom AS departement, l.nom AS salle, e.date_heure, COUNT(DISTINCT i.etudiant_id) AS nb_inscrits FROM examens e JOIN modules m ON m.id = e.module_id JOIN formations f ON f.id = m.formation_id JOIN departements d ON d.id = f.dept_id JOIN lieux_examen l ON l.id = e.lieu_id JOIN professeurs p ON p.id = e.prof_id LEFT JOIN inscriptions i ON i.module_id = m.id WHERE p.nom = %s GROUP BY e.id, m.nom, f.nom, d.nom, l.nom, e.date_heure ORDER BY e.date_heure"""
    mes_examens = execute_query(query, params=(st.session_state.user_name,))
    if not mes_examens.empty:
        st.markdown(f'<div class="neon-stat-card" style="text-align: center; max-width: 400px; margin: 2rem auto;"><div class="stat-icon">📘</div><div class="stat-number">{len(mes_examens)}</div><div class="stat-description">Surveillances assignées</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card"><h2 class="animated-section-header">📅 Mon calendrier de surveillance</h2>', unsafe_allow_html=True)
        for _, exam in mes_examens.iterrows():
            st.markdown(f'''<div class="advanced-exam-card"><div class="exam-header">📖 {exam['module']}</div><div class="exam-info-grid"><div class="info-item"><span class="info-icon">📚</span><span>{exam['formation']}</span></div><div class="info-item"><span class="info-icon">🏢</span><span>{exam['departement']}</span></div><div class="info-item"><span class="info-icon">📅</span><span>{exam['date_heure']}</span></div><div class="info-item"><span class="info-icon">🏫</span><span>{exam['salle']}</span></div></div></div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Aucune surveillance programmée")

def dashboard_etudiant():
    st.markdown(f'<div class="main-header"><h1 class="main-title">Mon Espace Étudiant</h1><p class="main-subtitle">Consultez votre planning d\'examens</p><div class="floating-role-badge">👤 Étudiant</div></div>', unsafe_allow_html=True)
    formations = get_formations_by_dept(st.session_state.user_dept_id)
    if not formations.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        formation_selected = st.selectbox("📚 Sélectionner formation", formations["nom"].tolist())
        formation_id = formations[formations["nom"] == formation_selected]["id"].values[0]
        st.markdown('</div>', unsafe_allow_html=True)
        edt_formation = get_edt_etudiant(formation_id)
        if not edt_formation.empty:
            st.markdown(f'<div class="neon-stat-card" style="text-align: center; max-width: 400px; margin: 2rem auto;"><div class="stat-icon">📘</div><div class="stat-number">{len(edt_formation)}</div><div class="stat-description">Mes examens</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="glass-card"><h2 class="animated-section-header">📅 Mon planning personnel</h2>', unsafe_allow_html=True)
            edt_formation["date"] = pd.to_datetime(edt_formation["date_heure"]).dt.date
            for date in sorted(edt_formation["date"].unique()):
                st.markdown(f'<div class="modern-date-badge">📅 {date.strftime("%A %d %B %Y")}</div>', unsafe_allow_html=True)
                examens_jour = edt_formation[edt_formation["date"] == date]
                for _, exam in examens_jour.iterrows():
                    st.markdown(f'''<div class="advanced-exam-card"><div style="display: flex; justify-content: space-between; align-items: center;"><div><div style="font-size: 1.8rem; font-weight: 700; color: #667eea; margin-bottom: 0.5rem;">⏰ {exam['date_heure'].strftime('%H:%M')}</div><div class="exam-header">{exam['module']}</div></div><div class="exam-info-grid" style="grid-template-columns: 1fr;"><div class="info-item"><span class="info-icon">🏫</span><span>{exam['salle']}</span></div><div class="info-item"><span class="info-icon">👨‍🏫</span><span>{exam['professeur']}</span></div></div></div></div>''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            csv = edt_formation.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger mon planning", csv, "mon_planning.csv", "text/csv", key="dl_student")
        else:
            st.info("Aucun examen programmé")
    else:
        st.warning("Aucune formation disponible")

# NAVIGATION PRINCIPALE
def main():
    with st.sidebar:
        if st.session_state.user_role:
            st.markdown('<div style="background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 20px; backdrop-filter: blur(20px);"><h3 style="color: #1a237e; margin-bottom: 1.5rem;">👤 Session active</h3>', unsafe_allow_html=True)
            st.markdown(f'<div class="floating-role-badge" style="margin: 1rem 0; animation: none;">{ROLES[st.session_state.user_role]}</div>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-weight: 700; color: #37474f; font-size: 1.1rem; margin-top: 1rem;">{st.session_state.user_name}</p></div>', unsafe_allow_html=True)
            if st.button("🚪 Se déconnecter", use_container_width=True, key="logout"):
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
