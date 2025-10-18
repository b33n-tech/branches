import streamlit as st
import pandas as pd
import os
import io

st.title("Recherche intelligente + documentation 🚀")

# ----- Étape 1 : Upload du fichier TXT -----
uploaded_file = st.file_uploader("Upload ton fichier arborescence (.txt)", type=["txt"])

if uploaded_file is not None:
    paths = [line.decode('utf-8').strip() if isinstance(line, bytes) else line.strip()
             for line in uploaded_file.readlines()]
    
    df = pd.DataFrame(paths, columns=["Chemin complet"])
    df["Nom fichier"] = df["Chemin complet"].apply(lambda x: os.path.basename(x) if isinstance(x, str) else "")
    df["Dossier parent"] = df["Chemin complet"].apply(lambda x: os.path.dirname(x) if isinstance(x, str) else "")
    
    # ----- Détecter type (Fichier / Dossier) -----
    def detect_type(path):
        if path.endswith(os.sep) or os.path.basename(path) == "":
            return "Dossier"
        elif '.' in os.path.basename(path):
            return "Fichier"
        else:
            return "Dossier"

    df["Type"] = df["Chemin complet"].apply(detect_type)

    # Colonnes pour la documentation
    df["Catégories"] = ""
    df["Description"] = ""
    df["Sélectionné"] = False  # Nouvelle colonne pour case à cocher
    
    st.success(f"{len(df)} fichiers/dossiers chargés.")

    # ----- Étape 1.5 : Filtrer par type (Fichier / Dossier / Tous) -----
    filter_type = st.selectbox("Type à documenter :", options=["Tous", "Fichier", "Dossier"])
    if filter_type != "Tous":
        df_filtered_type = df[df["Type"] == filter_type]
    else:
        df_filtered_type = df.copy()

    # ----- Étape 2 : Barre de recherche + mode ET/OU -----
    col1, col2 = st.columns([2, 1])  # mots-clés / mode ET-OU sur la même ligne
    with col1:
        query = st.text_input("Tape les mots-clés de recherche :", "")
    with col2:
        mode = st.radio("Mode de recherche :", ["ET (tous les mots)", "OU (au moins un mot)"])

    # ----- Étape 3 : Filtrer selon mots-clés -----
    results = df_filtered_type.copy()
    if query:
        keywords = query.lower().split()
        def match_keywords(filename):
            if not isinstance(filename, str):
                return False
            name_lower = filename.lower()
            if mode.startswith("ET"):
                return all(k in name_lower for k in keywords)
            else:
                return any(k in name_lower for k in keywords)
        results = results[results["Nom fichier"].apply(match_keywords)]
    
    st.write(f"Résultats trouvés : {len(results)}")

    # ----- Étape 4 : Affichage tableau + checkbox par ligne -----
    st.subheader("Résultats et sélection pour documentation")
    for idx, row in results.iterrows():
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            selected = st.checkbox("", key=f"select_{idx}", value=row["Sélectionné"])
            df.at[idx, "Sélectionné"] = selected
        with col2:
            st.text(f"{row['Nom fichier']} ({row['Type']})")

    # ----- Étape 5 : Ajouter catégories / description pour les éléments sélectionnés -----
    st.subheader("Documenter les éléments sélectionnés")
    for idx, row in df[df["Sélectionné"]].iterrows():
        st.markdown(f"**{row['Nom fichier']} ({row['Type']})**")
        categories = st.text_input(f"Catégories / tags (1 à 3) pour {row['Nom fichier']}", value=row["Catégories"], key=f"cat_{idx}")
        description = st.text_area(f"Description pour {row['Nom fichier']}", value=row["Description"], key=f"desc_{idx}")
        df.at[idx, "Catégories"] = categories
        df.at[idx, "Description"] = description

    # ----- Étape 6 : Export JSON / Excel -----
    if st.button("Exporter JSON/Excel des éléments documentés"):
        documented = df[df["Sélectionné"]].copy()
        if not documented.empty:
            # Excel
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                documented.to_excel(writer, index=False)
            output_excel.seek(0)
            st.download_button("Télécharger Excel", data=output_excel, file_name="documented_files.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            # JSON
            output_json = documented.to_json(orient="records", indent=2)
            st.download_button("Télécharger JSON", data=output_json, file_name="documented_files.json", mime="application/json")
        else:
            st.warning("Aucun élément sélectionné pour export.")
