import csv
import sacrebleu

def compute_bleu(prediction, reference):
    bleu = sacrebleu.corpus_bleu(prediction, reference, tokenize='13a')
    return bleu.score

def process_csv(file_path):
    pre1, ref1, pre2, ref2 = [], [], [], []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for i, row in enumerate(reader, start=2):
            if i > 1013:
                break
            col2, col3, col5 = row[1].strip(), row[2].strip(), row[4].strip() if len(row) > 4 else ''

            pre1.append(col3)
            ref1.append([col3, col2])

            if col5:
                pre2.append(col5)
                ref2.append([col5, col2])

    s1=compute_bleu(pre1, ref1)
    s2=compute_bleu(pre2, ref2)
    print("O:",f"{s1:.2f}")
    print("G:",f"{s2:.2f}")

#file_path = 'bleu_scores_fr.csv'
file_path = 'bleu_scores_de.csv'
process_csv(file_path)
