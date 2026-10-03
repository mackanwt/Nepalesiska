import json
import os
import random
import streamlit as st

# --- SIDKONFIGURATION ---
st.set_page_config(
    page_title="Nepalesisk Språkinlärning", page_icon="🇳🇵", layout="centered"
)

# --- MAPP & FIL-HANTERING ---
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def load_json(filename, default_data):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data
    else:
        save_json(filename, default_data)
        return default_data


def save_json(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Hämta alla kategori-filer dynamiskt från data-mappen
def get_category_files():
    # Standardfiler som alltid ska finnas
    files = ["nouns.json", "time.json"]
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.endswith(".json") and f not in [
                "sentences.json",
                "verbs.json",
                "user_sentences.json",
            ]:
                if f not in files:
                    files.append(f)
    return files


# Standarddata om filer saknas
DEFAULT_VERBS = [
    {
        "verb_sv": "att äta",
        "verb_np": "khanu",
        "transliteration": "khanu",
        "conjugations": {
            "Nutid (jag äter)": "ma khanchu",
            "Dåtid (jag åt)": "ma khaaye",
        },
    }
]
DEFAULT_NOUNS = [
    {
        "word_sv": "frukost",
        "word_np": "बिहानको खाजा",
        "transliteration": "bihanko khaja",
    },
    {"word_sv": "mat", "word_np": "खाना", "transliteration": "khana"},
]
DEFAULT_TIME = [
    {"word_sv": "idag", "word_np": "आज", "transliteration": "aja"},
    {"word_sv": "igår", "word_np": "हिजो", "transliteration": "hijo"},
]
DEFAULT_USER_SENTENCES = [
    {
        "sv": "Idag åt jag frukost.",
        "np": "Aja ma bihanko khaja khaaye.",
        "status": "Ej granskad",
    }
]

# Ladda data
verbs_data = load_json("verbs.json", DEFAULT_VERBS)
user_sentences_data = load_json("user_sentences.json", DEFAULT_USER_SENTENCES)

# --- APP-STRUKTUR (FLIKAR) ---
st.title("🇳🇵 Nepalesiska - Träningsapp")
st.write(
    "Bygg meningar fritt, hantera ditt ordförråd och träna glosor utan facit i förväg!"
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🧩 Bygg Meningar",
        "📖 Verbböjningar",
        "📚 Ordförråd & Kategorier",
        "✍️ Skrivbok & Fru",
        "🎯 Glos-Quiz",
    ]
)

# --- FLIK 1: BYGG MENINGAR (SLUMP & FRITT SKAPANDE) ---
with tab1:
    st.header("Aktiv Meningsbyggnad")
    st.write(
        "Slumpa fram ord från olika kategorier och sätt ihop en egen mening!"
    )

    cat_files = get_category_files()

    if st.button("🎲 Slumpa fram nya ord att bygga med"):
        selected_words = {}
        for cfile in cat_files:
            cdata = load_json(cfile, [])
            if cdata:
                chosen = random.choice(cdata)
                cat_name = cfile.replace(".json", "").capitalize()
                selected_words[cat_name] = chosen
        st.session_state.random_challenge = selected_words

    # Hämta eller generera första gången
    if "random_challenge" not in st.session_state:
        selected_words = {}
        for cfile in cat_files:
            cdata = load_json(cfile, [])
            if cdata:
                chosen = random.choice(cdata)
                cat_name = cfile.replace(".json", "").capitalize()
                selected_words[cat_name] = chosen
        st.session_state.random_challenge = selected_words

    st.markdown("### Dagens slumpade ord (Byggstenar):")
    cols = st.columns(len(st.session_state.random_challenge))
    for idx, (cat, word_obj) in enumerate(
        st.session_state.random_challenge.items()
    ):
        with cols[idx]:
            st.info(
                f"**{cat}**\n\n🇳🇵 {word_obj.get('word_np', '')}\n\n🔤 *{word_obj.get('transliteration', '')}*"
            )

    with st.expander(
        "💡 Visa alla tillgängliga ord i kategorierna som referens"
    ):
        for cfile in cat_files:
            cdata = load_json(cfile, [])
            cat_name = cfile.replace(".json", "").capitalize()
            st.markdown(f"**Kategori: {cat_name}**")
            for item in cdata:
                st.text(
                    f"• {item.get('word_np')} ({item.get('transliteration')}) - [Svenska döljs här]"
                )

    st.divider()
    st.markdown("### Skriv din mening:")
    user_sv_input = st.text_input(
        "1. Skriv din svenska översättning av meningen:"
    )
    user_np_input = st.text_area(
        "2. Skriv meningen på nepalesiska (med ditt tangentbord):"
    )

    if st.button("💾 Spara meningen till skrivboken"):
        if user_sv_input and user_np_input:
            new_entry = {
                "sv": user_sv_input,
                "np": user_np_input,
                "status": "Väntar på granskning",
            }
            user_sentences_data.append(new_entry)
            save_json("user_sentences.json", user_sentences_data)
            st.success("Meningen sparad till skrivboken för fru-rättning! 🎉")
        else:
            st.error("Fyll i både den svenska och nepalesiska meningen.")

# --- FLIK 2: VERBBÖJNINGAR ---
with tab2:
    st.header("Verbböjningar & Lexikon")

    if not verbs_data:
        st.warning("Inga verb inlagda än.")
    else:
        verb_choices = {
            f"{v['verb_sv']} - {v['verb_np']}": v for v in verbs_data
        }
        selected_verb_key = st.selectbox("Välj ett verb:", list(verb_choices.keys()))
        selected_verb = verb_choices[selected_verb_key]

        st.markdown(
            f"### Grundform: **{selected_verb['verb_np']}** (*{selected_verb.get('transliteration', '')}*)"
        )
        st.caption(f"Svenska: {selected_verb['verb_sv']}")

        st.write("#### Böjningar:")
        for tense, conjugation in selected_verb["conjugations"].items():
            st.info(f"**{tense}:** {conjugation}")

# --- FLIK 3: ORDFÖRRÅD & KATEGORIER ---
with tab3:
    st.header("Ordförråd & Kategorihantering")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("➕ Lägg till nytt ord")
        cat_files = get_category_files()
        category_names = [f.replace(".json", "") for f in cat_files]

        selected_cat = st.selectbox("Välj kategori:", category_names)
        word_sv = st.text_input("Svenska:")
        word_np = st.text_input("Nepalesiska tecken (Devanagari):")
        translit = st.text_input("Romaji / Transliteration (t.ex. 'khaja'):")

        if st.button("Spara ord"):
            if word_sv and word_np:
                filename = f"{selected_cat}.json"
                current_data = load_json(filename, [])
                current_data.append(
                    {
                        "word_sv": word_sv,
                        "word_np": word_np,
                        "transliteration": translit,
                    }
                )
                save_json(filename, current_data)
                st.success(
                    f"Sparade '{word_sv}' i kategorin '{selected_cat}'!"
                )
            else:
                st.error("Fyll i åtminstone svenska och nepalesiska tecken.")

    with col_b:
        st.subheader("📁 Skapa ny kategori")
        new_cat_name = st.text_input(
            "Namn på ny kategori (t.ex. 'platser', 'kläder'):"
        )
        if st.button("Skapa kategori"):
            if new_cat_name:
                clean_name = new_cat_name.strip().lower().replace(" ", "_")
                filename = f"{clean_name}.json"
                if not os.path.exists(os.path.join(DATA_DIR, filename)):
                    save_json(filename, [])
                    st.success(
                        f"Kategorin '{clean_name}' skapades! Du kan nu lägga till ord i den."
                    )
                    st.rerun()
                else:
                    st.warning("Kategorin finns redan.")
            else:
                st.error("Skriv ett namn på kategorin.")

    st.divider()
    st.subheader("Befintliga ord i vald kategori:")
    view_cat = st.selectbox("Visa ord i kategori:", category_names, key="view_cat")
    cat_items = load_json(f"{view_cat}.json", [])
    if cat_items:
        for item in cat_items:
            st.text(
                f"🇸🇪 {item.get('word_sv')}  |  🇳🇵 {item.get('word_np')}  |  🔤 {item.get('transliteration')}"
            )
    else:
        st.info("Inga ord i denna kategori än.")

# --- FLIK 4: SKRIVBOK & FRU-RÄTTNING ---
with tab4:
    st.header("Skrivbok & Fru-rättning")
    st.write(
        "Här samlas dina sparade meningar. Din fru kan läsa och rätta dem!"
    )

    if not user_sentences_data:
        st.info("Inga sparade meningar ännu. Bygg några i första fliken!")
    else:
        for idx, item in enumerate(user_sentences_data):
            with st.container():
                st.markdown(f"**Mening {idx+1}:**")
                st.markdown(f"**Svenska:** {item['sv']}")
                st.markdown(f"**Nepalesiska:** {item['np']}")
                st.caption(f"Status: {item.get('status', 'Ej granskad')}")

                if st.button(f"Radera mening {idx+1}", key=f"del_sent_{idx}"):
                    user_sentences_data.pop(idx)
                    save_json("user_sentences.json", user_sentences_data)
                    st.rerun()
                st.write("---")

# --- FLIK 5: GLOS-QUIZ ---
with tab5:
    st.header("Glos-Quiz")

    cat_files = get_category_files()
    cat_names = [f.replace(".json", "") for f in cat_files]
    quiz_cat = st.selectbox("Välj kategori att träna på:", cat_names, key="quiz_cat_select")

    active_vocab = load_json(f"{quiz_cat}.json", [])

    # Nollställ quiz-item om kategorin ändras
    if (
        "last_quiz_cat" not in st.session_state
        or st.session_state.last_quiz_cat != quiz_cat
    ):
        st.session_state.last_quiz_cat = quiz_cat
        if active_vocab:
            st.session_state.quiz_item = random.choice(active_vocab)
        else:
            st.session_state.quiz_item = None

    if not active_vocab:
        st.warning("Tom kategori. Lägg till ord i ordförråds-fliken först!")
    else:
        if "quiz_item" not in st.session_state or not st.session_state.quiz_item:
            st.session_state.quiz_item = random.choice(active_vocab)

        current_q = st.session_state.quiz_item

        st.markdown(
            f"### Vad betyder det svenska ordet **'{current_q.get('word_sv')}'** på nepalesiska?"
        )
        user_guess = st.text_input(
            "Skriv ditt svar (nepalesiska tecken eller translitterering):",
            key="quiz_input",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Kontrollera svar"):
                correct_np = current_q.get("word_np", "").strip().lower()
                correct_trans = (
                    current_q.get("transliteration", "").strip().lower()
                )
                guess = user_guess.strip().lower()

                if guess == correct_np or guess == correct_trans:
                    st.success("🎉 Rätt svar!")
                else:
                    st.error(
                        f"❌ Fel. Rätt svar är: **{current_q.get('word_np')}** (*{current_q.get('transliteration')}*)"
                    )
        with col2:
            if st.button("Nästa ord"):
                st.session_state.quiz_item = random.choice(active_vocab)
                st.rerun()
