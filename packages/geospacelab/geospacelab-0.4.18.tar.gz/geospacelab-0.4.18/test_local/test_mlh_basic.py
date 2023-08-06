import datetime
import matplotlib.pyplot as plt

import geospacelab.visualization.mpl.dashboards as dashboards


def test():
    dt_fr = datetime.datetime(2016, 3, 14, 18)
    dt_to = datetime.datetime(2016, 3, 15, 2, 0,)
    dashboard = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to)
    ds1 = dashboard.dock(
        datasource_contents=['madrigal', 'isr', 'millstonehill', 'basic'], data_file_type='combined',
        antenna='zenith', pulse_code='single pulse', pulse_length=480)
    ds1.select_beams(az_el_pairs=[[-13.5, 45]])
    n_e = dashboard.assign_variable('n_e')
    T_e = dashboard.assign_variable('T_e')
    T_i = dashboard.assign_variable('T_i')
    v_i_los = dashboard.assign_variable('v_i_los')
    az = dashboard.assign_variable('AZ')
    el = dashboard.assign_variable('EL')

    ds2 = dashboard.dock(
        datasource_contents=['madrigal', 'isr', 'millstonehill', 'gridded'])
    layout = [[n_e], [T_e], [T_i], [v_i_los], [az, [el]]]
    # layout = [[Bz, By], [v_sw], [n_p], [sym_h]]
    dashboard.set_layout(panel_layouts=layout, hspace=0.1)
    dashboard.draw()

    dashboard.save_figure(file_name='mlh_basic', append_time=True)
    pass


if __name__ == "__main__":
    test()
    plt.show()
