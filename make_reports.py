"""Builds reports/Research_Paper.docx and reports/Executive_Summary.docx from outputs/."""
import json, os
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

os.makedirs("reports", exist_ok=True)
r = json.load(open("outputs/results.json"))
prof = pd.read_csv("outputs/segment_profiles.csv", index_col=0)
feat = pd.read_csv("outputs/learner_features.csv")
rev_share = (feat.groupby("segment").total_spend.sum() / feat.total_spend.sum() * 100).round(1)
seg_n = feat.segment.value_counts()
seg_pct = (seg_n / len(feat) * 100).round(1)
PL, CF, FS = "Multi-Domain Power Learners", "Career-Focused Paid Learners", "Free-Course Samplers"
AUTHOR = "Thota Sathwika"
AFFIL = "Department of Computer Science and Engineering, B V Raju Institute of Technology (BVRIT), Narsapur"


def base_doc():
    d = Document()
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(0.9); s.top_margin = s.bottom_margin = Inches(0.8)
    return d


def para(d, text, bold=False, italic=False, size=None, align=None, color=None):
    p = d.add_paragraph(); run = p.add_run(text)
    run.bold, run.italic = bold, italic
    if size: run.font.size = Pt(size)
    if color: run.font.color.rgb = RGBColor(*color)
    if align: p.alignment = align
    return p


def bullets(d, items):
    for i in items:
        d.add_paragraph(i, style="List Bullet")


def table(d, df, index=True):
    df = df.reset_index() if index else df
    t = d.add_table(rows=1, cols=len(df.columns)); t.style = "Light Grid Accent 1"
    for i, c in enumerate(df.columns):
        t.rows[0].cells[i].text = str(c)
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = f"{v:,.2f}" if isinstance(v, float) else str(v)
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for run in p.runs: run.font.size = Pt(9)
    d.add_paragraph()


def fig(d, path, caption, w=6.3):
    d.add_picture(path, width=Inches(w))
    d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    para(d, caption, italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)


# ===================== RESEARCH PAPER =====================
d = base_doc()
para(d, "Student Segmentation and Personalized Course Recommendation System for EduPro",
     bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER)
para(d, AUTHOR, bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
para(d, AFFIL, italic=True, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
para(d, "Data Science Internship Project · Unified Mentor · 2026", size=10, align=WD_ALIGN_PARAGRAPH.CENTER)

d.add_heading("Abstract", 1)
para(d, f"Online learning platforms usually show every learner the same course list, even though learners behave very "
        f"differently. This paper builds a learner segmentation and recommendation system for EduPro using "
        f"{r['n_users']:,} learners, {r['n_courses']} courses and {r['n_tx']:,} enrolment transactions from 2025. We engineer "
        f"eleven learner-level features covering engagement, preference and behaviour, then segment learners with K-Means and "
        f"validate the result with Ward hierarchical clustering. Elbow and silhouette analysis select k = {r['k']} "
        f"(silhouette {r['silhouette']}); hierarchical clustering agrees closely (adjusted Rand index {r['ari_kmeans_vs_hier']}). "
        f"The three segments are {PL} ({seg_pct[PL]}% of learners, {rev_share[PL]}% of revenue), {CF} ({seg_pct[CF]}%, "
        f"{rev_share[CF]}%) and {FS} ({seg_pct[FS]}%, {rev_share[FS]}%). A hybrid, cluster-aware recommender combines content "
        f"similarity, popularity within the learner's segment and rating-weighted relevance. In a leave-last-out test it reaches "
        f"hit-rate@5 of {r['hit_rate@5']['hybrid']}, a {r['engagement_lift_vs_popularity']}× lift over global popularity. The lift "
        f"is small because enrolments in this dataset are spread almost evenly across courses, and we discuss what this means "
        f"for deployment. All results are served in an interactive Streamlit dashboard.")
para(d, "Keywords: learner segmentation, K-Means, hierarchical clustering, recommender systems, e-learning, personalization",
     italic=True, size=10)

d.add_heading("1. Introduction", 1)
para(d, "Learners on an online platform are not one group. Some sample free beginner courses across many subjects, some go "
        "deep in one subject, and others pay for career-oriented certifications. A single recommendation list serves none of "
        "these groups well: learners struggle to find relevant courses, and the platform loses chances to improve engagement, "
        "completion and loyalty. EduPro currently has no structured way to describe its learner types. This project shifts the "
        "focus from predicting course demand to understanding the learner and personalizing the learning journey.")
para(d, "Objectives:", bold=True)
bullets(d, ["Build learner profiles that combine demographics with enrolment behaviour.",
            "Segment learners with unsupervised clustering and choose the number of segments objectively.",
            "Recommend relevant courses using the learner's segment, history and course quality.",
            "Evaluate cluster quality and recommendation relevance with standard metrics.",
            "Deliver the analysis as an interactive Streamlit dashboard."])

d.add_heading("2. Related Work", 1)
para(d, "Learner segmentation with K-Means and hierarchical clustering is a common approach in educational data mining, "
        "used to group students by activity, performance or preferences. Recommender systems are usually content-based "
        "(matching item attributes to a user profile), collaborative (using similar users' behaviour) or hybrid. Cluster-based "
        "collaborative filtering reduces sparsity by computing popularity inside a group of similar users rather than across "
        "the whole population, which suits platforms where most users have only a few interactions. This project combines "
        "these ideas into a lightweight hybrid model that needs no explicit ratings from learners.")

d.add_heading("3. Dataset", 1)
para(d, "The EduPro workbook contains four sheets. Learner names and e-mail addresses were dropped because they are "
        "personal data and are not needed for modelling.")
table(d, pd.DataFrame({
    "Sheet": ["Users", "Courses", "Transactions", "Teachers"],
    "Rows": [r["n_users"], r["n_courses"], r["n_tx"], 60],
    "Fields used": ["UserID, Age (15-35), Gender",
                    "CourseID, CourseCategory (12), CourseType, CourseLevel, CourseRating, CoursePrice",
                    "UserID, CourseID, TransactionDate (Jan-Dec 2025), Amount",
                    "Not used (outside project scope)"]}), index=False)

d.add_heading("4. Exploratory Data Analysis", 1)
fig(d, "figures/eda_overview.png", "Figure 1. Enrolments by category, by level and by month.")
bullets(d, [
    f"{r['free_tx_share']*100:.0f}% of enrolments are in free courses; total paid revenue is ${r['revenue']:,.0f}. "
    "38 of the 60 courses are free.",
    "Enrolments are spread evenly: every course has between 140 and 196 enrolments, and the three levels are close to "
    "one third each (Beginner 35.7%, Advanced 34.8%, Intermediate 29.5%).",
    "Monthly enrolments are flat across 2025, with no strong seasonality.",
    "Revenue is concentrated in Artificial Intelligence, Business and Project Management, which carry the highest-priced courses."])
fig(d, "figures/eda_learners.png", "Figure 2. Courses per learner, categories explored and learner age.")
bullets(d, [
    f"Engagement is highly skewed: {r['single_course_share']*100:.0f}% of learners took only one course (median "
    f"{r['median_courses']:.0f}), while a small group took 10-16 courses.",
    "Age is uniform between 15 and 35 and gender is balanced (1,520 female, 1,480 male), so demographics alone do not "
    "separate learner types; behaviour does."])

d.add_heading("5. Methodology", 1)
d.add_heading("5.1 Learner-level feature engineering", 2)
para(d, "Transactions were joined to course attributes and aggregated by UserID.")
table(d, pd.DataFrame({
    "Group": ["Engagement", "Engagement", "Engagement", "Preference", "Preference", "Preference",
              "Behavioural", "Behavioural", "Behavioural", "Behavioural", "Demographic"],
    "Feature": ["total_courses", "avg_courses_per_category", "enroll_freq_per_month", "pref_category", "pref_level",
                "avg_rating_enrolled", "avg_spend / total_spend", "diversity_score", "depth_index", "paid_share",
                "age, gender"],
    "Definition": ["Number of enrolments", "total_courses ÷ distinct categories", "Enrolments per active month",
                   "Most frequent category", "Most frequent level", "Mean rating of enrolled courses",
                   "Mean / total amount paid", "Distinct categories explored",
                   "Mean level score (Beginner 0, Intermediate 1, Advanced 2) ÷ 2; 0 = all beginner, 1 = all advanced",
                   "Share of enrolments in paid courses", "From Users sheet"]}), index=False)
d.add_heading("5.2 Preprocessing", 2)
bullets(d, ["Log-transform of skewed counts and amounts (total_courses, spend, frequency) to reduce the noise from sparse "
            "one-course learners.",
            "Gender encoded as a binary variable; preferred category and level are kept for interpretation and recommendation "
            "rather than clustering, to avoid 12+ sparse dummy columns dominating the distance.",
            "All numeric features standardised to zero mean and unit variance."])
d.add_heading("5.3 Segmentation", 2)
para(d, "K-Means (20 initialisations) was run for k = 2-10. The elbow curve and silhouette score guided the choice. k = 2 "
        "only separates heavy from light users, so k was chosen as the best silhouette among k = 3-6. Ward hierarchical "
        "clustering with the same k validated the partition.")
fig(d, "figures/elbow_silhouette.png", "Figure 3. Elbow (inertia) and silhouette score for k = 2-10.")
d.add_heading("5.4 Cluster-aware hybrid recommender", 2)
para(d, "For learner u in segment s and every course c not yet taken:")
para(d, "score(u, c) = 0.40 × ContentSim(u, c) + 0.35 × SegmentPopularity(s, c) + 0.25 × Rating(c) / 5", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER)
bullets(d, ["ContentSim: cosine similarity between the course's one-hot vector (category weighted ×2, level, type) and the "
            "mean vector of the learner's past courses (content-based filtering).",
            "SegmentPopularity: enrolment count of the course among other learners in the same segment, scaled to 0-1 "
            "(similar learner profiles and popularity within cluster).",
            "Rating: course rating scaled to 0-1 (rating-weighted relevance).",
            "Results can be filtered by level and category, and are re-ordered Beginner → Intermediate → Advanced to form a "
            "learning path."])
d.add_heading("5.5 Evaluation design", 2)
para(d, f"Cluster quality: silhouette score, Davies-Bouldin index, and mean cosine similarity within versus between segments. "
        f"Recommendation relevance: for {r['eval_users']} randomly chosen learners with at least three enrolments, the most "
        f"recent enrolment was hidden, the model was trained on the rest, and we checked whether the hidden course appeared in "
        f"the top 5 (hit-rate@5, precision@5). Baselines were global popularity and random recommendation. Engagement lift "
        f"(proxy) is the hybrid hit-rate divided by the baseline hit-rate.")

d.add_heading("6. Results", 1)
d.add_heading("6.1 Learner segments", 2)
fig(d, "figures/clusters_pca.png", f"Figure 4. Learner segments in PCA space (PC1 {r['pca_var'][0]*100:.0f}%, "
                                   f"PC2 {r['pca_var'][1]*100:.0f}% of variance).", w=5.2)
show = prof[["learners", "total_courses", "diversity_score", "avg_spend", "total_spend", "paid_share", "depth_index",
             "avg_rating_enrolled", "top_category"]].copy()
show["revenue_share_%"] = rev_share
table(d, show)
fig(d, "figures/segment_heatmap.png", "Figure 5. Segment profiles as z-scores against all learners.")
bullets(d, [
    f"{PL} ({seg_n[PL]} learners, {seg_pct[PL]}%): about 13 courses across 8-9 categories, the highest enrolment "
    f"frequency and {rev_share[PL]}% of all revenue. These are the platform's most loyal learners and explore broadly.",
    f"{CF} ({seg_n[CF]}, {seg_pct[CF]}%): fewer than 2 courses each, but {prof.loc[CF,'paid_share']*100:.0f}% of them are "
    f"paid, with average spend of ${prof.loc[CF,'avg_spend']:.0f} per course. They buy targeted, higher-value courses "
    f"(most often Artificial Intelligence) and bring in {rev_share[CF]}% of revenue.",
    f"{FS} ({seg_n[FS]}, {seg_pct[FS]}%): about 1.3 free courses each and almost no spending. This is the largest group and "
    f"the main conversion and retention opportunity.",
    "Depth index and age are almost identical across segments: what separates learners is how much they engage and whether "
    "they pay, not their level or age."])
d.add_heading("6.2 Cluster validation", 2)
table(d, pd.DataFrame({
    "Metric": ["Silhouette (K-Means)", "Silhouette (Hierarchical, Ward)", "Adjusted Rand index (K-Means vs Ward)",
               "Davies-Bouldin index (lower is better)", "Intra-cluster cosine similarity", "Inter-cluster cosine similarity"],
    "Value": [r["silhouette"], r["hier_silhouette"], r["ari_kmeans_vs_hier"], r["davies_bouldin"],
              r["intra_cluster_similarity"], r["inter_cluster_similarity"]]}), index=False)
para(d, f"The two algorithms agree on {r['ari_kmeans_vs_hier']:.2f} ARI, so the segments are stable rather than an artefact "
        f"of K-Means initialisation. Learners are far more similar inside their segment ({r['intra_cluster_similarity']}) than "
        f"across segments ({r['inter_cluster_similarity']}), confirming behavioural consistency.")
fig(d, "figures/dendrogram.png", "Figure 6. Ward dendrogram on a 300-learner sample.")
d.add_heading("6.3 Recommendation performance", 2)
table(d, pd.DataFrame({
    "Model": ["Cluster-aware hybrid", "Global popularity", "Random"],
    "Hit-rate@5": [r["hit_rate@5"]["hybrid"], r["hit_rate@5"]["popularity"], r["hit_rate@5"]["random"]],
    "Precision@5": [r["precision@5"]["hybrid"], r["precision@5"]["popularity"], r["precision@5"]["random"]]}), index=False)
para(d, f"The hybrid model gives the best hit-rate, a {r['engagement_lift_vs_popularity']}× lift over popularity and "
        f"{r['engagement_lift_vs_random']}× over random. The margin is small. To understand why, we checked whether learners "
        f"return to categories they already took: for learners with three or more courses, the next course was in a "
        f"previously-seen category 45% of the time, compared with 49% expected by chance. In other words, enrolments in this "
        f"dataset show no category loyalty and are close to uniformly random across the 60 courses. Any offline evaluation on "
        f"such data will show only modest lift; the real benefit of personalization must be measured with a live A/B test.")

d.add_heading("7. Streamlit Dashboard", 1)
para(d, "The dashboard (app.py) has five modules:")
bullets(d, ["Overview: key platform metrics, enrolment trends and segment mix.",
            "Learner Profile & Recommendations: select a learner, see their segment, profile metrics and history, get "
            "personalized recommendations filtered by level or category, and a Beginner → Advanced learning path.",
            "Cluster Dashboard: interactive PCA and feature-pair scatter plots, category demand by segment.",
            "Segment Comparison: side-by-side profile table, box plots for any feature, level mix by segment.",
            "Model Evaluation: silhouette, ARI, Davies-Bouldin, intra/inter similarity and recommender hit-rates."])

d.add_heading("8. Recommendations for EduPro", 1)
bullets(d, [
    f"Convert {FS}: they are {seg_pct[FS]}% of learners but generate almost no revenue. Recommend highly rated free "
    "courses first, then a low-priced paid course in the same category, and use reminders after the first course.",
    f"Retain {PL}: they generate {rev_share[PL]}% of revenue. Offer bundles, subscriptions or multi-course certificates, "
    "and recommend new categories they have not yet explored.",
    f"Grow {CF}: they pay for focused content. Recommend structured certification paths (Beginner → Advanced) in their "
    "chosen field, especially AI, Business and Project Management.",
    "Fix low-rated courses: several courses have ratings below 2 (for example Natural Language Processing 1.13, "
    "AI for Beginners 1.20). The rating weight protects learners from them, but content review would help more.",
    "Run a controlled A/B test of segment-aware recommendations against the current list, measuring click-through, "
    "enrolment and completion, before full rollout."])

d.add_heading("9. Limitations and Future Work", 1)
bullets(d, ["The dataset has no completion, watch-time or explicit rating data, so engagement is measured only through "
            "enrolment and spend.",
            "Enrolments look close to randomly generated, which limits the measurable recommendation lift.",
            "Future work: add completion and session data, try matrix factorisation or sequence models, re-cluster monthly to "
            "track learners moving between segments, and test the recommender online."])

d.add_heading("10. Conclusion", 1)
para(d, f"This project gives EduPro a structured, data-driven view of its learners. Three stable segments emerge "
        f"(silhouette {r['silhouette']}, ARI {r['ari_kmeans_vs_hier']} between methods): a small group of multi-domain power "
        f"learners who drive most revenue, focused paid learners who buy career courses, and a large group of free samplers "
        f"who represent the biggest growth opportunity. A cluster-aware hybrid recommender turns these segments into "
        f"personalized, filterable learning paths, and the Streamlit dashboard makes the analysis usable by non-technical "
        f"teams. The honest evaluation also shows where better data is needed to prove impact.")

d.add_heading("References", 1)
for ref in ["MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. Proc. 5th Berkeley Symposium.",
            "Ward, J. H. (1963). Hierarchical grouping to optimize an objective function. JASA, 58(301), 236-244.",
            "Rousseeuw, P. J. (1987). Silhouettes: a graphical aid to the interpretation and validation of cluster analysis. J. Comput. Appl. Math., 20, 53-65.",
            "Ricci, F., Rokach, L., & Shapira, B. (2015). Recommender Systems Handbook (2nd ed.). Springer.",
            "Romero, C., & Ventura, S. (2010). Educational data mining: a review of the state of the art. IEEE Trans. SMC-C, 40(6), 601-618.",
            "Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. JMLR, 12, 2825-2830."]:
    d.add_paragraph(ref, style="List Number")
d.save("reports/Research_Paper.docx")

# ===================== EXECUTIVE SUMMARY =====================
e = base_doc()
para(e, "Executive Summary", bold=True, size=20, color=(0x1F, 0x3A, 0x68))
para(e, "Student Segmentation and Personalized Course Recommendation System for EduPro", bold=True, size=13)
para(e, f"Prepared by {AUTHOR} · Unified Mentor Data Science Internship · For government and public-sector stakeholders",
     italic=True, size=10)
e.add_heading("The problem", 2)
para(e, "EduPro shows every learner the same course recommendations. It has no structured way to understand who its learners "
        "are, so learners struggle to find relevant courses and opportunities to improve engagement and retention are lost.")
e.add_heading("What we did", 2)
para(e, f"We analysed {r['n_users']:,} learners and {r['n_tx']:,} course enrolments from 2025, built a behavioural profile "
        f"for every learner, grouped learners into segments with machine learning, and built a recommendation engine that "
        f"suggests courses based on each learner's segment, history and course quality. Results are available in an "
        f"interactive web dashboard.")
e.add_heading("Key findings", 2)
bullets(e, [
    f"Three distinct learner groups exist, confirmed by two independent methods (silhouette {r['silhouette']}, "
    f"{r['ari_kmeans_vs_hier']*100:.0f}% agreement).",
    f"{PL}: {seg_pct[PL]}% of learners, about 13 courses each across 8-9 subjects, {rev_share[PL]}% of revenue.",
    f"{CF}: {seg_pct[CF]}% of learners, few courses but mostly paid (avg ${prof.loc[CF,'avg_spend']:.0f}), "
    f"{rev_share[CF]}% of revenue.",
    f"{FS}: {seg_pct[FS]}% of learners, about one free course each, almost no revenue: the largest untapped group.",
    f"{r['single_course_share']*100:.0f}% of all learners stop after one course, so first-course follow-up is the biggest "
    f"retention lever.",
    f"Personalized recommendations beat the current popularity approach ({r['engagement_lift_vs_popularity']}× in offline "
    f"testing); the gain is modest because historical enrolments show little subject loyalty, so a live pilot is needed to "
    f"measure true impact."])
e.add_heading("Recommended actions", 2)
table(e, pd.DataFrame({
    "Priority": ["1", "2", "3", "4"],
    "Action": [f"Guide {FS} from a first free course to a second, well-rated course and a low-cost paid option",
               f"Offer bundles and multi-course certificates to {PL}",
               f"Promote structured Beginner → Advanced certification paths to {CF}",
               "Pilot segment-aware recommendations with an A/B test before full rollout"],
    "Expected benefit": ["Higher retention and conversion of the largest group", "Protect most revenue, deepen loyalty",
                         "Higher completion and paid enrolments", "Evidence-based decision on rollout"]}), index=False)
e.add_heading("Public-value considerations", 2)
bullets(e, ["Privacy: names and e-mails were removed; the model uses only age, gender and enrolment behaviour.",
            "Fairness: segments are driven by behaviour, not age or gender, which are nearly identical across groups.",
            "Transparency: every recommendation score is explainable (content match, peer popularity, rating).",
            "Access: highly rated free courses are recommended first to learners who do not pay, supporting inclusive learning."])
e.save("reports/Executive_Summary.docx")
print("reports written")
