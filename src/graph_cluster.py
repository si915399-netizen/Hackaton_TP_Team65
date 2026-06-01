import networkx as nx
from community import community_louvain

def cluster_keywords_by_cooccurrence(keywords_result, min_cooccurrence=2, top_n=100):
    if len(keywords_result) < 3:
        return []
    candidates = sorted(keywords_result, key=lambda x: x["score"], reverse=True)[:top_n]
    if len(candidates) < 2:
        return []
    word_to_files = {}
    word_to_score = {}
    for item in candidates:
        word_to_files[item["keyword"]] = set(item["examples"])
        word_to_score[item["keyword"]] = item["score"]
    words = list(word_to_files.keys())
    G = nx.Graph()
    G.add_nodes_from(words)
    for i in range(len(words)):
        for j in range(i+1, len(words)):
            common = len(word_to_files[words[i]].intersection(word_to_files[words[j]]))
            if common >= min_cooccurrence:
                G.add_edge(words[i], words[j], weight=common)
    if G.number_of_edges() == 0:
        return [{"name": w, "keywords": [w]} for w in words]
    partition = community_louvain.best_partition(G, weight="weight")
    clusters = {}
    for word, cid in partition.items():
        clusters.setdefault(cid, []).append(word)
    categories = []
    for word_list in clusters.values():
        best = max(word_list, key=lambda w: word_to_score.get(w, 0))
        word_list.sort(key=lambda w: word_to_score.get(w, 0), reverse=True)
        categories.append({"name": best, "keywords": word_list})
    categories.sort(key=lambda c: max(word_to_score.get(w, 0) for w in c["keywords"]), reverse=True)
    return categories