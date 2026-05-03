# CareerBridge Matching Engine

An algorithmic matching engine designed to quantify the relevance between job seekers (Graduates) and job postings (Employers). This service powers the core recommendation feeds and candidate ranking systems within the CareerBridge platform.

## Overview

The CareerBridge Matching Engine utilizes a hybrid scoring approach, combining deterministic rule-based skill matching with probabilistic Natural Language Processing (NLP). It generates a normalized `overall_score` (0–100) to ensure transparent, explainable, and highly relevant job-to-candidate matches.

### Key Features
* **Hybrid Scoring:** Balances hard-skill intersections (60% weight) with semantic resume-to-job description relevance (40% weight).
* **TF-IDF Text Analysis:** Handles unstructured data gracefully by extracting and comparing keywords using Term Frequency-Inverse Document Frequency and Cosine Similarity.
* **Fallback Mechanisms:** Includes basic word-overlap scoring if vectorization fails.
* **Explainable Analytics:** Stores granular score breakdowns (`skill_score`, `text_score`, `overall_score`) in the `MatchAnalytics` database model for transparency and reporting.


## The Mathematical Model

The scoring algorithm is divided into two primary components that are weighted and combined.

### 1. Skill Match Score (60%)
Calculates the proportion of job-required skills that are present in the candidate's skill set.

$$Match = \frac{|C \cap J|}{|J|} \times 100$$
*(Where **C** = Candidate Skills and **J** = Job Requirements)*

### 2. Text Similarity Score (40%)
Evaluates the semantic alignment between the candidate's full resume text and the job description using Cosine Similarity on TF-IDF vectors.

$$\text{Score}_{\text{text}} = \text{scale}_{0\to100} \left( \frac{ \mathbf{V}_{\text{resume}} \cdot \mathbf{V}_{\text{job}} }{ \| \mathbf{V}_{\text{resume}} \| \| \mathbf{V}_{\text{job}} \| } \right)$$

### 3. Overall Weighted Score
The final clamped output used for ranking and threshold filtering (default threshold $\ge$ 60).

$$\text{Score}_{\text{overall}} = \max\left(0, \min\left(100, 0.6 \times \text{Score}_{\text{skill}} + 0.4 \times \text{Score}_{\text{text}}\right)\right)$$

## Project Structure

```text
├── app.py                      # Main application entry point and API route definitions
├── routes/
│   ├── graduate.py             # Graduate job recommendation workflows
│   └── employer.py             # Employer candidate ranking workflows
├── utils/
│   ├── algorithms.py           # Core matching logic (TF-IDF, set intersections)
│   └── simple_similarity.py    # Fallback text similarity algorithms
├── requirements.txt            # Python dependencie
