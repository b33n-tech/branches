import streamlit as st
import pandas as pd
import os

st.title("Recherche dans l'arborescence 🚀")

# ----- Étape 1 : Upload du fichier TXT -----
uploaded_file = st.file_uploader("Upload ton fichier arborescence (.txt)", type=["txt"])

if uploaded_file is not None:
    # Lire le fichier txt et mettre chaque ligne dans une liste
    paths = [line.strip() for line in uploaded_file.readlines()]
    
    # Créer un DataFrame pour manipuler plus facilement
    df = pd.DataFrame(paths, columns=["Chemin complet"])
    df["Nom fichier"] = df["Chemin complet"].apply(lambda x: os.path.basename(x))
    
    st.success(f"{len(df)} fichiers/dossiers chargés.")
    
    # ----- Étape 2 : Barre de recherche -----
    query = st.text_input("Tape les mots-clés de recherche :", "")
    
    if query:
        # Séparer les mots-clés
        keywords = query.lower().split()
        
        # Filtrer les fichiers qui contiennent tous les mots-clés
        def match_keywords(filename):
            name_lower = filename.lower()
            return all(k in name_lower for k in keywords)
        
        results = df[df["Nom fichier"].apply(match_keywords)]
        
        st.write(f"Résultats trouvés : {len(results)}")
        st.dataframe(results)
        
        # Option : télécharger les résultats en Excel
        if not results.empty:
            excel_bytes = results.to_excel(index=False, engine='openpyxl')
            st.download_button(
                label="Télécharger les résultats en Excel",
                data=excel_bytes,
                file_name="recherche_resultats.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
