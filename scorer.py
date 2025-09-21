# scorer.py

def final_score(hard_score, semantic_score, hard_weight=0.6, semantic_weight=0.4):
    """
    Combine hard match and semantic match into final score
    """
    return round(hard_score * hard_weight + semantic_score * semantic_weight, 2)
