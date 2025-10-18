import streamlit as st
import pandas as pd
import os
import io
import json

st.title("Recherche intelligente + documentation JSON 🚀")

# ----- Étape 1 : Upload du fichier TXT -----
uploaded_file = st.file_uploader("Upload ton fichier arborescence (.txt)", type=["txt"])

if uploaded_file is not None:
    paths = [line.decode('utf-8').strip() if isinstance(line, bytes) else line.strip()
             for line in uploaded_file.readlines()]
    
    df = pd.DataFrame(paths, columns=["Chemin complet"])
    df["Nom fichier"] = df["Chemin complet"].apply(lambda x: os.path.basename(x) if isinstance(x, str) else "")
    df["Dossier parent"] = df["Chemin complet"].apply(lambda x: os.path.dirname(x) if isinstance(x, str) else "")
    
    st.success(f"{len(df)} fichiers/dossiers chargés.")
    
    # ----- Étape 2 : Barre de recherche + mode ET/OU -----
    query = st.text_input("Tape les mots-clés de recherche :", "")
    mode = st.radio("Mode de recherche :", ["ET (tous les mots)", "OU (au moins un mot)"])
    
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
        
        results = df[df["Nom fichier"].apply(match_keywords)].copy()
        st.write(f"Résultats trouvés : {len(results)}")
        
        # ----- Étape 3 : Sélection + documentation -----
        st.subheader("Sélectionner les fichiers à documenter")
        documented_data = []
        for idx, row in results.iterrows():
            st.markdown(f"**{row['Nom fichier']}**")
            doc_checkbox = st.checkbox("Documenter ce fichier", key=f"doc_{idx}")
            if doc_checkbox:
                categories = st.text_input(f"Catégories / tags (1 à 3) pour {row['Nom fichier']}", key=f"cat_{idx}")
                description = st.text_area(f"Description pour {row['Nom fichier']}", key=f"desc_{idx}")
                documented_data.append({
                    "Chemin complet": row["Chemin complet"],
                    "Nom fichier": row["Nom fichier"],
                    "Dossier parent": row["Dossier parent"],
                    "Catégories": categories,
                    "Description": description
                })
        
        # ----- Export JSON -----
        if documented_data:
            if st.button("Exporter JSON des fichiers documentés"):
                json_data = json.dumps(documented_data, indent=2, ensure_ascii=False)
                st.download_button(
                    "Télécharger JSON",
                    data=json_data,
                    file_name="fichiers_documentes.json",
                    mime="application/json"
                )
