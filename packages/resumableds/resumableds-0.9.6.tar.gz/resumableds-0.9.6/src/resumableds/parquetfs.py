import os
import pandas as pd

from .fs import Fs

class ParquetFs(Fs):
    '''
    Fs container using parquet as data files
    '''
    
    def __init__(self, output_dir):
        
        super().__init__(output_dir)
        # only for info. not used functionally
        self._backend = 'parquet'
        self._advanced_data_object_file_ext = '.parquet'
        
        
    def _load_advanced_data_storage(self, filename):
        '''
        Reads a parquet file from the output directory
        and loads it as attribute of this object.
        '''
        obj_name = os.path.basename(filename).split('.')[0]
        obj = pd.read_parquet(filename)
        obj_hash = None
        
        if self._hash_controlled:
            obj_hash = PandasObjectHasher(obj)
        
        return (obj_name, obj, obj_hash)
    
    def _save_advanced_data_object(self, obj_info, csv):
        '''
        saves one object as parquet
        obj_info is a tuple (obj_name, obj, obj_hash)
        '''
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
            obj.to_parquet(abs_fn) 
            
            if self._hash_controlled:
                obj_hash = PandasObjectHasher(obj)
            
            if csv:
                csv_fn = abs_fn[:-len(self._advanced_data_object_file_ext)] + '.csv'
                obj.to_csv(csv_fn, sep=';', decimal=',')
        
        # return (updated) obj_info
        return (obj_name, obj, obj_hash)