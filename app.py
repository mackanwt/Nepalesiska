import json
import os
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


# Standarddata om filer saknas
DEFAULT_SENTENCES = [
    {
        "id": 1,
        "name": "Mat och Tid",
        "template_sv": "[Time] åt jag [Food].",
        "template_np": "[Time_np] ma [Food_np] khaaye.",
        "slots": {"Time": "time.json", "Food": "nouns.json"},
    }
]

DEFAULT_VERBS = [
    {
        "verb_sv": "att äta",
        "verb_np": "khanu (खानू)",
        "conjugations": {
            "Nutid (jag äter)": "ma khanchu",
            "Dåtid (jag åt)": "ma khaaye",
            "Framtid (jag ska äta)": "ma khane chu",
        },
    },
    {
        "verb_sv": "att gå",
        "verb_np": "janu (जानू)",
        "conjugations": {
            "Nutid (jag går)": "ma janchu",
            "Dåtid (jag gick)": "ma gaye",
            "Framtid (jag ska gå)": "ma jane chu",
        },
    },
]

DEFAULT_NOUNS = [
    {"word_sv": "frukost", "word_np": "bihanko khaja", "transliteration": "khaja"},
    {"word_sv": "mat", "word_np": "khana", "transliteration": "khana"},
]

DEFAULT_TIME = [
    {"word_sv": "idag", "word_np": "aja", "transliteration": "aja"},
    {"word_sv": "igår", "word_np": "hijo", "transliteration": "hijo"},
    {"word_sv": "imorgon", "word_np": "bholi", "transliteration": "bholi"},
]

DEFAULT_USER_SENTENCES = [
    {
        "sv": "Idag åt jag frukost.",
        "np": "Aja ma bihanko khaja khaaye.",
        "status": "Ej granskad",
    }
]

# Ladda in data
sentences_data = load_json("sentences.json", DEFAULT_SENTENCES)
verbs_data = load_json("verbs.json", DEFAULT_VERBS)
nouns_data = load_json("nouns.json", DEFAULT_NOUNS)
time_data = load_json("time.json", DEFAULT_TIME)
user_sentences_data = load_json("user_sentences.json", DEFAULT_USER_SENTENCES)

# --- APP-STRUKTUR (FLIKAR) ---
st.title("🇳🇵 Nepalesiska - Substitutionsapp")
st.write(
    "Lär dig nepalesiska genom att bygga meningar, träna verb och spara för feedback!"
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["🧩 Bygg Meningar", "📖 Verbböjningar", "✍️ Skrivbok & Fru", "🎯 Glos-Quiz"]
)

# --- FLIK 1: BYGG MENINGAR (SUBSTITUTION) ---
with tab1:
    st.header("Substitutionsövning")
    st.write("Välj en mall och byt ut delar för att skapa meningar.")

    if not sentences_data:
        st.warning("Inga meningsmallar hittades.")
    else:
        # Välj mall
        sentence_options = {s["name"]: s for s in sentences_data}
        selected_name = st.selectbox(
            "Välj meningsmall:", list(sentence_options.keys())
        )
        current_sentence = sentence_options[selected_name]

        st.markdown(
            f"**Svensk mall:** `{current_sentence['template_sv']}`"
        )

        # Dynamiska val för platshållare
        slot_values = {}
        for slot_key in current_sentence["slots"]:
            filename = current_sentence["slots"][slot_key]

            # Välj rätt datakälla beroende på filnamn
            if filename == "time.json":
                options_list = time_data
            elif filename == "nouns.json":
                options_list = nouns_data
            else:
                options_list = nouns_data

            choices = {
                f"{item['word_sv']} ({item['word_np']})": item
                for item in options_list
            }

            selected_choice = st.selectbox(
                f"Välj {slot_key}:", list(choices.keys()), key=f"slot_{slot_key}"
            )
            slot_values[slot_key] = choices[selected_choice]

        # Bygg ihop meningen
        final_sv = current_sentence["template_sv"]
        final_np = current_sentence["template_np"]

        for slot_key, item in slot_values.items():
            final_sv = final_sv.replace(f"[{slot_key}]", item["word_sv"])
            final_np = final_np.replace(
                f"[{slot_key}_np]", item["word_np"]
            )  # Byt ut mot nepalesiska

        st.success("### Genererad Mening:")
        st.markdown(f"**Svenska:** {final_sv}")
        st.markdown(f"**Nepalesiska:** {final_np}")

        if st.button("💾 Spara meningen till min skrivbok"):
            new_entry = {
                "sv": final_sv,
                "np": final_np,
                "status": "Väntar på granskning",
            }
            user_sentences_data.append(new_entry)
            save_json("user_sentences.json", user_sentences_data)
            st.toast("Meningen sparades i skrivboken!", icon="✅")

# --- FLIK 2: VERBBÖJNINGAR ---
with tab2:
    st.header("Verbböjningar & Lexikon")
    st.write(
        "Klicka på ett verb för att se dess böjningar i olika tidsformer."
    )

    if not verbs_data:
        st.warning("Inga verb inlagda än.")
    else:
        verb_choices = {
            f"{v['verb_sv']} - {v['verb_np']}": v for v in verbs_data
        }
        selected_verb_key = st.selectbox("Välj ett verb:", list(verb_choices.keys()))
        selected_verb = verb_choices[selected_verb_key]

        st.markdown(f"### Grundform: **{selected_verb['verb_np']}**")
        st.caption(f"Svenska: {selected_verb['verb_sv']}")

        st.write("#### Böjningar:")
        for tense, conjugation in selected_verb["conjugations"].items():
            st.info(f"**{tense}:** {conjugation}")

        with st.expander("➕ Lägg till nytt verb (eller redigera i JSON)"):
            new_sv = st.text_input("Svensk betydelse (t.ex. att sova):")
            new_np = st.text_input("Nepalesisk grundform (t.ex. sutnu):")
            if st.button("Spara nytt verb"):
                if new_sv and new_np:
                    verbs_data.append(
                        {
                            "verb_sv": new_sv,
                            "verb_np": new_np,
                            "conjugations": {
                                "Nutid": f"ma {new_np[:-2]}nchu",
                                "Dåtid": f"ma {new_np[:-2]}e",
                            },
                        }
                    )
                    save_json("verbs.json", verbs_data)
                    st.success("Verbet tillagt! Ladda om sidan.")
                else:
                    st.error("Fyll i båda fälten.")

# --- FLIK 3: SKRIVBOK & FRU-RÄTTNING ---
with tab3:
    st.header("Skrivbok & Fru-rättning")
    st.write(
        "Här kan du skriva egna meningar fritt och se sparade meningar från dina övningar."
    )

    # Lägg till helt egen mening
    with st.form("custom_sentence_form"):
        st.subheader("Skriv en egen mening")
        custom_sv = st.text_input("Svenska:")
        custom_np = st.text_input("Nepalesiska (använd ditt tangentbord):")
        submitted = st.form_submit_button("Spara mening")
        if submitted and custom_sv and custom_np:
            user_sentences_data.append(
                {
                    "sv": custom_sv,
                    "np": custom_np,
                    "status": "Väntar på granskning",
                }
            )
            save_json("user_sentences.json", user_sentences_data)
            st.success("Meningen har sparats!")

    st.divider()
    st.subheader("Sparade meningar:")

    if not user_sentences_data:
        st.info("Inga sparade meningar ännu.")
    else:
        for idx, item in enumerate(user_sentences_data):
            with st.container():
                st.markdown(f"**{idx+1}. Svenska:** {item['sv']}")
                st.markdown(f"**   Nepalesiska:** {item['np']}")
                st.caption(f"Status: {item['status']}")
                if st.button(
                    f"Radera mening {idx+1}", key=f"del_sent_{idx}"
                ):
                    user_sentences_data.pop(idx)
                    save_json("user_sentences.json", user_sentences_data)
                    st.rerun()
                st.write("---")

# --- FLIK 4: GLOS-QUIZ ---
with tab4:
    st.header("Glos-Quiz")
    st.write("Testa ditt ordförråd från dina kategorier!")

    category_choice = st.selectbox(
        "Välj kategori att träna på:", ["Substantiv", "Tid"]
    )

    if category_choice == "Substantiv":
        active_vocab = nouns_data
    else:
        active_vocab = time_data

    if not active_vocab:
        st.warning("Tom kategori.")
    else:
        import random

        if "quiz_item" not in st.session_state:
            st.session_state.quiz_item = random.choice(active_vocab)

        current_q = st.session_state.quiz_item

        st.markdown(
            f"### Vad betyder det svenska ordet **'{current_q['word_sv']}'** på nepalesiska?"
        )
        user_guess = st.text_input(
            "Skriv ditt svar här (eller transkribering):", key="quiz_input"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Kontrollera svar"):
                if (
                    user_guess.strip().lower()
                    == current_q["word_np"].strip().lower()
                    or user_guess.strip().lower()
                    == current_q.get("transliteration", "").strip().lower()
                ):
                    st.success("🎉 Rätt svar!")
                else:
                    st.error(
                        f"❌ Fel. Rätt svar är: **{current_q['word_np']}** ({current_q.get('transliteration', '')})"
                    )
        with col2:
            if st.button("Nästa ord"):
                st.session_state.quiz_item = random.choice(active_vocab)
                st.rerun()
