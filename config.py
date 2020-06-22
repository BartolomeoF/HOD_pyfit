from numpy import linspace,logspace

#====================================================
# Global variables definitions
#====================================================

# Columns in the Rockstar halo catalogue
NAMES_STRING = "id num_p m200c mbound_200c r200c vmax rvmax vrms x y z vx vy vz Jx Jy Jz E Spin PosUncertainty VelUncertainty bulk_vx bulk_vy bulk_vz BulkVelUnc n_core m200b m200c_bis m500c m2500c Xoff Voff spin_bullock b_to_a c_to_a A[x] A[y] A[z] b_to_a(500c) c_to_a(500c) A[x](500c) A[y](500c) A[z](500c) Rs Rs_Klypin T/|U| M_pe_Behroozi M_pe_Diemer idx i_so i_ph num_cp mmetric" # Halfmass_Radius add for Hans paired sims
NAMES = NAMES_STRING.split(' ')

# Columns to keep
USE_COLS = ['id', 'x', 'y', 'z', 'vx', 'vy','vz', 'vrms', 'r200c', 'm200c', 'Rs']

# Default parameters for HOD
PARAM_DICT = { 'logMmin': 13.09,
               'sigma_logM': 0.596,
               'logM0': 13.077,
               'logM1': 14.00,
               'alpha': 1.0127      }

# Parameters of the catalogue
REDSHIFT = 0
BOXSIZE = 1024

# Paramters for the fit
MIN_PARAM_DICT = {'logMmin': 12.0,
               	'sigma_logM': 0.5,
               	'logM0': 11.0,
               	'logM1': 13.0,
               	'alpha': 0.9}
MAX_PARAM_DICT = {'logMmin': 14.0,
                'sigma_logM': 0.8,
               	'logM0': 15.0,
               	'logM1': 16.0,
               	'alpha': 1.1}
HALO_FID_PATH = '/mnt/lustre/bart/paired_sims/GR_L1024_NP1024/Box1/NBody/halo.dat'
HALO_2FIT_PATH = '/mnt/lustre/bart/paired_sims/GR_L1024_NP1024/Box1/halos/halo.dat'
OBJ_FUN_TYPE = 'chi2' # 'residuals' or 'chi2'
SEARCH_METHOD = 'nelder' # 'emcee' or 'nelder'
BIN_MODE = 'log' # 'lin' or 'log'
N_PROC = 20
#R_BINS = logspace(-1,1.5,26)
NELDER_SEARCH_ARGS = {'max_nfev':20} 
EMCEE_SEARCH_ARGS = { 'nwalkers':20, 'steps':1000, 'progress':True, 'is_weighted':True, 'float_behavior':'chi2'} 
NELDER_OPTIONS = {'adaptive':True, 'maxiter':10}
SEED = 1001


