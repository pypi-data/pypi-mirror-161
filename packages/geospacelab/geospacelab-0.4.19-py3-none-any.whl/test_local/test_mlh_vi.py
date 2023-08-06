import datetime
import matplotlib.pyplot as plt

import geospacelab.visualization.mpl.dashboards as dashboards


def test():
    dt_fr = datetime.datetime(2016, 3, 14, 18)
    dt_to = datetime.datetime(2016, 3, 15, 2,)
    dashboard = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to)
    ds1 = dashboard.dock(
        datasource_contents=['madrigal', 'isr', 'millstonehill', 'vi'])

    ds2 = dashboard.dock(
        datasource_contents=['madrigal', 'isr', 'millstonehill', 'gridded'])
    ds3 = dashboard.dock(
        datasource_contents=['madrigal', 'isr', 'millstonehill', 'basic'], data_file_type='combined',
        antenna='zenith', pulse_code='single pulse', pulse_length=480)
    v_i_N = dashboard.assign_variable('v_i_N', dataset=ds1)
    v_i_E = dashboard.assign_variable('v_i_E', dataset=ds1)
    v_i_Z = dashboard.assign_variable('v_i_Z', dataset=ds1)
    E_E = dashboard.assign_variable('E_E', dataset=ds1)
    E_N = dashboard.assign_variable('E_N', dataset=ds1)

    n_e = dashboard.assign_variable('n_e', dataset=ds3)

    v_i_Z.visual.axis[2].lim = [-80, 80]

    # ds2 = dashboard.dock(
    #     datasource_contents=['madrigal', 'isr', 'millstonehill', 'gridded'])
    layout = [[n_e], [v_i_Z], [v_i_E], [v_i_N], [E_E], [E_N]]
    # layout = [[Bz, By], [v_sw], [n_p], [sym_h]]
    dashboard.set_layout(panel_layouts=layout, hspace=0.1)
    dashboard.draw()
    # dashboard.save_figure(file_name='example_omni_6', append_time=False)
    pass


if __name__ == "__main__":
    test()
    plt.show()
