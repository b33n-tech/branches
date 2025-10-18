import streamlit as st
import pandas as pd
import os
import io  # pour buffer mémoire

st.title("Lecteur et recherche dans la base documentaire 📚")

# ----- Étape 1 : Upload du fichier CSV/JSON -----
uploaded_file = st.file_uploader(
    "Upload ton fichier annoté (.csv ou .json)", 
    type=["csv", "json"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:  # JSON
        df = pd.read_json(uploaded_file)
    
    st.success(f"{len(df)} fichiers/dossiers chargés dans la base documentaire.")

    # ----- Étape 2 : Barre de recherche + filtres sur la même ligne -----
    col1, col2 = st.columns([2, 1])  # proportion 2/3 pour mots-clés, 1/3 pour type fichier

    with col1:
        query = st.text_input("Recherche par mots-clés :", "")

    with col2:
        file_types = st.multiselect(
            "Filtrer par type de fichier (extensions)",
            options=sorted(df['Nom fichier'].apply(lambda x: os.path.splitext(x)[1].lower()).unique()),
            default=[]
        )

    # ----- Étape 3 : Filtrage des résultats -----
    results = df.copy()
    
    if query:
        keywords = query.lower().split()
        def match(row):
            text = f"{row.get('Nom fichier','')} {row.get('Description','')} {row.get('Catégories','')}".lower()
            return all(k in text for k in keywords)
        results = results[results.apply(match, axis=1)]
    
    if file_types:
        results = results[results['Nom fichier'].apply(lambda x: os.path.splitext(x)[1].lower() in file_types)]
    
    st.write(f"Résultats trouvés : {len(results)}")
    st.dataframe(results[['Nom fichier', 'Chemin complet', 'Catégories', 'Description']])

    # ----- Étape 4 : Export Excel / JSON via buffer mémoire -----
    if not results.empty:
        # Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            results.to_excel(writer, index=False)
        excel_buffer.seek(0)

        st.download_button(
            "Télécharger en Excel",
            data=excel_buffer,
            file_name="filtered_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # JSON
        json_str = results.to_json(orient="records", indent=2)
        st.download_button(
            "Télécharger en JSON",
            data=json_str,
            file_name="filtered_results.json",
            mime="application/json"
        )
