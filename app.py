import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# ── Load API key ────────────────────────────────────────────────────
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Page config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🎯",
    layout="centered"
)

# ── Session state setup ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "finished" not in st.session_state:
    st.session_state.finished = False

# ── Title ────────────────────────────────────────────────────────────
st.title("🎯 AI Interview Simulator")
st.caption("Practice real interviews with AI — get scored and improve instantly")

# ── Role selector ────────────────────────────────────────────────────
if not st.session_state.interview_started:
    st.subheader("Select your target role")
    role = st.selectbox(
        "Choose a role",
        ["Product Manager", "Data Analyst", "Business Analyst",
         "Software Engineer", "Marketing Manager", "AI/ML Engineer"]
    )
    if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
        st.session_state.role = role
        st.session_state.interview_started = True
        st.session_state.messages = [
            {
                "role": "system",
                "content": f"""You are a senior interviewer at a top tech company 
                interviewing a candidate for a {role} position. 
                Ask exactly 5 interview questions one at a time.
                After each answer evaluate it briefly (2-3 lines) then ask the next question.
                After the 5th answer give a final scorecard with:
                - Overall score out of 10
                - Score for each answer out of 10
                - Top 3 strengths
                - Top 3 areas to improve
                - One final piece of advice
                Be professional, specific and constructive."""
            }
        ]
        # Ask first question
        first_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages + [
                {"role": "user", "content": "Start the interview with your first question."}
            ],
            temperature=0.7,
            max_tokens=500
        )
        first_question = first_response.choices[0].message.content
        st.session_state.messages.append(
            {"role": "assistant", "content": first_question}
        )
        st.rerun()

# ── Interview in progress ─────────────────────────────────────────────
if st.session_state.interview_started:
    st.subheader(f"Interview for: {st.session_state.role}")

    # Progress bar
    progress = min(st.session_state.question_count / 5, 1.0)
    st.progress(progress)
    st.caption(f"Question {min(st.session_state.question_count + 1, 5)} of 5")

    st.divider()

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
        elif msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])

    # Input box
    if not st.session_state.finished:
        user_answer = st.chat_input("Type your answer here...")

        if user_answer:
            # Add user answer
            st.session_state.messages.append(
                {"role": "user", "content": user_answer}
            )
            st.session_state.question_count += 1

            # Check if interview is done
            if st.session_state.question_count >= 5:
                st.session_state.finished = True
                prompt = "Give me the final scorecard now."
            else:
                prompt = "Evaluate my answer briefly then ask the next question."

            # Get AI response
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages + [
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            ai_response = response.choices[0].message.content
            st.session_state.messages.append(
                {"role": "assistant", "content": ai_response}
            )
            st.rerun()

    # Finished state
    if st.session_state.finished:
        st.divider()
        st.success("Interview complete! See your scorecard above.")

        # Download transcript
        transcript = "\n\n".join([
            f"{m['role'].upper()}: {m['content']}"
            for m in st.session_state.messages
            if m["role"] != "system"
        ])
        st.download_button(
            label="⬇️ Download Interview Transcript",
            data=transcript,
            file_name="interview_transcript.txt",
            mime="text/plain"
        )

        if st.button("🔄 Start New Interview", use_container_width=True):
            for key in ["messages", "question_count", "interview_started",
                        "role", "finished"]:
                del st.session_state[key]
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────
st.divider()
st.caption("Built with Python · Groq LLaMA3 · Streamlit")
