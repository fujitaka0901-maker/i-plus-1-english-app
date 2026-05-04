import streamlit as st
import google.generativeai as genai
import json
import re

# --- ページ基本設定 ---
st.set_page_config(page_title="i+1 English Learning App", layout="centered")

# --- サイドバー設定 ---
st.sidebar.title("🛠 設定")
st.sidebar.info("Google AI Studioで取得した最新のAPIキーを使用してください。")
api_key_input = st.sidebar.text_input("Gemini API Keyを入力", type="password")

# APIキーの確定（空白削除）
api_key = api_key_input.strip() if api_key_input else None

if api_key:
    try:
        # APIの初期設定
        genai.configure(api_key=api_key)
        
        # モデルの設定（404エラー対策として最新の1.5-flashを指定）
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        
        st.title("📚 i+1 英語学習プロトタイプ")
        st.write("愛知県の教育現場や、探究学習（Aichi Inquiry）に活用できる教材生成アプリです。")

        # 1. 学習者レベルの選択
        level = st.selectbox(
            "現在のCEFR-Jレベルを選択してください",
            ("Pre-A1", "A1.1", "A1.2", "A1.3", "A2.1", "A2.2", "B1.1", "B1.2")
        )

        # 2. トピックの入力
        topic = st.text_input(
            "興味のあるトピック", 
            value="Traditional crafts in Aichi",
            help="例：Aichi agriculture, Basketball, Food loss, International cooperation"
        )

        # 3. 生成ボタン
        if st.button("教材を生成する"):
            # プロンプト（AIへの指示）
            prompt = f"""
            You are an expert English teacher. Create learning material based on Krashen's i+1 theory.
            Current level: CEFR-J {level}
            Topic: {topic}
            
            Instruction:
            1. Passage: Approx 150-200 words.
            2. Target Words: Select 5 words that are slightly (+1) above the current level.
            3. Quizzes: 1 reading comprehension question and 5 vocabulary questions.

            Output strictly in the following JSON format:
            {{
                "reading_text": "...",
                "reading_quiz": {{"question": "...", "options": ["A", "B", "C", "D"], "answer": "..."}},
                "target_words": [{{ "word": "...", "meaning": "..." }}],
                "word_quizzes": [{{ "question": "...", "options": ["A", "B", "C", "D"], "answer": "..." }}]
            }}
            """

            with st.spinner("AIが教材を作成しています..."):
                try:
                    response = model.generate_content(prompt)
                    
                    # AIの回答からJSON部分を正規表現で抽出
                    res_text = response.text
                    json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
                    
                    if json_match:
                        data = json.loads(json_match.group())
                        st.session_state.app_data = data
                    else:
                        st.error("データの抽出に失敗しました。もう一度「生成」を押してください。")
                except Exception as e:
                    st.error(f"生成エラーが発生しました。APIキーまたはモデル名を確認してください。\nエラー詳細: {e}")

        # --- 生成された教材の表示エリア ---
        if "app_data" in st.session_state:
            data = st.session_state.app_data

            st.divider()
            st.subheader("📖 Reading Passage")
            st.write(data["reading_text"])

            st.divider()
            st.subheader("❓ 内容理解クイズ")
            q = data["reading_quiz"]
            ans = st.radio(q["question"], q["options"], key="read_q")
            if st.button("内容クイズの正解を確認"):
                if ans == q["answer"]:
                    st.success("正解です！Excellent!")
                else:
                    st.error(f"残念！正解は「{q['answer']}」です。")

            st.divider()
            st.subheader("💡 ターゲット単語 (+1)")
            # 単語を横並びで表示
            cols = st.columns(5)
            for i, item in enumerate(data["target_words"]):
                with cols[i]:
                    st.info(f"**{item['word']}**\n\n{item['meaning']}")

            st.divider()
            st.subheader("✍️ 語彙力確認テスト")
            correct_count = 0
            for i, wq in enumerate(data["word_quizzes"]):
                user_ans = st.selectbox(
                    f"Q{i+1}: {wq['question']}", 
                    ["-- 選択してください --"] + wq["options"], 
                    key=f"word_q_{i}"
                )
                if user_ans == wq["answer"]:
                    correct_count += 1
            
            if st.button("単語テストの結果を見る"):
                st.write(f"### あなたのスコア: {correct_count} / 5")
                if correct_count == 5:
                    st.balloons()
                    st.success("満点です！素晴らしい語彙力ですね。")

    except Exception as e:
        st.error(f"初期設定エラー: {e}")

else:
    st.warning("👈 左側のサイドバーにGeminiのAPIキーを入力してください。")
