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
    # Colonnes pour la documentation
    df["Catégories"] = ""
    df["Description"] = ""
    df["Sélectionné"] = False  # Nouvelle colonne pour case à cocher
    
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
        
        # ----- Étape 3 : Affichage tableau + checkbox par ligne -----
        st.subheader("Résultats et sélection pour documentation")
        for idx, row in results.iterrows():
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                selected = st.checkbox("", key=f"select_{idx}", value=row["Sélectionné"])
                df.at[idx, "Sélectionné"] = selected
            with col2:
                st.text(row["Nom fichier"])
        
        # ----- Étape 4 : Ajouter catégories / description pour les fichiers sélectionnés -----
        st.subheader("Documenter les fichiers sélectionnés")
        for idx, row in df[df["Sélectionné"]].iterrows():
            st.markdown(f"**{row['Nom fichier']}**")
            categories = st.text_input(f"Catégories / tags (1 à 3) pour {row['Nom fichier']}", value=row["Catégories"], key=f"cat_{idx}")
            description = st.text_area(f"Description pour {row['Nom fichier']}", value=row["Description"], key=f"desc_{idx}")
            df.at[idx, "Catégories"] = categories
            df.at[idx, "Description"] = description
        
        # ----- Étape 5 : Export JSON / Excel -----
        if st.button("Exporter JSON/Excel des fichiers documentés"):
            documented = df[df["Sélectionné"]].copy()
            if not documented.empty:
                output_csv = io.BytesIO()
                documented.to_excel(output_csv, index=False, engine='openpyxl')
                output_csv.seek(0)
                
                output_json = documented.to_json(orient="records", indent=2)
                
                st.download_button("Télécharger CSV", data=output_csv, file_name="documented_files.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                st.download_button("Télécharger JSON", data=output_json, file_name="documented_files.json", mime="application/json")
            else:
                st.warning("Aucun fichier sélectionné pour export.")
