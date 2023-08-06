import datetime
import matplotlib.pyplot as plt
import numpy as np

from geospacelab import preferences as pref
pref.user_config['visualization']['mpl']['style'] = 'dark'  # or 'light'

import geospacelab.visualization.mpl.dashboards as dashboards

def test_champ_acc():
    # Set the starting and stopping time
    dt_fr = datetime.datetime(2005, 1, 20, 0)
    dt_to = datetime.datetime(2005, 1, 20, 23, 59)
    add_APEX = True     # if True, "SC_APEX_LAT" and "SC_APEX_LON" will be added, default is False

    # Create a dashboard object, equivalent to a datahub object, however, with the additional visulization control.
    db = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to, figure_config={'figsize': (12, 8)})

    # Dock the datasets. Different datasets store different types of data.
    # Dock the SWARM-A DNS-POD data
    ds_CH = db.dock(datasource_contents=['tud', 'champ', 'dns_acc'], add_APEX=add_APEX)
    ds_CH2 = db.dock(datasource_contents=['tud', 'champ', 'wnd_acc'], add_APEX=add_APEX) 
    # Assign variables from the datasets for visualization.
    rho_n_CH = db.assign_variable('rho_n', dataset=ds_CH)
    u_CROSS = db.assign_variable('u_CROSS', dataset=ds_CH2)
    u_E = db.assign_variable('u_CROSS_E', dataset=ds_CH2)
    u_N = db.assign_variable('u_CROSS_N', dataset=ds_CH2)
    u_U = db.assign_variable('u_CROSS_U', dataset=ds_CH2)

    glat_CH = db.assign_variable('SC_GEO_LAT', dataset=ds_CH)
    glat_CH.visual.axis[2].label = 'CHCE'

    glon_CH = db.assign_variable('SC_GEO_LON', dataset=ds_CH)
    lst_CH = db.assign_variable('SC_GEO_LST', dataset=ds_CH)
    
    glon_CH.visual.axis[2].label = 'CHAMP'
    # Dock the dataset for the geomagnetic activity indices.
    ds1 = db.dock(datasource_contents=['wdc', 'asysym'])
    sym_h = db.assign_variable('SYM_H', dataset=ds1)

    # Set the plotting layout
    db.set_layout([[sym_h], [rho_n_CH], [u_CROSS], [u_E, u_N, u_U], [glat_CH], [glon_CH, [lst_CH]]])
    db.draw()
    # plt.savefig('swarm_example', dpi=300)
    plt.show()

    # Extract the data array from variables:
    rho_n_A_array = rho_n_CH.value
    
if __name__ == "__main__":
    # test_grace_acc()
    # test_grace_wind()
    test_champ_acc() 