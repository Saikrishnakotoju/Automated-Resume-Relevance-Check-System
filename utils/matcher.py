def compute_hard_match(jd_text, resume_text):
    jd_words = jd_text.lower().split()
    resume_words = resume_text.lower().split()
    matched = [w for w in jd_words if w in resume_words]
    missing = [w for w in jd_words if w not in resume_words]
    score = len(matched) / len(jd_words) * 100
    return score, missing
