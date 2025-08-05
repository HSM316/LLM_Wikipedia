from bert_score import score

# 生成文本 (hypotheses)
cands = ["I like cats."]

# 参考文本 (references)
refs = ["I love cats."]

# 计算 BERTScore
P, R, F1 = score(cands, refs, lang="en", verbose=True)

# 输出结果
print("Precision:", P)
print("Recall:", R)
print("F1:", F1)
