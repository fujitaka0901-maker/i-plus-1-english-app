import streamlit as st
import google.generativeai as genai
import json
import re

# --- 設定 ---
st.set_page_config(page_title="i+1 English Learning App", layout="centered")

# サイドバーでAPIキーを設定
st.sidebar.title("🛠 設定")
api_key_input = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

# キーの確定（前後の空白を削除）
api_key = api_key_input.strip() if api_key_input else None

if api_key:
    try:
        genai.configure(api_key=api_key)
        # モデルの存在確認を兼ねてインスタンス化
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.title("📚 i+1 英語学習プロトタイプ")
        st.info("クラシェンのインプット仮説に基づき、あなたのレベルに合わせた教材を生成します。")

        # 1. 学習者レベルの選択
        level = st.selectbox(
            "あなたの現在のCEFR-Jレベルを選択してください",
            ("Pre-A1", "A1.1", "A1.2", "A1.3", "A2.1", "A2.2", "B1.1", "B1.2")
        )

        topic = st.text_input("トピック（例：Aichi culture, Basketball, Food loss）", "Regional cooperation in Aichi")

        if st.button("教材を生成する"):
            prompt = f"""
            You are an expert English teacher. Create a learning material based on Krashen's i+1 theory.
            
            Current student level: CEFR-J {level}
            Target vocabulary: 5 words from one level higher than {level}
            Topic: {topic}
            
            Output strictly in the following JSON format:
            {{
                "reading_text": "A passage of about 200 words",
                "reading_quiz": {{"question": "A comprehension question", "options": ["A", "B", "C", "D"], "answer": "Correct option text"}},
                "target_words": [{{ "word": "word", "meaning": "Japanese meaning" }}],
                "word_quizzes": [{{ "question": "Fill-in-the-blank or synonym question", "options": ["A", "B", "C", "D"], "answer": "Correct option text" }}]
            }}
            """

            with st.spinner("AIが最適な教材を編集中..."):
                try:
                    response = model.generate_content(prompt)
                    
                    # AIの回答からJSONを抽出する処理
                    res_text = response.text
                    json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                        st.session_state.app_data = data
                    else:
                        st.error("AIの回答形式が正しくありませんでした。もう一度お試しください。")
                except Exception as e:
                    st.error(f"生成エラーが発生しました: {e}")

        # --- 教材の表示 ---
        if "app_data" in st.session_state:
            data = st.session_state.app_data

            st.subheader("📖 Reading Passage")
            st.write(data["reading_text"])

            st.divider()

            st.subheader("❓ Comprehension Check")
            q = data["reading_quiz"]
            ans = st.radio(q["question"], q["options"], key="read_q")
            if st.button("内容クイズの答え合わせ"):
                if ans == q["answer"]:
                    st.success("正解です！")
                else:
                    st.error(f"残念。正解は「{q['answer']}」でした。")

            st.divider()

            st.subheader("💡 Target Words (+1)")
            cols = st.columns(len(data["target_words"]))
            for i, item in enumerate(data["target_words"]):
                with cols[i]:
                    st.info(f"**{item['word']}**\n\n{item['meaning']}")

            st.divider()

            st.subheader("✍️ Vocabulary Quiz")
            correct_count = 0
            for i, wq in enumerate(data["word_quizzes"]):
                user_ans = st.selectbox(f"Q{i+1}: {wq['question']}", ["選択してください"] + wq["options"], key=f"word_q_{i}")
                if user_ans == wq["answer"]:
                    correct_count += 1
            
            if st.button("単語クイズの結果を見る"):
                st.write(f"### スコア: {correct_count} / 5")
                if correct_count == 5:
                    st.balloons()

    except Exception as e:
        st.error(f"初期設定エラー: {e}")

else:
    st.warning("👈 左側のサイドバーにGeminiのAPIキーを入力してください。")