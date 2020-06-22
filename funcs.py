# Tools to read halos and produce the mock
from numpy import array, linspace, logspace
from nbodykit.source.catalog import CSVCatalog
from nbodykit.lab import HaloCatalog, cosmology
from halotools.empirical_models import PrebuiltHodModelFactory
from Corrfunc.theory.xi import xi
from time import time

# Tools to save results 
from pickle import dump
from datetime import datetime

# Global variables
from .config import * 

#====================================================
# Functions for the Class Mock
#====================================================
def Table_Pos(table):
    pos = (table['x'][:, None] * [1, 0, 0] + 
            table['y'][:, None] * [0, 1, 0] + 
            table['z'][:, None] * [0, 0, 1])
    return pos

def Table_Vel(table):
    vel = (table['vx'][:, None] * [1, 0, 0] + 
            table['vy'][:, None] * [0, 1, 0] + 
            table['vz'][:, None] * [0, 0, 1])
    return vel

def Galaxy_Corr(galaxy_table, mod='lin', **kwargs):
    '''
    Evaluates the galaxies correlation function.
    Possible inputs:
    mod: string, controlling the spacing of the bins. 'lin' or 'log'
    rbins: numpy.array for the bins. If specified, 'mod' is ignored
    '''
    X = array(galaxy_table['x'])
    Y = array(galaxy_table['y'])
    Z = array(galaxy_table['z'])
    
    try:
        rbins = kwargs['rbins']
    except:
        if mod=='lin':
            rbins = linspace(1, 100, 11)
        elif mod=='log':
            rbins = logspace(0, 2, 21)
        else:
            raise Exception

    return xi(1024,N_PROC,rbins, X,Y,Z, output_ravg=True)

class Mock:
        
    def __init__(self, path):
        '''
        Links the object to input catalog
        '''
        self.path = path
        self.model = self.path.split('/')[-2]
    
    def Read_Halo_Table(self):
        '''
        Using the path of the Rockstar catalogue, reads the it and stores the halo table in self.table
        '''
        # Reads the file 
        print('Reading Rockstar file', self.path,'...' )
        start = time()
        self.table = CSVCatalog(self.path, NAMES, usecols=USE_COLS)
        # Creates Position and Velocity columns
        self.table['Position'] = Table_Pos(self.table)
        self.table['Velocity'] = Table_Vel(self.table)
        print(f'\t Done. Elapsed time: {time()-start:.2f} s')
    
    def Create_Halo_Catalog(self):
        '''
        Using table, cosmology and redshift builds the Halo Catalog in self.halos
        '''
        print('Creating Halo catalog...')
        start = time()
        halos = HaloCatalog(self.table, cosmo=cosmology.Planck15, redshift=REDSHIFT, 
                                 mdef='vir', position='Position', velocity='Velocity', mass='m200c')
        self.halos = halos.to_halotools(BoxSize=BOXSIZE)
        print(f'\t Done. Elapsed time: {time()-start:.2f} s')
        
    def Add_Hod(self, param_dict=PARAM_DICT, **kwargs):
        '''
        Initializes a Zheng07 HOD model and populates the mock
        '''
        print('Adding and populating Zheng07 HOD model...')
        start = time()
        self.hod = PrebuiltHodModelFactory('zheng07', redshift=REDSHIFT, modulate_with_cenocc=True)
        self.hod.param_dict.update(param_dict)
        self.hod.populate_mock(self.halos, **kwargs)
        # Compute centrals and satellites numbers
        self.hod.Ncens = (self.hod.mock.galaxy_table['gal_type'] == 'centrals').sum()
        self.hod.Nsats = (self.hod.mock.galaxy_table['gal_type'] == 'satellites').sum()
        print(f'\t Done. Elapsed time: {time()-start:.2f} s')


#====================================================
# Functions for HOD paramteres fitting
#====================================================

def Chi2(xi_fid, xi_2fit):
    return 1**2*( (xi_2fit - xi_fid)**2 / xi_fid**2 ).sum()

def Residuals(xi_fid, xi_2fit):
    return 100*(xi_2fit - xi_fid) / xi_fid

def Read_Params(res):
    dum_param_dict = {}
    for key in PARAM_DICT.keys():
        dum_param_dict[key] = res.params[key].value
    return dum_param_dict

def save_results(res,out_name):
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    out_path = './Results/' + out_name + '.' + date_time
    print('Saving results in:',out_path)
    with open(out_path, 'wb') as file:
        dump(res, file)
