import os
import pandas as pd
import streamlit as st
from tkinter import Tk, filedialog

st.title("Scan Arborescence Dossier 🚀")

# ---- Bouton pour sélectionner un dossier ----
if st.button("Choisir un dossier à scanner"):

    # Masquer la fenêtre Tkinter principale
    root = Tk()
    root.withdraw()

    # Ouvrir la boîte de dialogue pour choisir un dossier
    folder = filedialog.askdirectory()
    root.destroy()  # fermer la fenêtre Tkinter

    if folder:
        st.success(f"Dossier sélectionné : {folder}")

        # ---- Fonction pour scanner le dossier ----
        def scan_folder(folder):
            data = []
            for dirpath, dirnames, filenames in os.walk(folder):
                level = dirpath.replace(folder, '').count(os.sep)
                parent = os.path.basename(os.path.dirname(dirpath)) if dirpath != folder else ""
                # Dossier courant
                data.append({
                    "Type": "Dossier",
                    "Nom": os.path.basename(dirpath),
                    "Chemin complet": dirpath,
                    "Parent": parent,
                    "Niveau": level,
                    "Taille (octets)": ""
                })
                # Fichiers
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

        # ---- Scan et affichage ----
        df = scan_folder(folder)
        st.dataframe(df)

        # ---- Bouton pour télécharger en Excel ----
        excel_bytes = df.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="Télécharger en Excel",
            data=excel_bytes,
            file_name="arborescence.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Aucun dossier sélectionné")
