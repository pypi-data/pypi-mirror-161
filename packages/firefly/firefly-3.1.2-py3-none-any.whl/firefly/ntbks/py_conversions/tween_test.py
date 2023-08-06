#!/usr/bin/env python
# coding: utf-8

# In[8]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[9]:


import numpy as np
import os

import sys
from firefly.data_reader import FIREreader,SimpleFIREreader,TweenParams


# # Convert FIRE data
# In this example notebook we demonstrate how to use the `firefly.data_reader.FIREreader` sub-class which creates specialized data files for FIRE formatted data. The details of how the `FIREreader` class is "specialized" see the <a href="https://ageller.github.io/Firefly/docs/build/html/reference/api/api.html">API documentation</a> and to see the example of this output visit <a href="https://ageller.github.io/firefly/src/firefly/index.html">the live demo version</a>.

# In[10]:


thetas = np.arange(0,360,1)
xs = np.sin(thetas/180*np.pi)*(-20)
zs = np.cos(thetas/180*np.pi)*(-20)
coords = np.zeros((thetas.size,3))
coords[:,0] = xs
coords[:,-1] = zs

my_tween = TweenParams(coords,duration=10)


# In[13]:


def make_test_scene(decimation):
    ## create a FIRE reader object
    reader = FIREreader(
        ## path to directory containing (optionally multiple) .hdf5 files
        snapdir = "/Users/agurvich/research/snaps/isolated_disks/Control_G4_20/snapdir_050/",
        ## the snapshot number, best to provide separately in order to disambiguate
        snapnum = 50,
        ## particle types one would like to extract from .hdf5 files
        ptypes=[0,0],
        ## what to call them in the UI
        UInames=['Gas','Gas1'],
        ## by what factor would we like to reduce the data for performance stability and disk space concerns
        decimation_factors=[decimation,decimation],
        ## what fields would we like to extract
        fields=['Density','Velocities','Temperature'],
        ## do we want to take the magnitude of any of these fields?
        magFlags=[False,False,False],
        ## do we want to take the log? 
        logFlags=[True,False,True],
        ## which fields do we want to be able to filter on?
        filterFlags=[True,True,True],
        ## which fields do we want to be able to colormap by?
        colormapFlags=[True,True,True],
        ## where should the output .json files be saved to? 
        ##  if a relative path is given, like here, saves to $HOME/<JSONdir>
        ##  and creates a soft-link to firefly/static/data
        JSONdir="FIREData_50_%d"%decimation,
        ## overwrite the existing startup.json file
        write_startup='append',
        tweenParams=my_tween)

    ## fetch data from .hdf5 files
    reader.loadData()

    ## set the color and size of the gas and star particles
    ##  to be aesthetically pleasing
    reader.settings['color']['Gas']=[1,0,0,1]
    reader.settings['sizeMult']['Gas']=1
    reader.settings['color']['Gas1']=[1,0,0,1]
    reader.settings['sizeMult']['Gas1']=1
    reader.settings['camera'] = [0,0,-20]
    reader.settings['showfps'] = True
    reader.settings['start_tween'] = True

    return reader

target_data = os.path.join(os.environ['HOME'],'FPS_test','static','data')
for decimation in [1,10,100]:
    reader = make_test_scene(decimation)
    
    if decimation == 1:
        reader.copyFireflySourceToTarget("FPS_test")
    else:
        reader.static_data_dir = target_data
        reader.dumpToJSON(symlink=False)
    
    


# In[12]:


from firefly.server import spawnFireflyServer,killAllFireflyServers

killAllFireflyServers()
spawnFireflyServer()


# In[7]:


killAllFireflyServers()


# In[ ]:




