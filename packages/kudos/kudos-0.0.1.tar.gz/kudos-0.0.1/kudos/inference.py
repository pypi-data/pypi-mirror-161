import pandas as pd
import numpy as np
import os

from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score, average_precision_score
from scipy.stats import binom, chi2, norm, percentileofscore
from multiprocessing import Pool
from copy import deepcopy

from .tools import *
from .metrics import *


def threshold(probs, cutoff=.5):
    return np.array(probs >= cutoff).astype(np.uint8)


def mcnemar_test(true, pred, cc=True):
    cm = confusion_matrix(true, pred)
    b = int(cm[0, 1])
    c = int(cm[1, 0])
    if cc:
        stat = (abs(b - c) - 1)**2 / (b + c)
    else:
        stat = (b - c)**2 / (b + c)
    p = 1 - chi2(df=1).cdf(stat)
    outmat = np.array([b, c, stat, p]).reshape(-1, 1)
    out = pd.DataFrame(outmat.transpose(),
                       columns=['b', 'c', 'stat', 'pval'])
    return out


def jackknife_metrics(targets, 
                      guesses, 
                      average='weighted'):
    # Replicates of the dataset with one row missing from each
    rows = np.array(list(range(targets.shape[0])))
    j_rows = [np.delete(rows, row) for row in rows]

    # using a pool to get the metrics across each
    scores = [clf_metrics(targets[idx],
                          guesses[idx],
                          average=average) for idx in j_rows]
    scores = pd.concat(scores, axis=0)
    means = scores.mean()
    
    return scores, means


def invert_BCA(q, b, acc, lower=True):
    if np.isnan(q):
        return q
    if np.any(q >= 1):
        q /= 100
    z = norm.ppf(q)
    numer = z - 2*b - z*b*acc - b**2*acc
    denom = 1 + b*acc + z*acc
    if lower:
        return 2 * norm.cdf(numer / denom)
    else:
        return 2 * (1 - norm.cdf(numer / denom))


def BCA_pval(bca, null=0.0):
    scores = bca.scores
    n_cols = bca.scores.shape[1]
    
    # Making the vector of null values
    if type(null) == type(0.0):
        null = np.array([null] * n_cols)
    
    # Figuring out which nulls exist in the bootstrap data
    good_nulls = []
    for i in range(n_cols):
        col = scores.iloc[:, i]
        good_nulls.append(col.min() <= null[i] <= col.max())
    
    # Getting the percentile for each null
    null_qs = np.array([percentileofscore(bca.scores.iloc[:, i], null[i]) 
               if good_nulls[i] else np.nan for i in range(n_cols)]) / 100
    
    # Figuring out whether to look at the lower or upper quantile
    lower = [q <= .5 if not np.isnan(q) else q for q in null_qs]
    
    # Getting the p-value associated with each null percentile
    pvals = np.array([invert_BCA(null_qs[i],
                                 bca.b[i],
                                 bca.acc[i],
                                 lower=lower[i])
                      for i in range(n_cols)])
    
    return pvals, good_nulls, null_qs, lower


def boot_stat_cis(stat,
                  jacks,
                  boots,
                  a=0.05,
                  exp=False,
                  method="bca",
                  interpolation="nearest",
                  transpose=True,
                  outcome_axis=1,
                  stat_axis=2):
    # Renaming because I'm lazy
    j = jacks
    n = len(boots)
    
    # Calculating the confidence intervals
    lower = (a / 2) * 100
    upper = 100 - lower

    # Making sure a valid method was chosen
    methods = ["pct", "diff", "bca"]
    assert method in methods, "Method must be pct, diff, or bca."

    # Calculating the CIs with method #1: the percentiles of the
    # bootstrapped statistics
    if method == "pct":
        cis = np.nanpercentile(boots,
                               q=(lower, upper),
                               interpolation=interpolation,
                               axis=0)
        cis = pd.DataFrame(cis.transpose(),
                           columns=["lower", "upper"],
                           index=colnames)

    # Or with method #2: the percentiles of the difference between the
    # obesrved statistics and the bootstrapped statistics
    elif method == "diff":
        diffs = stat - boots
        percents = np.nanpercentile(diffs,
                                    q=(lower, upper),
                                    interpolation=interpolation,
                                    axis=0)
        lower_bound = pd.Series(stat_vals + percents[0])
        upper_bound = pd.Series(stat_vals + percents[1])
        cis = pd.concat([lower_bound, upper_bound], axis=1)
        cis = cis.set_index(stat.index)

    # Or with method #3: the bias-corrected and accelerated bootstrap
    elif method == "bca":
        # Calculating the bias-correction factor
        n_less = np.sum(boots < stat, axis=0)
        p_less = n_less / n
        z0 = norm.ppf(p_less)

        # Fixing infs in z0
        z0[np.where(np.isinf(z0))[0]] = 0.0

        # Estiamating the acceleration factor
        diffs = j[1] - j[0]
        numer = np.sum(np.power(diffs, 3))
        denom = 6 * np.power(np.sum(np.power(diffs, 2)), 3/2)

        # Getting rid of 0s in the denominator
        zeros = np.where(denom == 0)[0]
        for z in zeros:
            denom[z] += 1e-6

        # Finishing up the acceleration parameter
        acc = numer / denom

        # Calculating the bounds for the confidence intervals
        zl = norm.ppf(a / 2)
        zu = norm.ppf(1 - (a / 2))
        lterm = (z0 + zl) / (1 - acc * (z0 + zl))
        uterm = (z0 + zu) / (1 - acc * (z0 + zu))
        ql = norm.cdf(z0 + lterm) * 100
        qu = norm.cdf(z0 + uterm) * 100

        # Returning the CIs based on the adjusted quantiles;
        # I know this code is hideous
        if len(boots.shape) > 2:
            n_outcomes = range(boots.shape[outcome_axis])
            n_vars = range(boots.shape[stat_axis])
            cis = np.array([
                [np.nanpercentile(boots[:, i, j],
                                  q =(ql[i][j], 
                                      qu[i][j]),
                                  axis=0) 
                                  for i in n_outcomes]
                for j in n_vars
            ])
        else:
            n_stats = range(len(ql))
            cis = np.array([
                np.nanpercentile(boots[:, i],
                                 q=(ql[i], qu[i]),
                                 interpolation=interpolation,
                                 axis=0) 
                for i in n_stats])
        
        # Optional exponentiation for log-link models
        if exp:
            cis = np.exp(cis)
        
        # Optional transposition
        if transpose:
            cis = cis.transpose()

    return cis


# Calculates bootstrap confidence intervals for an estimator
class boot_cis:
    def __init__(
        self,
        targets,
        guesses,
        n=100,
        a=0.05,
        group=None,
        method="bca",
        interpolation="nearest",
        average='weighted',
        mcnemar=False,
        seed=10221983,
        undef_val=0):
        # Converting everything to NumPy arrays, just in case
        stype = type(pd.Series([0]))
        if type(targets) == stype:
            targets = targets.values
        if type(guesses) == stype:
            guesses = guesses.values

        # Getting the point estimates
        stat = clf_metrics(targets,
                           guesses,
                           average=average,
                           mcnemar=mcnemar,
                           undef_val=undef_val).transpose()

        # Pulling out the column names to pass to the bootstrap dataframes
        colnames = list(stat.index.values)

        # Making an empty holder for the output
        scores = pd.DataFrame(np.zeros(shape=(n, stat.shape[0])),
                              columns=colnames)

        # Setting the seed
        if seed is None:
            seed = np.random.randint(0, 1e6, 1)
        np.random.seed(seed)
        seeds = np.random.randint(0, 1e6, n)

        # Generating the bootstrap samples and metrics
        boots = [boot_sample(targets, 
                             by=group, 
                             seed=seed) for seed in seeds]
        scores = [clf_metrics(targets[b], 
                              guesses[b], 
                              average=average,
                              undef_val=undef_val) for b in boots]
        scores = pd.concat(scores, axis=0)
        self.scores = scores

        # Calculating the confidence intervals
        lower = (a / 2) * 100
        upper = 100 - lower

        # Making sure a valid method was chosen
        methods = ["pct", "diff", "bca"]
        assert method in methods, "Method must be pct, diff, or bca."

        # Calculating the CIs with method #1: the percentiles of the
        # bootstrapped statistics
        if method == "pct":
            cis = np.nanpercentile(scores,
                                   q=(lower, upper),
                                   interpolation=interpolation,
                                   axis=0)
            cis = pd.DataFrame(cis.transpose(),
                               columns=["lower", "upper"],
                               index=colnames)

        # Or with method #2: the percentiles of the difference between the
        # obesrved statistics and the bootstrapped statistics
        elif method == "diff":
            stat_vals = stat.transpose().values.ravel()
            diffs = stat_vals - scores
            percents = np.nanpercentile(diffs,
                                        q=(lower, upper),
                                        interpolation=interpolation,
                                        axis=0)
            lower_bound = pd.Series(stat_vals + percents[0])
            upper_bound = pd.Series(stat_vals + percents[1])
            cis = pd.concat([lower_bound, upper_bound], axis=1)
            cis = cis.set_index(stat.index)

        # Or with method #3: the bias-corrected and accelerated bootstrap
        elif method == "bca":
            # Calculating the bias-correction factor
            stat_vals = stat.transpose().values.ravel()
            n_less = np.sum(scores < stat_vals, axis=0)
            p_less = n_less / n
            z0 = norm.ppf(p_less)

            # Fixing infs in z0
            z0[np.where(np.isinf(z0))[0]] = 0.0

            # Estiamating the acceleration factor
            j = jackknife_metrics(targets, guesses)
            diffs = j[1] - j[0]
            numer = np.sum(np.power(diffs, 3))
            denom = 6 * np.power(np.sum(np.power(diffs, 2)), 3 / 2)

            # Getting rid of 0s in the denominator
            zeros = np.where(denom == 0)[0]
            for z in zeros:
                denom[z] += 1e-6

            # Finishing up the acceleration parameter
            acc = numer / denom
            self.jack = j

            # Calculating the bounds for the confidence intervals
            zl = norm.ppf(a / 2)
            zu = norm.ppf(1 - (a / 2))
            lterm = (z0 + zl) / (1 - acc * (z0 + zl))
            uterm = (z0 + zu) / (1 - acc * (z0 + zu))
            ql = norm.cdf(z0 + lterm) * 100
            qu = norm.cdf(z0 + uterm) * 100
            
            # Passing things back to the class
            self.acc = acc.values
            self.b = z0
            self.ql = ql
            self.qu = qu

            # Returning the CIs based on the adjusted quintiles
            cis = [
                np.nanpercentile(
                    scores.iloc[:, i],
                    q=(ql[i], qu[i]),
                    interpolation=interpolation,
                    axis=0,
                ) for i in range(len(ql))
            ]
            cis = pd.DataFrame(cis, 
                               columns=["lower", "upper"], 
                               index=colnames)

        # Putting the stats with the lower and upper estimates
        cis = pd.concat([stat, cis], axis=1)
        cis.columns = ["stat", "lower", "upper"]

        # Passing the results back up to the class
        self.cis = cis
        self.scores = scores

        return


def average_pvals(p_vals, 
                  w=None, 
                  method='harmonic',
                  smooth=True,
                  smooth_val=1e-7):
    if smooth:
        p = p_vals + smooth_val
    else:
        p = deepcopy(p_vals)
    if method == 'harmonic':
        if w is None:
            w = np.repeat(1 / len(p), len(p))
        p_avg = 1 / np.sum(w / p)
    elif method == 'fisher':
        stat = -2 * np.sum(np.log(p))
        p_avg = 1 - chi2(df=1).cdf(stat)
    return p_avg


def jackknife_sample(X):
    rows = np.array(list(range(X.shape[0])))
    j_rows = [np.delete(rows, row) for row in rows]
    return j_rows


def boot_sample(df,
                by=None,
                size=None,
                seed=None,
                return_df=False):
    
    # Setting the random states for the samples
    if seed is None:
        seed = np.random.randint(1, 1e6, 1)[0]
    np.random.seed(seed)
    
    # Getting the sample size
    if size is None:
        size = df.shape[0]
    
    # Sampling across groups, if group is unspecified
    if by is None:
        np.random.seed(seed)
        idx = range(size)
        boot = np.random.choice(idx,
                                size=size,
                                replace=True)
    
    # Sampling by group, if group has been specified
    else:
        levels = np.unique(by)
        n_levels = len(levels)
        level_ids = [np.where(by == level)[0]
                     for level in levels]
        boot = [np.random.choice(ids, size=len(ids), replace=True)
                for ids in level_ids]
        boot = np.concatenate(boot).ravel()
    
    if not return_df:
        return boot
    else:
        return df.iloc[boot, :]
    

class diff_boot_cis:
    def __init__(self,
                 ref,
                 comp,
                 a=0.05,
                 abs_diff=False,
                 method='bca',
                 interpolation='nearest'):
        # Quick check for a valid estimation method
        methods = ['pct', 'diff', 'bca']
        assert method in methods, 'Method must be pct, diff, or bca.'
        
        # Pulling out the original estiamtes
        ref_stat = pd.Series(ref.cis.stat.drop('true_prev').values)
        ref_scores = ref.scores.drop('true_prev', axis=1)
        comp_stat = pd.Series(comp.cis.stat.drop('true_prev').values)
        comp_scores = comp.scores.drop('true_prev', axis=1)
        
        # Optionally Reversing the order of comparison
        diff_scores = comp_scores - ref_scores
        diff_stat = comp_stat - ref_stat
            
        # Setting the quantiles to retrieve
        lower = (a / 2) * 100
        upper = 100 - lower
        
        # Calculating the percentiles 
        if method == 'pct':
            cis = np.nanpercentile(diff_scores,
                                   q=(lower, upper),
                                   interpolation=interpolation,
                                   axis=0)
            cis = pd.DataFrame(cis.transpose())
        
        elif method == 'diff':
            diffs = diff_stat.values.reshape(1, -1) - diff_scores
            percents = np.nanpercentile(diffs,
                                        q=(lower, upper),
                                        interpolation=interpolation,
                                        axis=0)
            lower_bound = pd.Series(diff_stat + percents[0])
            upper_bound = pd.Series(diff_stat + percents[1])
            cis = pd.concat([lower_bound, upper_bound], axis=1)
        
        elif method == 'bca':
            # Removing true prevalence from consideration to avoid NaNs
            ref_j_means = ref.jack[1].drop('true_prev')
            ref_j_scores = ref.jack[0].drop('true_prev', axis=1)
            comp_j_means = comp.jack[1].drop('true_prev')
            comp_j_scores = comp.jack[0].drop('true_prev', axis=1)
            
            # Calculating the bias-correction factor
            n = ref.scores.shape[0]
            stat_vals = diff_stat.transpose().values.ravel()
            n_less = np.sum(diff_scores < stat_vals, axis=0)
            p_less = n_less / n
            z0 = norm.ppf(p_less)
            
            # Fixing infs in z0
            z0[np.where(np.isinf(z0))[0]] = 0.0
            
            # Estiamating the acceleration factor
            j_means = comp_j_means - ref_j_means
            j_scores = comp_j_scores - ref_j_scores
            diffs = j_means - j_scores
            numer = np.sum(np.power(diffs, 3))
            denom = 6 * np.power(np.sum(np.power(diffs, 2)), 3/2)
            
            # Getting rid of 0s in the denominator
            zeros = np.where(denom == 0)[0]
            for z in zeros:
                denom[z] += 1e-6
            
            acc = numer / denom
            
            # Calculating the bounds for the confidence intervals
            zl = norm.ppf(a / 2)
            zu = norm.ppf(1 - (a/2))
            lterm = (z0 + zl) / (1 - acc*(z0 + zl))
            uterm = (z0 + zu) / (1 - acc*(z0 + zu))
            ql = norm.cdf(z0 + lterm) * 100
            qu = norm.cdf(z0 + uterm) * 100
                                    
            # Returning the CIs based on the adjusted quantiles
            cis = [np.nanpercentile(diff_scores.iloc[:, i], 
                                    q=(ql[i], qu[i]),
                                    interpolation=interpolation,
                                    axis=0) 
                   for i in range(len(ql))]
            cis = pd.DataFrame(cis, columns=['lower', 'upper'])
                    
        cis = pd.concat([ref_stat, comp_stat, diff_stat, cis], 
                        axis=1)
        cis = cis.set_index(ref_scores.columns.values)
        cis.columns = ['ref', 'comp', 'd', 
                       'lower', 'upper']
        
        # Passing stuff back up to return
        self.cis = cis
        self.scores = diff_scores
        self.b = z0
        self.acc = acc
        
        return


def grid_metrics(targets,
                 guesses,
                 step=.01,
                 min=0.0,
                 max=1.0,
                 by='f1',
                 average='binary',
                 counts=True):
    cutoffs = np.arange(min, max, step)
    if len((guesses.shape)) == 2:
        if guesses.shape[1] == 1:
            guesses = guesses.flatten()
        else:
            guesses = guesses[:, 1]
    if average == 'binary':
        scores = []
        for i, cutoff in enumerate(cutoffs):
            threshed = threshold(guesses, cutoff)
            stats = clf_metrics(targets, threshed)
            stats['cutoff'] = pd.Series(cutoff)
            scores.append(stats)
    
    return pd.concat(scores, axis=0)


def merge_cis(c, round=4, mod_name=''):
    str_cis = c.round(round).astype(str)
    str_paste = pd.DataFrame(str_cis.stat + ' (' + str_cis.lower + 
                                 ', ' + str_cis.upper + ')',
                                 columns=[mod_name]).transpose()
    return str_paste


def merge_ci_list(l, mod_names=None, round=4):
    if type(l[0] != type(pd.DataFrame())):
        l = [c.cis for c in l]
    if mod_names is not None:
        merged_cis = [merge_cis(l[i], round, mod_names[i])
                      for i in range(len(l))]
    else:
        merged_cis = [merge_cis(c, round=round) for c in l]
    
    return pd.concat(merged_cis, axis=0)

