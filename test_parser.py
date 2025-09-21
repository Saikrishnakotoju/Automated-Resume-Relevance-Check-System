from utils.parser import extract_text
from utils.matcher import compute_hard_match, get_verdict
import os

# Automatically pick first JD and Resume
def get_first_file(folder_path):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        raise FileNotFoundError(f"No files found in {folder_path}")
    return os.path.join(folder_path, files[0])

jd_folder = os.path.join("data", "JD")
resume_folder = os.path.join("data", "Resumes")

jd_file = get_first_file(jd_folder)
resume_file = get_first_file(resume_folder)

jd_text = extract_text(jd_file)
resume_text = extract_text(resume_file)

# --- MATCHING ---
score, missing = compute_hard_match(jd_text, resume_text)
verdict = get_verdict(score)

print("\n----- MATCHING RESULTS -----")
print(f"Relevance Score: {score}")
print(f"Missing Keywords: {missing[:20]} ...")  # show first 20 missing keywords
print(f"Verdict: {verdict}")
