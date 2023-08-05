import logging
import traceback
import os
from time import time
import shutil
import glob
import pandas as pd
import datetime
import yaml
import platform
import concurrent.futures
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors import CellExecutionError

from .fs import Fs
from .plotfs import PlotFs
from .featherfs import FeatherFs
from .parquetfs import ParquetFs
from .functimelog import timelogger

class ProjectError(Exception):
    pass

class Project:
    '''
    Project incl. save/resume functionality.
    This class supports you in writing data science scripts.
    Data can be saved and resumed avoiding unnessary retrievals of raw data from data storages.

    Parameters
    ----------
    project_name: string
        The project name.
        Can be ommitted if a config file is passed to the config_file parameter
    dirs: list, optional
        List of sub-directory names that should be used in the project.
        Defaults to ['defs', 'raw', 'interim', 'processed']
    config_file: string, optional
        Path to the yml config file.
        Defaults to <project_name>.yml in the current working directory.
    output_dir: string, optional
        Location of data files, defaults to ./<project_name>
    analysis_start_date: datetime (can also be string, will be converted automatically), optional
        Start date of the analysis.
        Defaults to today - analysis_timespan
    analysis_end_date: datetime (can also be string, will be converted automatically), optional
        End date of the analysis.
        Defaults to today.
    analysis_timespan: timedelta (can also be string, will be converted automatically), optional
        Defaults to 180 days.
    start_clean: boolean, optional
        Skip resume if true.
        Defaults to False.
        
    Example
    -------
    proj1 = Project('project1') # create object from class (creates the dir if it doesn't exist yet)
    proj1.raw.df1 = pd.DataFrame() # create dataframe as attribute of proj1.raw (Fs 'raw')
    proj1.defs.variable1 = 'foo' # create simple objects as attribute of proj1.defs (Fs 'defs')
    proj1.save() # saved attributes of all RfdFs in proj1 to disk

    This will result in the following directory structure (plus some overhead of internals):
    - <output_dir>/defs/var_variable1.pkl
    - <output_dir>/raw/df1.pkl
    - <output_dir>/raw/df1.csv

    Later on or in another python session, you can do this:
    proj2 = Project('project1') # create object from class (doesn't touch the dir as it already exists) All vars and data is read back to their original names.
    proj2.defs.variable1 == 'foo' ==> True
    isinstance(proj2.raw.df1, pd.DataFrame) ==> True
    '''
    @timelogger
    def __init__(
                 self, 
                 project_name=None,
                 dirs=None,
                 configfile=None,
                 output_dir='data',
                 analysis_start_date=None,
                 analysis_end_date=None,
                 analysis_timespan=None,
                 start_clean=False,
                 backend='PICKLE',
                ):
        
        self.project_name = project_name
        self.configfile = configfile
        self.backend = str.upper(backend)
        
        self.logger = logging.getLogger(__name__)
        
        # defs: save project definitions like names, filters, etc
        self.DEFS = 'defs'
        
        # set names of output directories
        # external: files from outside this project,
        # external files can be copied here for further use
        # won't be used by default
        self.EXTERNAL = 'external'
        # raw: raw data retrieved from a data storage (like SQL server)
        self.RAW = 'raw'
        # half ready results / in-between steps
        self.INTERIM = 'interim'
        # analysis results
        self.PROCESSED = 'processed'


        # models (won't be used by default)
        self.MODELS = 'models'
        
        # graphs / plots (won't be used by default)
        # plots directory will be handled differently.
        # Assuming holoviews, plots will save and load hv objects
        self.PLOTS = 'plots'
        
        # get a list of data dirs that should be used
        self.output_dirs = []
        self.output_dirs = self.__update_dir_specs(dirs)
        
        # internals
        # how many Fs objects to handle concurrently?
        self._max_workers = 2
        # list of supported backend (Fs flavors)
        self._supported_backends = {
                                    'PICKLE': Fs,
                                    'FEATHER': FeatherFs,
                                    'PARQUET': ParquetFs,
                                   }
        
        
        # --- start logic
        
        # if configfile is passed, use it
        if self.configfile:
            # if configfile is not present, start clean
            if not os.path.isfile(self.configfile):
                start_clean = True
                # if project_name is not set wihtout an existing configfile, raise error
                if not self.project_name:
                    self.logger.error('either a valid configfile or project_name must be passed. Cannot start without name and with empty config file.')
                    raise ProjectError('configfile "{}" doesn\'t exist and project_name is not set'.format(self.configfile))
        
        # if no config file, use project_name and default 
        else:
            # check if project_name is given. Then use default config file
            if self.project_name:
                self.configfile = os.path.join(os.getcwd(), project_name + '.yml')
            else:
                self.logger.error('either a valid configfile or project_name must be passed. Cannot start without name and with empty config file.')
                raise ProjectError('no configfile given and no project_name set')
                
        
        # get project root dir based on yml file location
        self.project_root_dir = os.path.dirname(self.configfile)
        
        
        # if clean startup is required, write passed parameters to configfile and clean dirs
        if start_clean:
            if not self.project_name:
                raise ProjectError('Project name cannot be None if start_clean is passed')
                
            # if output dir is not default, create a link in pwd to output dir
            if output_dir == 'data':
                self.output_dir = os.path.join(self.project_root_dir, 'data')
            else:
                self.output_dir = output_dir
                '''
                try:
                    os.symlink(self.output_dir, os.path.join(self.project_root_dir, 'data'))
                except Exception as e:
                    self.logger.debug(e)
                    self.logger.debug('cannot create a link to data directory. Skip and continue without.')
                '''
            # get start, end date, timeframe consistent
            self._get_analysis_time(analysis_start_date, analysis_end_date, analysis_timespan)
            
            self.save_configfile()

        # else read parameters from configfile (and ignore possible passed parameters from constructor)
        else:
            if os.path.isfile(self.configfile):
                # read project paramters from config file
                with open(self.configfile, 'r') as ymlfile:
                    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)
                    self.output_dir = cfg.get('output_dir', 'data')
                    self.backend = str.upper(cfg.get('backend', 'pickle'))
                    self.project_name = cfg.get('project_name', self.project_name)
                    analysis_start_date = cfg.get('analysis_start_date', None)
                    analysis_end_date = cfg.get('analysis_end_date', None)
                    analysis_timespan = cfg.get('analysis_timespan', None)
                self._get_analysis_time(analysis_start_date, analysis_end_date, analysis_timespan)
            else:
                raise ProjectError('cannot read config_file "{}"'.format(self.configfile))
        
        # init working dirs
        self.__init_sub_dirs(self.output_dirs)
        
        # clean data dirs if required
        if start_clean:
            self.clean()
        
        self._status('started')

        self.resume(dirs)
        
    def __str__(self):
        return 'resumableds Project "%s"' % self.project_name

    def __repr__(self):
        return '''
{caption}
{underline}
Analysis time:\t{a_start} - {a_end} ({a_delta})
Status file:\t{s_file}
Output dir:\t{output_dir}
Backend:\t{backend}
Loaded dirs:\t{dirs}
'''.format(
           caption=str(self),
           underline='=' * len(str(self)),
           #state=self.status,
           s_file=self.configfile,
           backend=self.backend,
           a_start=str(self.analysis_start_date),
           a_end=str(self.analysis_end_date),
           a_delta=str(self.analysis_timespan),
           output_dir=self.output_dir,
           dirs=str(self.output_dirs),
          )


    def save_configfile(self):
        # save yaml
        # write status file
        y_out = {
                    'project_name': self.project_name,
                    'output_dir': self.output_dir,
                    'backend': self.backend,
                    'analysis_start_date': str(self.analysis_start_date),
                    'analysis_end_date': str(self.analysis_end_date),
                    'analysis_timespan': str(self.analysis_timespan),
                }
        with open(self.configfile, 'w') as ymlfile:
            ymlfile.write(yaml.dump(y_out))
        
    @timelogger
    def save(self, dirs=None, csv=False):
        '''
        Saves the state of ds project to disk.

        Parameters
        ----------
        dirs: list, optional
            List of sub-directoies that should be saved to disk.
            By default all subdirectories defined in the contructor are taken into account.
        csv: boolean, optional
            Save data files also as csv
            Defaults to false
        '''
        
        # save config file of project
        self.save_configfile()
        
        # save data sub dirs
        dirs = self.__update_dir_specs(dirs)
        
        results = []    
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_sub_dirs = [executor.submit(lambda x: self.__dict__[x].save(csv=csv), sub_dir) for sub_dir in dirs]
            for future in concurrent.futures.as_completed(future_sub_dirs):
                results.append(future.result())
        
        if all(results):
            self._status('saved')
            self.logger.info('saved {} in {}'.format(str(dirs), self.output_dir))
            return True
        else:
            self.logger.error('couldn\'t save completely!! Check the logs.')
            return False

    @timelogger
    def resume(self, dirs=None):
        '''
        Resumes an existing project.
        Check if this project has been saved, if so, resume
        check for save can be skipped by forcing resume

        Parameters
        ----------
        dirs: list, optional
            List of sub-directoies that should be resumed.
            By default all subdirectories defined in the contructor are taken into account.
        '''  
        # get to be resumed dirs
        dirs = self.__update_dir_specs(dirs)
        
        # init sub dirs
        self.__init_sub_dirs(dirs)
        
        results = []    
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_sub_dirs = [executor.submit(lambda x: self.__dict__[x].load(), sub_dir) for sub_dir in dirs]
            for future in concurrent.futures.as_completed(future_sub_dirs):
                results.append(future.result())
        
        if all(results):
            self._status('resumed')
            return True
        else:
            raise ProjectError('couldn\'t resume completely!! Check the logs.')    
    
    @timelogger
    def reset(self, dirs=None):
        '''
        Reset the project state.
        This includes deleting all files from the output_dir.
        Objects in memory are saved to disk then. RAM and disk will be in sync after resetting.

        Parameters
        ----------
        dirs: list, optional
            List of sub-directoies that should be reset.
            By default all subdirectories defined in the contructor are taken into account.
        '''
        self.clean(dirs)
        self.save(dirs)

    @timelogger
    def clean(self, dirs=None):
        '''
        Delete all files in data dirs.
        
        Parameters
        ----------
        dirs: list, optional
            List of sub-directoies that should be reset.
            By default all subdirectories defined in the contructor are taken into account.
        '''
        t0 = time()
        dirs = self.__update_dir_specs(dirs)

        def clean_dir(sub_dir):
            return self.__dict__[sub_dir].clean()
        
        results = []    
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_sub_dirs = [executor.submit(clean_dir, sub_dir) for sub_dir in dirs]
            for future in concurrent.futures.as_completed(future_sub_dirs):
                results.append(future.result())
        
        if all(results):
            self._status('cleaned')
            return True
        else:
            self.logger.error('couldn\'t clean completely!! Check the logs.')
            return False

    @timelogger
    def unload(self, dirs=None):
        '''
        unload all data of given dirs from RAM
        
        Parameters
        ----------
        dirs: list, optional
            List of sub-directoies that should be unloaded from RAM.
            By default all subdirectories defined in the contructor are taken into account.
        '''
        dirs = self.__update_dir_specs(dirs)
        # don't unload defs
        dirs.remove('defs')

        for sub_dir in dirs:
            del(self.__dict__[sub_dir])
            self.output_dirs.remove(sub_dir)
        
        return True

    def get_container_by_name(self, fs_container_name):
        '''
        return object matching given name
        
        Parameters
        ----------
        fs_container_name: str
        '''
        if fs_container_name in self.output_dirs:
            return self.__dict__[fs_container_name]
        else:
            return None

    def _get_analysis_time(self, analysis_start_date, analysis_end_date, analysis_timespan):
        
        default_timespan = pd.Timedelta('365 days')
        
        def parse_date(analysis_date):
        
            if isinstance(analysis_date, str):
                try:
                    parsed_analysis_date = datetime.datetime.fromisoformat(analysis_date)
                    # this only works on > Python 3.7
                    #parsed_analysis_date = datetime.datetime.fromisoformat(analysis_date) if isinstance(analysis_date, str) else analysis_date
                    
                # < Python3.7
                except AttributeError:
                    # string incl. microseconds
                    try:
                        parsed_analysis_date = datetime.datetime.strptime(analysis_date, '%Y-%m-%d %H:%M:%S.%f')
                    # string excl. microseconds
                    except ValueError:
                        parsed_analysis_date = datetime.datetime.strptime(analysis_date, '%Y-%m-%d %H:%M:%S')
            
                return parsed_analysis_date
            return analysis_date
        
        # analsysis timespan
        self.analysis_timespan = pd.Timedelta(analysis_timespan) if isinstance(analysis_timespan, str) else analysis_timespan
        
        # analysis start date
        self.analysis_start_date = parse_date(analysis_start_date)
        
        # analysis start date
        self.analysis_end_date = parse_date(analysis_end_date)
        
        if self.analysis_start_date and self.analysis_end_date:
            #print('start and end')
            self.analysis_timespan = self.analysis_end_date - self.analysis_start_date
        
        elif self.analysis_start_date and self.analysis_timespan:
            #print('start and span')
            self.analysis_end_date = self.analysis_start_date + self.analysis_timespan
        
        elif self.analysis_end_date and self.analysis_timespan:
            #print('end and span')
            self.analysis_start_date = self.analysis_end_date - self.analysis_timespan
        
        elif self.analysis_timespan:
            #print('now and timespan')
            self.analysis_end_date = datetime.datetime.now()
            self.analysis_start_date = self.analysis_end_date - self.analysis_timespan
        
        elif self.analysis_start_date:
            #print('start and default timespan')
            self.analysis_end_date = self.analysis_start_date + default_timespan
            self.analysis_timespan = default_timespan
        
        elif self.analysis_end_date:
            #print('end and default timespan')
            self.analysis_start_date = self.analysis_end_date - default_timespan
            self.analysis_timespan = default_timespan
        
        else:
            #print('now and default timespan')
            self.analysis_end_date = datetime.datetime.now()
            self.analysis_timespan = default_timespan
            self.analysis_start_date = self.analysis_end_date - self.analysis_timespan
    
    def __init_sub_dirs(self, dirs):
        
        if self.backend not in self._supported_backends.keys():
                raise ProjectError('Backend "{}" not supported. Only supporting {}'.format(self.backend, list(self._supported_backends.keys())))
        
        # get corresponding Fs class
        selected_backend_class = self._supported_backends.get(self.backend)
        self.logger.debug('selected backend: {}: {}'.format(self.backend, str(selected_backend_class)))
            
        # init working directories
        for sub_dir in dirs:
            abs_sub_dir = os.path.join(self.output_dir, sub_dir)
            
            # special treated plot directory
            if sub_dir == self.PLOTS:
                self.__dict__[sub_dir] = PlotFs(abs_sub_dir)
                continue
            
            # init object
            self.__dict__[sub_dir] = selected_backend_class(abs_sub_dir)
    
    def _status(self, status):
        '''
        Change the internal status of project.
        The internal attributes will be synced to defs and to the status file as well.
        
        Parameters
        ----------
        status: string
            New status as text.
        '''
        self.logger.debug('"%s" status changed to "%s"' % (self.project_name, status))
        self.status = status
        
        return self.status

    def __update_dir_specs(self, dirs):
        '''
        Do a precheck for output dirs and return a list with currently managed output dirs.
        '''
        
        if dirs is None:
            # bootstrap
            if not self.output_dirs:
                dirs = sorted(
                              [
                                #self.EXTERNAL, don't use external by default anymore
                                self.RAW,
                                self.INTERIM,
                                self.PROCESSED,
                                self.DEFS,
                              ]
                             )
            # if no dirs are added, return currently managed list
            else:
                return self.output_dirs

        # if single directory is given, make it a list for generic processing
        if not isinstance(dirs, list):
            dirs = [dirs]

        # always add defs
        dirs.append(self.DEFS)

        # update data_dirs based on maybe newly added items
        self.output_dirs.extend(dirs)
        self.output_dirs = list(set(self.output_dirs))
        self.output_dirs = sorted(self.output_dirs)
        
        return sorted(set(dirs)) # only return new items for save / resume actions
    
    @timelogger
    def make(self, notebooks, cell_execution_timeout=3600):
        '''
        Run a make config that is previously defined by make_config().
        
        Parameters
        ----------
        notebooks:  list
            List of notebooks (absolute paths) to be executed in list order
        cell_execution_timeout: int
            Cell execution timeout in seconds.
            Defaults to 3600.
        '''
        
        total_t0 = time()

        for k, abs_notebook_path in enumerate(notebooks):
            self.logger.info('Execute item %d / %d' % (k+1, len(notebooks)))
            self._run_notebook(abs_notebook_path, cell_execution_timeout)
            
        self.logger.info('all %d notebooks sucessfully executed in %d seconds' % (len(notebooks), (time()-total_t0)))
        return True

    @timelogger
    def _run_notebook(self, abs_notebook_path, cell_execution_timeout):
        '''
        Execute single notebook
        '''
        notebook = os.path.basename(abs_notebook_path)
        w_dir = os.path.dirname(abs_notebook_path)
        
        # create notebooks/executed dir 
        exec_nb_dir = os.path.join(self.project_root_dir, 'notebooks', 'executed', self.project_name) # notebooks dir like suggested by cookiecutter
        os.makedirs(exec_nb_dir,  exist_ok=True)
        executed_notebook = os.path.join(exec_nb_dir, notebook)

        self.logger.debug('running "%s"', abs_notebook_path)

        # start timer
        t0 = time()

        with open(abs_notebook_path, encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

            # configure preprocessor with cell execution timeout
            ep = ExecutePreprocessor(timeout=cell_execution_timeout)

            try:
                # execute notebook in working directory
                out = ep.preprocess(nb, {'metadata': {'path': w_dir}})
            except CellExecutionError:
                out = None
                msg = 'Error executing the notebook "%s". See notebook "%s" for more details.' % (notebook, executed_notebook)
                self.logger.error(msg)
                self.logger.error(traceback.format_exc())
                raise
            finally:
                self.logger.debug('process execution "%s" took %d seconds' % (abs_notebook_path, time()-t0))
                with open(executed_notebook, mode='wt', encoding='utf-8') as f:
                    try:
                        nbformat.write(nb, f)
                    except Exception as e:
                        self.logger.debug(e)
                        self.logger.debug("Couldn't save notebook %s to disk. Continuing anyway." % executed_notebook)
        
        # return exec time
        return time() - t0
     
    def create_project_structure(self):
        # create dirs
        for new_dir in (
                        #'docs',
                        #'models', will be created when loading models
                        os.path.join('notebooks', 'executed'),
                        'references',
                        'reports',
                        'src',
                        #os.path.join('reports', 'figures') # link figures to plots
                       ):
            os.makedirs(os.path.join(self.project_root_dir, new_dir), exist_ok=True)
            
        # create files
        md_template = '''\
# {}

## Short description

## Purpose

## Input 

## Output

## Author

## Owner

## Schedule

## Development Status

'''.format(self.project_name)
        
        readme_file = os.path.join(self.project_root_dir, 'README.md')
        if not os.path.isfile(readme_file):
            with open(readme_file, 'w') as f:
                f.write(md_template)
    
    def create_notebook_templates(self):
        '''
        Create notebook templates in current working directory.
        The notebooks contain a skeleton to support the resumableds workflow.
        '''
        
        nb_defs = {
                    '''\
# Definitions

Define project variables, etc.''': nbformat.v4.new_markdown_cell,
                    '''\
import resumableds''': nbformat.v4.new_code_cell,
                    '''\
# DS project name
project = '%s'

# create project
rds = resumableds.Project(project, 'defs')''' % self.project_name: nbformat.v4.new_code_cell,
                    '''\
# your variables / definitions go here...

#rds.defs.a = 'a variable'
''': nbformat.v4.new_code_cell,
                    '''\
# save defs to disk
rds.save('defs')''': nbformat.v4.new_code_cell,
            '''\
*(Notebook is based on resumableds template)*''': nbformat.v4.new_markdown_cell,
                }


        nb_collection = {
                    '''\
# Data collection

Get raw data from data storages.''': nbformat.v4.new_markdown_cell,
                    '''\
import resumableds''': nbformat.v4.new_code_cell,
                    '''\
# DS project name
project = '%s'

# create project
rds = resumableds.Project(project, 'raw')''' % self.project_name: nbformat.v4.new_code_cell,
                    '''\
# your data retrieval here

#rds.raw.customer_details = pd.read_sql_table('customer_details', example_con)
''': nbformat.v4.new_code_cell,
                    '''\
# save project
rds.save('raw')''': nbformat.v4.new_code_cell,
                    '''\
*(Notebook is based on resumableds template)*''': nbformat.v4.new_markdown_cell,
                        }

        nb_processing = {
                    '''\
# Processing

Manipulate your data.''': nbformat.v4.new_markdown_cell,
                    '''\
import resumableds''': nbformat.v4.new_code_cell,
                    '''\
# DS project name
project = '%s'

# create project
rds = resumableds.Project(project, ['raw', 'interim', 'processed'])''' % self.project_name: nbformat.v4.new_code_cell,
                    '''\
# your data processing here

#rds.interim.german_customers = rds.raw.customer_details.loc[rds.raw.customer_details['country'] == 'Germany']
#rds.processed.customers_by_city = rds.interim.german_customers.groupby('city').customer_name.count()
''': nbformat.v4.new_code_cell,
                    '''\
# save project
rds.save(['interim', 'processed'])''': nbformat.v4.new_code_cell,
                    '''\
*(Notebook is based on resumableds template)*''': nbformat.v4.new_markdown_cell,
                        }

        nb_graphs = {
                    '''\
# Graphical output

Visualize your data.''': nbformat.v4.new_markdown_cell,
                    '''\
import resumableds''': nbformat.v4.new_code_cell,
                    '''\
# DS project name
project = '%s'

# create project
rds = resumableds.Project(project, ['processed', 'plots'])''' % self.project_name: nbformat.v4.new_code_cell,
                    '''\
# your data visualization here

#rds.processed.customers_by_city.plot()
''': nbformat.v4.new_code_cell,
                    '''\
# save project
rds.save('plots')''': nbformat.v4.new_code_cell,
                    '''\
*(Notebook is based on resumableds template)*''': nbformat.v4.new_markdown_cell,
                  }


        nb_templates = {
                            os.path.join(self.project_root_dir, 'notebooks', '01_definitions.ipynb'): nb_defs,
                            os.path.join(self.project_root_dir, 'notebooks', '10_collection.ipynb'): nb_collection,
                            os.path.join(self.project_root_dir, 'notebooks', '20_processing.ipynb'): nb_processing,
                            os.path.join(self.project_root_dir, 'notebooks', '30_graphs.ipynb'): nb_graphs,
                            #'40_publication.ipynb': nb_publication,
                       }

        for nb_name, nb_cells in nb_templates.items():
            self.logger.debug('create notebook "%s" from template' % nb_name)
            nb = nbformat.v4.new_notebook()
            nb['cells'] = [f(arg) for arg, f in nb_cells.items()]
            nbformat.write(nb, nb_name)
