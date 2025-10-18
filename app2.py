import streamlit as st
import pandas as pd
from pathlib import Path

st.title("📂 Encodage guidé d'arborescence")

# 1️⃣ Upload du fichier .txt
uploaded_file = st.file_uploader("Upload ton fichier .txt d'arborescence", type="txt")

if uploaded_file:
    lines = [line.strip() for line in uploaded_file.read().decode("utf-8").splitlines() if line.strip()]
    
    # Créer un dataframe de base
    df = pd.DataFrame({
        "Chemin": lines,
        "Commentaire": [""]*len(lines)
    })
    
    st.write("Sélectionne les fichiers/dossiers à documenter :")
    
    # 2️⃣ Affichage en liste avec checkbox
    selected_indices = []
    for idx, row in df.iterrows():
        if st.checkbox(row["Chemin"], key=idx):
            selected_indices.append(idx)
            # 3️⃣ Zone de texte pour commentaire
            comment = st.text_input(f"Commentaire pour {row['Chemin']}", key=f"comment_{idx}")
            df.at[idx, "Commentaire"] = comment
    
    # 4️⃣ Export du fichier enrichi
    if st.button("Exporter CSV enrichi"):
        export_path = "arborescence_enrichie.csv"
        df.to_csv(export_path, index=False)
        st.success(f"Fichier exporté : {export_path}")
        st.download_button(
            label="Télécharger le CSV",
            data=open(export_path, "rb").read(),
            file_name="arborescence_enrichie.csv",
            mime="text/csv"
        )
