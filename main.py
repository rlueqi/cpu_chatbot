# 참고: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps

from openai import OpenAI
import streamlit as st
import os

prompt = """
당신은 모든 언어에 통달한 언어 천재입니다. 대화를 할 때 특정 언어에
대한 주제가 나오면 그 언어에 대해 자세히 알려주고 잘못된 표현을
고쳐주려고 합니다.

표현 수정:
잘못된 표현을 쓰거나 더 평범하게 쓸 수 있는 말이 있는 경우
1. "그 표현보다 더 좋은 표현이 있어"라고 반응
2. 곧이어 "나라면 이런 표현을 쓸거야" 대답
3. 적절한 표현에 대해 설명 및 문화적 배경, 역사적 배경 등 설명
4. 표현이 이해가 되었는지 질문
5. 다음에는 어떤 것이 궁금한지 묻기

질문 스타일:
- "XX라는 표현은 이러한 XX적 배경이 있어서야"
- "이것과 비슷한 표현은 XX가 있어!"
- "콜로케이션과 구동사를 쓰는 이유는 XX야"
- "또 궁금한 내용이 있어"

규칙:
- 현재 쓰는 표현만 사용하기
- 정보가 부족해서 못 알려주는 언어는 "자료 부족"으로 표시
- 질문을 할 때 사용하는 언어로 대답하기
"""

# Cerebras API를 사용하여 OpenAI API 클라이언트 초기화
client = OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# Cerebras 모델 사용
# https://inference-docs.cerebras.ai/models/overview
# "qwen-3-32b"
# "qwen-3-235b-a22b-instruct-2507",
# "qwen-3-coder-480b"
# "llama-4-scout-17b-16e-instruct"
# "qwen-3-235b-a22b-thinking-2507"
# "llama-3.3-70b"
# "llama3.1-8b"
# "gpt-oss-120b"
llm_model = "gpt-oss-120b"  
if "llm_model" not in st.session_state:
    st.session_state["llm_model"] = llm_model

st.title("언어 습득용 특화 AI")

# 시스템 메시지 설정
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": prompt,
        }
    ]

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("무엇이든 물어보세요."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 스트리밍 응답 받기
        stream = client.chat.completions.create(
            model=st.session_state["llm_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            temperature=0.7,
            max_completion_tokens=1000,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    import subprocess
    import sys
    
    # 환경 변수로 재실행 방지
    if not os.environ.get("STREAMLIT_RUNNING"):
        os.environ["STREAMLIT_RUNNING"] = "1"
        subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])

# python -m streamlit run main.py
# streamlit run main.py