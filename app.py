import os
import pandas as pd
import streamlit as st

st.title("Scan Arborescence Dossier 🚀")

# Sélection du dossier (local)
folder = st.text_input("Chemin du dossier à scanner :", "")

if folder and os.path.exists(folder):
    st.info(f"Scan de : {folder}")
    
    def scan_folder(folder):
        data = []
        for dirpath, dirnames, filenames in os.walk(folder):
            level = dirpath.replace(folder, '').count(os.sep)
            parent = os.path.basename(os.path.dirname(dirpath)) if dirpath != folder else ""
            data.append({
                "Type": "Dossier",
                "Nom": os.path.basename(dirpath),
                "Chemin complet": dirpath,
                "Parent": parent,
                "Niveau": level,
                "Taille (octets)": ""
            })
            for f in filenames:
                full_path = os.path.join(dirpath, f)
                size = os.path.getsize(full_path)
                data.append({
                    "Type": "Fichier",
                    "Nom": f,
                    "Chemin complet": full_path,
                    "Parent": os.path.basename(dirpath),
                    "Niveau": level + 1,
                    "Taille (octets)": size
                })
        return pd.DataFrame(data)
    
    df = scan_folder(folder)
    st.dataframe(df)
    
    # Bouton pour télécharger en Excel
    st.download_button(
        label="Télécharger en Excel",
        data=df.to_excel(index=False, engine='openpyxl'),
        file_name="arborescence.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Merci d'entrer un chemin de dossier valide")

