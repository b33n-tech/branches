import streamlit as st
import pandas as pd
from collections import defaultdict

st.title("📂 Encodage guidé d'arborescence (Lazy Load)")

# 1️⃣ Upload du fichier .txt
uploaded_file = st.file_uploader("Upload ton fichier .txt d'arborescence", type="txt")

def build_hierarchy(lines):
    """Construit un dict hiérarchique {dossier_principal: [sous-elements]}"""
    hierarchy = defaultdict(list)
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split("/")
        root = parts[0]
        hierarchy[root].append("/".join(parts[1:]) if len(parts)>1 else "")
    return hierarchy

if uploaded_file:
    lines = uploaded_file.read().decode("utf-8").splitlines()
    st.success(f"Fichier chargé : {len(lines)} lignes")
    
    hierarchy = build_hierarchy(lines)
    
    # 2️⃣ Affichage des dossiers principaux
    selected_comments = {}
    for root, sub_items in hierarchy.items():
        if st.checkbox(f"{root}", key=root):
            # 3️⃣ Affichage sous-dossiers/fichiers uniquement si root coché
            with st.expander(f"Voir les éléments de {root}"):
                for idx, sub in enumerate(sub_items):
                    if sub:  # Si sous-dossier/fichier
                        full_path = f"{root}/{sub}"
                    else:
                        full_path = root
                    # Checkbox pour chaque sous-élément
                    if st.checkbox(full_path, key=f"{root}_{idx}"):
                        comment = st.text_input(f"Commentaire pour {full_path}", key=f"comment_{root}_{idx}")
                        selected_comments[full_path] = comment
    
    # 4️⃣ Export CSV / JSON enrichi
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
