# utils/algorithms.py - Enhanced with better debugging
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class MatchingAlgorithms:
    @staticmethod
    def parse_skills(skills_string):
        """Parse skills from string to list, handling both formats"""
        if not skills_string:
            return []
        
        try:
            # If it's a JSON-like string, try to parse it
            if skills_string.startswith('[') and skills_string.endswith(']'):
                import json
                return json.loads(skills_string)
            else:
                # Parse as comma-separated string
                skills = [skill.strip() for skill in skills_string.split(',') if skill.strip()]
                return skills
        except:
            # Fallback to comma-separated parsing
            return [skill.strip() for skill in skills_string.split(',') if skill.strip()]

    @staticmethod
    def calculate_skill_match(candidate_skills, job_skills):
        """
        Skill Matching Algorithm (Rule-Based + Weighted Similarity)
        M = |Sg ∩ Sj| / |Sj| × 100
        """
        if not job_skills:
            return 0
        
        # Parse skills to lists
        candidate_skills_list = MatchingAlgorithms.parse_skills(candidate_skills)
        job_skills_list = MatchingAlgorithms.parse_skills(job_skills)
        
        if not job_skills_list:
            return 0
            
        # Convert to lowercase for case-insensitive matching
        candidate_skills_lower = [skill.lower().strip() for skill in candidate_skills_list]
        job_skills_lower = [skill.lower().strip() for skill in job_skills_list]
        
        # Calculate intersection
        intersection = set(candidate_skills_lower) & set(job_skills_lower)
        match_score = (len(intersection) / len(job_skills_lower)) * 100
        return round(match_score)

    @staticmethod
    def calculate_text_similarity(resume_text, job_description):
        """
        TF-IDF and Cosine Similarity for Resume-Job Description Matching
        """
        print(f"=== TEXT SIMILARITY CALCULATION ===")
        print(f"Resume text length: {len(resume_text) if resume_text else 0}")
        print(f"Job description length: {len(job_description) if job_description else 0}")
        
        if not resume_text or not job_description:
            print("Missing resume or job description")
            return 0
        
        # Clean the texts - more aggressive cleaning
        resume_clean = re.sub(r'[^\w\s]', ' ', resume_text.lower())
        job_clean = re.sub(r'[^\w\s]', ' ', job_description.lower())
        
        # Remove extra whitespace
        resume_clean = ' '.join(resume_clean.split())
        job_clean = ' '.join(job_clean.split())
        
        print(f"Cleaned resume words: {len(resume_clean.split())}")
        print(f"Cleaned job words: {len(job_clean.split())}")
        
        # Create TF-IDF vectorizer with better parameters
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=500,  # Reduced for better performance
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.85,
                strip_accents='unicode',
                analyzer='word'
            )
            
            # Combine texts for fitting
            combined_texts = [resume_clean, job_clean]
            
            print("Fitting TF-IDF vectorizer...")
            tfidf_matrix = vectorizer.fit_transform(combined_texts)
            
            print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
            print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            similarity_score = similarity[0][0] * 100
            
            print(f"Raw similarity: {similarity[0][0]}")
            print(f"Similarity score: {similarity_score}%")
            
            # Ensure score is between 0-100
            final_score = max(0, min(100, round(similarity_score, 2)))
            print(f"Final text similarity score: {final_score}%")
            
            return final_score
            
        except Exception as e:
            print(f"TF-IDF Error: {e}")
            # Enhanced fallback: word overlap with weighting
            try:
                resume_words = set(resume_clean.split())
                job_words = set(job_clean.split())
                
                common_words = resume_words & job_words
                total_job_words = len(job_words)
                
                if total_job_words > 0:
                    overlap_score = (len(common_words) / total_job_words) * 100
                    # Apply some scaling to make it more realistic
                    scaled_score = min(100, overlap_score * 1.5)
                    print(f"Fallback overlap score: {scaled_score}%")
                    return round(scaled_score, 2)
                else:
                    return 0
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")
                return 0

    @staticmethod
    def calculate_overall_match(candidate_skills, resume_text, job_skills, job_description):
        """
        Combined matching algorithm using both skill matching and text similarity
        """
        print(f"\n=== OVERALL MATCH CALCULATION ===")
        print(f"Candidate skills: {candidate_skills}")
        print(f"Job skills: {job_skills}")
        
        skill_match = MatchingAlgorithms.calculate_skill_match(candidate_skills, job_skills)
        text_similarity = MatchingAlgorithms.calculate_text_similarity(resume_text, job_description)
        
        print(f"Skill match: {skill_match}%")
        print(f"Text similarity: {text_similarity}%")
        
        # Weighted average (60% skills, 40% text similarity)
        overall_score = (skill_match * 0.6) + (text_similarity * 0.4)
        
        final_score = max(0, round(overall_score, 2))
        print(f"Overall score: {final_score}%")
        print("=" * 50)
        
        return {
            'overall_score': final_score,
            'skill_match': skill_match,
            'text_similarity': text_similarity
        }

    @staticmethod
    def find_candidate_matches(job, graduates, threshold=60):
        """
        Find matching candidates for a job
        """
        matches = []
        
        for graduate in graduates:
            # Skip graduates without basic profile info
            if not graduate.skills and not graduate.resume_text:
                continue
                
            print(f"\n*** Processing graduate: {graduate.full_name} ***")
            match_result = MatchingAlgorithms.calculate_overall_match(
                graduate.skills,
                graduate.resume_text or "",
                job.requirements,
                job.description
            )
            
            print(f"*** Result for {graduate.full_name}: {match_result['overall_score']}% ***")
            
            if match_result['overall_score'] >= threshold:
                matches.append({
                    'graduate': graduate,
                    'match_score': match_result['overall_score'],
                    'skill_match': match_result['skill_match'],
                    'text_similarity': match_result['text_similarity']
                })
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches