#cython: language_level=3
#cython: boundscheck=False
#cython: cdivision=True

import numpy as np
import pandas as pd
from sklearn.cluster import dbscan
import joblib, os, eaglec, math, glob
from cooler import ice

def map_coordinates(k_p, res, chrom_1, chrom_2, unit='bp'):
    
    # Coordinates on chrom 1
    if k_p[0] < k_p[1]:
        endbin = k_p[1]//res
        if endbin*res < k_p[1]:
            endbin += 1
        startbin = k_p[0]//res
        pl_1 = endbin - startbin
        if unit=='bp':
            D1 = dict(zip(range(k_p[0],k_p[1],res), range(0,pl_1)))
        else:
            D1 = dict(zip(range(startbin,endbin), range(0,pl_1)))
    else:
        endbin = k_p[0]//res
        if endbin*res < k_p[0]:
            endbin += 1
        startbin = k_p[1]//res
        pl_1 = endbin - startbin
        if unit=='bp':
            D1 = dict(zip(range(k_p[1],k_p[0],res), range(pl_1-1,-1,-1)))
        else:
            D1 = dict(zip(range(startbin,endbin), range(pl_1-1,-1,-1)))
    
    # Coordinates on chrom 2
    if k_p[2] < k_p[3]:
        endbin = k_p[3]//res
        if endbin*res < k_p[3]:
            endbin += 1
        startbin = k_p[2]//res
        pl_2 = endbin - startbin
        if unit=='bp':
            D2 = dict(zip(range(k_p[2],k_p[3],res), range(pl_1,pl_1+pl_2)))
        else:
            D2 = dict(zip(range(startbin,endbin), range(pl_1,pl_1+pl_2)))
    else:
        endbin = k_p[2]//res
        if endbin*res < k_p[2]:
            endbin += 1
        startbin = k_p[3]//res
        pl_2 = endbin - startbin
        if unit=='bp':
            D2 = dict(zip(range(k_p[3],k_p[2],res), range(pl_1+pl_2-1,pl_1-1,-1)))
        else:
            D2 = dict(zip(range(startbin,endbin), range(pl_1+pl_2-1,pl_1-1,-1)))
    
    forward = {} # global coordinates to region bin index
    for k in D1:
        forward[(chrom_1, k)] = D1[k]
    for k in D2:
        forward[(chrom_2, k)] = D2[k]
    
    reverse = {v:k for k,v in forward.items()}
    
    return forward, reverse

def distance_normaize_core(sub, x_arr, y_arr, exp_bychrom):

    D = y_arr - x_arr[:,np.newaxis]
    D = np.abs(D)
    min_dis = D.min()
    max_dis = D.max()
    if max_dis >= exp_bychrom.size:
        return sub
    else: # only normalize for short-range SVs
        exp_sub = np.zeros(sub.shape)
        for d in range(min_dis, max_dis+1):
            xi, yi = np.where(D==d)
            exp_sub[xi, yi] = exp_bychrom[d]
        normed = sub / exp_sub

        return normed

class Fusion(object):

    def __init__(self, clr, c1, c2, p1, p2, probs, window=15, col='sweight'):

        self.clr = clr
        self.p1 = p1
        self.p2 = p2
        self.res = clr.binsize
        pre = find_chrom_pre(list(self.clr.chromnames))
        self.c1 = pre + c1.lstrip('chr')
        self.c2 = pre + c2.lstrip('chr')
        self.chromsize1 = self.clr.chromsizes[self.c1]
        self.chromsize2 = self.clr.chromsizes[self.c2]
        self.balance_type = col
        self.w = window

        strands = ['++', '+-', '-+', '--']
        probs = np.r_[probs]
        self.strands = []
        for i, p in enumerate(probs):
            if p > 0.5:
                self.strands.append(strands[i])
        self.strand = strands[np.argmax(probs)]
        self.s1, self.s2 = self.strand
    
    def get_matrix(self):

        res = self.res
        chromsize1 = self.chromsize1
        chromsize2 = self.chromsize2
        p1 = self.p1 // res
        p2 = self.p2 // res
        r = 2000000//res
        
        # 4 kind of directions
        if (self.s1 == '+') and (self.s2 == '+'):
            minx_1 = max(p1-r, 0)
            if self.c1 != self.c2:
                minx_2 = max(p2 - r, 0)
            else:
                minx_2 = max(p2 - r, p1 + 1)

            k_p = [minx_1 * res, min(p1 * res + res, chromsize1),
                   min(p2 * res + res, chromsize2), minx_2 * res]
            
            # part 3
            M3 = self.clr.matrix(balance=self.balance_type).fetch((self.c1, k_p[0], k_p[1]),
                                                                  (self.c2, k_p[3], k_p[2]))
            M3 = M3[:,::-1]
        elif (self.s1 == '+') and (self.s2 == '-'):
            minx = max(p1 - r, 0)
            maxx = min((p2 + r + 1) * res, chromsize2)
            k_p = [minx * res, min(p1 * res + res, chromsize1),
                   p2 * res, maxx]
            # part 3
            M3 = self.clr.matrix(balance=self.balance_type).fetch((self.c1, k_p[0], k_p[1]),
                                                                  (self.c2, k_p[2], k_p[3]))
        elif (self.s1 == '-') and (self.s2 == '-'):
            if self.c1 != self.c2:
                maxx_1 = min((p1 + r + 1) * res, chromsize1)
            else:
                maxx_1 = min((p1 + r + 1) * res, p2 * res - res)
            maxx_2 = min((p2 + r + 1) * res, chromsize2)
            k_p = [maxx_1, p1 * res, p2 * res, maxx_2]
            
            # part 3
            M3 = self.clr.matrix(balance=self.balance_type).fetch((self.c1, k_p[1], k_p[0]),
                                                                  (self.c2, k_p[2], k_p[3]))
            M3 = M3[::-1,:] # - --> +, + --> -
        else:
            if self.c1 != self.c2:
                maxx = min((p1 + r + 1) * res, chromsize1)
                minx = max(p2 - r, 0)
                k_p = [maxx, p1 * res, min(p2 * res + res, chromsize2), minx * res]
            else:
                maxx_1 = min(p1 + r + 1, p2 - int((p2 - p1) / 2) - 1)
                minx_2 = max(p2 - r, p1 + int((p2 - p1) / 2) + 1)
                k_p = [maxx_1 * res, p1 * res, min(p2 * res + res, chromsize2), minx_2 * res]
            
            # part 3
            M3 = self.clr.matrix(balance=self.balance_type).fetch((self.c1, k_p[1], k_p[0]),
                                                                  (self.c2, k_p[3], k_p[2]))
            M3 = M3[::-1,::-1] # - --> +, - --> +
        
        if self.balance_type:
            M3[np.isnan(M3)] = 0
        
        self.p1L = M3.shape[0]
        self.p2L = M3.shape[1]
        self.fusion_matrix = M3
        self.k_p = k_p
        self.coords_map = map_coordinates(k_p, res, self.c1, self.c2)[1]
    
    def detect_bounds(self):

        from sklearn.decomposition import PCA
        from scipy.ndimage import gaussian_filter

        self.get_matrix()
        n = self.p1L + self.p2L
        junc = self.p1L

        # Detect bounds by using the induced contacts
        up_i = 0
        down_i = n - 1
        up_var_ratio = 0
        down_var_ratio = 0
        # locate the upstream and downstream bound independently
        inter = self.fusion_matrix
        rowmask = inter.sum(axis=1) != 0
        colmask = inter.sum(axis=0) != 0
        if (rowmask.sum() >= 10) and (colmask.sum() >= 10):
            # row, upstream
            new = inter[rowmask][:,colmask]
            corr = gaussian_filter(np.corrcoef(new, rowvar=True), sigma=1)
            try:
                pca = PCA(n_components=3, whiten=True)
                pca1 = pca.fit_transform(corr)[:,0]
                up_var_ratio = pca.explained_variance_ratio_[0]
                loc = self.locate(pca1, left_most=False)
                up_i = np.where(rowmask)[0][loc] # included
            except:
                up_i = 0
                up_var_ratio = 0

            # column, downstream
            corr = gaussian_filter(np.corrcoef(new, rowvar=False), sigma=1)
            try:
                pca = PCA(n_components=3, whiten=True)
                pca1 = pca.fit_transform(corr)[:,0]
                down_var_ratio = pca.explained_variance_ratio_[0]
                loc = self.locate(pca1, left_most=True)
                down_i = np.where(colmask)[0][loc] + junc
            except:
                down_i = n - 1
                down_var_ratio = 0
        
        self.up = self.coords_map[up_i]
        self.down = self.coords_map[down_i]
        self.up_var_ratio = up_var_ratio
        self.down_var_ratio = down_var_ratio

    def candidate_within_SV_block(self):

        self.detect_bounds()
        up = self.up[1]
        down = self.down[1]
        res = self.res
        if self.strand == '++':
            x_arr = np.arange(up//res-1, self.p1//res+1)
            y_arr = np.arange(down//res-1, self.p2//res+1)
        elif self.strand == '+-':
            x_arr = np.arange(up//res-1, self.p1//res+1)
            y_arr = np.arange(self.p2//res-1, down//res+1)
        elif self.strand == '-+':
            x_arr = np.arange(self.p1//res-1, up//res+1)
            y_arr = np.arange(down//res-1, self.p2//res+1)
        else:
            x_arr = np.arange(self.p1//res-1, up//res+1)
            y_arr = np.arange(self.p2//res-1, down//res+1)
        
        return x_arr, y_arr

    
    def extend_stretches(self, arr, min_seed_len=2, max_gap=1, min_stripe_len=5):

        arr.sort()
        pieces = np.split(arr, np.where(np.diff(arr)!=1)[0]+1)
        filtered = [p for p in pieces if len(p) >= min_seed_len] # can't be empty
        stripes = []
        seed = filtered[0]
        for p in filtered[1:]:
            if p[0] - seed[-1] < (max_gap + 2):
                seed = np.r_[seed, p]
            else:
                if seed[-1] - seed[0] + 1 >= min_stripe_len:
                    stripes.append([seed[0], seed[-1]+1])
                seed = p
        
        if seed[-1] - seed[0] + 1 >= min_stripe_len:
            stripes.append([seed[0], seed[-1]+1])
        
        return stripes
    
    def locate(self, pca1, left_most=True):
        
        loci_1 = self.extend_stretches(np.where(pca1>=0)[0])
        loci_2 = self.extend_stretches(np.where(pca1<=0)[0])
        loci = loci_1 + loci_2
        loci.sort()
        if left_most:
            b = loci[0][1] - 1
        else:
            b = loci[-1][0]
        
        return b

def find_chrom_pre(chromlabels):

    ini = chromlabels[0]
    if ini.startswith('chr'):
        return 'chr'
    
    else:
        return ''

def load_gap(clr, ref_genome='hg38', balance='weight'):

    gaps = {}
    if ref_genome in ['hg19', 'hg38', 'chm13']:
        folder = os.path.join(os.path.split(eaglec.__file__)[0], 'data')
        if clr.binsize <= 10000:
            ref_gaps = joblib.load(os.path.join(folder, '{0}.gap-mask.10k.pkl'.format(ref_genome)))
        elif 10000 < clr.binsize <= 50000:
            ref_gaps = joblib.load(os.path.join(folder, '{0}.gap-mask.50k.pkl'.format(ref_genome)))
        else:
            ref_gaps = joblib.load(os.path.join(folder, '{0}.gap-mask.500k.pkl'.format(ref_genome)))

        if not balance:
            valid_bins = get_valid_bins(clr, clr.chromnames)
            
        for c in clr.chromnames:
            chromlabel = 'chr'+c.lstrip('chr')
            if chromlabel in ref_gaps:
                if type(balance) == bool:
                    if not balance:
                        valid_idx = np.where(valid_bins[c])[0]
                    else:
                        weights = clr.bins().fetch(c)['weight'].values
                        valid_idx = np.where(np.isfinite(weights))[0]
                else:
                    weights = clr.bins().fetch(c)[balance].values
                    valid_idx = np.where(np.isfinite(weights))[0]

                gaps[c] = np.zeros(len(clr.bins().fetch(c)), dtype=bool)
                for i in range(len(gaps[c])):
                    if clr.binsize <= 10000:
                        ref_i = i * clr.binsize // 10000
                    elif 10000 < clr.binsize <= 50000:
                        ref_i = i * clr.binsize // 50000
                    else:
                        ref_i = i * clr.binsize // 500000
                    if ref_gaps[chromlabel][ref_i]:
                        gaps[c][i] = True

                gaps[c][valid_idx] = False
            else:
                gaps[c] = np.zeros(len(clr.bins().fetch(c)), dtype=bool)
    else:
        for c in clr.chromnames:
            gaps[c] = np.zeros(len(clr.bins().fetch(c)), dtype=bool)

    return gaps
    

def cluster_SVs(preSVs, r=15000):

    SVs = []
    for sv_type in preSVs:
        by_sv = preSVs[sv_type]
        sort_list = [(by_sv[key]['prob'], key) for key in by_sv]
        sort_list.sort(reverse=True)
        pos = np.r_[[i[1] for i in sort_list]]
        if len(pos) >= 2:
            pool = set()
            _, labels = dbscan(pos, eps=r, min_samples=2)
            for i, p in enumerate(sort_list):
                if p[1] in pool:
                    continue
                c = labels[i]
                if c==-1:
                    pool.add(p[1])
                    SVs.append(by_sv[p[1]]['record'])
                else:
                    SVs.append(by_sv[p[1]]['record'])
                    sub = pos[labels==c]
                    for q in sub:
                        pool.add(tuple(q))
        else:
            for key in by_sv:
                SVs.append(by_sv[key]['record'])
    
    return SVs

def filter_diagonal_calls(SVs, mindis=100000):

    out = []
    for c1, p1, c2, p2, prob1, prob2, prob3, prob4, N_passes in SVs:
        if (c1 == c2) and abs(p2 - p1) < mindis:
            continue
        out.append([c1, p1, c2, p2, prob1, prob2, prob3, prob4, N_passes])
    
    return out

def check_gaps_and_decays(clr, SVs, binsize, balance, ref):

    gaps = load_gap(clr, ref_genome=ref, balance=balance)

    out = []
    for c1, p1, c2, p2, prob1, prob2, prob3, prob4, N_passes in SVs:
        decay = Fusion(clr, c1, c2, p1, p2, [prob1, prob2, prob3, prob4], col=balance)
        b1 = p1 // binsize
        b2 = p2 // binsize

        if decay.strand == '+-':
            gap_x = gaps[c1][(b1+1):(b1+6)].sum()
            gap_y = gaps[c2][(b2-5):b2].sum()
        elif decay.strand == '++':
            gap_x = gaps[c1][(b1+1):(b1+6)].sum()
            gap_y = gaps[c2][(b2+1):(b2+6)].sum()
        elif decay.strand == '-+':
            gap_x = gaps[c1][(b1-5):b1].sum()
            gap_y = gaps[c2][(b2+1):(b2+6)].sum()
        else:
            gap_x = gaps[c1][(b1-5):b1].sum()
            gap_y = gaps[c2][(b2-5):b2].sum()
        
        out.append([c1, p1, c2, p2, '{0},{1}'.format(gap_x, gap_y), prob1, prob2, prob3, prob4, N_passes])
    
    return out

def get_valid_bins(clr, chroms):

    table, _ = get_marginals(clr, exclude=[], nproc=1)
    valid = {}
    for c in chroms:
        tmp = table[table['chrom']==c]['Coverage'].values
        valid[c] = tmp > 0
    
    return valid

def get_marginals(clr, exclude=['M', 'Y', 'MT', 'EBV'], chunksize=int(1e7), nproc=1):

    if nproc > 1:
        pool = ice.Pool(nproc)
        map_ = pool.imap_unordered
    else:
        map_ = map

    nnz = clr.info['nnz']
    n_bins = clr.info['nbins']
    edges = np.arange(0, nnz+chunksize, chunksize)
    spans = list(zip(edges[:-1], edges[1:]))

    marg = (
        ice.split(clr, spans=spans, map=map_, use_lock=False)
            .prepare(ice._init)
            .pipe([])
            .pipe(ice._marginalize)
            .reduce(ice.add, np.zeros(n_bins))
    )
    table = clr.bins()[:][['chrom', 'start', 'end']]
    table['Coverage'] = marg.astype(int)
    pool = []
    chroms = [c for c in clr.chromnames if ((not c.lstrip('chr') in exclude) and (not '_' in c))]
    for chrom in chroms:
        pool.append(table[table['chrom']==chrom])
    
    table = pd.concat(pool)

    return table, clr.binsize

def load_SVs_full(fil, chromlist):

    bychroms = {}
    chrom_order = dict(zip(chromlist, range(len(chromlist))))
    with open(fil, 'r') as source:
        source.readline()
        for line in source:
            c1, p1, c2, p2, prob1, prob2, prob3, prob4 = line.rstrip().split()
            p1, p2 = int(p1), int(p2)
            prob1, prob2, prob3, prob4 = float(prob1), float(prob2), float(prob3), float(prob4)
            if (c1 in chrom_order) and (c2 in chrom_order):
                if chrom_order[c1] > chrom_order[c2]:
                    c1, c2 = c2, c1
                    p1, p2 = p2, p1
                
                if not (c1, c2) in bychroms:
                    bychroms[(c1, c2)] = []
                
                bychroms[(c1, c2)].append((p1, p2, prob1, prob2, prob3, prob4))
    
    return bychroms

def list_intra_cache(cache_folder):

    queue = glob.glob(os.path.join(cache_folder, '*.completed'))
    collect = []
    for f in queue:
        fname = os.path.split(f)[1]
        c1, c2 = fname.split('.')[0].split('_')
        if c1 == c2:
            collect.append(os.path.join(cache_folder, '{0}_{1}.txt'.format(c1, c2)))
    
    return collect

def list_inter_cache(cache_folder):

    queue = glob.glob(os.path.join(cache_folder, '*.completed'))
    collect = []
    for f in queue:
        fname = os.path.split(f)[1]
        c1, c2 = fname.split('.')[0].split('_')
        if c1 != c2:
            collect.append(os.path.join(cache_folder, '{0}_{1}.txt'.format(c1, c2)))
    
    return collect