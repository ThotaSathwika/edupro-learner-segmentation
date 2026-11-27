# Student Segmentation & Personalized Course Recommendation System — EduPro
Unified Mentor Data Science Internship · Thota Sathwika

Segments 3,000 EduPro learners by behaviour and recommends courses with a cluster-aware hybrid recommender, served in a Streamlit dashboard.

## Run locally
```bash
pip install -r requirements.txt
python analysis.py       # EDA, features, clustering, evaluation -> outputs/, figures/
python make_reports.py   # research paper + executive summary -> reports/
streamlit run app.py     # dashboard
```

## Structure
| File | Purpose |
|---|---|
| `utils.py` | data loading, learner feature engineering, scaling, K-Means, segment naming, hybrid recommender |
| `analysis.py` | EDA, elbow/silhouette, K-Means + hierarchical validation, leave-last-out recommender evaluation |
| `app.py` | Streamlit app: Overview, Learner Profile & Recommendations, Cluster Dashboard, Segment Comparison, Model Evaluation |
| `make_reports.py` | builds `reports/Research_Paper` and `reports/Executive_Summary` (.docx/.pdf) |
| `outputs/` | learner features, segment profiles, `results.json` |
| `figures/` | charts used in the paper |

## Method
- **Features:** total courses, avg courses per category, enrolment frequency, preferred category/level, avg rating enrolled, avg/total spend, diversity score, learning depth index, paid share, age, gender.
- **Preprocessing:** log-transform skewed counts and spend, encode gender, standardise.
- **Segmentation:** K-Means (k chosen by elbow + silhouette), validated with Ward hierarchical clustering.
- **Recommender:** `0.40 × content similarity + 0.35 × popularity within segment + 0.25 × rating/5`, filterable by level and category, ordered into a Beginner → Advanced learning path.

## Headline results
| Metric | Value |
|---|---|
| Segments (k) | 3 |
| Silhouette (K-Means / Hierarchical) | 0.329 / 0.320 |
| Agreement K-Means vs Hierarchical (ARI) | 0.91 |
| Intra- vs inter-cluster similarity | 0.39 vs −0.24 |
| Hit-rate@5: hybrid / popularity / random | 0.113 / 0.107 / 0.108 |

| Segment | Learners | Revenue share |
|---|---|---|
| Multi-Domain Power Learners (~13 courses, 8-9 categories) | 15.4% | 62.4% |
| Career-Focused Paid Learners (77% paid courses) | 36.4% | 37.6% |
| Free-Course Samplers (~1 free course) | 48.2% | ~0% |

54% of learners take only one course. Enrolments are spread almost evenly across courses with no category loyalty, so offline recommender lift is modest (1.06× over popularity); a live A/B test is recommended.

## Deploy
share.streamlit.io → New app → this repo, branch `main`, file `app.py`.
