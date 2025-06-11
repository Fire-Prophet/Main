import numpy as np
from scipy.stats import ks_2samp

def detect_drift(ref_data, new_data):
    drift_stats = {}
    for col in ref_data.columns:
        stat, pval = ks_2samp(ref_data[col], new_data[col])
        drift_stats[col] = {'p-value': pval, 'drift': pval < 0.05}
    return drift_stats
