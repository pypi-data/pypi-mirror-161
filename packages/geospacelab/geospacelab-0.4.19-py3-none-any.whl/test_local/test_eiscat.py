import datetime
import geospacelab.express.eiscat_dashboard as eiscat

dt_fr = datetime.datetime.strptime('20201121' + '2100', '%Y%m%d%H%M')
dt_to = datetime.datetime.strptime('20201122' + '0300', '%Y%m%d%H%M')

site = 'UHF'
antenna = 'UHF'
modulation = 'ant'
load_mode = 'AUTO'
dashboard = eiscat.EISCATDashboard(
    dt_fr, dt_to, site=site, antenna=antenna, modulation=modulation, load_mode='AUTO'
)
dashboard.quicklook()

# dashboard.save_figure() # comment this if you need to run the following codes
# dashboard.show()   # comment this if you need to run the following codes.

"""
As the dashboard class (EISCATDashboard) is a inheritance of the classes Datahub and TSDashboard.
The variables can be retrieved in the same ways as shown in Example 1. 
"""
n_e = dashboard.assign_variable('n_e')
aalat_arr = dashboard.assign_variable('AACGM_LAT').value
height_arr = dashboard.assign_variable('HEIGHT').value
h_beam1 = height_arr[0,:]
print(h_beam1)

print(aalat_arr[0, 26], aalat_arr[3, 26], aalat_arr[1, 26])

print(n_e.value)
print(n_e.error)

"""
Several marking tools (vertical lines, shadings, and top bars) can be added as the overlays 
on the top of the quicklook plot.
"""
# add vertical line
dt_fr_2 = datetime.datetime.strptime('20201121' + '2230', "%Y%m%d%H%M")
dt_to_2 = datetime.datetime.strptime('20201122' + '0130', "%Y%m%d%H%M")
dashboard.add_vertical_line(dt_fr_2, bottom_extend=0, top_extend=0.02, label='Line 1', label_position='top')
# add shading
dashboard.add_shading(dt_fr_2, dt_to_2, bottom_extend=0, top_extend=0.02, label='Shading 1', label_position='top')
# add top bar
dt_fr_3 = datetime.datetime.strptime('20201122' + '0130', "%Y%m%d%H%M")
dt_to_3 = datetime.datetime.strptime('20201122' + '0230', "%Y%m%d%H%M")
dashboard.add_top_bar(dt_fr_3, dt_to_3, bottom=0., top=0.02, label='Top bar 1')

# save figure
# dashboard.save_figure()
# show on screen
dashboard.show()