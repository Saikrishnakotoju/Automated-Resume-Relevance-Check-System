# utils/model_loader.py
import streamlit as st
from sentence_transformers import SentenceTransformer

@st.cache_resource
def get_sentence_transformer_model():
    # Lazy-load the model once
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model
