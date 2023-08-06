from tkinter import TRUE
import scipy.io as sio
import pathlib
import datetime
import numpy as np
import pandas as pd

from geospacelab.datahub import DatasetUser
from geospacelab.visualization.mpl.dashboards import TSDashboard
from geospacelab.cs import GEOCSpherical
import geospacelab.visualization.mpl.geomap.geodashboards as geomap


def visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N'):
    
    ds_swarm_pf = load_swarm_poynting_flux(swarm_dn, swarm_sat_id)
    
    band = 'LBHS'
    dt_fr = dmsp_dn - datetime.timedelta(minutes=60)
    dt_to = dmsp_dn + datetime.timedelta(minutes=60)
    time1 = dmsp_dn
    sat_id = dmsp_sat_id
    orbit_id = dmsp_orbit_id

    # Create a geodashboard object
    dashboard = geomap.GeoDashboard(dt_fr=dt_fr, dt_to=dt_to, figure_config={'figsize': (18, 15)})

    # If the orbit_id is specified, only one file will be downloaded. This option saves the downloading time.
    # dashboard.dock(datasource_contents=['jhuapl', 'dmsp', 'ssusi', 'edraur'], pole='N', sat_id='f17', orbit_id='46863')
    # If not specified, the data during the whole day will be downloaded.
    dashboard.dock(datasource_contents=['jhuapl', 'dmsp', 'ssusi', 'edraur'], pole=pole, sat_id=sat_id, orbit_id=orbit_id)
    ds_s1 = dashboard.dock(
        datasource_contents=['madrigal', 'satellites', 'dmsp', 's1'],
        dt_fr=time1 - datetime.timedelta(minutes=45),
        dt_to=time1 + datetime.timedelta(minutes=45),
        sat_id=sat_id, replace_orbit=True)

    dashboard.set_layout(1, 1, left=0.05, right=0.3, top=0.7, hspace=0.02)

    # Get the variables: LBHS emission intensiy, corresponding times and locations
    lbhs = dashboard.assign_variable('GRID_AUR_' + band, dataset_index=1)
    dts = dashboard.assign_variable('DATETIME', dataset_index=1).value.flatten()
    mlat = dashboard.assign_variable('GRID_MLAT', dataset_index=1).value
    mlon = dashboard.assign_variable('GRID_MLON', dataset_index=1).value
    mlt = dashboard.assign_variable(('GRID_MLT'), dataset_index=1).value

    # Search the index for the time to plot, used as an input to the following polar map
    ind_t = dashboard.datasets[1].get_time_ind(ut=time1)
    if (dts[ind_t] - time1).total_seconds()/60 > 60:     # in minutes
        raise ValueError("The time does not match any SSUSI data!")
    lbhs_ = lbhs.value[ind_t]
    mlat_ = mlat[ind_t]
    mlon_ = mlon[ind_t]
    mlt_ = mlt[ind_t]
    # Add a polar map panel to the dashboard. Currently the style is the fixed MLT at mlt_c=0. See the keywords below:
    panel1 = dashboard.add_polar_map(
        row_ind=0, col_ind=0, style='mlt-fixed', cs='AACGM',
        mlt_c=0., pole=pole, ut=time1, boundary_lat=55., mirror_south=True
    )

    # Some settings for plotting.
    pcolormesh_config = lbhs.visual.plot_config.pcolormesh
    # Overlay the SSUSI image in the map.
    ipc = panel1.overlay_pcolormesh(
        data=lbhs_, coords={'lat': mlat_, 'lon': mlon_, 'mlt': mlt_}, cs='AACGM', **pcolormesh_config)
    # Add a color bar
    panel1.add_colorbar(ipc, c_label=band + " (R)", c_scale=pcolormesh_config['c_scale'], left=1.1, bottom=0.1,
                        width=0.05, height=0.7)

    # Overlay the gridlines
    panel1.overlay_gridlines(lat_res=5, lon_label_separator=5)

    # Overlay the coastlines in the AACGM coordinate
    panel1.overlay_coastlines()

    # Overlay cross-track velocity along satellite trajectory
    sc_dt = ds_s1['SC_DATETIME'].value.flatten()
    sc_lat = ds_s1['SC_GEO_LAT'].value.flatten()
    sc_lon = ds_s1['SC_GEO_LON'].value.flatten()
    sc_alt = ds_s1['SC_GEO_ALT'].value.flatten()
    sc_coords = {'lat': sc_lat, 'lon': sc_lon, 'height': sc_alt}

    v_H = ds_s1['v_i_H'].value.flatten()
    panel1.overlay_cross_track_vector(
        vector=v_H, unit_vector=1000, vector_unit='m/s', alpha=0.3, color='red',
        sc_coords=sc_coords, sc_ut=sc_dt, cs='GEO',
    )
    # Overlay the satellite trajectory with ticks
    panel1.overlay_sc_trajectory(sc_ut=sc_dt, sc_coords=sc_coords, cs='GEO')
    
    # Overlay swarm satellite trajectory
    sc2_dt = ds_swarm_pf['SC_DATETIME'].value.flatten()
    sc2_lat = ds_swarm_pf['SC_GEO_LAT'].value.flatten()
    sc2_lon = ds_swarm_pf['SC_GEO_LON'].value.flatten()
    sc2_alt = ds_swarm_pf['SC_GEO_ALT'].value.flatten()
    sc2_coords = {'lat': sc2_lat, 'lon': sc2_lon, 'height': sc2_alt}

    panel1.overlay_sc_trajectory(sc_ut=sc2_dt, sc_coords=sc2_coords, cs='GEO', color='m')

    # Overlay sites
    panel1.overlay_sites(site_ids=['TRO', 'ESR'], coords={'lat': [69.58, 78.15], 'lon': [19.23, 16.02], 'height': 0.}, cs='GEO', marker='^', markersize=2)

    # Add the title and save the figure
    polestr = 'North' if pole == 'N' else 'South'
    panel1.add_title(
            title='DMSP/SSUSI, ' + band + ', ' + sat_id.upper() + ', ' + polestr + ', ' + time1.strftime('%Y-%m-%d %H%M UT'))
    
    delta_t = 10
    dt_fr = swarm_dn - datetime.timedelta(minutes=delta_t)
    dt_to = swarm_dn + datetime.timedelta(minutes=delta_t)

    timeline_extra_labels = ['GEO_LAT', 'GEO_LON', 'AACGM_LAT', 'AACGM_MLT']
    db_swarm = TSDashboard(dt_fr=dt_fr, dt_to=dt_to, timeline_extra_labels=timeline_extra_labels, figure=dashboard.figure)
    
    db_swarm.add_dataset(ds_swarm_pf, kind='user-defined')
    
    pf_h = db_swarm.assign_variable('S_FA_H')
    pf_v = db_swarm.assign_variable('S_FA_V') 
    d_B_x = db_swarm.assign_variable('d_B_x')
    d_B_y = db_swarm.assign_variable('d_B_y')
    d_B_z = db_swarm.assign_variable('d_B_z')
    qflag = db_swarm.assign_variable('Q_FLAG')
    cflag = db_swarm.assign_variable('CALIB_FLAG')
    
    
    ds_lp = db_swarm.dock(
        datasource_contents=['esa_eo', 'swarm', 'advanced', 'efi_lp_hm'], 
        product='LP_HM', sat_id=swarm_sat_id, quality_control=False
        )

    n_e = db_swarm.assign_variable('n_e', dataset=ds_lp)
    T_e = db_swarm.assign_variable('T_e', dataset=ds_lp)
    
    ds_tii = db_swarm.dock(
        datasource_contents=['esa_eo', 'swarm', 'advanced', 'efi_tct02'], 
        product='TCT02', sat_id=swarm_sat_id, quality_control=False
        )

    v_i_H_x = db_swarm.assign_variable('v_i_H_x', dataset=ds_tii)
    v_i_H_y = db_swarm.assign_variable('v_i_H_y', dataset=ds_tii)
    v_i_V_x = db_swarm.assign_variable('v_i_V_x', dataset=ds_tii)
    v_i_V_z = db_swarm.assign_variable('v_i_V_z', dataset=ds_tii)
     
    db_swarm.set_layout([[n_e], [T_e], [d_B_x, d_B_y, d_B_z], [v_i_H_x, v_i_H_y, v_i_V_x, v_i_V_z], [pf_h, pf_v]],
                       left=0.5, right=0.9, top=0.7, hspace=0.6 )
    db_swarm.draw()
    
    """ SWARM/POD
    """
    try:
        db_rou = TSDashboard(dt_fr=dt_fr, dt_to=dt_to, figure=dashboard.figure)

        # Dock the datasets. Different datasets store different types of data.
        # Dock the SWARM-A DNS-POD data
        ds_pod = db_rou.dock(datasource_contents=['tud', 'swarm', 'dns_pod'], sat_id='C')
        ds_acc = db_rou.dock(datasource_contents=['tud', 'swarm', 'dns_acc'], sat_id='C')

        # Assign variables from the datasets for visualization.
        rho_n_pod = db_rou.assign_variable('rho_n', dataset=ds_pod)
        rho_n_acc = db_rou.assign_variable('rho_n', dataset=ds_acc)
        rho_n_pod.visual.axis[1].label = r'$\rho$'
        rho_n_pod.visual.axis[2].label = 'POD'
        rho_n_acc.visual.axis[2].label = 'ACC'

        glat = db_rou.assign_variable('SC_GEO_LAT', dataset=ds_pod)
        glon = db_rou.assign_variable('SC_GEO_LON', dataset=ds_pod)

        db_rou.set_layout([[rho_n_pod, rho_n_acc]], left=0.5, right=0.9, bottom=0.8, hspace=0.01)
        db_rou.draw()
    except:
        print(swarm_dn.strftime('%Y-%m-%d %H:%M UT'))
    
    db_swarm.add_title(title='SWARM-' + swarm_sat_id.upper() + ', ' + swarm_dn.strftime('%Y-%m-%d %H:%M UT'))
    db_swarm.save_figure(file_name = 'compare_v2_E' + swarm_dn.strftime('%Y-%m-%d') + '_SWARM-' + swarm_sat_id + '_DMSP-' + dmsp_sat_id.upper(), 
                         file_dir = pathlib.Path('/home/lei/01-Work/01-Project/OY22-IonosphereElectrodynamics/Lei_20220707/results'))
    # db_swarm.show()
    
    # return dashboard
    

def load_swarm_poynting_flux(dn0: datetime.datetime, sat_id):
    file_dir = pathlib.Path('/home/lei/01-Work/01-Project/OY22-IonosphereElectrodynamics/Lei_20220707/results')
    dstr = dn0.strftime('%Y%m%d-%H%M%S')
    file_path = list(file_dir.glob("*" + sat_id.upper() + "*" + dstr + '*.mat'))[0]
    matdata = sio.loadmat(file_path)
     
    ds = DatasetUser(visual='on')
    
    depend_0 = {
        'UT': 'SC_DATETIME', 
        'GEO_LAT': 'SC_GEO_LAT', 'GEO_LON': 'SC_GEO_LON', 
        'AACGM_LAT': 'SC_AACGM_LAT', 'AACGM_LON': 'SC_AACGM_LON', 'AACGM_MLT': 'SC_AACGM_MLT'
        }
    
    var_name = 'SC_DATETIME'
    var_value: np.ndarray = matdata['tl']
    ntl = var_value.shape[0]
    var_value = pd.to_datetime(var_value.flatten() - 719529, unit='D').to_numpy()
    var_value = [datetime.datetime.utcfromtimestamp(((var_value[i] - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')))
                 for i in range(ntl)]
    var_value = np.array(var_value, dtype=datetime.datetime).reshape((ntl, 1))
    ut = var_value.flatten()
    var = ds.add_variable(var_name, value=var_value)
    var.visual.plot_config.style = '1P'
    
    var_name = 'SC_GEO_LAT'
    var_value: np.ndarray = matdata['glat']
    glat = var_value.flatten()
    var_value = var_value.reshape((ntl, 1))
    var = ds.add_variable(var_name, value=var_value)
    var.visual.plot_config.style = '1P'
    
    var_name = 'SC_GEO_LON'
    var_value: np.ndarray = matdata['glon']
    var_value = var_value.reshape((ntl, 1))
    glon = var_value.flatten()
    var = ds.add_variable(var_name, value=var_value)
    var.visual.plot_config.style = '1P'
    
    var_name = 'SC_GEO_R'
    var_value: np.ndarray = matdata['gR']
    var_value = var_value.reshape((ntl, 1))
    r = var_value.flatten()
    var = ds.add_variable(var_name, value=var_value)
    var.visual.plot_config.style = '1P'
    
    var_name = 'S_FA_V'
    var_value: np.np.ndarray = matdata['Pvpara']
    var_value = var_value.reshape((ntl, 1))
    var = ds.add_variable(var_name, value=var_value)
    var.depends[0] = depend_0
    var.visual.plot_config.style = '1P'
    var.visual.axis[1].label = 'S'
    var.visual.axis[1].unit = r'W$\cdot$m$^{-3}$'
    var.visual.axis[2].label = r'S$^V$'
    
    var_name = 'S_FA_H'
    var_value: np.ndarray = matdata['Phpara']
    var_value = var_value.reshape((ntl, 1))
    var = ds.add_variable(var_name, value=var_value)
    var.depends[0] = depend_0
    var.visual.plot_config.style = '1P'
    var.visual.axis[1].label = 'S'
    var.visual.axis[1].unit = r'W$\cdot$m$^{-3}$'
    var.visual.axis[2].label = r'S$^H$'    
    
    var_name = 'd_B_x'
    var_value: np.ndarray = matdata['Bx']
    var_value = var_value.reshape((ntl, 1))
    var = ds.add_variable(var_name, value=var_value)
    var.depends[0] = depend_0
    var.visual.plot_config.style = '1P'
    var.visual.axis[1].label = 'B'
    var.visual.axis[1].unit = 'nT'
    var.visual.axis[2].label = r'$\delta B_x$'
    
    var_name = 'd_B_y'
    var_value: np.ndarray = matdata['By']
    var_value = var_value.reshape((ntl, 1))
    var = ds.add_variable(var_name, value=var_value)
    var.depends[0] = depend_0
    var.visual.plot_config.style = '1P'
    var.visual.axis[2].label = r'$\delta B_y$'
    
    var_name = 'd_B_z'
    var_value: np.ndarray = matdata['Bz']
    var_value = var_value.reshape((ntl, 1))
    var = ds.add_variable(var_name, value=var_value)
    var.depends[0] = depend_0
    var.visual.plot_config.style = '1P'
    var.visual.axis[2].label = r'$\delta B_z$'
    
    var_name = 'Q_FLAG'
    var_value: np.ndarray = matdata['tmpQ']
    var_value = var_value.reshape((ntl, 1))
    var = ds.add_variable(var_name, value=var_value)
    var.depends[0] = depend_0
    var.visual.plot_config.style = '1P'
    var.visual.axis[1].label = 'FLAG'
    var.visual.axis[2].label = r'Quality=1 OK'
    
    var_name = 'CALIB_FLAG'
    var_value: np.ndarray = matdata['tmpC']
    var_value = var_value.reshape((ntl, 1))
    var = ds.add_variable(var_name, value=var_value)
    var.depends[0] = depend_0
    var.visual.plot_config.style = '1P'
    var.visual.axis[1].label = 'FLAG'
    var.visual.axis[2].label = r'Calib=0 OK'

    cs = GEOCSpherical(coords={'lat': glat, 'lon': glon, 'r': r/6371.2}, ut=ut)
    cs_new = cs.to_AACGM(append_mlt=True)
    var = ds.add_variable('SC_AACGM_LAT', value=cs_new['lat'])
    var = ds.add_variable('SC_AACGM_LON', value=cs_new['lon'])
    var = ds.add_variable('SC_AACGM_MLT', value=cs_new['mlt'])
    var = ds.add_variable('SC_GEO_ALT', value=ds['SC_GEO_R'].value - 6371.2)

    
    return ds


def event_1_1():
    dmsp_dn = datetime.datetime.strptime('20151221' + '131300', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f19'
    dmsp_orbit_id = '08855'
    
    swarm_dn = datetime.datetime.strptime('20151221' + '130400', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='S')
    
    
def event_1_2():
    dmsp_dn = datetime.datetime.strptime('20151221' + '115700', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f16'
    dmsp_orbit_id = '62817'
    
    swarm_dn = datetime.datetime.strptime('20151221' + '130400', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='S')
    
    
def event_1_3():
    dmsp_dn = datetime.datetime.strptime('20151221' + '145300', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f19'
    dmsp_orbit_id = '08856'
    
    swarm_dn = datetime.datetime.strptime('20151221' + '143600', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='S')    
    
def event_1_4():
    dmsp_dn = datetime.datetime.strptime('20151221' + '163300', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f19'
    dmsp_orbit_id = '08857'
    
    swarm_dn = datetime.datetime.strptime('20151221' + '160700', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='S')   
    
def event_1_5():
    dmsp_dn = datetime.datetime.strptime('20151221' + '133700', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f16'
    dmsp_orbit_id = '62818'
    
    swarm_dn = datetime.datetime.strptime('20151221' + '141000', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='S')       
    
def event_1_6():
    dmsp_dn = datetime.datetime.strptime('20151221' + '145300', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f19'
    dmsp_orbit_id = '08856'
    
    swarm_dn = datetime.datetime.strptime('20151221' + '141000', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='S') 
     
def event_1_7():
    dmsp_dn = datetime.datetime.strptime('20151221' + '151700', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f16'
    dmsp_orbit_id = '62819'
    
    swarm_dn = datetime.datetime.strptime('20151221' + '154400', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='S')    
    
def event_2_1():
    dmsp_dn = datetime.datetime.strptime('20150908' + '183800', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f17'
    dmsp_orbit_id = '45631'
    
    swarm_dn = datetime.datetime.strptime('20150908' + '175800', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')   
    
def event_2_2():
    dmsp_dn = datetime.datetime.strptime('20150908' + '185900', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '30373'
    
    swarm_dn = datetime.datetime.strptime('20150908' + '193100', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')  
            
def event_2_3():
    dmsp_dn = datetime.datetime.strptime('20150908' + '204000', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '30374'
    
    swarm_dn = datetime.datetime.strptime('20150908' + '210400', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')  
    
def event_2_4():
    dmsp_dn = datetime.datetime.strptime('20150908' + '222100', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '30375'
    
    swarm_dn = datetime.datetime.strptime('20150908' + '223800', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')  

def event_2_5():
    dmsp_dn = datetime.datetime.strptime('20150908' + '171800', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '30372'
    
    swarm_dn = datetime.datetime.strptime('20150908' + '173600', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')   

def event_2_6():
    dmsp_dn = datetime.datetime.strptime('20150908' + '185900', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '30373'
    
    swarm_dn = datetime.datetime.strptime('20150908' + '191100', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')   
    

def event_3_1():
    dmsp_dn = datetime.datetime.strptime('20140828' + '065600', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '25056'
    
    swarm_dn = datetime.datetime.strptime('20140828' + '072600', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 

def event_3_2():
    dmsp_dn = datetime.datetime.strptime('20140828' + '074700', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f16'
    dmsp_orbit_id = '56033'
    
    swarm_dn = datetime.datetime.strptime('20140828' + '072600', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 

def event_3_3():
    dmsp_dn = datetime.datetime.strptime('20140828' + '083900', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '25057'
    
    swarm_dn = datetime.datetime.strptime('20140828' + '090000', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_3_4():
    dmsp_dn = datetime.datetime.strptime('20140828' + '092900', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f16'
    dmsp_orbit_id = '56034'
    
    swarm_dn = datetime.datetime.strptime('20140828' + '090000', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')     
    
def event_3_5():
    dmsp_dn = datetime.datetime.strptime('20140828' + '065600', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '25056'
    
    swarm_dn = datetime.datetime.strptime('20140828' + '070300', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
        
def event_3_6():
    dmsp_dn = datetime.datetime.strptime('20140828' + '083900', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '25057'
    
    swarm_dn = datetime.datetime.strptime('20140828' + '083600', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_4_1():
    dmsp_dn = datetime.datetime.strptime('20160803' + '024900', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f17'
    dmsp_orbit_id = '50285'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '025100', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_4_2():
    dmsp_dn = datetime.datetime.strptime('20160803' + '024900', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '35024'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '025100', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_4_3():
    dmsp_dn = datetime.datetime.strptime('20160803' + '043100', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f17'
    dmsp_orbit_id = '50286'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '042500', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_4_4():
    dmsp_dn = datetime.datetime.strptime('20160803' + '043100', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '35025'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '042500', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_4_5():
    dmsp_dn = datetime.datetime.strptime('20160803' + '061400', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '35026'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '060000', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 

def event_4_6():
    dmsp_dn = datetime.datetime.strptime('20160803' + '075700', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '35027'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '073400', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 

def event_4_7():
    dmsp_dn = datetime.datetime.strptime('20160803' + '024900', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '35024'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '023300', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 

def event_4_8():
    dmsp_dn = datetime.datetime.strptime('20160803' + '034300', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f16'
    dmsp_orbit_id = '66006'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '040500', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_4_9():
    dmsp_dn = datetime.datetime.strptime('20160803' + '052600', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f16'
    dmsp_orbit_id = '66007'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '053900', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_4_10():
    dmsp_dn = datetime.datetime.strptime('20160803' + '070800', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f16'
    dmsp_orbit_id = '66008'
    
    swarm_dn = datetime.datetime.strptime('20160803' + '071400', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N') 
    
def event_5_1():
    dmsp_dn = datetime.datetime.strptime('20170529' + '090400', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f17'
    dmsp_orbit_id = '54514'
    
    swarm_dn = datetime.datetime.strptime('20170529' + '085100', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')     
    
def event_5_2():
    dmsp_dn = datetime.datetime.strptime('20170529' + '100200', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '39251'
    
    swarm_dn = datetime.datetime.strptime('20170529' + '102400', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')      
    
       
def event_5_3():
    dmsp_dn = datetime.datetime.strptime('20170529' + '104600', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f17'
    dmsp_orbit_id = '54515'
    
    swarm_dn = datetime.datetime.strptime('20170529' + '102400', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')   
    
def event_5_4():
    dmsp_dn = datetime.datetime.strptime('20170529' + '114400', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '39252'
    
    swarm_dn = datetime.datetime.strptime('20170529' + '115800', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')   
    
def event_5_5():
    dmsp_dn = datetime.datetime.strptime('20170529' + '132600', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '39253'
    
    swarm_dn = datetime.datetime.strptime('20170529' + '133200', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')  
    
def event_5_6():
    dmsp_dn = datetime.datetime.strptime('20170529' + '150700', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '39254'
    
    swarm_dn = datetime.datetime.strptime('20170529' + '150300', '%Y%m%d%H%M%S')
    swarm_sat_id = 'A'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')      
    
def event_5_7():
    dmsp_dn = datetime.datetime.strptime('20170529' + '114400', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '39252'
    
    swarm_dn = datetime.datetime.strptime('20170529' + '114300', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')    
    
def event_5_8():
    dmsp_dn = datetime.datetime.strptime('20170529' + '132600', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '39253'
    
    swarm_dn = datetime.datetime.strptime('20170529' + '132000', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')        
    
def event_6_1():
    dmsp_dn = datetime.datetime.strptime('20170804' + '093600', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f18'
    dmsp_orbit_id = '40197'
    
    swarm_dn = datetime.datetime.strptime('20170804' + '093200', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')    

def event_6_2():
    dmsp_dn = datetime.datetime.strptime('20170804' + '092200', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f17'
    dmsp_orbit_id = '55461'
    
    swarm_dn = datetime.datetime.strptime('20170804' + '093200', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')    
    
def event_6_3():
    dmsp_dn = datetime.datetime.strptime('20170804' + '110400', '%Y%m%d%H%M%S')
    dmsp_sat_id = 'f17'
    dmsp_orbit_id = '55462'
    
    swarm_dn = datetime.datetime.strptime('20170804' + '110600', '%Y%m%d%H%M%S')
    swarm_sat_id = 'B'   
    
    visual_dmsp_swarm(dmsp_dn, dmsp_sat_id, dmsp_orbit_id, swarm_dn, swarm_sat_id, pole='N')        

if __name__ == '__main__':
    event_1_1()
    event_1_2()
    event_1_3()
    event_1_4()
    event_1_5()
    event_1_6()
    event_1_7()
    
    event_2_1()
    event_2_2()
    event_2_3()
    event_2_4()
    event_2_5()
    event_2_6()
    
    event_3_1()
    event_3_2()
    event_3_3()
    event_3_4()
    event_3_5()
    event_3_6()
    
    event_4_1()
    event_4_2() 
    event_4_3() 
    event_4_4() 
    event_4_5() 
    event_4_6() 
    event_4_7() 
    event_4_8() 
    event_4_9()
    event_4_10()
      
    # event_5_1()
    # event_5_2() 
    # event_5_3() 
    # event_5_4()
    # event_5_5()
    # event_5_6()
    # event_5_7()
    # event_5_8()
    
    # event_6_1()
    # event_6_2() 
    # event_6_3() 