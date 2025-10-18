import streamlit as st
import pandas as pd
import os

st.title("Lecteur et recherche dans la base documentaire 📚")

# ----- Étape 1 : Upload du fichier CSV/JSON -----
uploaded_file = st.file_uploader(
    "Upload ton fichier annoté (.csv ou .json)", 
    type=["csv", "json"]
)

if uploaded_file is not None:
    # Détection du type de fichier et lecture
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:  # JSON
        df = pd.read_json(uploaded_file)
    
    st.success(f"{len(df)} fichiers/dossiers chargés dans la base documentaire.")

    # ----- Étape 2 : Barre de recherche + filtres -----
    query = st.text_input("Recherche par mots-clés :", "")
    st.write("Astuce : tu peux chercher des types de fichier (excel, word, pdf…) ou des mots dans la description/catégories.")
    
    # Filtre par type de fichier
    file_types = st.multiselect(
        "Filtrer par type de fichier (extensions)",
        options=sorted(df['Nom fichier'].apply(lambda x: os.path.splitext(x)[1].lower()).unique()),
        default=[]
    )

    results = df.copy()
    
    # Filtrer par mots-clés dans nom ou description ou catégories
    if query:
        keywords = query.lower().split()
        def match(row):
            text = f"{row.get('Nom fichier','')} {row.get('Description','')} {row.get('Catégories','')}".lower()
            return all(k in text for k in keywords)
        results = results[results.apply(match, axis=1)]
    
    # Filtrer par type de fichier
    if file_types:
        results = results[results['Nom fichier'].apply(lambda x: os.path.splitext(x)[1].lower() in file_types)]
    
    st.write(f"Résultats trouvés : {len(results)}")
    
    # ----- Étape 3 : Affichage tableau des résultats -----
    st.dataframe(results[['Nom fichier', 'Chemin complet', 'Catégories', 'Description']])
    
    # ----- Étape 4 : Export -----
    st.subheader("Exporter les résultats")
    
    if not results.empty:
        # Export Excel
        excel_buffer = pd.ExcelWriter("filtered_results.xlsx", engine='openpyxl')
        results.to_excel(excel_buffer, index=False)
        excel_buffer.save()
        excel_buffer.close()
        
        st.download_button(
            "Télécharger en Excel",
            data=open("filtered_results.xlsx", "rb").read(),
            file_name="filtered_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Export JSON
        st.download_button(
            "Télécharger en JSON",
            data=results.to_json(orient="records", indent=2),
            file_name="filtered_results.json",
            mime="application/json"
        )
