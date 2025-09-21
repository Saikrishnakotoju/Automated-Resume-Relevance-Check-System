# semantic_matcher_multiJD.py

from utils.parser import extract_text
from utils.matcher import compute_hard_match, get_verdict
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- Helper functions ---
def get_all_files(folder_path):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
            if os.path.isfile(os.path.join(folder_path, f))]

# --- Load SentenceTransformer model ---
print("Loading SentenceTransformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully.\n")

# --- Paths ---
jd_folder = os.path.join("data", "JD")
resume_folder = os.path.join("data", "Resumes")
output_csv = os.path.join("results", "resume_semantic_multiJD.csv")
os.makedirs("results", exist_ok=True)

# --- Load files ---
jd_files = get_all_files(jd_folder)
resume_files = get_all_files(resume_folder)

if len(jd_files) == 0:
    print("❌ No JD files found in data/JD.")
    exit()
if len(resume_files) == 0:
    print("❌ No resumes found in data/Resumes.")
    exit()

print(f"Found {len(jd_files)} JD(s) and {len(resume_files)} resume(s).\n")

results = []

# --- Loop through all JD files ---
for jd_idx, jd_file in enumerate(jd_files, start=1):
    print(f"[JD {jd_idx}/{len(jd_files)}] Processing JD: {jd_file}")
    jd_text = extract_text(jd_file)
    jd_embedding = model.encode(jd_text)

    # Loop through all resumes for this JD
    for resume_idx, resume_file in enumerate(resume_files, start=1):
        print(f"  [{resume_idx}/{len(resume_files)}] Matching resume: {resume_file}")
        resume_text = extract_text(resume_file)
        
        # Hard match
        hard_score, missing = compute_hard_match(jd_text, resume_text)
        
        # Semantic similarity
        resume_embedding = model.encode(resume_text)
        semantic_score = float(cosine_similarity([jd_embedding], [resume_embedding])[0][0]) * 100
        
        # Final score
        final_score = round(0.6 * hard_score + 0.4 * semantic_score, 2)
        verdict = get_verdict(final_score)
        
        results.append({
            "JD_file": os.path.basename(jd_file),
            "resume_file": os.path.basename(resume_file),
            "hard_match_score": hard_score,
            "semantic_score": round(semantic_score, 2),
            "final_score": final_score,
            "verdict": verdict,
            "missing_keywords": ", ".join(missing[:20])  # first 20 for brevity
        })

# --- Save CSV ---
df = pd.DataFrame(results)
df.to_csv(output_csv, index=False)

print("\n✅ Multi-JD resume evaluation complete!")
print(f"Results saved to: {output_csv}")

# --- Optional: print top 3 for each JD ---
for jd in df['JD_file'].unique():
    print(f"\n📊 Top 3 resumes for JD: {jd}")
    top3 = df[df['JD_file'] == jd].sort_values(by='final_score', ascending=False).head(3)
    print(top3[['resume_file', 'final_score', 'verdict']])
