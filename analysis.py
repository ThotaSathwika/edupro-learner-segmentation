"""Full pipeline: EDA -> features -> clustering -> recommendations -> evaluation.
Writes outputs/ (csv, json) and figures/ (png)."""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from utils import *

os.makedirs("figures", exist_ok=True); os.makedirs("outputs", exist_ok=True)
sns.set_theme(style="whitegrid", palette="Set2")
users, courses, tx = load_data()
res = {}

# ---------- EDA ----------
res["n_users"], res["n_courses"], res["n_tx"] = len(users), len(courses), len(tx)
res["free_tx_share"] = round((tx.Amount == 0).mean(), 3)
res["revenue"] = round(tx.Amount.sum(), 2)
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
tx.CourseCategory.value_counts().plot.barh(ax=ax[0], title="Enrolments by category")
tx.CourseLevel.value_counts().plot.bar(ax=ax[1], title="Enrolments by level", rot=0)
tx.groupby(tx.TransactionDate.dt.month).size().plot(ax=ax[2], marker="o", title="Enrolments per month (2025)")
plt.tight_layout(); plt.savefig("figures/eda_overview.png", dpi=130); plt.close()

feat = build_features(users, tx)
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
feat.total_courses.plot.hist(bins=16, ax=ax[0], title="Courses per learner")
feat.diversity_score.value_counts().sort_index().plot.bar(ax=ax[1], title="Categories explored (diversity)", rot=0)
feat.age.plot.hist(bins=21, ax=ax[2], title="Learner age")
plt.tight_layout(); plt.savefig("figures/eda_learners.png", dpi=130); plt.close()
res["single_course_share"] = round((feat.total_courses == 1).mean(), 3)
res["median_courses"] = float(feat.total_courses.median())

# ---------- Cluster selection ----------
X, cols = scale(feat)
ks, inertia, sil = range(2, 11), [], []
for k in ks:
    m = fit_kmeans(X, k)
    inertia.append(m.inertia_); sil.append(silhouette_score(X, m.labels_))
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
ax[0].plot(list(ks), inertia, "o-"); ax[0].set_title("Elbow method (inertia)"); ax[0].set_xlabel("k")
ax[1].plot(list(ks), sil, "o-", color="C1"); ax[1].set_title("Silhouette score"); ax[1].set_xlabel("k")
plt.tight_layout(); plt.savefig("figures/elbow_silhouette.png", dpi=130); plt.close()
res["k_search"] = {int(k): round(s, 4) for k, s in zip(ks, sil)}
# choose best silhouette among k=3..6 (k=2 only splits active vs one-course learners)
K = max(range(3, 7), key=lambda k: sil[k - 2])
res["k"] = K
km = fit_kmeans(X, K)
feat["cluster"] = km.labels_
res["silhouette"] = round(silhouette_score(X, km.labels_), 4)
res["davies_bouldin"] = round(davies_bouldin_score(X, km.labels_), 4)

# hierarchical validation
hc = AgglomerativeClustering(n_clusters=K, linkage="ward").fit(X)
res["hier_silhouette"] = round(silhouette_score(X, hc.labels_), 4)
res["ari_kmeans_vs_hier"] = round(adjusted_rand_score(km.labels_, hc.labels_), 4)

# intra vs inter cluster cosine similarity
S = cosine_similarity(X)
same = km.labels_[:, None] == km.labels_[None, :]
np.fill_diagonal(same, False)
diff = km.labels_[:, None] != km.labels_[None, :]
res["intra_cluster_similarity"] = round(S[same].mean(), 4)
res["inter_cluster_similarity"] = round(S[diff].mean(), 4)

names = name_segments(feat)
feat["segment"] = feat.cluster.map(names)
res["segments"] = {names[c]: int(n) for c, n in feat.cluster.value_counts().sort_index().items()}

pca = PCA(2, random_state=42).fit(X)
P = pca.transform(X); feat["pc1"], feat["pc2"] = P[:, 0], P[:, 1]
res["pca_var"] = [round(v, 3) for v in pca.explained_variance_ratio_]
plt.figure(figsize=(8, 6))
sns.scatterplot(data=feat, x="pc1", y="pc2", hue="segment", s=18, alpha=.7)
plt.title(f"Learner segments (K-Means, k={K}) - PCA projection"); plt.tight_layout()
plt.savefig("figures/clusters_pca.png", dpi=130); plt.close()

prof = feat.groupby("segment")[NUM_FEATURES].mean().round(2)
prof["learners"] = feat.segment.value_counts()
prof["top_category"] = feat.groupby("segment").pref_category.agg(lambda s: s.value_counts().index[0])
prof["top_level"] = feat.groupby("segment").pref_level.agg(lambda s: s.value_counts().index[0])
prof.to_csv("outputs/segment_profiles.csv")
z = feat.groupby("segment")[NUM_FEATURES].mean()
z = (z - feat[NUM_FEATURES].mean()) / feat[NUM_FEATURES].std()
plt.figure(figsize=(11, 4)); sns.heatmap(z, annot=True, fmt=".2f", cmap="RdBu_r", center=0)
plt.title("Segment profiles (z-score vs all learners)"); plt.tight_layout()
plt.savefig("figures/segment_heatmap.png", dpi=130); plt.close()

# dendrogram on a sample for the paper
from scipy.cluster.hierarchy import linkage, dendrogram
idx = np.random.RandomState(0).choice(len(X), 300, replace=False)
plt.figure(figsize=(12, 4)); dendrogram(linkage(X[idx], "ward"), no_labels=True, color_threshold=None)
plt.title("Hierarchical clustering (Ward) - 300-learner sample"); plt.tight_layout()
plt.savefig("figures/dendrogram.png", dpi=130); plt.close()

feat.to_csv("outputs/learner_features.csv", index=False)

# ---------- Recommendation evaluation (leave-last-out) ----------
txs = tx.sort_values("TransactionDate")
eligible = feat.loc[feat.total_courses >= 3, "UserID"]
rng = np.random.RandomState(42)
sample = rng.choice(eligible, size=min(600, len(eligible)), replace=False)
train_tx = txs.groupby("UserID").head(-1)  # drop each user's last enrolment
global_pop = train_tx.CourseID.value_counts()
N = 5
hits = {"hybrid": 0, "popularity": 0, "random": 0}
prec_cat = 0
for u in sample:
    ut = txs[txs.UserID == u]
    hist, target = ut.CourseID.iloc[:-1].tolist(), ut.CourseID.iloc[-1]
    if target in hist:
        continue
    recs = recommend(u, train_tx, courses, feat, top_n=N, history=hist)
    hits["hybrid"] += target in recs.CourseID.values
    tgt_cat = courses.set_index("CourseID").CourseCategory[target]
    prec_cat += (recs.CourseCategory == tgt_cat).mean()
    pop = [c for c in global_pop.index if c not in hist][:N]
    hits["popularity"] += target in pop
    cand = [c for c in courses.CourseID if c not in hist]
    hits["random"] += target in rng.choice(cand, N, replace=False)
n_eval = len(sample)
res["eval_users"] = n_eval
res["hit_rate@5"] = {k: round(v / n_eval, 4) for k, v in hits.items()}
res["precision@5"] = {k: round(v / n_eval / N, 4) for k, v in hits.items()}
res["category_precision@5"] = round(prec_cat / n_eval, 4)
res["engagement_lift_vs_popularity"] = round(hits["hybrid"] / max(hits["popularity"], 1), 3)
res["engagement_lift_vs_random"] = round(hits["hybrid"] / max(hits["random"], 1), 3)
pd.Series(res["hit_rate@5"]).plot.bar(rot=0, color=["C0", "C1", "C2"], title="Hit-rate@5 (leave-last-out)")
plt.tight_layout(); plt.savefig("figures/rec_eval.png", dpi=130); plt.close()

json.dump(res, open("outputs/results.json", "w"), indent=2, default=str)
print(json.dumps(res, indent=2, default=str))
print(prof.to_string())
