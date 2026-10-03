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
        "verb_np": "खानू",
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

# --- FLIK 1: BYGG MENINGAR (VALBARA KATEGORIER & HINT) ---
with tab1:
    st.header("Aktiv Meningsbyggnad")
    st.write(
        "Välj vilka kategorier du vill inkludera och slumpa fram ord att bygga med!"
    )

    cat_files = get_category_files()
    cat_display_names = {f: f.replace(".json", "").capitalize() for f in cat_files}

    # Multiselect för att välja vilka kategorier som ska slumpas
    selected_cats = st.multiselect(
        "Välj kategorier att slumpa ord från:",
        options=cat_files,
        format_func=lambda x: cat_display_names[x],
        default=cat_files,
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

    # Hämta eller initiera om den är tom
    if "random_challenge" not in st.session_state or not st.session_state.random_challenge:
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
                st.info(
                    f"**{cat}**\n\n🇳🇵 {word_obj.get('word_np', '')}\n\n🔤 *{word_obj.get('transliteration', '')}*"
                )

        # Hint-knapp för att se svensk betydelse
        with st.expander("🔍 Hint: Visa svensk betydelse för de slumpade orden"):
            for cat, word_obj in st.session_state.random_challenge.items():
                st.write(
                    f"**{cat}:** {word_obj.get('word_sv', '')} (*{word_obj.get('transliteration', '')}*)"
                )

    with st.expander("💡 Visa alla tillgängliga ord i kategorierna som referens"):
        for cfile in cat_files:
            cat_name = cat_display_names[cfile]
            cdata = load_json(cfile, [])
            st.markdown(f"**Kategori: {cat_name}**")
            for item in cdata:
                st.text(
                    f"• {item.get('word_np')} ({item.get('transliteration')})"
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

# --- FLIK 2: VERBBÖJNINGAR & NYA BÖJNINGAR ---
with tab2:
    st.header("Verbböjningar & Lexikon")

    if not verbs_data:
        st.warning("Inga verb inlagda än.")
    else:
        verb_choices = {
            f"{v['verb_sv']} - {v.get('verb_np', '')} ({v.get('transliteration', '')})": v
            for v in verbs_data
        }
        selected_verb_key = st.selectbox("Välj ett verb:", list(verb_choices.keys()))
        selected_verb = verb_choices[selected_verb_key]

        st.markdown(
            f"### Grundform: **{selected_verb.get('verb_np', '')}** (*{selected_verb.get('transliteration', '')}*)"
        )
        st.caption(f"Svenska: {selected_verb['verb_sv']}")

        st.write("#### Nuvarande böjningar:")
        if selected_verb.get("conjugations"):
            for tense, conjugation in selected_verb["conjugations"].items():
                st.info(f"**{tense}:** {conjugation}")
        else:
            st.write("Inga böjningar tillagda än.")

        st.divider()
        st.subheader("➕ Lägg till ny böjning för detta verb")
        new_tense_name = st.text_input(
            "Tidsform / Beskrivning (t.ex. 'Imperativ (gör det!)' eller 'Dåtid'):"
        )
        new_tense_value = st.text_input("Böjd form på nepalesiska / romaji:")

        if st.button("Spara ny böjning"):
            if new_tense_name and new_tense_value:
                # Hitta rätt verb i listan och uppdatera
                for v in verbs_data:
                    if v["verb_sv"] == selected_verb["verb_sv"]:
                        if "conjugations" not in v:
                            v["conjugations"] = {}
                        v["conjugations"][new_tense_name] = new_tense_value
                        break
                save_json("verbs.json", verbs_data)
                st.success(
                    f"Lade till '{new_tense_name}' för {selected_verb['verb_sv']}! Ladda om sidan om det inte syns direkt."
                )
            else:
                st.error("Fyll i både tidsform och böjd form.")

        st.divider()
        with st.expander("➕ Lägg till ett helt nytt verb i lexikonet"):
            new_v_sv = st.text_input("Svenska (t.ex. att sova):")
            new_v_np = st.text_input("Nepalesiska tecken (t.ex. सुत्नु):")
            new_v_trans = st.text_input("Romaji (t.ex. sutnu):")
            if st.button("Spara nytt verb"):
                if new_v_sv and new_v_trans:
                    verbs_data.append(
                        {
                            "verb_sv": new_v_sv,
                            "verb_np": new_v_np,
                            "transliteration": new_v_trans,
                            "conjugations": {},
                        }
                    )
                    save_json("verbs.json", verbs_data)
                    st.success("Nytt verb tillagt!")
                else:
                    st.error("Fyll i åtminstone svenska och romaji.")

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
            if word_sv and (word_np or translit):
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
                st.error("Fyll i svenska samt minst en nepalesisk variant.")

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

# --- FLIK 5: GLOS-QUIZ (Fritext eller Flerval) ---
with tab5:
    st.header("Glos-Quiz")

    cat_files = get_category_files()
    cat_names = [f.replace(".json", "") for f in cat_files]
    quiz_cat = st.selectbox("Välj kategori att träna på:", cat_names, key="quiz_cat_select")

    active_vocab = load_json(f"{quiz_cat}.json", [])

    # Välj svarsläge
    quiz_mode = st.radio(
        "Välj träningsläge:", ["Fritext (skriv själv)", "Flerval (välj bland 10 alternativ)"], horizontal=True
    )

    # Nollställ quiz-item om kategorin eller läget ändras
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
            # Om flerval, generera 10 alternativ
            if quiz_mode == "Flerval (välj bland 10 alternativ)" and len(active_vocab) > 1:
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
        if "quiz_item" not in st.session_state or not st.session_state.quiz_item:
            st.session_state.quiz_item = random.choice(active_vocab)
            if quiz_mode == "Flerval (välj bland 10 alternativ)" and len(active_vocab) > 1:
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
                "Skriv ditt svar (nepalesiska tecken eller translitterering):",
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

                    if guess and (guess == correct_np or guess == correct_trans):
                        st.success("🎉 Rätt svar!")
                    else:
                        st.error(
                            f"❌ Fel. Rätt svar är: **{current_q.get('word_np')}** (*{current_q.get('transliteration')}*)"
                        )
            with col2:
                if st.button("Nästa ord"):
                    st.session_state.quiz_item = random.choice(active_vocab)
                    st.rerun()
        else:
            # Flervalsläge med upp till 10 alternativ
            if "quiz_options" in st.session_state:
                options = st.session_state.quiz_options
                option_labels = [
                    f"{opt.get('word_np')} ({opt.get('transliteration')})" for opt in options
                ]

                chosen_label = st.radio("Välj rätt översättning:", option_labels, key="quiz_radio")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Kontrollera svar (Flerval)"):
                        correct_label = f"{current_q.get('word_np')} ({current_q.get('transliteration')})"
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
                        others = [item for item in active_vocab if item != correct]
                        selected_others = random.sample(others, min(9, len(others)))
                        options = selected_others + [correct]
                        random.shuffle(options)
                        st.session_state.quiz_options = options
                        st.rerun()
            else:
                st.warning("Kunde inte ladda flervalsalternativ. Byt kategori eller lägg till fler ord.")
