import logging
import os
from time import time

from .fs import Fs

class PlotFs(Fs):
    '''
    Plot container
    Will only work with holoviews object.
    All other stuff is simply ignored and won't be saved / loaded
    '''
    
    def __init__(self, output_dir):
        
        import holoviews as hv
        hv.extension('bokeh', logo=False)
        #from holoviews.core.io import Pickler
        #from holoviews.core.io import Unpickler
        
        super().__init__(output_dir)
        
        # everything goes to simple_data_objects
        self._advanced_data_object_types = [
                                            #pd.Series,
                                            #pd.DataFrame,
                                           ]
        
        # only for info. not used functionally
        self._backend = 'holoviews'
        
        
    def _save_simple_data_object(self, obj_info):
        '''
        Saves all holoviews objects as files to the output directory.
        '''
        
        t0 = time()
        import holoviews as hv
        hv.extension('bokeh', logo=False)
        renderer = hv.renderer('bokeh')
        
        obj_name, obj, obj_hash = obj_info
        base_name = obj_name + '.hvplot'
        abs_fn = os.path.join(self.output_dir, base_name)
        # pickle for re-use
        try:
            #Pickler.save(obj, abs_fn)
            hv.Store.dump(obj, open(abs_fn, 'wb'))
        except Exception as e:
            self._logger.warning(e)
            self._logger.warning('Couldn\'t pickle "{}". Skip.'.format(obj_name))
            #return (None, None, None)  #try html anyway

        # html output
        try:
            abs_fn = os.path.join(self.output_dir, obj_name)
            renderer.save(obj, abs_fn, fmt='html')
        except Exception as e:
            self._logger.error(e)
            self._logger.error('Couldn\'t save "{}". Skip.'.format(obj_name))
            raise
        
        self._logger.debug('saved plot object "%s" in %.2fs' % (obj_name, time() - t0))
        return obj_name, obj, obj_hash
        
    def _load_simple_data_object(self, abs_fn):
        '''
        Reads all hvz files from the output directory
        and loads them as attributes of this object.
        '''
        
        # not working yet. styles are lost during load.
        # temp disabled for now.
        
        self._logger.warning('loading doesn\'t work yet for plots. Continue with empty container.')
        return (None, None, None)
        
        
        '''
        import holoviews as hv
        #from holoviews import Store
        hv.extension('bokeh')
        #from holoviews.core.io import Pickler
        #from holoviews.core.io import Unpickler
    
        t0 = time()
        
        # get all data objects from dir
        to_load = {k:v for k, v in self._ls().items() if k.endswith('.hvplot')}

        logging.debug('load {} items...'.format(len(to_load)))
        for k, v in enumerate(to_load.items()):
            fn, mtime = v
            base_name = os.path.basename(fn)
            var_name = base_name[0:-1*len('.hvplot')]
            #var = Unpickler.load(open(fn, 'rb'))
            var = hv.Store.load(open(fn, 'rb'))
            
            self._load_in_class([var_name, var, None])
        
        logging.debug('sync to ram done for "%s": %d objects in %.2fs' % (
                                                                                self.output_dir,
                                                                                len(to_load),
                                                                                time() - t0
                                                                               )
                         )
        return True
        '''
