import datetime
import matplotlib.pyplot as plt
import numpy as np

from geospacelab import preferences as pref
pref.user_config['visualization']['mpl']['style'] = 'dark'  # or 'light'

import geospacelab.visualization.mpl.dashboards as dashboards


def test_grace_acc():
    # Set the starting and stopping time
    dt_fr = datetime.datetime(2004, 3, 9, 0)
    dt_to = datetime.datetime(2004, 3, 12, 23, 59)
    add_APEX = True     # if True, "SC_APEX_LAT" and "SC_APEX_LON" will be added, default is False

    # Create a dashboard object, equivalent to a datahub object, however, with the additional visulization control.
    db = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to, figure_config={'figsize': (12, 8)})

    # Dock the datasets. Different datasets store different types of data.
    # Dock the SWARM-A DNS-POD data
    ds_A = db.dock(datasource_contents=['tud', 'grace', 'dns_acc'], sat_id='A', product_version='v01', add_APEX=add_APEX)
    # Dock the SWARM-C DNS-POD data
    ds_B = db.dock(datasource_contents=['tud', 'grace', 'dns_acc'], sat_id='B', product_version='v02', add_APEX=add_APEX)

    # Assign variables from the datasets for visualization.
    rho_n_A = db.assign_variable('rho_n', dataset=ds_A)
    rho_n_B = db.assign_variable('rho_n', dataset=ds_B)
    rho_n_A.visual.axis[1].label = r'$\rho$'
    rho_n_A.visual.axis[2].label = 'GRACE-A'
    rho_n_B.visual.axis[2].label = 'GRACE-B'

    glat_A = db.assign_variable('SC_GEO_LAT', dataset=ds_A)
    glat_B = db.assign_variable('SC_GEO_LAT', dataset=ds_B)
    glat_A.visual.axis[2].label = 'GRACE-A'
    glat_B.visual.axis[2].label = 'GRACE-B'

    glon_A = db.assign_variable('SC_GEO_LON', dataset=ds_A)
    glon_B = db.assign_variable('SC_GEO_LON', dataset=ds_B)
    lst_A = db.assign_variable('SC_GEO_LST', dataset=ds_A)
    
    glon_A.visual.axis[2].label = 'GRACE-A'
    glon_B.visual.axis[2].label = 'GRACE-C'
    # Dock the dataset for the geomagnetic activity indices.
    ds1 = db.dock(datasource_contents=['wdc', 'asysym'])
    sym_h = db.assign_variable('SYM_H', dataset=ds1)

    # Set the plotting layout
    db.set_layout([[sym_h], [rho_n_A, rho_n_B], [glat_A, glat_B], [glon_A, [lst_A]]])
    db.draw()
    # plt.savefig('swarm_example', dpi=300)
    plt.show()

    # Extract the data array from variables:
    rho_n_A_array = rho_n_A.value

def test_grace_wind():
    # Set the starting and stopping time
    dt_fr = datetime.datetime(2015, 2, 15, 0)
    dt_to = datetime.datetime(2015, 2, 15, 23, 59)
    add_APEX = True     # if True, "SC_APEX_LAT" and "SC_APEX_LON" will be added, default is False

    # Create a dashboard object, equivalent to a datahub object, however, with the additional visulization control.
    db = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to, figure_config={'figsize': (12, 8)})

    # Dock the datasets. Different datasets store different types of data.
    # Dock the SWARM-A DNS-POD data
    ds_A = db.dock(datasource_contents=['tud', 'grace', 'wnd_acc'], sat_id='A', product_version='v02', add_APEX=add_APEX)
    # Dock the SWARM-C DNS-POD data
    ds_B = db.dock(datasource_contents=['tud', 'grace', 'wnd_acc'], sat_id='B', product_version='v02', add_APEX=add_APEX)

    # Assign variables from the datasets for visualization.
    u_A = db.assign_variable('u_CROSS', dataset=ds_A)
    u_B = db.assign_variable('u_CROSS', dataset=ds_B)
    u_A.visual.axis[1].label = r'$u$'
    u_A.visual.axis[2].label = 'GRACE-A'
    u_B.visual.axis[2].label = 'GRACE-B'

    glat_A = db.assign_variable('SC_GEO_LAT', dataset=ds_A)
    glat_B = db.assign_variable('SC_GEO_LAT', dataset=ds_B)
    glat_A.visual.axis[2].label = 'GRACE-A'
    glat_B.visual.axis[2].label = 'GRACE-B'

    glon_A = db.assign_variable('SC_GEO_LON', dataset=ds_A)
    glon_B = db.assign_variable('SC_GEO_LON', dataset=ds_B)
    lst_A = db.assign_variable('SC_GEO_LST', dataset=ds_A)
    
    glon_A.visual.axis[2].label = 'GRACE-A'
    glon_B.visual.axis[2].label = 'GRACE-C'
    # Dock the dataset for the geomagnetic activity indices.
    ds1 = db.dock(datasource_contents=['wdc', 'asysym'])
    sym_h = db.assign_variable('SYM_H', dataset=ds1)

    # Set the plotting layout
    db.set_layout([[sym_h], [u_A, u_B], [glat_A, glat_B], [glon_A, [lst_A]]])
    db.draw()
    # plt.savefig('swarm_example', dpi=300)
    plt.show()

    # Extract the data array from variables:
    rho_n_A_array = u_A.value


def test_gracefo_acc():
    # Set the starting and stopping time
    dt_fr = datetime.datetime(2020, 3, 9, 0)
    dt_to = datetime.datetime(2020, 3, 12, 23, 59)
    add_APEX = True     # if True, "SC_APEX_LAT" and "SC_APEX_LON" will be added, default is False

    # Create a dashboard object, equivalent to a datahub object, however, with the additional visulization control.
    db = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to, figure_config={'figsize': (12, 8)})

    # Dock the datasets. Different datasets store different types of data.
    # Dock the SWARM-A DNS-POD data
    ds_C = db.dock(datasource_contents=['tud', 'grace_fo', 'dns_acc'], sat_id='FO1', product_version='v02', add_APEX=add_APEX)

    # Assign variables from the datasets for visualization.
    rho_n_C = db.assign_variable('rho_n', dataset=ds_C)
    rho_n_mean_C = db.assign_variable('rho_n_MEAN', dataset=ds_C)
    rho_n_C.visual.axis[1].label = r'$\rho$'
    rho_n_C.visual.axis[2].label = 'GRACE-C'

    glat_C = db.assign_variable('SC_GEO_LAT', dataset=ds_C)
    glat_C.visual.axis[2].label = 'GRACE-FO1'

    glon_C = db.assign_variable('SC_GEO_LON', dataset=ds_C)
    lst_C = db.assign_variable('SC_GEO_LST', dataset=ds_C)
    
    glon_C.visual.axis[2].label = 'GRACE-FO1'
    # Dock the dataset for the geomagnetic activity indices.
    ds1 = db.dock(datasource_contents=['wdc', 'asysym'])
    sym_h = db.assign_variable('SYM_H', dataset=ds1)

    # Set the plotting layout
    db.set_layout([[sym_h], [rho_n_C, rho_n_mean_C], [glat_C], [glon_C, [lst_C]]])
    db.draw()
    # plt.savefig('swarm_example', dpi=300)
    plt.show()

    # Extract the data array from variables:
    rho_n_A_array = rho_n_C.value
    
if __name__ == "__main__":
    test_grace_acc()
    test_grace_wind()
    test_gracefo_acc() 
    # test_swarm_pod_acc()