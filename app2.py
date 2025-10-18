import streamlit as st
import pandas as pd
import os
import io

st.title("Recherche intelligente + documentation 🚀")

# ----- Étape 1 : Upload du fichier TXT -----
uploaded_file = st.file_uploader("Upload ton fichier arborescence (.txt)", type=["txt"])

if uploaded_file is not None:
    # Lire chaque ligne
    paths = [line.decode('utf-8').strip() if isinstance(line, bytes) else line.strip()
             for line in uploaded_file.readlines()]
    
    df = pd.DataFrame(paths, columns=["Chemin complet"])
    df["Nom fichier"] = df["Chemin complet"].apply(lambda x: os.path.basename(x) if isinstance(x, str) else "")
    df["Dossier parent"] = df["Chemin complet"].apply(lambda x: os.path.dirname(x) if isinstance(x, str) else "")
    
    # Colonnes pour la documentation
    df["Catégories"] = ""
    df["Description"] = ""
    
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
        st.dataframe(results[["Chemin complet", "Nom fichier"]])
        
        # ----- Étape 3 : Documentation des résultats -----
        st.subheader("Documenter les fichiers trouvés")
        documented = []
        for idx, row in results.iterrows():
            st.markdown(f"**{row['Nom fichier']}**")
            categories = st.text_input(f"Catégories / tags (1 à 3) pour {row['Nom fichier']}", key=f"cat_{idx}")
            description = st.text_area(f"Description pour {row['Nom fichier']}", key=f"desc_{idx}")
            if categories or description:
                documented.append((idx, categories, description))
        
        # Appliquer les modifications
        for idx, cat, desc in documented:
            df.at[idx, "Catégories"] = cat
            df.at[idx, "Description"] = desc
        
        # ----- Télécharger les résultats en Excel -----
        if not results.empty:
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="Télécharger l'arborescence enrichie",
                data=output,
                file_name="arborescence_enrichie.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # ----- Optionnel : afficher la hiérarchie légère -----
        show_hierarchy = st.checkbox("Afficher la hiérarchie légère")
        if show_hierarchy:
            min_depth = min(path.count(os.sep) for path in results["Chemin complet"])
            for path in results["Chemin complet"]:
                depth = path.count(os.sep) - min_depth
                st.text("    " * depth + os.path.basename(path))
