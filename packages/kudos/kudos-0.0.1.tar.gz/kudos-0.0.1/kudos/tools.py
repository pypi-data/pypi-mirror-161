"""Generic support functions"""
import numpy as np
import pandas as pd
import math


def prop_table(y, pred, axis=0, round=2):
    """Makes a proportions table for a vector of binary predictions."""
    tab = pd.crosstab(y, pred)
    if axis == 1:
        tab = tab.transpose()
        out = tab / np.sum(tab, axis=0)
        out = out.transpose()
    else:
        out = tab / np.sum(tab, axis=0)
    if round is not None:
        out = np.round(out, round)
    return out


def onehot_matrix(y, sparse=False):
    """Converts a 1-D vector of class guesses to a one-hot matrix."""
    if not sparse:
        y_mat = np.zeros((y.shape[0], len(np.unique(y))))
        for row, col in enumerate(y):
            y_mat[row, col] = 1
    return y_mat


def max_probs(arr, maxes=None, axis=1):
    if maxes is None:
        maxes = np.argmax(arr, axis=axis)
    out = [arr[i, maxes[i]] for i in range(arr.shape[0])]
    return np.array(out)


def smash_log(x, B=10, d=0):
    """Logistic function with a little extra kick."""
    return 1 / (1 + np.exp(-x * B)) - d


def sparsify(col, 
             reshape=True, 
             return_df=True,
             long_names=False):
    """Makes a sparse array out of data frame of discrete variables."""
    levels = np.unique(col)
    out = np.array([col == level for level in levels],
                   dtype=np.uint8).transpose()
    if long_names:
        var = col.name + '.'
        levels = [var + level for level in levels]
    columns = [col.lower() for col in levels]
    if return_df:
        out = pd.DataFrame(out, columns=columns)
    return out


def row_sums(c, min=1):
    sums = np.sum(c, axis=1)
    return np.array(sums >= min, dtype=np.uint8)


def pair_sum(X, c, min=(1, 1)):
    a = row_sums(X[:, c[0]], min=min[0])
    b = row_sums(X[:, c[1]], min=min[1])
    return (a, b)


def combo_sum(ctup):
    sums = np.sum(ctup, axis=0)
    and_y = np.array(sums == 2, dtype=np.uint8)
    or_y = np.array(sums >= 1, dtype=np.uint8)
    out = np.concatenate([and_y.reshape(-1, 1),
                          or_y.reshape(-1, 1)],
                         axis=1)
    return out


def flatten(l):
    '''Flattens a list.'''
    return [item for sublist in l for item in sublist]


def unique_combo(c):
    """Determines if a combination of symptoms is unique."""
    if len(np.intersect1d(c[0], c[1])) == 0:
        return c
    else:
        return None


def pair_info(pair, link, col_list):
    """Turns lists of column strings and a prefix into a compound rule."""
    pair_cols = pair[1]
    pair_m = pair[2]
    m1 = pair_m[0]
    m2 = pair_m[1]
    n1 = len(pair_cols[0])
    n2 = len(pair_cols[1])
    
    # Making the string specifying the condition
    cnames = []
    for cols in pair_cols:
        cnames.append(' '.join([str(col_list[c]) 
                                     for c in cols]))
    out = [
        m1, cnames[0], link,
        m2, cnames[1], n1, n2
    ]
    return out


def zm_to_y(z, m, X):
    """Converts a variable choice vector, minimum count, and variables 
    to a binary guess vector.
    """
    return np.array(np.dot(X, z) >= m, dtype=np.uint8)


def zm_to_rule(z, m, cols, rule_num=1, return_df=True):
    """Converts a choice vector and minimum count to a rule string."""
    var_names = [cols[i] for i in np.where(z == 1)[0]]
    n = len(var_names)
    rule = ' '.join(var_names)
    m_col = 'm' + str(rule_num)
    n_col = 'n' + str(rule_num)
    rule_col = 'rule' + str(rule_num)
    if return_df:
        out = pd.DataFrame([m, rule, n]).transpose()
        out.columns = [m_col, rule_col, n_col]
    else:
        out = m, rule, n
    return out


def split_rule(rule, var_names):
    """Splits a single-string compound rule into two sub-rules."""
    link_dict = {'and': 1, 'or': 0}
    link_id = np.where([x not in var_names for x in rule])[0][0]
    link_val = link_dict[rule[link_id]]
    return rule[:link_id], rule[link_id + 1:], link_val
    

def rule_to_y(X, rule_df):
    """Converts a rule from DataFrame results format to a vector of guesses."""
    if rule_df.shape[0] > 1:
        rule_df = rule_df.to_frame().transpose()
    
    link_dict = {'and': 1, 'or': 0}
    cols1 = list(rule_df.rule1.values)[0].split()
    y1 = np.array(X[cols1].sum(1) >= rule_df.m1.values[0],
                  dtype=np.uint8)
    if ('n2' in rule_df.columns.values) and (rule_df.n2.values != 0):
        link_val = link_dict[rule_df.link.values[0]]
        cols2 = list(rule_df.rule2.values)[0].split()
        y2 = np.array(X[cols2].sum(1) >= rule_df.m2.values[0],
                      dtype=np.uint8)
        return np.array(y1 + y2 > link_val,
                        dtype=np.uint8)  
    else:
        return y1


def rule_to_str(rule_df, n):
    n_str = str(n)
    m = rule_df['m' + n_str].values[0]
    n = rule_df['n' + n_str].values[0]
    rule = rule_df['rule' + n_str].values[0]
    return 'At least ' + str(m) + ' of (' + rule + ')'


def rule_df_to_str(rule_df):
    out = rule_to_str(rule_df, 1)
    if 'n2' in rule_df.columns.values:
        if rule_df.n2 != 0:
            out += ' ' + rule_df.link + ' At least ' + rule_to_str(rule_df, 2)
    return out


def tab_to_vecs(tp, tn, fp, fn):
    tp = np.array([[1, 1]] * tp)
    tn = np.array([[0, 0]] * tn)
    fn = np.array([[1, 0]] * fn)
    fp = np.array([[0, 1]] * fp)
    good = [a for a in [tp, tn, fn, fp] if a.shape[0] != 0]
    return np.concatenate(good)
