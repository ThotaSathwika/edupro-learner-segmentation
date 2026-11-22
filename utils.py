"""Feature engineering, clustering and recommendation logic for EduPro."""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DATA = "data/EduPro Online Platform.xlsx"
LEVEL_SCORE = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}

NUM_FEATURES = [
    "total_courses", "avg_courses_per_category", "enroll_freq_per_month",
    "avg_rating_enrolled", "avg_spend", "total_spend", "diversity_score",
    "depth_index", "paid_share", "age",
]


def load_data(path=DATA):
    x = pd.read_excel(path, sheet_name=None)
    users, courses, tx = x["Users"], x["Courses"], x["Transactions"]
    users = users.drop(columns=["UserName", "Email"])  # personal data not needed
    tx = tx.merge(courses, on="CourseID", how="left")
    return users, courses, tx


def build_features(users, tx):
    """One row per learner: engagement, preference and behavioural features."""
    g = tx.groupby("UserID")
    f = pd.DataFrame({
        "total_courses": g.size(),
        "diversity_score": g["CourseCategory"].nunique(),
        "avg_rating_enrolled": g["CourseRating"].mean(),
        "avg_spend": g["Amount"].mean(),
        "total_spend": g["Amount"].sum(),
        "paid_share": g["CourseType"].apply(lambda s: (s == "Paid").mean()),
        "first_date": g["TransactionDate"].min(),
        "last_date": g["TransactionDate"].max(),
    })
    f["avg_courses_per_category"] = f["total_courses"] / f["diversity_score"]
    months = ((f["last_date"] - f["first_date"]).dt.days / 30.44).clip(lower=1)
    f["enroll_freq_per_month"] = f["total_courses"] / months
    lv = tx.assign(score=tx["CourseLevel"].map(LEVEL_SCORE))
    f["depth_index"] = lv.groupby("UserID")["score"].mean() / 2  # 0 = all beginner, 1 = all advanced
    f["pref_category"] = g["CourseCategory"].agg(lambda s: s.value_counts().index[0])
    f["pref_level"] = g["CourseLevel"].agg(lambda s: s.value_counts().index[0])
    f = f.drop(columns=["first_date", "last_date"]).reset_index()
    f = f.merge(users, on="UserID", how="left").rename(columns={"Age": "age"})
    return f


def scale(feat):
    X = feat[NUM_FEATURES].copy()
    # log-transform skewed counts/money to reduce noise from sparse enrolments
    for c in ["total_courses", "total_spend", "avg_spend", "enroll_freq_per_month"]:
        X[c] = np.log1p(X[c])
    X["gender_male"] = (feat["Gender"] == "Male").astype(int)
    return StandardScaler().fit_transform(X), X.columns.tolist()


def fit_kmeans(X, k, seed=42):
    return KMeans(n_clusters=k, n_init=20, random_state=seed).fit(X)


def name_segments(feat):
    """Give each cluster a readable name from its centroid profile."""
    prof = feat.groupby("cluster")[NUM_FEATURES].mean()
    names = {}
    for c, r in prof.iterrows():
        if r.total_courses >= prof.total_courses.quantile(0.75) and r.diversity_score >= 3:
            n = "Multi-Domain Power Learners"
        elif r.paid_share <= 0.1:
            n = "Free-Course Samplers"
        elif r.avg_spend >= prof.avg_spend.quantile(0.75):
            n = "Career-Focused Paid Learners"
        elif r.depth_index >= 0.6:
            n = "Advanced Specialists"
        elif r.depth_index <= 0.4:
            n = "Beginner Explorers"
        else:
            n = "Casual Intermediate Learners"
        names[c] = n
    # make names unique
    seen = {}
    for c in sorted(names):
        n = names[c]
        seen[n] = seen.get(n, 0) + 1
        if seen[n] > 1:
            names[c] = f"{n} {seen[n]}"
    return names


# ---------------- Recommendation engine ----------------

def course_vectors(courses):
    """One-hot content vector per course (category, level, type)."""
    v = pd.get_dummies(courses.set_index("CourseID")[["CourseCategory", "CourseLevel", "CourseType"]]).astype(float)
    cat_cols = [c for c in v.columns if c.startswith("CourseCategory_")]
    v[cat_cols] *= 2.0  # category matters more than level/type
    return v


def recommend(user_id, tx, courses, feat, top_n=5, weights=(0.4, 0.35, 0.25),
              level=None, category=None, history=None):
    """Hybrid score = content similarity + popularity within the learner's cluster
    + rating-weighted relevance. Already-taken courses are excluded."""
    w_content, w_pop, w_rating = weights
    vec = course_vectors(courses)
    hist = history if history is not None else tx.loc[tx.UserID == user_id, "CourseID"].tolist()
    cl = feat.loc[feat.UserID == user_id, "cluster"].iloc[0]

    # content-based: cosine similarity between user profile and each course
    prof = vec.loc[hist].mean(axis=0) if hist else vec.mean(axis=0)
    sim = vec.values @ prof.values / (np.linalg.norm(vec.values, axis=1) * np.linalg.norm(prof.values) + 1e-9)
    content = pd.Series(sim, index=vec.index)

    # popularity among similar learners (same cluster)
    peers = feat.loc[feat.cluster == cl, "UserID"]
    pop = tx[tx.UserID.isin(peers) & (tx.UserID != user_id)].CourseID.value_counts()
    pop = (pop / pop.max()).reindex(vec.index).fillna(0)

    rating = courses.set_index("CourseID")["CourseRating"] / 5

    score = w_content * content + w_pop * pop + w_rating * rating
    out = courses.set_index("CourseID").assign(
        score=score, content_sim=content, cluster_popularity=pop).drop(index=hist, errors="ignore")
    if level:
        out = out[out.CourseLevel.isin(level)]
    if category:
        out = out[out.CourseCategory.isin(category)]
    return out.sort_values("score", ascending=False).head(top_n).reset_index()


def learning_path(recs):
    order = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
    return recs.assign(o=recs.CourseLevel.map(order)).sort_values(["o", "score"], ascending=[True, False]).drop(columns="o")
