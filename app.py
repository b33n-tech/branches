import streamlit as st
import pandas as pd
import os
import io

st.title("Recherche intelligente dans l'arborescence 🚀")

# ----- Étape 1 : Upload du fichier TXT -----
uploaded_file = st.file_uploader("Upload ton fichier arborescence (.txt)", type=["txt"])

if uploaded_file is not None:
    # Lire chaque ligne en string
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
        
        results = df[df["Nom fichier"].apply(match_keywords)]
        st.write(f"Résultats trouvés : {len(results)}")
        st.dataframe(results)
        
        # ----- Télécharger les résultats en Excel -----
        if not results.empty:
            output = io.BytesIO()  # buffer mémoire
            results.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)  # revenir au début du buffer

            st.download_button(
                label="Télécharger les résultats en Excel",
                data=output,
                file_name="recherche_resultats.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # ----- Optionnel : afficher la hiérarchie légère -----
        show_hierarchy = st.checkbox("Afficher la hiérarchie légère")
        if show_hierarchy:
            min_depth = min(path.count(os.sep) for path in results["Chemin complet"])
            for path in results["Chemin complet"]:
                depth = path.count(os.sep) - min_depth
                st.text("    " * depth + os.path.basename(path))
