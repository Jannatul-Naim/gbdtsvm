import random
import numpy as np
import pandas as pd
import os
from matplotlib import pyplot as plt
from numpy import interp
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_curve, roc_curve, auc, confusion_matrix, accuracy_score, classification_report
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score


# Define input and output directories
input_data_dir = "data"
output_dir = "results"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read CSV files using the input data directory path
disease_name = pd.read_csv(os.path.join(input_data_dir, 'disease_name.csv'))
snoRNA_name = pd.read_csv(os.path.join(input_data_dir, 'snoRNA_name.csv'))
SnoRNA_similarity = pd.read_csv(os.path.join(output_dir, 'IRS_matrix.csv'), header=None)
known_association = pd.read_csv(os.path.join(input_data_dir, 'known_snoRNA_disease.csv'), header=None)
disease_similarity = pd.read_csv(os.path.join(output_dir, 'IDS_matrix.csv'), header=None)

print(f"Starting the GBDT association framework for {len(disease_name)} diseases and {len(snoRNA_name)} snoRNAs")

disease_semantic_similarity = np.zeros(disease_similarity.shape) 
snoRNA_functional_similarity = np.zeros(SnoRNA_similarity.shape) 
adjacency_matrix = np.zeros(known_association.shape) 


# csv to array disease_semantic_similarity
for i in range(len(disease_name)):
    for j in range(len(disease_name)):
        disease_semantic_similarity[i, j] = disease_similarity.iloc[i, j]


# csv to array adjacency_matrix
for i in range(known_association.shape[0]):
    for j in range(known_association.shape[1]):
        adjacency_matrix[i, j] = known_association.iloc[i, j]

# csv to array snoRNA_functional_similarity
for i in range(len(snoRNA_name)):
    for j in range(len(snoRNA_name)):
        snoRNA_functional_similarity[i, j] = SnoRNA_similarity.iloc[i, j]

print("Seperating the known and unknown associations..")
unknown = []
known = []
for x in range(known_association.shape[0]):
    for y in range(known_association.shape[1]):
        if adjacency_matrix[x, y] == 0:
            unknown.append((x, y))
        else:
            known.append((x, y))

major = []
for z in range(len(unknown)):
    a = disease_semantic_similarity[unknown[z][1], :].tolist()
    b = snoRNA_functional_similarity[unknown[z][0], :].tolist()
    q = a + b
    major.append(q)

print("Staring the clustering based sampling for unknown i.e. negative associations")
kmeans = KMeans(n_clusters=23, random_state=0).fit(major)
center = kmeans.cluster_centers_
labels = kmeans.labels_ # label is given to all the datapoints but within 1 to 20


# we have seperated x and y of each centre pair.
center_x = []
center_y = []
for j in range(len(center)):
    center_x.append(center[j][0])
    center_y.append(center[j][1])

disease_rna_tup = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
for i in range(len(labels)):
    if labels[i] == 0:
        disease_rna_tup[0].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 1:
        disease_rna_tup[1].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 2:
        disease_rna_tup[2].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 3:
        disease_rna_tup[3].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 4:
        disease_rna_tup[4].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 5:
        disease_rna_tup[5].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 6:
        disease_rna_tup[6].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 7:
        disease_rna_tup[7].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 8:
        disease_rna_tup[8].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 9:
        disease_rna_tup[9].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 10:
        disease_rna_tup[10].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 11:
        disease_rna_tup[11].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 12:
        disease_rna_tup[12].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 13:
        disease_rna_tup[13].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 14:
        disease_rna_tup[14].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 15:
        disease_rna_tup[15].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 16:
        disease_rna_tup[16].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 17:
        disease_rna_tup[17].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 18:
        disease_rna_tup[18].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 19:
        disease_rna_tup[19].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 20:
        disease_rna_tup[20].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 21:
        disease_rna_tup[21].append((unknown[i][0], unknown[i][1]))
    elif labels[i] == 22:
        disease_rna_tup[22].append((unknown[i][0], unknown[i][1]))


print("Final datasets are being prepared now..")
sampled_disease_rna_tup = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
for i in range(len(disease_rna_tup)):
    # print(int((len(disease_rna_tup[i])/len(labels)) * len(known)))
    sampled_disease_rna_tup[i] = random.sample(disease_rna_tup[i], int((len(disease_rna_tup[i])/len(labels)) * len(known)))

dataset = []
for rna in range(known_association.shape[0]):
    # print(f"rna val:{rna}")
    for disease in range(known_association.shape[1]):
        # print(f"disease val:{disease}")
        for i in range(len(sampled_disease_rna_tup)):
            if (rna, disease) in sampled_disease_rna_tup[i]:
                dataset.append((rna, disease))

for rna in range(known_association.shape[0]):
    for disease in range(known_association.shape[1]):
        if (rna, disease) in known:
            dataset.append((rna, disease))

length = len(dataset)
print(f"Total number of samples in the final dataset for training: {length}")
selected_x = []
selected_y = []
#now I am just taking only the similarities of disease and rna of sampled data.
for data in dataset:
    a = disease_semantic_similarity[data[1], :].tolist()
    b = snoRNA_functional_similarity[data[0], :].tolist()
    q = a + b
    selected_x.append(q)

    if (data[0], data[1]) in known:
        selected_y.append(1)
    else:
        selected_y.append(0)

selected_data_np = np.array(selected_x)
selected_label_np = np.array(selected_y)

x = selected_data_np
y = selected_label_np

