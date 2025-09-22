# utils/matcher.py

import re

def compute_hard_match(jd_text, resume_text):
    jd_keywords = re.findall(r'\b\w+\b', jd_text.lower())
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))

    matched = [kw for kw in jd_keywords if kw in resume_words]
    missing = [kw for kw in jd_keywords if kw not in resume_words]

    score = len(matched) / len(jd_keywords) * 100
    return round(score, 2), missing

def get_verdict(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"
