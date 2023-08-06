import datetime
import matplotlib.pyplot as plt
import numpy as np

from geospacelab import preferences as pref
pref.user_config['visualization']['mpl']['style'] = 'dark'  # or 'light'

import geospacelab.visualization.mpl.dashboards as dashboards


def test_swarm_pod():
    # Set the starting and stopping time
    dt_fr = datetime.datetime(2020, 3, 6, 11)
    dt_to = datetime.datetime(2020, 3, 9, 18, 59)
    add_APEX = True     # if True, "SC_APEX_LAT" and "SC_APEX_LON" will be added, default is False

    # Create a dashboard object, equivalent to a datahub object, however, with the additional visulization control.
    db = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to, figure_config={'figsize': (12, 8)})

    # Dock the datasets. Different datasets store different types of data.
    # Dock the SWARM-A DNS-POD data
    ds_A = db.dock(datasource_contents=['tud', 'swarm', 'dns_pod'], sat_id='A', add_APEX=add_APEX)
    # Dock the SWARM-C DNS-POD data
    ds_C = db.dock(datasource_contents=['tud', 'swarm', 'dns_pod'], sat_id='C', add_APEX=add_APEX)

    # Assign variables from the datasets for visualization.
    rho_n_A = db.assign_variable('rho_n', dataset=ds_A)
    rho_n_C = db.assign_variable('rho_n', dataset=ds_C)
    rho_n_A.visual.axis[1].label = r'$\rho$'
    rho_n_A.visual.axis[2].label = 'Swarm-A'
    rho_n_C.visual.axis[2].label = 'Swarm-C'

    glat_A = db.assign_variable('SC_GEO_LAT', dataset=ds_A)
    glat_C = db.assign_variable('SC_GEO_LAT', dataset=ds_A)
    glat_A.visual.axis[2].label = 'Swarm-A'
    glat_C.visual.axis[2].label = 'Swarm-C'

    glon_A = db.assign_variable('SC_GEO_LON', dataset=ds_A)
    glon_C = db.assign_variable('SC_GEO_LON', dataset=ds_C)
    lst_A = db.assign_variable('SC_GEO_LST', dataset=ds_A)
    
    glon_A.visual.axis[2].label = 'Swarm-A'
    glon_C.visual.axis[2].label = 'Swarm-C'
    # Dock the dataset for the geomagnetic activity indices.
    ds1 = db.dock(datasource_contents=['wdc', 'asysym'])
    sym_h = db.assign_variable('SYM_H', dataset=ds1)

    # Set the plotting layout
    db.set_layout([[sym_h], [rho_n_A, rho_n_C], [glat_A, glat_C], [glon_A, [lst_A]]])
    db.draw()
    # plt.savefig('swarm_example', dpi=300)
    plt.show()

    # Extract the data array from variables:
    rho_n_A_array = rho_n_A.value


def test_swarm_pod_acc():
    # Set the starting and stopping time
    dt_fr = datetime.datetime(2015, 12, 21, 11)
    dt_to = datetime.datetime(2015, 12, 21, 18, 59)

    # Create a dashboard object, equivalent to a datahub object, however, with the additional visulization control.
    db = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to, figure='new', figure_config={'figsize': (12, 8)})

    # Dock the datasets. Different datasets store different types of data.
    # Dock the SWARM-A DNS-POD data
    ds_pod = db.dock(datasource_contents=['tud', 'swarm', 'dns_pod'], sat_id='C')
    ds_acc = db.dock(datasource_contents=['tud', 'swarm', 'dns_acc'], sat_id='C')

    # Assign variables from the datasets for visualization.
    rho_n_pod = db.assign_variable('rho_n', dataset=ds_pod)
    rho_n_acc = db.assign_variable('rho_n', dataset=ds_acc)
    rho_n_pod.visual.axis[1].label = r'$\rho$'
    rho_n_pod.visual.axis[2].label = 'POD'
    rho_n_acc.visual.axis[2].label = 'ACC'

    glat = db.assign_variable('SC_GEO_LAT', dataset=ds_pod)
    glon = db.assign_variable('SC_GEO_LON', dataset=ds_pod)

    db.set_layout([[rho_n_pod, rho_n_acc], [glat], [glon]])
    db.draw()
    # plt.savefig('swarm_example', dpi=300)
    plt.show()


if __name__ == "__main__":
    test_swarm_pod()
    # test_swarm_pod_acc()