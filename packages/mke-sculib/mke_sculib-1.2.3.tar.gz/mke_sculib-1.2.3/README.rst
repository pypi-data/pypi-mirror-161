.. highlight:: rst

============================
mke_sculib
============================

MeerKAT Extension (MKE)
(SCU) Science Computation Unit interface (lib)rary for the MKE antennas and some basic simulators

-----------------
Installing
-----------------

.. code-block:: bash
   pip install mke-sculib


-----------------
Usage for Antenna Control:
-----------------

In order to connect to the REST API of the Telescope SCU use the library as follows:

.. code-block:: python
   from mke_sculib.scu import scu
   mpi = scu('134.104.22.44', '8080')

 

-----------------
Usage as Simulator:
-----------------

Using the simulator with the same script as used for operating the telescope can be 
achieved like this:

.. code-block:: python
   from mke_sculib.sim import plot_motion_pyplot as plot_motion
   
   # instead of THIS:
   # from mke_sculib.scu import scu
   # mpi = scu('134.104.22.44', '8080')

   # do THIS for simulation:
   from mke_sculib.sim import scu_sim as scu
   mpi = scu()

After a test has been done, the whole test history can be plotted in pyplot via:

.. code-block:: python
   # show the history data
   dfh = mpi.get_history_df(interval_ms = None)
   axs = plot_motion(dfh)

-----------------
Using the library within Test Scripts:
-----------------

After installation, the library can be used to script automatic tests. A minimal 
example for a tracking test is given below:


.. code-block:: python
   # Init
   import astropy.units as u
   from astropy.time import Time
   import numpy as np
   import pandas as pd

   import matplotlib.pyplot as plt
   from mke_sculib.sim import plot_motion_pyplot as plot_motion
   from mke_sculib.sim import scu_sim as scu

   mpi = scu()

   # Startup 
   mpi.unstow()
   mpi.wait_duration(30) # sec
   mpi.activate_dmc()
   mpi.wait_duration(wait10)

   # Move to starting az, el
   mpi.abs_azimuth(-90, 3) # degree, degree / s
   mpi.abs_elevation(53, 1) # degree, degree / s
   mpi.wait_settle()
   mpi.wait_duration(5) # sec

   # move to Band 2
   mpi.move_to_band('Band 2')
   mpi.wait_settle()
   mpi.wait_duration(wait5)

   # make a dummy tracking table
   t = mpi.t_internal + (np.arange(5) * astropy.units.u.s)
   az = np.linspace(-90, -89, len(t))
   el = np.linspace(53, 54, len(t))

   # start a tracking table
   mpi.upload_track_table(t, az, el)

   # start logging for my testrun
   mpi.start_logger('full_configuration')
   
   # wait for track table to finish
   mpi.wait_duration(np.ptp(t) + 5)

   # shut down
   mpi.stop_logger()
   mpi.wait_duration(5)
   mpi.deactivate_dmc()
   mpi.wait_duration(10)
   mpi.stow()

   # show the sessions data
   df = mpi.get_session_as_df(interval_ms = 100)
   plot_motion(df)
   df.to_csv('testdata_acu.csv')


See also `scripts` for examples on how to use this library


HTTP Dummy server
=====

This library has a dummy server with dashboard implemented which can run on any machine with anaconda installed. 

See: `servers` for the examples. 

NOTE: Change the absolut path in the files if necessary

.. code-block:: bash
   python /servers/dashboard.py