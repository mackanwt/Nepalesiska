import json
import os
import random
import streamlit as st

# --- SIDKONFIGURATION ---
st.set_page_config(
    page_title="Nepalesisk Språkinlärning", page_icon="🇳🇵", layout="wide"
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
                data = json.load(f)
                for item in data:
                    if "word_np" in item and "devanagari" not in item:
                        item["devanagari"] = item["word_np"]
                return data
        except Exception:
            return default_data
    else:
        save_json(filename, default_data)
        return default_data


def save_json(filename, data):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_category_files():
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


# Standarddata
DEFAULT_VERBS = [
    {
        "word_sv": "att äta",
        "transliteration": "khanu",
        "devanagari": "खानू",
        "conjugations": {
            "Nutid": {"translit": "ma khanchu", "devanagari": "म खानछु"},
            "Dåtid": {"translit": "ma khaaye", "devanagari": "म खाइए"},
        },
    }
]
DEFAULT_NOUNS = [
    {
        "word_sv": "frukost",
        "transliteration": "bihanko khaja",
        "devanagari": "बिहानको खाजा",
    },
    {"word_sv": "mat", "transliteration": "khana", "devanagari": "खाना"},
]
DEFAULT_TIME = [
    {"word_sv": "idag", "transliteration": "aja", "devanagari": "आज"},
    {"word_sv": "igår", "transliteration": "hijo", "devanagari": "हिजो"},
]
DEFAULT_USER_SENTENCES = [
    {
        "sv": "Idag åt jag frukost.",
        "np": "Aja ma bihanko khaja khaaye.",
        "status": "Granskad",
    }
]

# Ladda data
user_sentences_data = load_json("user_sentences.json", DEFAULT_USER_SENTENCES)
load_json("verbs.json", DEFAULT_VERBS)
load_json("nouns.json", DEFAULT_NOUNS)
load_json("time.json", DEFAULT_TIME)

# --- HJÄLPFUNKTION FÖR SPECIALTECKEN PÅ HÖGERSIDAN ---
def render_special_chars_sidebar():
    st.markdown("### 🔤 Specialtecken")
    st.caption("Klicka för att kopiera tecken:")
    
    chars = ["ā", "ī", "ū", "ṭ", "ṇ", "ḍ", "ṛ", "ṣ", "ś", "ṅ", "ñ", "ã"]
    
    cols = st.columns(3)
    for idx, char in enumerate(chars):
        with cols[idx % 3]:
            st.code(char, language=None)


# --- HUVUDLAYOUT ---
st.title("🇳🇵 Nepalesiska - Träningsapp")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🧩 Bygg Meningar",
        "📖 Verbböjningar",
        "📚 Ordförråd",
        "✍️ Skrivbok & Fru",
        "🎯 Glos-Quiz",
        "💬 Meningsquiz",
    ]
)

# --- FLIK 1: BYGG MENINGAR ---
with tab1:
    main_col, right_col = st.columns([3, 1])
    with main_col:
        st.header("Aktiv Meningsbyggnad")
        st.write("Välj kategorier och slumpa fram ord att bygga med!")

        cat_files = get_category_files()
        cat_display_names = {f: f.replace(".json", "").capitalize() for f in cat_files}

        selected_cats = st.multiselect(
            "Välj kategorier:",
            options=cat_files,
            format_func=lambda x: cat_display_names[x],
            default=[c for c in cat_files if c in ["nouns.json", "time.json"]],
            key="t1_multiselect"
        )

        if st.button("🎲 Slumpa fram nya ord", key="t1_btn"):
            if not selected_cats:
                st.warning("Välj minst en kategori!")
            else:
                selected_words = {}
                for cfile in selected_cats:
                    cdata = load_json(cfile, [])
                    if cdata:
                        chosen = random.choice(cdata)
                        selected_words[cat_display_names[cfile]] = chosen
                st.session_state.random_challenge = selected_words

        if "random_challenge" not in st.session_state or not st.session_state.random_challenge:
            if selected_cats:
                selected_words = {}
                for cfile in selected_cats:
                    cdata = load_json(cfile, [])
                    if cdata:
                        chosen = random.choice(cdata)
                        selected_words[cat_display_names[cfile]] = chosen
                st.session_state.random_challenge = selected_words

        if "random_challenge" in st.session_state and st.session_state.random_challenge:
            st.markdown("### Dagens byggstenar:")
            cols = st.columns(len(st.session_state.random_challenge))
            for idx, (cat, word_obj) in enumerate(st.session_state.random_challenge.items()):
                with cols[idx]:
                    trans = word_obj.get("transliteration", "")
                    dev = word_obj.get("devanagari", word_obj.get("word_np", ""))
                    st.info(f"**{cat}**\n\n🔤 {trans}\n\n🇳🇵 {dev}")

            with st.expander("🔍 Hint: Visa svensk betydelse"):
                for cat, word_obj in st.session_state.random_challenge.items():
                    st.write(f"**{cat}:** {word_obj.get('word_sv', '')} (*{word_obj.get('transliteration', '')}* / {word_obj.get('devanagari', '')})")

        with st.expander("💡 Visa alla tillgängliga ord som referens"):
            for cfile in cat_files:
                st.markdown(f"**{cat_display_names[cfile]}**")
                for item in load_json(cfile, []):
                    st.text(f"• 🔤 {item.get('transliteration', '')}  |  🇳🇵 {item.get('devanagari', '')}")

        st.divider()
        user_sv_input = st.text_input("1. Svensk översättning:", key="t1_sv")
        user_np_input = st.text_area("2. Nepalesisk mening:", key="t1_np")

        if st.button("💾 Spara till skrivboken", key="t1_save"):
            if user_sv_input and user_np_input:
                user_sentences_data.append({"sv": user_sv_input, "np": user_np_input, "status": "Ej granskad"})
                save_json("user_sentences.json", user_sentences_data)
                st.success("Sparat till skrivboken!")
            else:
                st.error("Fyll i båda fälten.")

    with right_col:
        render_special_chars_sidebar()

# --- FLIK 2: VERBBÖJNINGAR ---
with tab2:
    main_col, right_col = st.columns([3, 1])
    with main_col:
        st.header("Verbböjningar")
        verbs_data = load_json("verbs.json", DEFAULT_VERBS)

        if not verbs_data:
            st.warning("Inga verb inlagda än.")
        else:
            verb_choices = {
                f"{v.get('word_sv', 'Okänd')} - {v.get('transliteration', '')} ({v.get('devanagari', '')})": v 
                for v in verbs_data
            }
            selected_verb_key = st.selectbox("Välj ett verb:", list(verb_choices.keys()), key="t2_verb_select")
            selected_verb = verb_choices[selected_verb_key]

            st.markdown(f"### Grundform: 🔤 {selected_verb.get('transliteration', '')}  |  🇳🇵 {selected_verb.get('devanagari', '')}")
            st.caption(f"Svenska: {selected_verb.get('word_sv', '')}")

            st.write("#### Nuvarande böjningar:")
            conjugations = selected_verb.get("conjugations", {})
            if not conjugations:
                st.info("Inga böjningar tillagda för detta verb ännu.")
            else:
                for tense, conj_data in conjugations.items():
                    if isinstance(conj_data, dict):
                        st.info(f"**{tense}:** 🔤 {conj_data.get('translit', '')}  |  🇳🇵 {conj_data.get('devanagari', '')}")
                    else:
                        st.info(f"**{tense}:** {conj_data}")

            st.divider()
            st.subheader("➕ Lägg till ny böjning")
            new_tense_name = st.text_input("Tidsform / Beskrivning:", key="t2_tense")
            new_tense_trans = st.text_input("Romaji:", key="t2_trans")
            new_tense_dev = st.text_input("Devanagari:", key="t2_dev")

            if st.button("Spara böjning", key="t2_save"):
                if new_tense_name and (new_tense_trans or new_tense_dev):
                    for v in verbs_data:
                        if v.get("word_sv") == selected_verb.get("word_sv"):
                            if "conjugations" not in v:
                                v["conjugations"] = {}
                            v["conjugations"][new_tense_name] = {"translit": new_tense_trans, "devanagari": new_tense_dev}
                            break
                    save_json("verbs.json", verbs_data)
                    st.success("Böjning sparad!")
                    st.rerun()
                else:
                    st.error("Fyll i tidsform och minst en form.")

            st.divider()
            with st.expander("✏️ Redigera eller Radera detta verb"):
                edit_sv = st.text_input("Svenska (grundform):", value=selected_verb.get("word_sv", ""), key="t2_edit_sv")
                edit_trans = st.text_input("Romaji (grundform):", value=selected_verb.get("transliteration", ""), key="t2_edit_trans")
                edit_dev = st.text_input("Devanagari (grundform):", value=selected_verb.get("devanagari", ""), key="t2_edit_dev")

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    if st.button("💾 Spara ändringar i verb", key="t2_save_edit"):
                        for v in verbs_data:
                            if v.get("word_sv") == selected_verb.get("word_sv"):
                                v["word_sv"] = edit_sv
                                v["transliteration"] = edit_trans
                                v["devanagari"] = edit_dev
                                break
                        save_json("verbs.json", verbs_data)
                        st.success("Verbet uppdaterat!")
                        st.rerun()
                with col_e2:
                    if st.button("🗑️ Radera hela verbet", key="t2_delete_verb"):
                        verbs_data = [v for v in verbs_data if v.get("word_sv") != selected_verb.get("word_sv")]
                        save_json("verbs.json", verbs_data)
                        st.success("Verbet raderades!")
                        st.rerun()

    with right_col:
        render_special_chars_sidebar()

# --- FLIK 3: ORDFÖRRÅD ---
with tab3:
    main_col, right_col = st.columns([3, 1])
    with main_col:
        st.header("Ordförråd & Kategorier")
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("➕ Lägg till ord")
            cat_files = get_category_files()
            category_names = [f.replace(".json", "") for f in cat_files]
            selected_cat = st.selectbox("Kategori:", category_names, key="t3_cat")
            word_sv = st.text_input("Svenska:", key="t3_sv")
            translit = st.text_input("Romaji:", key="t3_trans")
            devanagari = st.text_input("Devanagari:", key="t3_dev")

            if st.button("Spara ord", key="t3_save"):
                if word_sv and (translit or devanagari):
                    filename = f"{selected_cat}.json"
                    current_data = load_json(filename, [])
                    # Om det är verb-kategorin ser vi till att skicka med en tom conjugations-struktur om den saknas
                    new_item = {"word_sv": word_sv, "transliteration": translit, "devanagari": devanagari}
                    if selected_cat == "verbs":
                        new_item["conjugations"] = {}
                    current_data.append(new_item)
                    save_json(filename, current_data)
                    st.success("Ord sparat!")
                else:
                    st.error("Fyll i svenska samt romaji eller devanagari.")

        with col_b:
            st.subheader("📁 Ny kategori")
            new_cat_name = st.text_input("Kategorinamn:", key="t3_new_cat")
            if st.button("Skapa", key="t3_create_cat"):
                if new_cat_name:
                    clean_name = new_cat_name.strip().lower().replace(" ", "_")
                    filename = f"{clean_name}.json"
                    if not os.path.exists(os.path.join(DATA_DIR, filename)):
                        save_json(filename, [])
                        st.success(f"Skapade '{clean_name}'!")
                        st.rerun()
                    else:
                        st.warning("Kategorin finns redan.")

        st.divider()
        st.subheader("📋 Hantera ord i kategori (Redigera / Radera)")
        view_cat = st.selectbox("Välj kategori att hantera:", category_names, key="t3_manage_cat")
        cat_items = load_json(f"{view_cat}.json", [])

        if not cat_items:
            st.info("Inga ord i denna kategori än.")
        else:
            item_choices = {f"🇸🇪 {item.get('word_sv')} | 🔤 {item.get('transliteration')}": idx for idx, item in enumerate(cat_items)}
            
            if "t3_last_manage_cat" not in st.session_state or st.session_state.t3_last_manage_cat != view_cat:
                st.session_state.t3_last_manage_cat = view_cat
                st.session_state.t3_item_select_idx = 0

            selected_item_label = st.selectbox("Välj ord att redigera/radera:", list(item_choices.keys()), key="t3_item_select")
            selected_idx = item_choices[selected_item_label]
            current_item = cat_items[selected_idx]

            ed_sv = st.text_input("Ändra svenska:", value=current_item.get("word_sv", ""), key=f"t3_ed_sv_{selected_idx}")
            ed_trans = st.text_input("Ändra romaji:", value=current_item.get("transliteration", ""), key=f"t3_ed_trans_{selected_idx}")
            ed_dev = st.text_input("Ändra devanagari:", value=current_item.get("devanagari", current_item.get("word_np", "")), key=f"t3_ed_dev_{selected_idx}")

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                if st.button("💾 Spara ändringar i ord", key="t3_save_word"):
                    current_item["word_sv"] = ed_sv
                    current_item["transliteration"] = ed_trans
                    current_item["devanagari"] = ed_dev
                    cat_items[selected_idx] = current_item
                    save_json(f"{view_cat}.json", cat_items)
                    st.success("Ordet uppdaterades!")
                    st.rerun()
            with col_m2:
                if st.button("🗑️ Radera ordet", key="t3_del_word"):
                    cat_items.pop(selected_idx)
                    save_json(f"{view_cat}.json", cat_items)
                    st.success("Ordet raderades!")
                    st.rerun()

    with right_col:
        render_special_chars_sidebar()

# --- FLIK 4: SKRIVBOK & FRU-RÄTTNING ---
with tab4:
    main_col, right_col = st.columns([3, 1])
    with main_col:
        st.header("Skrivbok & Fru-rättning")
        user_sentences_data = load_json("user_sentences.json", DEFAULT_USER_SENTENCES)

        if not user_sentences_data:
            st.info("Inga sparade meningar.")
        else:
            for idx, item in enumerate(user_sentences_data):
                with st.container():
                    st.markdown(f"**Mening {idx+1}:**")
                    st.markdown(f"**Svenska:** {item['sv']}")
                    st.markdown(f"**Nepalesiska:** {item['np']}")
                    status = item.get('status', 'Ej granskad')
                    st.caption(f"Status: {status}")

                    c1, c2 = st.columns(2)
                    with c1:
                        if status != "Granskad":
                            if st.button("✔️ Markera som Granskad", key=f"rev_{idx}"):
                                user_sentences_data[idx]['status'] = "Granskad"
                                save_json("user_sentences.json", user_sentences_data)
                                st.rerun()
                        else:
                            if st.button("↩️ Ändra till Ej granskad", key=f"unrev_{idx}"):
                                user_sentences_data[idx]['status'] = "Ej granskad"
                                save_json("user_sentences.json", user_sentences_data)
                                st.rerun()
                    with c2:
                        if st.button(f"🗑️ Radera", key=f"del_sent_{idx}"):
                            user_sentences_data.pop(idx)
                            save_json("user_sentences.json", user_sentences_data)
                            st.rerun()
                    st.write("---")
    with right_col:
        render_special_chars_sidebar()

# --- FLIK 5: GLOS-QUIZ ---
with tab5:
    main_col, right_col = st.columns([3, 1])
    with main_col:
        st.header("Glos-Quiz")
        cat_files = get_category_files()
        cat_names = [f.replace(".json", "") for f in cat_files]
        quiz_cat = st.selectbox("Kategori:", cat_names, key="t5_cat")
        active_vocab = load_json(f"{quiz_cat}.json", [])
        quiz_mode = st.radio("Läge:", ["Fritext", "Flerval (10 alternativ)"], horizontal=True, key="t5_mode")

        if "t5_item" not in st.session_state or st.session_state.get("t5_cat_last") != quiz_cat:
            st.session_state.t5_cat_last = quiz_cat
            if active_vocab:
                st.session_state.t5_item = random.choice(active_vocab)

        if not active_vocab:
            st.warning("Tom kategori.")
        else:
            current_q = st.session_state.get("t5_item", random.choice(active_vocab))
            st.markdown(f"### Vad betyder **'{current_q.get('word_sv')}'**?")

            if "Fritext" in quiz_mode:
                user_guess = st.text_input("Ditt svar:", key="t5_free")
                if st.button("Kontrollera", key="t5_check"):
                    if user_guess.strip().lower() in [current_q.get('devanagari', '').lower(), current_q.get('transliteration', '').lower()]:
                        st.success("🎉 Rätt!")
                    else:
                        st.error(f"❌ Rätt svar: 🔤 {current_q.get('transliteration')} | 🇳🇵 {current_q.get('devanagari')}")
                if st.button("Nästa ord", key="t5_next"):
                    st.session_state.t5_item = random.choice(active_vocab)
                    st.rerun()
            else:
                others = [i for i in active_vocab if i != current_q]
                options = random.sample(others, min(9, len(others))) + [current_q]
                random.shuffle(options)
                opt_labels = [f"🔤 {o.get('transliteration')} | 🇳🇵 {o.get('devanagari')}" for o in options]
                chosen = st.radio("Välj alternativ:", opt_labels, key="t5_radio")
                if st.button("Kontrollera flerval", key="t5_check_mc"):
                    correct_label = f"🔤 {current_q.get('transliteration')} | 🇳🇵 {current_q.get('devanagari')}"
                    if chosen == correct_label:
                        st.success("🎉 Rätt!")
                    else:
                        st.error(f"❌ Rätt svar: {correct_label}")
                if st.button("Nästa", key="t5_next_mc"):
                    st.session_state.t5_item = random.choice(active_vocab)
                    st.rerun()
    with right_col:
        render_special_chars_sidebar()

# --- FLIK 6: MENINGSQUIZ ---
with tab6:
    main_col, right_col = st.columns([3, 1])
    with main_col:
        st.header("💬 Meningsquiz (Granskade meningar)")
        
        raw_reviewed = [s for s in user_sentences_data if s.get("status") == "Granskad"]
        unique_reviewed = []
        seen = set()
        for s in raw_reviewed:
            identifier = (s.get("sv"), s.get("np"))
            if identifier not in seen:
                seen.add(identifier)
                unique_reviewed.append(s)

        direction = st.radio("Quiz-riktning:", ["Nepalesiska ➔ Svenska", "Svenska ➔ Nepalesiska"], horizontal=True, key="t6_dir")

        if not unique_reviewed:
            st.info("Inga granskade meningar finns i skrivboken än. Gå till Skrivboken och markera några meningar som granskade!")
        else:
            if "t6_item" not in st.session_state:
                st.session_state.t6_item = random.choice(unique_reviewed)

            current_sent = st.session_state.t6_item

            if "Nepalesiska" in direction:
                st.markdown(f"### Översätt till svenska:\n\n🇳🇵 **{current_sent['np']}**")
                if st.button("Visa rätt svar", key="t6_show"):
                    st.success(f"🇸🇪 **{current_sent['sv']}**")
            else:
                st.markdown(f"### Översätt till nepalesiska:\n\n🇸🇪 **{current_sent['sv']}**")
                if st.button("Visa rätt svar", key="t6_show"):
                    st.success(f"🇳🇵 **{current_sent['np']}**")

            if st.button("➡️ Nästa mening", key="t6_next"):
                st.session_state.t6_item = random.choice(unique_reviewed)
                st.rerun()
    with right_col:
        render_special_chars_sidebar()
