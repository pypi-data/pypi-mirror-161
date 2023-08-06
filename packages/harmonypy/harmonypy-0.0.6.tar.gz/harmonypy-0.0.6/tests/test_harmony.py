import pandas as pd
import numpy as np
from scipy.stats import multivariate_normal
import matplotlib.pyplot as plt

x, y = np.mgrid[-1:1:.01, -1:1:.01]
pos = np.empty(x.shape + (2,))
pos[:, :, 0] = x
pos[:, :, 1] = y
rv = multivariate_normal([0.5, -0.2], [[2.0, 0.3], [0.3, 0.5]])
# plt.contourf(x, y, rv.pdf(pos))
plt.plot(pos[:,1], pos[:,2], 'ro')


plt.clf()
plt.plot([1, 2, 3, 4], [1, 4, 9, 16], 'ro')
plt.axis([0, 6, 0, 20])
plt.show()






import pandas as pd
import numpy as np
#from scipy.cluster.vq import kmeans
#from scipy.stats.stats import pearsonr
#import harmonypy as hm
import os.path

import scanpy as sc

# Concatenate datasets:
# https://github.com/theislab/single-cell-tutorial/blob/master/latest_notebook/Case-study_Mouse-intestinal-epithelium_1906.ipynb

d1 = sc.read_text(
    filename = os.path.expanduser("~/Downloads/GSE81076_D2_3_7_10_17.txt.gz"),
    delimiter = "\t",
    first_column_names = True
).transpose()

d2 = sc.read_text(
    filename = os.path.expanduser("~/Downloads/GSE85241_cellsystems_dataset_4donors_updated.csv.gz"),
    delimiter = "\t",
    first_column_names = True
).transpose()

d3 = pd.read_csv(
    os.path.expanduser("~/Downloads/GSE84133_RAW/GSM2230757_human1_umifm_counts.csv.gz")
)
d3 = d3.drop(columns = ['Unnamed: 0', 'assigned_cluster'])
d3.to_csv(
    os.path.expanduser("~/Downloads/GSE84133_RAW/GSM2230757_human1_umifm_counts_scanpy.csv.gz"),
    index = False,
    header = True
)

d3 = sc.read_text(
    filename = os.path.expanduser("~/Downloads/GSE84133_RAW/GSM2230757_human1_umifm_counts_scanpy.csv.gz"),
    delimiter = ",",
    first_column_names = True
)
d3.obs_names_make_unique()



meta_data = pd.read_csv("../harmonypy_extra_files/data/meta.tsv.gz", sep = "\t")
data_mat = pd.read_csv("../harmonypy_extra_files/data/pcs.tsv.gz", sep = "\t")
data_mat = np.array(data_mat)
vars_use = ['dataset', 'cell_type']

ho = run_harmony(
    data_mat, meta_data, 'dataset', theta = 1, lamb = 0.1, verbose = True,
    max_iter_harmony = 20, max_iter_kmeans = 20
)















import pandas as pd
import numpy as np
#from scipy.cluster.vq import kmeans
from scipy.stats.stats import pearsonr
#import harmonypy as hm

meta_data = pd.read_csv("../harmonypy_extra_files/data/meta.tsv.gz", sep = "\t")
data_mat = pd.read_csv("../harmonypy_extra_files/data/pcs.tsv.gz", sep = "\t")
data_mat = np.array(data_mat)
vars_use = ['dataset', 'cell_type']

ho = run_harmony(data_mat, meta_data, 'dataset', theta = 1, lamb = 0.1, max_iter_harmony = 20, verbose = True)
res = pd.DataFrame(ho.Z_corr).T
res.columns = ['PC{}'.format(i + 1) for i in range(res.shape[1])]
harm = pd.read_csv("../harmonypy_extra_files/data/300_cells_pcs_harmonized_dataset.tsv.gz", sep = "\t").T
harm.columns = ['PC{}'.format(i + 1) for i in range(harm.shape[1])]
cors = []
for i in range(res.shape[1]):
    cors.append(pearsonr(res.iloc[:,i].values, harm.iloc[:,i].values))
print([np.round(x[0], 3) for x in cors])
np.mean(res.to_numpy() - harm.to_numpy())

###

ho = run_harmony(data_mat, meta_data, ['dataset', 'cell_type'], theta = 1, lamb = 0.1)
# ho = run_harmony(data_mat, meta_data, ['dataset', 'cell_type'], theta = [1, 2], lamb = 0.1)
res = pd.DataFrame(ho.Z_corr).T
res.columns = ['PC{}'.format(i + 1) for i in range(res.shape[1])]
harm = pd.read_csv("data/300_cells_pcs_harmonized_dataset_celltype.tsv.gz", sep = "\t").T
cors = []
for i in range(res.shape[1]):
    cors.append(pearsonr(res.iloc[:,i].values, harm.iloc[:,i].values))
print([np.round(x[0], 3) for x in cors])
np.mean(res.to_numpy() - harm.to_numpy())

# ho = hm.run_harmony(data_mat, meta_data, vars_use)

# ho = hm.run_harmony(data_mat, meta_data, ['cell_type'])

## Write the adjusted PCs to a new file.
#res = pd.DataFrame(ho.Z_corr)
#res.columns = ['X{}'.format(i + 1) for i in range(res.shape[1])]
#res.to_csv("data/adj.tsv.gz", sep = "\t", index = False)

# Test 2
########################################################################

# vprof -c p tests/test_harmony.py

import pandas as pd
import numpy as np
from scipy.cluster.vq import kmeans
from scipy.stats.stats import pearsonr
# import harmonypy as hm
from time import time

meta_data = pd.read_csv("data/pbmc_3500_meta.tsv.gz", sep = "\t")
data_mat = pd.read_csv("data/pbmc_3500_pcs.tsv.gz", sep = "\t")

# for compiled in ["with compliation", "after compilation"]:
compiled = ""
start = time()
ho = hm.run_harmony(data_mat, meta_data, ['donor'])
end = time()
print("({}) elapsed {:.2f} seconds".format(compiled, end - start))
    # 24 seconds for python, 5 seconds for Rcpp

res = pd.DataFrame(ho.Z_corr).T
res.columns = ['PC{}'.format(i + 1) for i in range(res.shape[1])]
res.to_csv("data/pbmc_3500_pcs_harmonized_python.tsv.gz", sep = "\t", index = False)

harm = pd.read_csv("data/pbmc_3500_pcs_harmonized.tsv.gz", sep = "\t")

cors = []
for i in range(res.shape[1]):
    cors.append(pearsonr(res.iloc[:,i].values, harm.iloc[:,i].values))
print([np.round(x[0], 3) for x in cors])


############
# 19.86 seconds for 1e4 cells, 31.90 seconds for regular numpy
# 59.59 seconds for 2e4 cells, 60.00 seconds for regular numpy
df = pd.read_csv("~/work/github.com/slowkow/colitis/analysis/pegasus/case_control_pca.tsv.gz", sep = "\t")
pcs = ["PC{}".format(i) for i in range(1, 31)]
n_cells = 20000
data_mat = df.loc[:n_cells,pcs]
meta_data = df.loc[:n_cells,["cell","channel"]]
start = time()
ho = run_harmony(data_mat, meta_data, ['channel'])
end = time()
print("elapsed {:.2f} seconds".format(end - start))


