import logging
import os
from time import time
import shutil
import glob
import pandas as pd
import datetime
import pickle
import concurrent.futures

from .hasher import PandasObjectHasher
from .functimelog import timelogger

class FsError(Exception):
    pass

class Fs:
    '''
    Data Science "file system"
    The class  Fs handles syncing between memory and disk of python objects and pandas dataframes.
    It supports saving and resuming of abritrary python objects by means of pickling.
    Pandas dataframes are pickled for further processing and optionally saved as csv files for easy exploration.
    The csv files are only saved but never read back.
    The directory can be copied or moved on file system level to another location and later resumed in python.
    The file names on disk correspond with the object name in python.
    Python objects (as well as dataframes) must be created as attribute of the object of this class.
    All attributes of this object will be synced between ram and disk when using load() or save()
    During loading from disk, the data objects can be hashed for later comparison.
    During dumping to disk, a check is done to only dump if there is a change compared to the disk version.
    The class may not very useful on its own. It is used by the class RdsProject.
    Users acutally should use RdsProject.

    Parameters
    ----------
    output_dir: string
        Path to the data directory; location of the data files on disk.
    
    hash_controlled: bool
    	defaults to False
        Defines if the advanced data objects should be hashed or not

    Example
    -------
    proj1 = Fs('/mnt/data/project1') # create object from class
    proj1.df1 = pd.DataFrame() # create dataframe as attribute of proj1
    proj1.variable1 = 'foo' # create simple objects as attribute of proj1
    proj1.save() # save attributes of proj1 to disk

    This will result in two files in /mnt/data/project1:
    - var_variable1.pkl
    - df1.pkl

    Later on or in another python session, you can do this:
    proj2 = Fs('/mnt/data/project1') # create object from class
    proj2.load() # reads files back to python objects
    proj2.variable1 == 'foo' ==> True
    isinstance(proj2.df1, pd.DataFrame) ==> True
    '''

    def __init__(self, output_dir, hash_controlled=False):
        
        self._logger = logging.getLogger(__name__)
        
        self.output_dir = output_dir
        
        self._short_name = self.output_dir.split(os.path.sep)[-1]
        if self._short_name == '':
            self._short_name = self.output_dir.split(os.path.sep)[-2]
        
        self._simple_data_object_prefix = 'var_'
        self._simple_data_object_file_ext = '.pkl'
        self._advanced_data_object_file_ext = '.pkl'
        
        self._advanced_data_object_types = [
                                            pd.Series,
                                            pd.DataFrame,
                                        ]
        
        # only for info. not used functionally
        self._backend = 'pickle'
        
        self._hash_controlled = hash_controlled
        self._hash_objects = {}

        self.make_output_dir()

    def __str__(self):
        '''
        Returns
        -------
        The output directory (w/o full path) as string.
        '''
        return 'resumableds FS container "{}"'.format(self._short_name)

    def __repr__(self):
        '''
        Returns
        -------
        Returns a string that contains:
        - an overview of all files in the output directory
        - an overview of all loaded python objects (name and content) (for dataframes the shape is shown rather than the full content)
        '''

        props = {'backend': self._backend}
        props['hash_controlled'] = self._hash_controlled
        properties = '\n'.join(['\t%s: %s' % (str(k), str(v)) for k, v in props.items()])

        files = '\n'.join(['\t%s: %s' % (str(k), str(v)) for k, v in self.ls().items()])
        objects = '\n'.join(['\t%s: %s' % (str(k), str(v)) if (not isinstance(v, pd.DataFrame)) and (not isinstance(v, pd.Series)) else '\t%s: %s' % (str(k), str(v.shape)) for k, v in {k:v for k,v in self.__dict__.items() if not k.startswith('_')}.items()])

        return '''
{caption}
{underline}
properties:
{properties}
existing files:
{files}
loaded objects:
{objects}
'''.format(
           caption=str(self),
           underline='=' * len(str(self)),
           files=files,
           objects=objects,
           properties=properties,
          )
    
    def make_output_dir(self):
        '''
        Creates the output directory to read/write files.
        '''
        try:
            os.makedirs(self.output_dir, exist_ok=True) # had some issues without try except here
        except FileExistsError:
            pass

    def clean(self):
        '''
        Deletes the output directory including all its content and recreates an empty directory.
        '''
        
        shutil.rmtree(self.output_dir)
        # recreate empty dir structure
        self.make_output_dir()

        return True
    
    def _ls(self):
        '''
        Returns output directory content including mtime.

        Returns
        -------
        Dict with file names as keys and mtime as values.
        '''
        ls_content = glob.glob(os.path.join(self.output_dir, '*'))
        ls_content = {f:str(datetime.datetime.fromtimestamp(os.path.getmtime(f))) for f in ls_content}
        
        return ls_content

    def ls(self):
        '''
        Prints dataframe files from the output directory including mtime as returned by _ls().
        Internal python objects are skipped and not shown.
        '''
        return {os.path.basename(k): v for k, v in self._ls().items() if not os.path.basename(k).startswith(self._simple_data_object_prefix)}

    def _is_advanced_data_storage(self, stg_name):
        '''
        determines if an data storage is (can be) 'advanced'
        '''
        basename = os.path.basename(stg_name)
        if basename.startswith(self._simple_data_object_prefix):
            return False
        if basename.endswith(self._advanced_data_object_file_ext):    
            return True    
        return False
    
    def _is_advanced_data_object(self, obj_name):
        '''
        determines if an data object is (can be) 'advanced'
        '''
        obj = self.__dict__[obj_name]
        for adv_data_object_type in self._advanced_data_object_types:
            if isinstance(obj, adv_data_object_type):
                return True
        return False
    
    def _get_data_storage_names(self):
        '''
        Get data storage names
        
        returns tuple of lists: [all, simple, advanced]
        '''
        
        # filter internal objects and output_dir
        data_storage_names = [stg_name for stg_name in self._ls().keys() if (stg_name.endswith(self._advanced_data_object_file_ext) or stg_name.endswith(self._simple_data_object_file_ext))]
        
        advanced_storage_names = []
        simple_storage_names = []
        
        for stg_name in data_storage_names:
            if self._is_advanced_data_storage(stg_name):
                advanced_storage_names.append(stg_name)
            else:
                simple_storage_names.append(stg_name)
        
        return (data_storage_names, simple_storage_names, advanced_storage_names)
    
    def _get_data_object_info(self):
        '''
        Get data object names
        
        returns tuple of lists: [all, simple, advanced]
        '''
        
        # filter internal objects and output_dir
        data_object_names = [obj_name for obj_name in self.__dict__.keys() if (not obj_name.startswith('_') and obj_name != 'output_dir')]
        
        data_object_info = []
        for obj_name in data_object_names:
            obj = self.__dict__[obj_name]
            obj_hash = self._hash_objects.get(obj_name, None)
            data_object_info.append((obj_name, obj, obj_hash))
            
        advanced_object_info = []
        simple_object_info = []
        
        for obj_info in data_object_info:
            obj_name = obj_info[0]
            if self._is_advanced_data_object(obj_name):
                advanced_object_info.append(obj_info)
            else:
                simple_object_info.append(obj_info)
        
        return (data_object_info, simple_object_info, advanced_object_info)
    
    @timelogger
    def load(self):
        '''
        Reads all data objects from storage
        and loads them as attributes of this object.
        '''
                
        t0 = time()
        all_data_storage_names, simple_data_storage_names, advanced_data_storage_names = self._get_data_storage_names()
        
        self._logger.debug('{}: load {} items...'.format(self.output_dir, len(all_data_storage_names)))
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_simple_objects = {executor.submit(self._load_simple_data_storage, abs_fn): abs_fn for abs_fn in simple_data_storage_names}
            future_advanced_objects = {executor.submit(self._load_advanced_data_storage, abs_fn): abs_fn for abs_fn in advanced_data_storage_names}
            future_objects = {**future_simple_objects, **future_advanced_objects}
            for future in concurrent.futures.as_completed(future_objects):
                try:
                    data_object_info = future.result()
                except Exception as e:
                    self._logger.error(e)
                    self._logger.error('Cannot load {}'.format(future_objects[future]))
                    raise
                    
                try:
                    obj_name, obj, obj_hash = data_object_info
                except Exception as e:
                    self._logger.error(e)
                    error_msg = 'Got: "{}". Expected a tuple (obj_name, obj, obj_hash) as return value of functions _load_advanced_data_storage and _load_simple_data_storage'.format(str(data_object_info))
                    self._logger.error(error_msg)
                    raise FsError(error_msg)
            
                if obj_name:
                    self.__dict__[obj_name] = obj
                if obj_hash:
                    self._hash_objects[obj_name] = obj_hash

        self._logger.debug('"%s": loaded %d objects in %.2fs' % (self.output_dir, len(all_data_storage_names), time() - t0))
        
        # must return something that is True (RdsProject resume function relies on it)
        return True 
    
    def save(self, csv=False):
        '''
        Saves all data objects to storage
        '''
                
        t0 = time()
        all_data_object_names, simple_data_object_names, advanced_data_object_names = self._get_data_object_info()
        
        self._logger.debug('{}: save {} items...'.format(self.output_dir, len(all_data_object_names)))
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_simple_objects = {executor.submit(self._save_simple_data_object, obj_info): obj_info for obj_info in simple_data_object_names}
            future_advanced_objects = {executor.submit(self._save_advanced_data_object, obj_info, csv): obj_info for obj_info in advanced_data_object_names}
            future_objects = {**future_simple_objects, **future_advanced_objects}
            for future in concurrent.futures.as_completed(future_objects):
                try:
                    data_object_info = future.result()
                except Exception as e:
                    self._logger.error(e)
                    self._logger.error('Cannot save {}'.format(future_objects[future]))
                    raise
                
                try:
                    obj_name, obj, obj_hash = data_object_info
                except Exception as e:
                    self._logger.error(e)
                    error_msg = 'Got: "{}". Expected a tuple (obj_name, obj, obj_hash) as return value of functions _load_advanced_data_storage and _load_simple_data_storage'.format(str(data_object_info))
                    self._logger.error(error_msg)
                    raise FsError(error_msg)
            
                #if obj_name:
                #    self.__dict__[obj_name] = obj
                if obj_hash:
                    self._hash_objects[obj_name] = obj_hash

        self._logger.debug('"%s": saved %d objects in %.2fs' % (self.output_dir, len(all_data_object_names), time() - t0))
        
        return True

    def _load_simple_data_storage(self, filename):
        '''
        Reads a pickle file from the output directory
        and loads it as attribute of this object.
        '''
        basename = os.path.basename(filename)
        obj_name = basename[len(self._simple_data_object_prefix):-1*len(self._simple_data_object_file_ext)]
        with open(filename, 'rb') as f:
            obj = pickle.load(f)
        obj_hash = None
        
        # return obj_info
        return (obj_name, obj, obj_hash)
    
    def _load_advanced_data_storage(self, filename):
        '''
        Reads a pickle file from the output directory
        and loads it as attribute of this object.
        '''
        #t0 = time()
        obj_name = os.path.basename(filename).split('.')[0]
        #self._logger.debug('execute {} = pd.read_pickle("{}")'.format(obj_name, filename))
        obj = pd.read_pickle(filename)
        obj_hash = None
        
        if self._hash_controlled:
            # create data hash object and add it to dict of hash objects
            #t1 = time()
            #self._logger.debug('create hash object for "{}" to track changes...'.format(obj_name))
            obj_hash = PandasObjectHasher(obj)
            #self._logger.debug('hash object for "%s" created in %.2fs' % (obj_name, time() - t1))
        
        #self._logger.debug('object "%s" loaded in %.2fs' % (obj_name, time() - t0))
        
        return (obj_name, obj, obj_hash)
    
    def _save_simple_data_object(self, obj_info):
        '''
        saves one object as pickle
        obj_info is a tuple (obj_name, obj, obj_hash)
        '''
        obj_name, obj, obj_hash = obj_info
        base_name = self._simple_data_object_prefix + obj_name + self._simple_data_object_file_ext
        abs_fn = os.path.join(self.output_dir, base_name)
        with open(abs_fn, 'wb') as f:
            pickle.dump(obj, f)
        
        #return obj_info
        return (obj_name, obj, obj_hash)
    
    def _save_advanced_data_object(self, obj_info, csv):
        '''
        saves one object as pickle
        obj_info is a tuple (obj_name, obj, obj_hash)
        '''
        
        #t0 = time()
        
        obj_name, obj, obj_hash = obj_info
        
        dump_required = True
        # actually check if dump is required
        if self._hash_controlled and obj_hash:
            if obj_hash.obj_changed(obj):
                dump_required = True
            else:
                dump_required = False
        
        if dump_required:  
            abs_fn = os.path.join(self.output_dir, obj_name) + self._advanced_data_object_file_ext
            #self._logger.debug('execute {}.to_pickle("{}")'.format(obj_name, abs_fn))
            obj.to_pickle(abs_fn) 
            
            if self._hash_controlled:
                # update data hash object
                #t1 = time()
                #self._logger.debug('create hash object for "{}" to track changes...'.format(obj_name))
                obj_hash = PandasObjectHasher(obj)
                #self._logger.debug('hash object for "%s" created in %.2fs' % (obj_name, time() - t1))
            
            if csv:
                csv_fn = abs_fn[:-len(self._advanced_data_object_file_ext)] + '.csv'
                #self._logger.debug('execute {}.to_csv("{}")'.format(obj_name, csv_fn))
                obj.to_csv(csv_fn, sep=';', decimal=',')
                
            #self._logger.debug('object "%s" saved in %.2fs' % (obj_name, time() - t0))
        #else:
            #self._logger.debug('"{}" has not changed since last dump'.format(obj_name))
        
        # return (updated) obj_info
        return (obj_name, obj, obj_hash)