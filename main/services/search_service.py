import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from main.models import CyberCrime

class CyberCrimeSearchService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self._corpus_ids = []
        self._substring_cache = []
        self._tfidf_matrix = None
        self._is_fitted = False
    
    def _build_corpus(self):
        """Rebuilds the TF-IDF matrix from the database"""
        crimes = CyberCrime.objects.all()
        if not crimes.exists():
            self._is_fitted = False
            return
            
        corpus = []
        self._corpus_ids = []
        self._substring_cache = []
        
        for crime in crimes:
            # Combine fields with different weights using repetition
            text_parts = [crime.type] * 3 
            text_parts.append(crime.description)
            text_parts.append(crime.get_category_display())
            
            if crime.keywords:
                text_parts.extend(crime.keywords * 2)
            
            if crime.tags:
                text_parts.extend(crime.tags)
                
            if crime.related_domains:
                text_parts.extend(crime.related_domains)
                
            combined_text = " ".join(text_parts)
            corpus.append(combined_text)
            self._corpus_ids.append(crime.id)
            
            # Cache text for direct substring matching (autocomplete)
            keywords_text = " ".join(crime.keywords) if crime.keywords else ""
            self._substring_cache.append(f"{crime.type} {crime.get_category_display()} {keywords_text}".lower())
            
        self._tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self._is_fitted = True

    def ensure_fitted(self):
        if not self._is_fitted:
            self._build_corpus()

    def search(self, query, top_k=10):
        """
        Returns ranked cybercrime IDs and their relevance scores based on the query.
        """
        self.ensure_fitted()
        if not self._is_fitted or not query.strip():
            return []
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self._tfidf_matrix).flatten()
        
        # Boost score for partial substring matches (enables predictive autocomplete)
        query_lower = query.lower()
        for idx, text in enumerate(self._substring_cache):
            if query_lower in text:
                similarities[idx] += 0.5
        
        # Get top indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score > 0.01: # Lowered threshold to catch weaker TF-IDF connections
                results.append({
                    'id': self._corpus_ids[idx],
                    'score': float(score)
                })
                
        return results

    def get_related_crimes(self, crime_id, top_k=4):
        """
        Finds similar crimes to a given crime ID using the TF-IDF matrix.
        """
        self.ensure_fitted()
        if not self._is_fitted:
            return []
            
        try:
            idx = self._corpus_ids.index(crime_id)
        except ValueError:
            return []
            
        # Get the vector for this specific crime
        crime_vec = self._tfidf_matrix[idx]
        similarities = cosine_similarity(crime_vec, self._tfidf_matrix).flatten()
        
        # Sort and exclude the crime itself (which will have score ~1.0)
        top_indices = similarities.argsort()[::-1]
        
        results = []
        for i in top_indices:
            if i != idx and similarities[i] > 0.1: # Skip itself and require some similarity
                results.append({
                    'id': self._corpus_ids[i],
                    'score': float(similarities[i])
                })
                if len(results) >= top_k:
                    break
                    
        return results

# Singleton instance to avoid rebuilding TF-IDF matrix on every request
search_engine = CyberCrimeSearchService()