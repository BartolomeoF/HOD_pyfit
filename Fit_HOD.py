from .funcs import Residuals, Chi2, save_results, Galaxy_Corr, Mock, Read_Params
from .config import *

from lmfit import minimize, Parameters
from time import time

from random import uniform
from numpy import array

def main():
    if OBJ_FUN_TYPE == 'chi2':
        Obj_Fun = Chi2
    elif OBJ_FUN_TYPE == 'residuals':
        Obj_Fun = Residuals
    else:
        raise Exception

    xi_args = {'mod':BIN_MODE}
    try:
        xi_args['rbins'] = R_BINS
    except:
        pass

    print('Seed:',SEED)

    def ObjFun_FromParams( params):
        # Update paramters
        new_param_dict = {}
        for key in PARAM_DICT.keys():
            new_param_dict[key] = params[key]

        mock_2fit.hod.param_dict.update(new_param_dict)
        
        # Populate mock
        mock_2fit.hod.mock.populate(seed=SEED)
        
        # Evaluate corr_func
        xi_2fit = Galaxy_Corr(mock_2fit.hod.mock.galaxy_table, **xi_args)['xi']

        val = Obj_Fun( xi_fid, xi_2fit)
        print(f'Chi^2 : {Chi2( xi_fid, xi_2fit):.2f}' )

        return val

    # Read fiducial mock
    mock_fid = Mock(HALO_FID_PATH)
    mock_fid.Read_Halo_Table()
    mock_fid.Create_Halo_Catalog()
    mock_fid.Add_Hod(seed=SEED)

    # Read the mock to fit
    mock_2fit = Mock(HALO_2FIT_PATH)
    mock_2fit.Read_Halo_Table()
    mock_2fit.Create_Halo_Catalog()
    mock_2fit.Add_Hod(seed=SEED)

    # Compute fiducial correlation function
    xi_fid = Galaxy_Corr( mock_fid.hod.mock.galaxy_table, **xi_args) ['xi']

    # Set up paramters for the fit
    params = Parameters()
    if SEARCH_METHOD == 'nelder':
        for key,value in zip(PARAM_DICT.keys(),PARAM_DICT.values()):
            params.add(key,value)   
        search_args = NELDER_SEARCH_ARGS
    elif SEARCH_METHOD == 'emcee':
        for key,value in zip(PARAM_DICT.keys(),PARAM_DICT.values()):
            params.add(key,value, min=MIN_PARAM_DICT[key], max=MAX_PARAM_DICT[key]) 
        search_args = EMCEE_SEARCH_ARGS

        # Evaluate initial states for MCMC walkers
        def Get_Random_params():
            dum_params = Parameters()
            for key in PARAM_DICT.keys():
                value = uniform(MIN_PARAM_DICT[key], MAX_PARAM_DICT[key])
                dum_params.add(key,value)
            return dum_params

        def Get_Simplex_Params():
            dum_params = Get_Random_params() 
            dum_res = minimize(ObjFun_FromParams, dum_params, method='nelder', options=NELDER_OPTIONS)
            return list(Read_Params(dum_res).values())

        n_states = EMCEE_SEARCH_ARGS['nwalkers']
        in_states = [Get_Random_params() for i in range(n_states)] # Attention!!
        print('The initial states vector is:\n',in_states)

        #search_args['pos'] = array(in_states)


    # Perform the fit
    print('Performing the', SEARCH_METHOD, 'search...')
    start = time()
    res = minimize(ObjFun_FromParams, params, method=SEARCH_METHOD, **search_args)
    print(f'Search done. Elapsed time: {time()-start:.2f} s')

    # Save results
    save_results( res, mock_2fit.model + '_' + SEARCH_METHOD + '_' + BIN_MODE)
    print('Finished!')


if __name__=='__main__':
    main()
