import json
import os
import numpy as np
import faiss
from django.conf import settings


def _ensure_dir():
    os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)


def get_index_path(subject_name):
    return os.path.join(settings.FAISS_INDEX_DIR, f"{subject_name}.index")


def get_metadata_path(subject_name):
    return os.path.join(settings.FAISS_INDEX_DIR, f"{subject_name}_meta.json")


def add_to_index(subject_name, embeddings, metadata_list):
    _ensure_dir()
    index_path = get_index_path(subject_name)
    meta_path = get_metadata_path(subject_name)

    vectors = np.array(embeddings, dtype='float32')
    faiss.normalize_L2(vectors)

    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        with open(meta_path, 'r') as f:
            existing_meta = json.load(f)
    else:
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        existing_meta = []

    index.add(vectors)
    existing_meta.extend(metadata_list)

    faiss.write_index(index, index_path)
    with open(meta_path, 'w') as f:
        json.dump(existing_meta, f)


def search_index(subject_name, query_embedding, top_k=3):
    index_path = get_index_path(subject_name)
    meta_path = get_metadata_path(subject_name)

    if not os.path.exists(index_path):
        return [], []

    index = faiss.read_index(index_path)
    with open(meta_path, 'r') as f:
        metadata = json.load(f)

    query_vec = np.array([query_embedding], dtype='float32')
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, min(top_k, index.ntotal))

    results_meta = []
    results_scores = []
    for i, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        results_scores.append(float(scores[0][i]))
        results_meta.append(metadata[idx])

    return results_scores, results_meta


def get_random_chunks(subject_name, k=7):
    meta_path = get_metadata_path(subject_name)
    if not os.path.exists(meta_path):
        return []
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    if len(metadata) <= k:
        return metadata
    indices = np.random.choice(len(metadata), size=k, replace=False)
    return [metadata[i] for i in indices]
