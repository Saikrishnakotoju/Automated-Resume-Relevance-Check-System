from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_semantic_score(jd_text, resume_text):
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    cosine_sim = util.cos_sim(jd_emb, resume_emb).item()
    return round(cosine_sim * 100, 2)
