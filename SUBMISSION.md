# Submission guide

| Field | Where it comes from |
|---|---|
| GitHub Repository Link | https://github.com/ThotaSathwika/edupro-learner-segmentation |
| Research paper link | `reports/Research_Paper.pdf` shared from Google Drive ("Anyone with the link") |
| Deployed project link | share.streamlit.io → repo `edupro-learner-segmentation`, branch `main`, file `app.py` |
| Project Explanation Video | 3-5 min screen recording (script below), YouTube Unlisted or Drive link |
| Internship Experience & Feedback Video | 1-2 min selfie/screen video in your own words (script below) |

## Project explanation video script (~4 min)
1. **Intro (20s)** – "I'm Thota Sathwika, final-year CSE at BVRIT. This is my Unified Mentor project: a student segmentation and personalized course recommendation system for EduPro."
2. **Problem (20s)** – EduPro shows everyone the same courses; learners differ (explorers, specialists, career learners).
3. **Data (30s)** – 3,000 learners, 60 courses in 12 categories, 10,000 enrolments in 2025. 64% of enrolments are free; 54% of learners took only one course.
4. **Features (40s)** – total courses, enrolment frequency, diversity score, learning depth index, average spend, paid share, average rating, age, gender. Log-transform + standardise.
5. **Clustering (45s)** – K-Means k=2-10; elbow + silhouette pick k=3 (0.329). Ward hierarchical agrees, ARI 0.91. Show PCA plot.
6. **Segments (40s)** – Multi-Domain Power Learners: 15% of learners, 62% of revenue. Career-Focused Paid Learners: 36%, 38% of revenue. Free-Course Samplers: 48%, almost no revenue.
7. **Recommender + demo (60s)** – score = 0.40 content similarity + 0.35 popularity in segment + 0.25 rating. Open the app, pick a learner, show segment, filter by level/category, show learning path, segment comparison, evaluation tab.
8. **Evaluation & close (25s)** – hit-rate@5 0.113 vs 0.107 popularity; small lift because enrolments in the data are almost uniform, so an A/B test is the next step. Thank you.

## Internship experience & feedback video (talking points — say it in your own words)
- What the internship was and how long it ran.
- Skills you practised: feature engineering, clustering, recommender design, Streamlit deployment, writing a research paper.
- A challenge you faced (e.g. the data had almost no category loyalty, so you learned to report results honestly) and how you handled it.
- What you liked about the mentorship/programme and one suggestion for improvement.
- How it helps your placement goals.
