import datetime
import matplotlib.pyplot as plt

import geospacelab.visualization.mpl.dashboards as dashboards


def test():
    dt_fr = datetime.datetime(2016, 3, 14, 0)
    dt_to = datetime.datetime(2016, 3, 15, 23,)
    dashboard = dashboards.TSDashboard(dt_fr=dt_fr, dt_to=dt_to)
    ds1 = dashboard.dock(
        datasource_contents=['madrigal', 'isr', 'millstonehill', 'vi'])

    ds2 = dashboard.dock(
        datasource_contents=['madrigal', 'isr', 'millstonehill', 'gridded'])
    v_i_N = dashboard.assign_variable('v_i_N', dataset=ds1)
    v_i_E = dashboard.assign_variable('v_i_E', dataset=ds1)
    v_i_Z = dashboard.assign_variable('v_i_Z', dataset=ds1)
    E_E = dashboard.assign_variable('E_E', dataset=ds1)
    E_N = dashboard.assign_variable('E_N', dataset=ds1)

    n_e = dashboard.assign_variable('n_e', dataset=ds2)
    T_e = dashboard.assign_variable('T_e', dataset=ds2)
    T_i = dashboard.assign_variable('T_i', dataset=ds2)
    v_i_up = dashboard.assign_variable('v_i_UP', dataset=ds2)

    # ds2 = dashboard.dock(
    #     datasource_contents=['madrigal', 'isr', 'millstonehill', 'gridded'])
    layout = [[n_e], [v_i_up], [T_e], [T_i]]
    # layout = [[Bz, By], [v_sw], [n_p], [sym_h]]
    dashboard.set_layout(panel_layouts=layout, hspace=0.1)
    dashboard.draw()
    # dashboard.save_figure(file_name='example_omni_6', append_time=False)
    pass


def example(dt_fr, dt_to):

    #dt_fr = datetime.datetime.strptime('20160315' + '1200', '%Y%m%d%H%M')
    #dt_to = datetime.datetime.strptime('20160316' + '1200', '%Y%m%d%H%M')

    antenna = 'misa'
    pulse_code = 'alternating'
    pulse_length = 480
    load_mode = 'AUTO'
    dashboard = MillstoneHillISRDashboard(
        dt_fr, dt_to, antenna=antenna, pulse_code=pulse_code, pulse_length=pulse_length,
    )
    dashboard.select_beams(az_el_pairs=[[-40.5, 45]])
    dashboard.quicklook()
    dashboard.save_figure()
    # dashboard.show()

def example2():

    for i in range(6):
        dt0 = datetime.datetime(2016, 3, 13)
        example(dt_fr=dt0 + datetime.timedelta(days=i, hours=12), dt_to = dt0 + datetime.timedelta(days=i+1, hours=12))

if __name__ == '__main__':
    example2()
