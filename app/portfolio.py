import pandas as pd
import faiss
import numpy as np
import uuid
from sklearn.feature_extraction.text import TfidfVectorizer

class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.index = None
        self.vectorizer = TfidfVectorizer()
        self.embeddings = []

    def load_portfolio(self):
        # Vectorize the techstack and store it in the FAISS index
        if self.index is None:
            techstack = self.data["Techstack"].tolist()
            self.embeddings = self.vectorizer.fit_transform(techstack).toarray()

            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

            self.index.add(np.array(self.embeddings, dtype=np.float32))

    def query_links(self, skills):
        query_vec = self.vectorizer.transform([skills]).toarray().astype(np.float32)

        distances, indices = self.index.search(query_vec, 2) 

        links = []
        for idx in indices[0]:
            if idx != -1:
                links.append(self.data.iloc[idx]["Links"])

        return links
