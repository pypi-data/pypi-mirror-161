import pdb
import time
import numpy as np
import copy

from .util_ import print_log, compute_zeta
from .util_ import Param

from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix

import multiprocess as mp
import itertools

# Computes bid[k,:], min(bid[k,:]), c[neigh_ind_k[argmin(bid[k,:])]]
def bid_for_point(k, d_e, neigh_ind_k, U_k, local_param, c, n_C,
                   Utilde, eta_min, eta_max):
    c_k = c[k]
    # Compute |C_{c_k}|
    n_C_c_k = n_C[c_k]
    
    c_U_k = c[neigh_ind_k]
    
    
    # Check if |C_{c_k}| < eta_{min}
    # If not then c_k is already
    # an intermediate cluster
    if n_C_c_k >= eta_min:
        return np.zeros(c_U_k.shape)-1, -1, -1
    
    n = c.shape[0]
    bid_by_cluster = np.zeros(n)-1
    # Initializations
    n = n_C.shape[0]
    
    # Compute neighboring clusters c_{U_k} of x_k
    c_U_k_uniq = np.unique(c_U_k).tolist()
    
    # Iterate over all m in c_{U_k}
    for m in c_U_k_uniq:
        if m == c_k:
            continue
            
        # Compute |C_{m}|
        n_C_m = n_C[m]
        # Check if |C_{m}| < eta_{max}. If not
        # then mth cluster has reached the max
        # allowed size of the cluster. Move on.
        if n_C_m >= eta_max:
            continue
        
        # Check if |C_{m}| >= |C_{c_k}|. If yes, then
        # mth cluster satisfies all required conditions
        # and is a candidate cluster to move x_k in.
        if n_C_m >= n_C_c_k:
            # Compute union of Utilde_m U_k
            U_k_U_Utilde_m = list(U_k.union(Utilde[m]))
            # Compute the bid by cluster m for x_k,
            # that is cost_{x_k \rightarrow m}
            bid_by_cluster[m] = 1/compute_zeta(d_e[np.ix_(U_k_U_Utilde_m,U_k_U_Utilde_m)],
                                               local_param.eval_({'view_index': m,
                                                                  'data_mask': U_k_U_Utilde_m}))
        
    
    # find the cluster with minimum bid
    # to move x_k in.
    max_bid_cluster = c_U_k_uniq[np.argmax(bid_by_cluster[c_U_k_uniq])]
    max_bid = bid_by_cluster[max_bid_cluster]
    if max_bid == -1:
        max_bid_cluster = -1
        
    return bid_by_cluster[c_U_k], max_bid, max_bid_cluster



class IntermedViews:
    def __init__(self, exit_at, verbose=True, debug=False):
        self.exit_at = exit_at
        self.verbose = verbose
        self.debug = debug
        
        self.c = None
        self.C = None
        self.n_C = None
        self.Utilde = None
        self.intermed_param = None
        
        self.local_start_time = time.time()
        self.global_start_time = time.time()
    
    def log(self, s='', log_time=False):
        if self.verbose:
            self.local_start_time = print_log(s, log_time,
                                              self.local_start_time, 
                                              self.global_start_time)
    
    def fit(self, d, d_e, U, neigh_ind, local_param, intermed_opts):
        n = d_e.shape[0]
        c = np.arange(n)
        n_C = np.zeros(n) + 1
        Clstr = list(map(set, np.arange(n).reshape((n,1)).tolist()))
        Utilde = []
        U_ = []
        for k in range(n):
            neigh_ind_k = set(neigh_ind[k,:])
            Utilde.append(neigh_ind_k)
            U_.append(neigh_ind_k)
            
        eta_max = intermed_opts['eta_max']
        n_proc = intermed_opts['n_proc']
        k_nn = neigh_ind.shape[1]
        
        # Compute bids by clusters for points
        bid = np.zeros(neigh_ind.shape) -1
        max_bid = np.zeros(n) -1
        max_bid_cluster = np.zeros(n, dtype='int') -1
        
        # Vary eta from 2 to eta_{min}
        self.log('Constructing intermediate views.')
        for eta in range(2,intermed_opts['eta_min']+1):
            self.log('eta = %d.' % eta)
            self.log('# non-empty views with sz < %d = %d' % (eta, np.sum((n_C > 0)*(n_C < eta))))
            self.log('#nodes in views with sz < %d = %d' % (eta, np.sum(n_C[c]<eta)))
            
            ###########################################
            # Proc for computing the cost and dest
            def target_proc(p_num, chunk_sz, q_, n_, S):
                start_ind = p_num*chunk_sz
                if p_num == (n_proc-1):
                    end_ind = n_
                else:
                    end_ind = (p_num+1)*chunk_sz
                n_ind = end_ind-start_ind
                bid0 = np.zeros((n_ind, k_nn))-1
                max_bid0 = np.zeros(n_ind)-1
                max_bid_cluster0 = np.zeros(n_ind, dtype='int')-1
                for k in range(start_ind, end_ind):
                    k0 = k-start_ind
                    k1 = k
                    # if S is None:
                    #     k1 = k
                    # else:
                    #     k1 = S[k]
                    bid_, max_bid_, max_bid_cluster_ = bid_for_point(k1, d_e, neigh_ind[k1,:], U_[k1],
                                                                     local_param, c, n_C,
                                                                     Utilde, eta, eta_max)
                    bid0[k0,:] = bid_
                    max_bid0[k0] = max_bid_
                    max_bid_cluster0[k0] = max_bid_cluster_
                    
                q_.put((start_ind, end_ind, bid0, max_bid0, max_bid_cluster0))
            
            ###########################################
            # Parallel cost and dest computation
            q_ = mp.Queue()
            proc = []
            for p_num in range(n_proc):
                proc.append(mp.Process(target=target_proc,
                                       args=(p_num,int(n/n_proc),q_,n,None),
                                       daemon=True))
                proc[-1].start()
            
            for p_num in range(n_proc):
                start_ind, end_ind, bid_, max_bid_, max_bid_cluster_ = q_.get()
                bid[start_ind:end_ind,:] = bid_
                max_bid[start_ind:end_ind] = max_bid_
                max_bid_cluster[start_ind:end_ind] = max_bid_cluster_
                
            q_.close()
                
            for p_num in range(n_proc):
                proc[p_num].join()
            ###########################################
            
            # Sequential version of above
            # for k in range(n):
            #     bid_, max_bid_, max_bid_cluster_ = bid_for_point(k, d_e, neigh_ind[k,:], U_[k],
            #                                                      local_param, c, n_C,
            #                                                      Utilde, eta, eta_max)
            #     bid[k,:] = bid_
            #     max_bid[k] = max_bid_
            #     max_bid_cluster[k] = max_bid_cluster_
            
            # Compute point with minimum cost
            # Compute k and cost^* 
            k = np.argmax(max_bid)
            bid_star = max_bid[k]
            
            self.log('eta = %d, Bids computed.' % eta, log_time=True)
            
            # Loop until minimum cost is inf
            while bid_star > 0:
                # Move x_k from cluster s to
                # max_bid_cluster[k] and update variables
                s = c[k]
                m = max_bid_cluster[k]
                c[k] = m
                n_C[s] -= 1
                n_C[m] += 1
                Clstr[s].remove(k)
                Clstr[m].add(k)
                Utilde[m] = U_[k].union(Utilde[m])
                Utilde[s] = set(neigh_ind[list(Clstr[s]),:].flatten())
                
                # Compute the set of points S for which 
                # bids are to be recomputed
                #S = list(Clstr[m].union(Clstr[s]))
                #S = set(np.where(U[:,S].sum(1))[0]).union(S)
                S = np.where((c==m) | (max_bid_cluster==m) | np.any(U[:,list(Clstr[s])].toarray(),1))[0].tolist()
                len_S = len(S)
                #print(len_S)
                for k in S:
                    bid_, max_bid_, max_bid_cluster_ = bid_for_point(k, d_e, neigh_ind[k,:], U_[k],
                                                                     local_param, c, n_C,
                                                                     Utilde, eta, eta_max)
                    bid[k,:] = bid_
                    max_bid[k] = max_bid_
                    max_bid_cluster[k] = max_bid_cluster_
                
                k = np.argmax(max_bid)
                bid_star = max_bid[k]
            print('Remaining #nodes in views with sz < %d = %d' % (eta, np.sum(n_C[c]<eta)))
            self.log('Done with eta = %d.' % eta, log_time=True)
        
        self.log('Pruning and cleaning up.')
        del U_
        del Clstr
        del Utilde
        del bid
        del max_bid
        del max_bid_cluster
        
        # Prune empty clusters
        non_empty_C = n_C > 0
        M = np.sum(non_empty_C)
        old_to_new_map = np.arange(n)
        old_to_new_map[non_empty_C] = np.arange(M)
        c = old_to_new_map[c]
        n_C = n_C[non_empty_C]
        
        # Construct a boolean array C s.t. C[m,i] = 1 if c_i == m, 0 otherwise
        C = csr_matrix((np.ones(n), (c, np.arange(n))),
                       shape=(M,n), dtype=bool)
        
        # Compute intermediate views
        intermed_param = copy.deepcopy(local_param)
        if intermed_opts['algo'] == 'LDLE':
            intermed_param.Psi_i = local_param.Psi_i[non_empty_C,:]
            intermed_param.Psi_gamma = local_param.Psi_gamma[non_empty_C,:]
            intermed_param.b = intermed_param.b[non_empty_C]
        elif intermed_opts['algo'] == 'LTSA':
            intermed_param.Psi = local_param.Psi[non_empty_C,:]
            intermed_param.mu = local_param.mu[non_empty_C,:]
            intermed_param.b = intermed_param.b[non_empty_C]
        
        # Compute Utilde_m
        Utilde = C.dot(U)
        
        intermed_param.zeta = np.ones(M);
        for m in range(M):
            Utilde_m = Utilde[m,:].indices
            d_e_Utilde_m = d_e[np.ix_(Utilde_m,Utilde_m)]
            intermed_param.zeta[m] = compute_zeta(d_e_Utilde_m,
                                                  intermed_param.eval_({'view_index': m,
                                                                        'data_mask': Utilde_m}))

        self.log('Done.', log_time=True)
        print("After clustering, max distortion is %f" % (np.max(intermed_param.zeta)))
        self.C = C
        self.c = c
        self.n_C = n_C
        self.Utilde = Utilde
        self.intermed_param = intermed_param