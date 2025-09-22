import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from utils.parser import extract_text
from utils.matcher import compute_hard_match, get_verdict
from scorer import final_score
from database import SessionLocal, ResumeLog

st.set_page_config(page_title="Automated Resume Relevance Check", layout="wide")
st.title("📝 Automated Resume Relevance Check System")

# Sidebar navigation
menu = st.sidebar.radio("📂 Navigation", ["Resume Analysis", "Audit Log"])

# Initialize session state
if "jd_text" not in st.session_state:
    st.session_state["jd_text"] = None
if "results_df" not in st.session_state:
    st.session_state["results_df"] = None

# ========== PAGE 1: Resume Analysis ==========
if menu == "Resume Analysis":
    jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"])

    # If new JD uploaded
    if jd_file:
        jd_text = extract_text(jd_file)
        st.session_state["jd_text"] = jd_text
        st.markdown("**Job Description Preview:**")
        st.text_area("JD Text", jd_text, height=200)

    # If no new JD, but one exists in session
    elif st.session_state["jd_text"]:
        st.markdown("**Job Description Preview (Cached):**")
        st.text_area("JD Text", st.session_state["jd_text"], height=200)

    resume_files = st.file_uploader(
        "Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True
    )

    # Process resumes
    if resume_files and st.session_state["jd_text"]:
        data = []
        db = SessionLocal()

        for r_file in resume_files:
            resume_text = extract_text(r_file)

            # Hard match
            hard_score, missing_keywords = compute_hard_match(st.session_state["jd_text"], resume_text)
            verdict = get_verdict(hard_score)


            # TEMPORARY: Skip semantic match for quick deployment
            semantic_score = 0.0

            # Semantic match
            semantic_score = compute_semantic_score(st.session_state["jd_text"], resume_text)
                (Add session time tracking for Resume Analysis page)

            # Final combined score
            combined_score = final_score(hard_score, semantic_score)

            # Highlight missing keywords
            highlighted_resume = resume_text
            for kw in missing_keywords:
                highlighted_resume = highlighted_resume.replace(
                    kw, f"<span style='background-color:#FF6347;color:white;padding:2px 4px;border-radius:3px'>{kw}</span>"
                )

            # Save to database
            log = ResumeLog(
                resume_name=r_file.name,
                hard_score=hard_score,
                semantic_score=semantic_score,
                final_score=combined_score,
                verdict=verdict,
                missing_keywords=", ".join(missing_keywords)
            )
            db.add(log)
            db.commit()

            data.append({
                "Resume": r_file.name,
                "Hard Score": hard_score,
                "Semantic Score": semantic_score,
                "Final Score": combined_score,
                "Verdict": verdict,
                "Missing Keywords": ", ".join(missing_keywords),
                "Highlighted Resume": highlighted_resume
            })

        db.close()

        st.session_state["results_df"] = pd.DataFrame(data)

    # If results already exist in session, show them
    if st.session_state["results_df"] is not None:
        df = st.session_state["results_df"]

        # Summary Table
        st.subheader("📊 Resume Analysis Results")
        st.dataframe(df[["Resume", "Hard Score", "Semantic Score", "Final Score", "Verdict", "Missing Keywords"]])

        # CSV download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="resume_relevance_results.csv",
            mime="text/csv"
        )

        # Highlights
        st.subheader("📄 Resume Highlights & Missing Keywords")
        top_n = st.slider("Show top N resumes", 1, len(df), min(5, len(df)))

        for i in range(top_n):
            with st.expander(f"Resume: {df.iloc[i]['Resume']}"):
                highlighted_html = f"""
                <div style="border:1px solid #ccc; padding:10px; height:200px; overflow-y:auto;">
                    {df.iloc[i]['Highlighted Resume']}
                </div>
                """
                components.html(highlighted_html, height=220)

                missing_keywords = df.iloc[i]["Missing Keywords"].split(", ")
                top_missing = missing_keywords[:5]
                badges_html = " ".join(
                    [f"<span style='background-color:#FF6347;color:white;padding:3px 8px;border-radius:5px;margin:2px;'>{kw}</span>" for kw in top_missing]
                )
                st.markdown(f"**Top Missing Keywords / Suggestions:** {badges_html}", unsafe_allow_html=True)

# ========== PAGE 2: Audit Log ==========
elif menu == "Audit Log":
    st.subheader("📜 Resume Audit Log (Stored in Database)")

    db = SessionLocal()
    logs = db.query(ResumeLog).order_by(ResumeLog.created_at.desc()).all()
    db.close()

    if logs:
        log_data = [
            {
                "ID": log.id,
                "Resume": log.resume_name,
                "Hard Score": log.hard_score,
                "Semantic Score": log.semantic_score,
                "Final Score": log.final_score,
                "Verdict": log.verdict,
                "Missing Keywords / Suggestions": log.missing_keywords,
                "Created At": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for log in logs
        ]

        log_df = pd.DataFrame(log_data)
        st.dataframe(log_df)

        csv = log_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Full Audit Log",
            data=csv,
            file_name="resume_audit_log.csv",
            mime="text/csv"
        )
    else:
        st.info("No logs found in the database yet.")
