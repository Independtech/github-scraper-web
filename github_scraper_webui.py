import streamlit as st
from datetime import datetime
import os
from github_scraper_core import fetch_profiles, sort_profiles, save_to_excel, LANGUAGE_ORDER

st.set_page_config(page_title="GitHub Profile Scraper", layout="centered")
st.title("🔍 GitHub Profile Scraper")

# --- Inputs ---
languages_input = st.text_input("Vilka språk vill du söka efter? (kommaseparerat)", "Java, Python, JavaScript")
languages = [lang.strip() for lang in languages_input.split(",") if lang.strip()]

mode = st.selectbox(
    "Vilken typ av profiler vill du söka efter?",
    ["För anställning (filtrerar bort frilansare)", "Endast konsulter", "Alla typer"],
    index=0
)
mode_map = {
    "För anställning (filtrerar bort frilansare)": "for_employment",
    "Endast konsulter": "only_consultants",
    "Alla typer": "all"
}
selected_mode = mode_map[mode]

count_option = st.selectbox("Hur många profiler vill du hämta?", [30, 60, 90, "Alla"], index=1)
max_results = -1 if count_option == "Alla" else count_option

if st.button("🔎 Kör sökning"):
    with st.spinner("Hämtar profiler från GitHub..."):
        location = "Stockholm"
        profiles = fetch_profiles(languages, location=location, max_results=max_results, mode=selected_mode)

        if len(profiles) == 0:
            st.warning("Inga profiler hittades i Stockholm – försöker med 'Sweden' istället...")
            profiles = fetch_profiles(languages, location="Sweden", max_results=max_results, mode=selected_mode)

        profiles = sort_profiles(profiles)

        # Visa summering
        lang_counts = {lang: 0 for lang in LANGUAGE_ORDER}
        for p in profiles:
            lang = p["Primärt språk"]
            if lang not in lang_counts:
                lang = "Annat"
            lang_counts[lang] += 1

        st.subheader("🔢 Antal profiler per primärt språk:")
        for lang in LANGUAGE_ORDER:
            st.write(f"- {lang}: {lang_counts.get(lang, 0)}")

        # Exportera till Excel
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"github_profiles_{'-'.join([l.lower() for l in languages])}_{timestamp}.xlsx"
        save_to_excel(profiles, filename)

        with open(filename, "rb") as f:
            st.download_button("⬇️ Ladda ner resultat som Excel", f, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
