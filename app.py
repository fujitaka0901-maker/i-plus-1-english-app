import streamlit as st
import google.generativeai as genai
import json

# --- 設定 ---
st.set_page_config(page_title="i+1 English Learning App", layout="centered")

# サイドバーでAPIキーを設定（公開時はStreamlitのSecretsを使用することを推奨）
api_key = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    st.title("📚 i+1 英語学習プロトタイプ")
    st.write("あなたの現在のレベルより「少しだけ上」の英文をAIが生成します。")

    # 1. 学習者レベルの選択
    level = st.selectbox(
        "あなたの現在のCEFR-Jレベルを選択してください",
        ("Pre-A1", "A1.1", "A1.2", "A1.3", "A2.1", "A2.2", "B1.1", "B1.2")
    )

    topic = st.text_input("興味のあるトピック（例：愛知県の伝統工芸、バスケットボール、フードロス）", "日本の文化")

    if st.button("教材を生成する"):
        # AIへのプロンプト（指示書）
        prompt = f"""
        あなたは英語教育の専門家です。クラシェンのi+1理論に基づき教材を作成してください。
        
        【条件】
        1. 基本レベル: CEFR-J {level}
        2. ターゲット: 上記より一段階上の語彙を5つ含める
        3. 構成: 
           - 約200語の英文（トピック: {topic}）
           - 内容理解を確認する4択問題 1問
           - ターゲット単語5つのリスト（意味付き）
           - その単語を使った4択クイズ 5問
        
        【出力形式】
        必ず以下のJSON形式のみで出力してください。
        {{
            "reading_text": "英文の内容",
            "reading_quiz": {{"question": "問題文", "options": ["A", "B", "C", "D"], "answer": "正解"}},
            "target_words": [{{ "word": "単語", "meaning": "意味" }}],
            "word_quizzes": [{{ "question": "問題", "options": ["A", "B", "C", "D"], "answer": "正解" }}]
        }}
        """

        with st.spinner("AIが教材を作成中..."):
            response = model.generate_content(prompt)
            # JSON部分を抽出
            try:
                data = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                st.session_state.app_data = data
            except:
                st.error("データの生成に失敗しました。もう一度お試しください。")

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
                st.error(f"残念。正解は {q['answer']} です。")

        st.divider()

        st.subheader("💡 Target Words (+1)")
        for item in data["target_words"]:
            st.write(f"**{item['word']}**: {item['meaning']}")

        st.divider()

        st.subheader("✍️ Vocabulary Quiz")
        correct_count = 0
        for i, wq in enumerate(data["word_quizzes"]):
            user_ans = st.selectbox(f"Q{i+1}: {wq['question']}", ["選んでください"] + wq["options"], key=f"word_q_{i}")
            if user_ans == wq["answer"]:
                correct_count += 1
        
        if st.button("単語クイズの結果を見る"):
            st.write(f"スコア: {correct_count} / 5")

else:
    st.warning("左側のサイドバーにGeminiのAPIキーを入力してください。")