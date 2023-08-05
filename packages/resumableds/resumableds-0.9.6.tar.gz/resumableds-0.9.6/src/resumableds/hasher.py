import logging
import pandas as pd
from hashlib import md5
from pandas.util import hash_pandas_object

from .functimelog import timelogger

class PandasObjectHasher:
    '''
    Class to compare two dataframes (or the same dataframe at different times).
    This class will be used to determine if a loaded data object has changed
    since the last load from disk.
    '''
    
    @timelogger
    def __init__(self, df):
        self.logger = logging.getLogger(__name__)
        self.data_hash_exception_occured = False
        self.index_hash = self.__create_index_hash(df)
        self.columns_hash = self.__create_columns_hash(df)
        self.data_hash = self.__create_data_hash(df)
    
    def __create_index_hash(self, df):
        return df.index.values.tolist()
    
    def __create_columns_hash(self, df):
        if isinstance(df, pd.DataFrame):
            return df.columns.values.tolist()
        return None
    
    def __create_data_hash(self, df):
        data_hash = None
        try:
            data_hash = md5(hash_pandas_object(df).values).hexdigest()
        except Exception as e:
            # hashing dataframes with mutable objects like lists inside will throw an exception
            self.logger.debug(e) # debug because lib is also working without hashes
            self.data_hash_exception_occured = True
        return data_hash
        
    def index_changed(self, df):
        return self.__create_index_hash(df) != self.index_hash
    
    def columns_changed(self, df):
        return self.__create_columns_hash(df) != self.columns_hash
    
    def data_changed(self, df):
        return self.__create_data_hash(df) != self.data_hash

    @timelogger
    def obj_changed(self, df):
        
        if self.data_hash_exception_occured:
            #no data hash available, play safe -> presume data is changed
            return True
    
        if self.index_changed(df):
            return True
        if self.columns_changed(df):
            return True
        if self.data_changed(df):
            return True
        return False