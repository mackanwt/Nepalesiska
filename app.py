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
    # Inkluderar verbs.json som en vanlig kategori om den finns
    files = ["nouns.json", "time.json", "verbs.json"]
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.endswith(".json") and f not in [
                "sentences.json",
                "user_sentences.json",
            ]:
                if f not in files:
                    files.append(f)
    return files


# Standarddata om filer saknas
DEFAULT_VERBS = [
    {
        "word_sv": "att äta",
        "word_np": "खानू",
        "transliteration": "khanu",
        "conjugations": {
            "Nutid (jag äter)": {
                "translit": "ma khanchu",
                "np": "म खानschu",
            },
            "Dåtid (jag åt)": {"translit": "ma khaaye", "np": "म खाइए"},
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
user_sentences_data = load_json("user_sentences.json", DEFAULT_USER_SENTENCES)
# Säkerställ att grundfiler finns
load_json("verbs.json", DEFAULT_VERBS)
load_json("nouns.json", DEFAULT_NOUNS)
load_json("time.json", DEFAULT_TIME)

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

# --- FLIK 1: BYGG MENINGAR (VALBARA KATEGORIER & HINT) ---
with tab1:
    st.header("Aktiv Meningsbyggnad")
    st.write(
        "Välj vilka kategorier du vill inkludera och slumpa fram ord att bygga med!"
    )

    cat_files = get_category_files()
    cat_display_names = {f: f.replace(".json", "").capitalize() for f in cat_files}

    selected_cats = st.multiselect(
        "Välj kategorier att slumpa ord från:",
        options=cat_files,
        format_func=lambda x: cat_display_names[x],
        default=[c for c in cat_files if c in ["nouns.json", "time.json"]],
    )

    if st.button("🎲 Slumpa fram nya ord"):
        if not selected_cats:
            st.warning("Du måste välja minst en kategori!")
        else:
            selected_words = {}
            for cfile in selected_cats:
                cdata = load_json(cfile, [])
                if cdata:
                    chosen = random.choice(cdata)
                    cat_name = cat_display_names[cfile]
                    selected_words[cat_name] = chosen
            st.session_state.random_challenge = selected_words

    if (
        "random_challenge" not in st.session_state
        or not st.session_state.random_challenge
    ):
        if selected_cats:
            selected_words = {}
            for cfile in selected_cats:
                cdata = load_json(cfile, [])
                if cdata:
                    chosen = random.choice(cdata)
                    cat_name = cat_display_names[cfile]
                    selected_words[cat_name] = chosen
            st.session_state.random_challenge = selected_words

    if "random_challenge" in st.session_state and st.session_state.random_challenge:
        st.markdown("### Dagens slumpade ord (Byggstenar):")
        cols = st.columns(len(st.session_state.random_challenge))
        for idx, (cat, word_obj) in enumerate(
            st.session_state.random_challenge.items()
        ):
            with cols[idx]:
                np_text = word_obj.get("word_np", "")
                trans_text = word_obj.get("transliteration", "")
                st.info(
                    f"**{cat}**\n\n🔤 *{trans_text}*\n\n🇳🇵 {np_text}"
                )

        with st.expander("🔍 Hint: Visa svensk betydelse för de slumpade orden"):
            for cat, word_obj in st.session_state.random_challenge.items():
                trans = word_obj.get("transliteration", "")
                np_t = word_obj.get("word_np", "")
                st.write(
                    f"**{cat}:** {word_obj.get('word_sv', '')} (*{trans}* / {np_t})"
                )

    with st.expander("💡 Visa alla tillgängliga ord i kategorierna som referens"):
        for cfile in cat_files:
            cat_name = cat_display_names[cfile]
            cdata = load_json(cfile, [])
            st.markdown(f"**Kategori: {cat_name}**")
            for item in cdata:
                trans = item.get("transliteration", "")
                np_t = item.get("word_np", "")
                st.text(f"• {trans} ({np_t})")

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

    verbs_data = load_json("verbs.json", DEFAULT_VERBS)

    if not verbs_data:
        st.warning(
            "Inga verb inlagda än. Lägg till verb i 'Ordförråd & Kategorier' under kategorin 'verbs'."
        )
    else:
        verb_choices = {
            f"{v.get('word_sv', '')} - {v.get('transliteration', '')} ({v.get('word_np', '')})": v
            for v in verbs_data
        }
        selected_verb_key = st.selectbox("Välj ett verb:", list(verb_choices.keys()))
        selected_verb = verb_choices[selected_verb_key]

        st.markdown(
            f"### Grundform: 🔤 *{selected_verb.get('transliteration', '')}* | 🇳🇵 {selected_verb.get('word_np', '')}"
        )
        st.caption(f"Svenska: {selected_verb.get('word_sv', '')}")

        st.write("#### Nuvarande böjningar:")
        if selected_verb.get("conjugations"):
            for tense, conj_data in selected_verb["conjugations"].items():
                # Hantera både gammal struktur (sträng) och ny struktur (dict med romaji och np)
                if isinstance(conj_data, dict):
                    t_val = conj_data.get("translit", "")
                    np_val = conj_data.get("np", "")
                    st.info(f"**{tense}:** 🔤 {t_val}  |  🇳🇵 {np_val}")
                else:
                    st.info(f"**{tense}:** {conj_data}")
        else:
            st.write("Inga böjningar tillagda än.")

        st.divider()
        st.subheader("➕ Lägg till ny böjning för detta verb")
        new_tense_name = st.text_input(
            "Tidsform / Beskrivning (t.ex. 'Nutid', 'Dåtid'):"
        )
        new_tense_trans = st.text_input("Böjd form med Romaji (t.ex. ma khanchu):")
        new_tense_np = st.text_input("Böjd form med Devanagari (t.ex. म खानchu):")

        if st.button("Spara ny böjning"):
            if new_tense_name and new_tense_trans:
                for v in verbs_data:
                    if v.get("word_sv") == selected_verb.get("word_sv"):
                        if "conjugations" not in v:
                            v["conjugations"] = {}
                        v["conjugations"][new_tense_name] = {
                            "translit": new_tense_trans,
                            "np": new_tense_np,
                        }
                        break
                save_json("verbs.json", verbs_data)
                st.success(
                    f"Lade till '{new_tense_name}' för {selected_verb.get('word_sv')}!"
                )
                st.rerun()
            else:
                st.error("Fyll i åtminstone tidsform och romaji.")

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
        translit = st.text_input("Romaji / Transliteration (t.ex. 'khaja'):")
        word_np = st.text_input("Nepalesiska tecken (Devanagari):")

        if st.button("Spara ord"):
            if word_sv and (translit or word_np):
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
                st.error(
                    "Fyll i svenska samt minst en variant (romaji eller devanagari)."
                )

    with col_b:
        st.subheader("📁 Skapa ny kategori")
        new_cat_name = st.text_input(
            "Namn på ny kategori (t.ex. 'platser', 'kläder'):", key="new_cat_input"
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
            # Bakåtkompatibilitet för äldre objekt i nouns/time
            t_val = item.get("transliteration", "")
            np_val = item.get("word_np", "")
            sv_val = item.get("word_sv", "")
            st.text(
                f"🇸🇪 {sv_val}  |  🔤 {t_val}  |  🇳🇵 {np_val}"
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

# --- FLIK 5: GLOS-QUIZ (Fritext eller Flerval) ---
with tab5:
    st.header("Glos-Quiz")

    cat_files = get_category_files()
    cat_names = [f.replace(".json", "") for f in cat_files]
    quiz_cat = st.selectbox(
        "Välj kategori att träna på:", cat_names, key="quiz_cat_select"
    )

    active_vocab = load_json(f"{quiz_cat}.json", [])

    quiz_mode = st.radio(
        "Välj träningsläge:",
        ["Fritext (skriv själv)", "Flerval (välj bland 10 alternativ)"],
        horizontal=True,
    )

    if (
        "last_quiz_cat" not in st.session_state
        or st.session_state.last_quiz_cat != quiz_cat
        or "last_quiz_mode" not in st.session_state
        or st.session_state.last_quiz_mode != quiz_mode
    ):
        st.session_state.last_quiz_cat = quiz_cat
        st.session_state.last_quiz_mode = quiz_mode
        if active_vocab:
            st.session_state.quiz_item = random.choice(active_vocab)
            if (
                quiz_mode == "Flerval (välj bland 10 alternativ)"
                and len(active_vocab) > 1
            ):
                correct = st.session_state.quiz_item
                others = [item for item in active_vocab if item != correct]
                selected_others = random.sample(others, min(9, len(others)))
                options = selected_others + [correct]
                random.shuffle(options)
                st.session_state.quiz_options = options
        else:
            st.session_state.quiz_item = None

    if not active_vocab:
        st.warning("Tom kategori. Lägg till ord i ordförråds-fliken först!")
    else:
        if (
            "quiz_item" not in st.session_state
            or not st.session_state.quiz_item
        ):
            st.session_state.quiz_item = random.choice(active_vocab)
            if (
                quiz_mode == "Flerval (välj bland 10 alternativ)"
                and len(active_vocab) > 1
            ):
                correct = st.session_state.quiz_item
                others = [item for item in active_vocab if item != correct]
                selected_others = random.sample(others, min(9, len(others)))
                options = selected_others + [correct]
                random.shuffle(options)
                st.session_state.quiz_options = options

        current_q = st.session_state.quiz_item

        st.markdown(
            f"### Vad betyder det svenska ordet **'{current_q.get('word_sv')}'**?"
        )

        if "Fritext" in quiz_mode:
            user_guess = st.text_input(
                "Skriv ditt svar (romaji eller devanagari):",
                key="quiz_input_free",
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Kontrollera svar"):
                    correct_np = current_q.get("word_np", "").strip().lower()
                    correct_trans = (
                        current_q.get("transliteration", "").strip().lower()
                    )
                    guess = user_guess.strip().lower()

                    if guess and (
                        guess == correct_np or guess == correct_trans
                    ):
                        st.success("🎉 Rätt svar!")
                    else:
                        t_str = current_q.get("transliteration", "")
                        np_str = current_q.get("word_np", "")
                        st.error(
                            f"❌ Fel. Rätt svar är: 🔤 {t_str} | 🇳🇵 {np_str}"
                        )
            with col2:
                if st.button("Nästa ord"):
                    st.session_state.quiz_item = random.choice(active_vocab)
                    st.rerun()
        else:
            if "quiz_options" in st.session_state:
                options = st.session_state.quiz_options
                option_labels = [
                    f"🔤 {opt.get('transliteration', '')}  |  🇳🇵 {opt.get('word_np', '')}"
                    for opt in options
                ]

                chosen_label = st.radio(
                    "Välj rätt översättning:", option_labels, key="quiz_radio"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Kontrollera svar (Flerval)"):
                        correct_label = f"🔤 {current_q.get('transliteration', '')}  |  🇳🇵 {current_q.get('word_np', '')}"
                        if chosen_label == correct_label:
                            st.success("🎉 Rätt svar!")
                        else:
                            st.error(
                                f"❌ Fel. Rätt svar var: **{correct_label}**"
                            )
                with col2:
                    if st.button("Nästa ord (Flerval)"):
                        st.session_state.quiz_item = random.choice(active_vocab)
                        correct = st.session_state.quiz_item
                        others = [
                            item for item in active_vocab if item != correct
                        ]
                        selected_others = random.sample(
                            others, min(9, len(others))
                        )
                        options = selected_others + [correct]
                        random.shuffle(options)
                        st.session_state.quiz_options = options
                        st.rerun()
            else:
                st.warning(
                    "Kunde inte ladda flervalsalternativ. Byt kategori eller lägg till fler ord."
                )
