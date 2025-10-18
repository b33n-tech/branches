import streamlit as st
import pandas as pd
from collections import defaultdict

st.title("📂 Encodage guidé d'arborescence (Lazy Load avec racine)")

# 1️⃣ Définir la racine de ton scan
ROOT = st.text_input("Chemin racine (ex: /Users/monnomid/Desktop/workshops-ecosystem-grand-est)")

# 2️⃣ Upload du fichier .txt
uploaded_file = st.file_uploader("Upload ton fichier .txt d'arborescence", type="txt")

def build_hierarchy(lines, root_path):
    """Construit un dict hiérarchique {dossier_principal: [sous-elements]}"""
    hierarchy = defaultdict(list)
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Retirer la racine
        if root_path and line.startswith(root_path):
            relative_path = line[len(root_path):].lstrip("/\\")
        else:
            relative_path = line
        parts = relative_path.split("/")
        root = parts[0]  # dossier principal métier
        hierarchy[root].append("/".join(parts[1:]) if len(parts) > 1 else "")
    return hierarchy

if uploaded_file and ROOT:
    lines = uploaded_file.read().decode("utf-8").splitlines()
    st.success(f"Fichier chargé : {len(lines)} lignes")
    
    hierarchy = build_hierarchy(lines, ROOT)
    
    selected_comments = {}
    
    st.subheader("Dossiers principaux de votre arborescence :")
    
    for root, sub_items in hierarchy.items():
        if st.checkbox(f"{root}", key=root):
            with st.expander(f"Voir les éléments de {root}"):
                for idx, sub in enumerate(sub_items):
                    if sub:  # Si sous-dossier/fichier
                        full_path = f"{root}/{sub}"
                    else:
                        full_path = root
                    if st.checkbox(full_path, key=f"{root}_{idx}"):
                        comment = st.text_input(f"Commentaire pour {full_path}", key=f"comment_{root}_{idx}")
                        selected_comments[full_path] = comment
    
    # Export CSV / JSON enrichi
    if st.button("Exporter CSV/JSON enrichi"):
        if selected_comments:
            df_export = pd.DataFrame({
                "Chemin": list(selected_comments.keys()),
                "Commentaire": list(selected_comments.values())
            })
            csv_path = "arborescence_enrichie.csv"
            json_path = "arborescence_enrichie.json"
            df_export.to_csv(csv_path, index=False)
            df_export.to_json(json_path, orient="records", indent=2)
            
            st.success("Fichier exporté !")
            st.download_button("Télécharger CSV", data=open(csv_path,"rb").read(), file_name="arborescence_enrichie.csv", mime="text/csv")
            st.download_button("Télécharger JSON", data=open(json_path,"rb").read(), file_name="arborescence_enrichie.json", mime="application/json")
        else:
            st.warning("Aucun élément sélectionné pour export.")
