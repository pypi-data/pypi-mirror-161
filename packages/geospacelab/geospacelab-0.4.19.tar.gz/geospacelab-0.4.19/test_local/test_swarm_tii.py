import datetime
import matplotlib.pyplot as plt
import numpy as np

import geospacelab.visualization.mpl.dashboards as dashboards


def test_swarm():
    dt_fr = datetime.datetime(2014, 8, 28, 7, 16)
    dt_to = datetime.datetime(2014, 8, 28, 7, 36)
    # specify the file full path

    db = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to, figure_config={'figsize': (8, 8)})

    db.dock(datasource_contents=['esa_eo', 'swarm', 'advanced', 'efi_lp_hm'], product='LP_HM', sat_id='A', quality_control=False)

    n_e = db.assign_variable('n_e')
    T_e = db.assign_variable('T_e')
    flag = db.assign_variable('QUALITY_FLAG')
    
    ds_tii = db.dock(
        datasource_contents=['esa_eo', 'swarm', 'advanced', 'efi_tct02'], 
        product='TCT02', sat_id='A', quality_control=False
        )

    v_i_H_x = db.assign_variable('v_i_H_x', dataset=ds_tii)
    v_i_H_y = db.assign_variable('v_i_H_y', dataset=ds_tii)
    v_i_V_x = db.assign_variable('v_i_V_x', dataset=ds_tii)
    v_i_V_z = db.assign_variable('v_i_V_z', dataset=ds_tii)

    db.set_layout(panel_layouts=[[n_e], [T_e], [v_i_H_x, v_i_H_y, v_i_V_x, v_i_V_z], [flag]])
    db.draw()
    plt.savefig('swarm_example', dpi=300)
    plt.show()


if __name__ == "__main__":
    test_swarm()
