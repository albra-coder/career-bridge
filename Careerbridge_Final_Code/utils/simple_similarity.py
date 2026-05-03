# utils/simple_similarity.py - Fallback implementation
import re
from collections import Counter
import math

class SimpleTextSimilarity:
    @staticmethod
    def calculate_similarity(text1, text2):
        """
        Simple text similarity using word overlap and TF-IDF like scoring
        """
        if not text1 or not text2:
            return 0
            
        # Clean and tokenize
        words1 = SimpleTextSimilarity.clean_and_tokenize(text1)
        words2 = SimpleTextSimilarity.clean_and_tokenize(text2)
        
        if not words1 or not words2:
            return 0
            
        # Calculate word frequencies
        freq1 = Counter(words1)
        freq2 = Counter(words2)
        
        # Get all unique words
        all_words = set(words1 + words2)
        
        # Calculate simple cosine similarity
        dot_product = 0
        magnitude1 = 0
        magnitude2 = 0
        
        for word in all_words:
            count1 = freq1.get(word, 0)
            count2 = freq2.get(word, 0)
            
            dot_product += count1 * count2
            magnitude1 += count1 ** 2
            magnitude2 += count2 ** 2
            
        magnitude1 = math.sqrt(magnitude1)
        magnitude2 = math.sqrt(magnitude2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
            
        similarity = dot_product / (magnitude1 * magnitude2)
        return max(0, min(100, similarity * 100))
    
    @staticmethod
    def clean_and_tokenize(text):
        """Clean text and tokenize into words"""
        if not text:
            return []
            
        # Convert to lowercase and remove punctuation
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        # Remove extra whitespace and split
        words = [word for word in text_clean.split() if len(word) > 2]  # Filter very short words
        return words

    @staticmethod
    def calculate_with_keyword_matching(resume_text, job_description):
        """
        Combined approach: keyword matching + simple similarity
        """
        if not resume_text or not job_description:
            return 0
            
        # Simple similarity score
        simple_score = SimpleTextSimilarity.calculate_similarity(resume_text, job_description)
        
        # Keyword bonus - check for important job keywords in resume
        job_words = SimpleTextSimilarity.clean_and_tokenize(job_description)
        resume_words = SimpleTextSimilarity.clean_and_tokenize(resume_text)
        
        # Get top frequent words from job description (potential keywords)
        job_word_freq = Counter(job_words)
        top_job_words = [word for word, count in job_word_freq.most_common(10)]
        
        # Calculate keyword coverage
        keyword_matches = sum(1 for word in top_job_words if word in resume_words)
        keyword_coverage = (keyword_matches / len(top_job_words)) * 100 if top_job_words else 0
        
        # Combine scores (70% simple similarity, 30% keyword coverage)
        final_score = (simple_score * 0.7) + (keyword_coverage * 0.3)
        
        return round(final_score, 2)