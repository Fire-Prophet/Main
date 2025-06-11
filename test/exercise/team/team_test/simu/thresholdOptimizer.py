from sklearn.metrics import f1_score

def find_best_threshold(probs, labels):
    best = 0
    for t in [i / 100 for i in range(20, 90)]:
        preds = (probs >= t).astype(int)
        score = f1_score(labels, preds)
        if score > best:
            best, best_t = score, t
    return best_t
