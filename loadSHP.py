import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
import numpy as np
import pyvista as pv
import pymysql
import os
from PIL import Image
from pathlib import Path
import pyproj
import shapefile
import fiona
from shapely.geometry import shape

def convert_tm60_to_lat_long(easting, northing):
    # Define the TM60 (Irish Transverse Mercator) projection
    # tm60 = pyproj.Proj("+proj=tmerc +lat_0=53.5 +lon_0=-8 +k=1.000035 +x_0=600000 +y_0=750000 +ellps=GRS80 +units=m +no_defs")
    tm60 = pyproj.Proj("EPSG:5186")
    
    # Define the WGS84 (latitude and longitude) projection
    wgs84 = pyproj.Proj("EPSG:4326")
    
    # Perform the coordinate transformation from TM60 to WGS84
    longitude, latitude = pyproj.transform(tm60, wgs84, easting, northing)
    
    return latitude, longitude

def save_dem_tif(conn, cur):
    file_list = os.listdir("L:/지형정보제공2302/고도자료/Lv4/한반도 고도자료(5M급)2019_ED2")
    for file_name in file_list:
        file_ext = os.path.splitext(file_name)[1]
        if file_ext == '.tif' :
            file_path = "L:/지형정보제공2302/고도자료/Lv4/한반도 고도자료(5M급)2019_ED2/" + file_name
            src = rasterio.open(file_path)
            sql = "INSERT INTO dem_tif (bounds_left, bounds_bottom, bounds_right, bounds_top, file_name) VALUES ({}, {}, {}, {}, '{}')".format(src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top, file_name)
            # sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES (" + str(moa_id[0]) + ", " + z_value + ", '" + time_str + "')"
            cur.execute(sql)
            conn.commit()
            del src

def save_map_recursive(parent_path, relative_path, tb_name, conn, cur):
    folder_list = os.listdir(parent_path)
    for file_name in folder_list:
        current_path = parent_path + "/" + file_name
        if os.path.isdir(current_path):
            save_map_recursive(current_path, relative_path + file_name + "/", tb_name, conn, cur)
        else:
            file_ext = os.path.splitext(file_name)[1]
            if file_ext == '.tif' :
                file_path = current_path
                
                sql = "SELECT id from map_100 where file_name = '" + relative_path + file_name + "'"
                cur.execute(sql)
                results = cur.fetchall()        
                if len(results) < 1:               
                    try:
                        src = rasterio.open(file_path)
                        sql = "INSERT INTO {} (bounds_left, bounds_bottom, bounds_right, bounds_top, file_name) VALUES ({}, {}, {}, {}, '{}')".format(tb_name, src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top, relative_path + file_name)
                        # sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES (" + str(moa_id[0]) + ", " + z_value + ", '" + time_str + "')"
                        cur.execute(sql)
                        conn.commit()
                        del src
                    except (rasterio.RasterioIOError) as e:
                        print(e)
                
                pre, ext = os.path.splitext(file_path)
                new_file_path = pre + ".jpg"

                if not os.path.exists(new_file_path):
                    im = Image.open(file_path)
                    im.save(new_file_path, 'jpeg')
                    
# def save_vw_building_recursive(parent_path, relative_path, conn, cur):
#     folder_list = os.listdir(parent_path)
#     for file_name in folder_list:
#         current_path = parent_path + "/" + file_name
#         if os.path.isdir(current_path):
#             save_vw_building_recursive(current_path, relative_path + file_name + "/", conn, cur)
#         else:
#             file_ext = os.path.splitext(file_name)[1]
#             if file_ext == '.shp' :
#                 file_path = current_path
#                 try:
#                     test = gpd.read_file(file_path, encoding='CP949')
#                     print(test.crs)
#                     test.columns = test.columns.str.upper()
#                     column_names = list(test.columns.values)
#                     for i in range(len(test.index)):
#                         # if (gpd.pd.notna(test.BDG_BOTTOM[i])) and (gpd.pd.notna(test.BDG_TOP[i])) and (gpd.pd.notna(test.BDG_HEIGHT[i])) and (gpd.pd.notna(test.BDG_TM60_X[i])) and (gpd.pd.notna(test.BDG_TM60_Y[i])):
#                         if 'TRN3D_FNM' in column_names:
#                             bdg_name = test.TRN3D_FNM[i]
#                         elif 'TRN3D_NAME' in column_names:
#                             bdg_name = test.TRN3D_NAME[i]
#                         else:
#                             bdg_name = ""
                        
#                         if 'UTL3D_TTE' in column_names:
#                             ds_file_name = test.UTL3D_TTE[i]
#                         elif 'TRN3D_TN' in column_names:
#                             ds_file_name = test.TRN3D_TN[i]
#                         elif 'ETC3D_MAX' in column_names:
#                             ds_file_name = test.ETC3D_MAX[i]
#                         else:
#                             ds_file_name = ""

#                         if ('TRN3D_TYPE' in column_names) and (gpd.pd.notna(test.TRN3D_TYPE[i])):
#                             trn3d_type = test.TRN3D_TYPE[i]
#                         else:
#                             trn3d_type = -1
                        
#                         if ('BDG_TM60_X' in column_names):
#                             pos_x = test.BDG_TM60_X[i]
#                             pos_y = test.BDG_TM60_Y[i]
#                         else:
#                             pos_x = test.boundary.centroid[i].x
#                             pos_y = test.boundary.centroid[i].y
                        
#                         lat, lon = convert_tm60_to_lat_long(pos_y, pos_x)
                        
#                         if ('BDG_BOTTOM' in column_names) and (gpd.pd.notna(test.BDG_BOTTOM[i])):
#                             bdg_bottom = test.BDG_BOTTOM[i]
#                         else:
#                             bdg_bottom = 0.0
                        
#                         if ('BDG_TOP' in column_names) and (gpd.pd.notna(test.BDG_TOP[i])):
#                             bdg_top = test.BDG_TOP[i]
#                         else:
#                             bdg_top = 0.0
                        
#                         if ('BDG_HEIGHT' in column_names) and (gpd.pd.notna(test.BDG_HEIGHT[i])):
#                             bdg_height = test.BDG_HEIGHT[i]
#                         else:
#                             bdg_height = 0.0
                        
#                         if ds_file_name == "":
#                             print("ds file not defined")
#                         else:
#                             sql = "INSERT INTO vw_building (TRN3D_TYPE, UTL3D_TTE, BDG_BOTTOM, BDG_TOP, BDG_HEIGHT, BDG_TM60_X, BDG_TM60_Y, TRN3D_FNM, 3DS_FILE, LAT, LON) VALUES ({}, '{}', {}, {}, {}, {}, {}, '{}', '{}', {}, {})".format(trn3d_type, ds_file_name, bdg_bottom, bdg_top, bdg_height, pos_x, pos_y, bdg_name, "", lat, lon)
#                             # sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES (" + str(moa_id[0]) + ", " + z_value + ", '" + time_str + "')"
#                             cur.execute(sql)
#                             conn.commit()
#                     del test
#                     print("OK : " + file_path)
#                     exit
#                 except Exception as err:
#                     print(file_path)
#                     print(f"Unexpected {err=}, {type(err)=}")
                    
def save_vw_building_check_files_recursive(parent_path, relative_path, conn, cur):
    folder_list = os.listdir(parent_path)
    check_db = False
    save_db = False
    save_count = 0
    
    for file_name in folder_list:
        current_path = parent_path + "/" + file_name
        if os.path.isdir(current_path):
            save_vw_building_check_files_recursive(current_path, relative_path + file_name + "/", conn, cur)
        else:
            file_ext = os.path.splitext(file_name)[1]
            if file_ext.lower() == '.shp' or file_ext.lower() == '.3ds':
                if check_db == False:
                    check_db = True
                    sql = "SELECT * from vw_building_import WHERE file_path='{}'".format(relative_path + file_name)
                    cur.execute(sql)
                    results = cur.fetchall()                
                    if len(results) < 1: 
                        save_db = False
                        conn.begin()
                    else:
                        save_db = True
                        break
                
                if check_db == True:
                    if save_db == False:
                        is_3ds = 0
                        if file_ext.lower() == '.3ds':
                            is_3ds = 1
                        sql = "INSERT INTO vw_building_import (file_path, status, 3ds, is_3ds, UTL3D_TTE) VALUES ('{}', {}, {}, {}, '{}')".format(relative_path + file_name, 0, 0, is_3ds, file_name)
                        cur.execute(sql)
                        save_count = save_count + 1
                    else:
                        break
                else:
                    print("check_db : False")
    if save_db == False:
        conn.commit()
    print("Save Path{} : {}".format(save_count, parent_path))

def save_vw_building_path(conn, cur):
    start_limit = 0
    end_limit = start_limit + 10000
    
    while 1:
        sql = "SELECT file_path FROM vw_building_import WHERE is_3ds = 1 LIMIT {}, {}".format(start_limit, end_limit)
        cur.execute(sql)
        results = cur.fetchall()
        if len(results) > 0:
            result_count = len(results)
            conn.begin()
            for i in range(result_count):
                result_list = results[i][0].split("/")
                file_name = result_list[-1]
                sql = "UPDATE vw_building SET 3DS_FILE='{}' WHERE UTL3D_TTE='{}'".format(results[i][0], file_name)
                cur.execute(sql)
                print("{}-{} : {} / {} : {}".format(start_limit, end_limit, i+1, result_count, file_name))
            conn.commit()
            
            start_limit = end_limit + 1
            end_limit = start_limit + 10000
        else:
            break

def save_vw_building_geopandas(file_path, file_id, conn, cur):
    conn.begin()
    try:
        test = gpd.read_file(file_path, encoding='CP949')
        crs_string = str(test.crs)
        test.columns = test.columns.str.upper()
        column_names = list(test.columns.values)
        for i in range(len(test.index)):
            # if (gpd.pd.notna(test.BDG_BOTTOM[i])) and (gpd.pd.notna(test.BDG_TOP[i])) and (gpd.pd.notna(test.BDG_HEIGHT[i])) and (gpd.pd.notna(test.BDG_TM60_X[i])) and (gpd.pd.notna(test.BDG_TM60_Y[i])):
            if 'TRN3D_FNM' in column_names:
                bdg_name = test.TRN3D_FNM[i]
            elif 'TRN3D_NAME' in column_names:
                bdg_name = test.TRN3D_NAME[i]
            else:
                bdg_name = ""
            
            if 'UTL3D_TTE' in column_names:
                ds_file_name = test.UTL3D_TTE[i]
            elif 'TRN3D_TN' in column_names:
                ds_file_name = test.TRN3D_TN[i]
            elif 'ETC3D_MAX' in column_names:
                ds_file_name = test.ETC3D_MAX[i]
            else:
                ds_file_name = ""

            if ('TRN3D_TYPE' in column_names) and (gpd.pd.notna(test.TRN3D_TYPE[i])):
                trn3d_type = test.TRN3D_TYPE[i]
            else:
                trn3d_type = -1
            
            if ('BDG_TM60_X' in column_names):
                pos_x = test.BDG_TM60_X[i]
                pos_y = test.BDG_TM60_Y[i]
            else:
                pos_x = test.GEOMETRY[i].centroid.x
                pos_y = test.GEOMETRY[i].centroid.y
            
            lat, lon = convert_tm60_to_lat_long(pos_y, pos_x)
            
            if ('BDG_BOTTOM' in column_names) and (gpd.pd.notna(test.BDG_BOTTOM[i])):
                bdg_bottom = test.BDG_BOTTOM[i]
            else:
                bdg_bottom = 0.0
            
            if ('BDG_TOP' in column_names) and (gpd.pd.notna(test.BDG_TOP[i])):
                bdg_top = test.BDG_TOP[i]
            else:
                bdg_top = 0.0
            
            if ('BDG_HEIGHT' in column_names) and (gpd.pd.notna(test.BDG_HEIGHT[i])):
                bdg_height = test.BDG_HEIGHT[i]
            else:
                bdg_height = 0.0
            
            if ds_file_name != "" and gpd.pd.notna(ds_file_name):
                sql = "INSERT INTO vw_building (TRN3D_TYPE, UTL3D_TTE, BDG_BOTTOM, BDG_TOP, BDG_HEIGHT, BDG_TM60_X, BDG_TM60_Y, TRN3D_FNM, 3DS_FILE, LAT, LON) VALUES ({}, '{}', {}, {}, {}, {}, {}, '{}', '{}', {}, {})".format(trn3d_type, ds_file_name, bdg_bottom, bdg_top, bdg_height, pos_x, pos_y, bdg_name, "", lat, lon)
                # sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES (" + str(moa_id[0]) + ", " + z_value + ", '" + time_str + "')"
                cur.execute(sql)
            else:
                print("ds file not defined")
                
        sql = "UPDATE vw_building_import SET status = 1, crs='{}' WHERE id = {}".format(crs_string[0:200], file_id)
        cur.execute(sql)
        conn.commit()                
        del test
        return True
    
    except Exception as err:
        conn.rollback()
        sql = "UPDATE vw_building_import SET crs='{}' WHERE id = {}".format(str(err)[0:200].replace("'", "").replace("\"", ""), file_id)
        cur.execute(sql)
        conn.commit()
        return False
    return False

def save_vw_building_shapefile(file_path, file_id, conn, cur):
    conn.begin()
    try:
        test = shapefile.Reader(file_path, encoding='CP949')
        # crs_string = str(test.crs)
        column_count = len(test.fields)
        column_names = []
        for i in range(column_count):
            column_names.append(test.fields[i][0].upper())
        test_count = len(test.shapeRecords())
        # test.columns = test.columns.str.upper()
        # column_names = list(test.columns.values)
        # for i in range(len(test.index)):
        for i in range(test_count):
            current = test.shapeRecords()[i]
            # if (gpd.pd.notna(test.BDG_BOTTOM[i])) and (gpd.pd.notna(test.BDG_TOP[i])) and (gpd.pd.notna(test.BDG_HEIGHT[i])) and (gpd.pd.notna(test.BDG_TM60_X[i])) and (gpd.pd.notna(test.BDG_TM60_Y[i])):
            if 'TRN3D_FNM' in column_names:
                bdg_name = current.record.TRN3D_FNM
            elif 'TRN3D_NAME' in column_names:
                bdg_name = current.record.TRN3D_NAME
            else:
                bdg_name = ""
            
            if 'UTL3D_TTE' in column_names:
                ds_file_name = current.record.UTL3D_TTE
            elif 'TRN3D_TN' in column_names:
                ds_file_name = current.record.TRN3D_TN
            elif 'ETC3D_MAX' in column_names:
                ds_file_name = current.record.ETC3D_MAX
            else:
                ds_file_name = ""

            if ('TRN3D_TYPE' in column_names) and (gpd.pd.notna(current.record.TRN3D_TYPE)):
                trn3d_type = current.record.TRN3D_TYPE
            else:
                trn3d_type = -1
            
            if ('BDG_TM60_X' in column_names):
                pos_x = current.record.BDG_TM60_X
                pos_y = current.record.BDG_TM60_Y
            else:
                pos_x = (current.shape.bbox[0] + current.shape.bbox[2]) / 2.0
                pos_y = (current.shape.bbox[1] + current.shape.bbox[3]) / 2.0
            
            lat, lon = convert_tm60_to_lat_long(pos_y, pos_x)
            
            if ('BDG_BOTTOM' in column_names) and (gpd.pd.notna(current.record.BDG_BOTTOM)):
                bdg_bottom = current.record.BDG_BOTTOM
            else:
                bdg_bottom = 0.0
            
            if ('BDG_TOP' in column_names) and (gpd.pd.notna(current.record.BDG_TOP)):
                bdg_top = current.record.BDG_TOP
            else:
                bdg_top = 0.0
            
            if ('BDG_HEIGHT' in column_names) and (gpd.pd.notna(current.record.BDG_HEIGHT)):
                bdg_height = current.record.BDG_HEIGHT
            else:
                bdg_height = 0.0
            
            if ds_file_name != "" and gpd.pd.notna(ds_file_name):
                sql = "INSERT INTO vw_building (TRN3D_TYPE, UTL3D_TTE, BDG_BOTTOM, BDG_TOP, BDG_HEIGHT, BDG_TM60_X, BDG_TM60_Y, TRN3D_FNM, 3DS_FILE, LAT, LON) VALUES ({}, '{}', {}, {}, {}, {}, {}, '{}', '{}', {}, {})".format(trn3d_type, ds_file_name, bdg_bottom, bdg_top, bdg_height, pos_x, pos_y, bdg_name, "", lat, lon)
                # sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES (" + str(moa_id[0]) + ", " + z_value + ", '" + time_str + "')"
                cur.execute(sql)
            else:
                print("ds file not defined")
            print("{} / {}".format(i+1, test_count))
                
        sql = "UPDATE vw_building_import SET status = 1, crs='{}' WHERE id = {}".format("PyShp", file_id)
        cur.execute(sql)
        conn.commit()                
        del test
        return True
    
    except Exception as err:
        conn.rollback()
        sql = "UPDATE vw_building_import SET crs='{}' WHERE id = {}".format(str(err)[0:200].replace("'", "").replace("\"", ""), file_id)
        cur.execute(sql)
        conn.commit()
        return False
    return False

def save_vw_building_fiona(file_path, file_id, conn, cur):
    conn.begin()
    try:
        test = fiona.open(file_path, encoding='CP949')
        # crs_string = str(test.crs)
        # column_count = len(test)
        column_names = []
        test_count = len(test)
        # test.columns = test.columns.str.upper()
        # column_names = list(test.columns.values)
        # for i in range(len(test.index)):
        for i in range(test_count):
            current = test[i]['properties']
            if i == 0:
                column_names = list(test[i]['properties'].keys())
                
            # if (gpd.pd.notna(test.BDG_BOTTOM[i])) and (gpd.pd.notna(test.BDG_TOP[i])) and (gpd.pd.notna(test.BDG_HEIGHT[i])) and (gpd.pd.notna(test.BDG_TM60_X[i])) and (gpd.pd.notna(test.BDG_TM60_Y[i])):
            if 'TRN3D_FNM' in column_names:
                bdg_name = current['TRN3D_FNM']
            elif 'TRN3D_NAME' in column_names:
                bdg_name = current['TRN3D_NAME']
            else:
                bdg_name = ""
            
            if 'UTL3D_TTE' in column_names:
                ds_file_name = current['UTL3D_TTE']
            elif 'TRN3D_TN' in column_names:
                ds_file_name = current['TRN3D_TN']
            elif 'ETC3D_MAX' in column_names:
                ds_file_name = current['ETC3D_MAX']
            else:
                ds_file_name = ""

            if ('TRN3D_TYPE' in column_names) and (gpd.pd.notna(current['TRN3D_TYPE'])):
                trn3d_type = current['TRN3D_TYPE']
            else:
                trn3d_type = -1
            
            if ('BDG_TM60_X' in column_names):
                pos_x = current['BDG_TM60_X']
                pos_y = current['BDG_TM60_X']
            else:
                bbox = shape(test[i]['geometry']).bounds
                pos_x = (bbox[0] + bbox[2]) / 2.0
                pos_y = (bbox[1] + bbox[3]) / 2.0
            
            lat, lon = convert_tm60_to_lat_long(pos_y, pos_x)
            
            if ('BDG_BOTTOM' in column_names) and (gpd.pd.notna(current['BDG_BOTTOM'])):
                bdg_bottom = current['BDG_BOTTOM']
            else:
                bdg_bottom = 0.0
            
            if ('BDG_TOP' in column_names) and (gpd.pd.notna(current['BDG_TOP'])):
                bdg_top = current['BDG_TOP']
            else:
                bdg_top = 0.0
            
            if ('BDG_HEIGHT' in column_names) and (gpd.pd.notna(current['BDG_HEIGHT'])):
                bdg_height = current['BDG_HEIGHT']
            else:
                bdg_height = 0.0
            
            if ds_file_name != "" and gpd.pd.notna(ds_file_name):
                sql = "INSERT INTO vw_building (TRN3D_TYPE, UTL3D_TTE, BDG_BOTTOM, BDG_TOP, BDG_HEIGHT, BDG_TM60_X, BDG_TM60_Y, TRN3D_FNM, 3DS_FILE, LAT, LON) VALUES ({}, '{}', {}, {}, {}, {}, {}, '{}', '{}', {}, {})".format(trn3d_type, ds_file_name, bdg_bottom, bdg_top, bdg_height, pos_x, pos_y, bdg_name, "", lat, lon)
                # sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES (" + str(moa_id[0]) + ", " + z_value + ", '" + time_str + "')"
                cur.execute(sql)
            else:
                print("ds file not defined")
            print("{} / {}".format(i+1, test_count))
                
        sql = "UPDATE vw_building_import SET status = 1, crs='{}' WHERE id = {}".format("PyShp", file_id)
        cur.execute(sql)
        conn.commit()                
        del test
        return True
    
    except Exception as err:
        conn.rollback()
        sql = "UPDATE vw_building_import SET crs='{}' WHERE id = {}".format(str(err)[0:200].replace("'", "").replace("\"", ""), file_id)
        cur.execute(sql)
        conn.commit()
        return False
    return False


def save_vw_building_db(parent_path, conn, cur):
    sql = "SELECT file_path, id FROM vw_building_import WHERE is_3ds = 0 AND status = 0"
    cur.execute(sql)
    results = cur.fetchall()
    if len(results) > 0:

        result_count = len(results)
        for r_i in range(result_count):
            file_path = parent_path + "/" + results[r_i][0]
            file_id = results[r_i][1]
            r_value = save_vw_building_geopandas(file_path, file_id, conn, cur)
            if r_value:
                print("saved {}/{} : {}".format(r_i + 1, result_count, file_path))
            else:
                print("error {}/{} : {}".format(r_i + 1, result_count, file_path))
                
        
def save_vw_building_path_recursive(parent_path, relative_path, conn, cur):
    folder_list = os.listdir(parent_path)
    for file_name in folder_list:
        current_path = parent_path + "/" + file_name
        if os.path.isdir(current_path):
            save_vw_building_path_recursive(current_path, relative_path + file_name + "/", conn, cur)
        else:
            file_ext = os.path.splitext(file_name)[1]
            if file_ext == '.3ds' :
                file_path = current_path
                try:
                    sql = "UPDATE vw_building SET 3DS_FILE='{}' WHERE UTL3D_TTE='{}'".format(relative_path + file_name, file_name)
                    cur.execute(sql)
                    conn.commit()
                except Exception as err:
                    print(file_path)
                    print(f"Unexpected {err=}, {type(err)=}")

def update_3ds_file_path(x0, x1, y0, y1, conn, cur):
    sql = "SELECT id, 3DS_FILE, UTL3D_TTE, TRN3D_FNM, LAT, LON from vw_building WHERE LAT >= {} and LAT <= {} and LON >= {} and LON <= {}".format(x0, x1, y0, y1)
    cur.execute(sql)
    results = cur.fetchall()
    if len(results) > 0:

        result_count = len(results)
        for r_i in range(result_count):
            print("{} / {}".format(r_i, result_count))
            current_id = results[r_i][0]
            current_3s_file = results[r_i][1]
            current_file_name = results[r_i][2]
            if current_3s_file == "":
                sql = "SELECT id from vw_building_import WHERE UTL3D_TTE ='{}'".format(current_file_name)
                cur.execute(sql)
                results1 = cur.fetchall()
                if len(results1) > 0:
                    for j in range(len(results1)):
                        if j == 0:
                            current_3s_file = str(results1[j][0])
                        else:
                            current_3s_file = current_3s_file + "," + str(results1[j][0])
                
                sql = "UPDATE vw_building SET 3DS_FILE = '{}' WHERE id = {}".format(current_3s_file, current_id)
                cur.execute(sql)
                conn.commit()
                print("current_3s_file : {}".format(current_3s_file))
                


conn = pymysql.connect(host='127.0.0.1',user='root',passwd='opt6176',db='rams',charset='utf8')
cur = conn.cursor()

# save_vw_building_check_files_recursive("L:/지형정보제공2302/브이월드/남한지역(브이월드자료)", "", conn, cur)
# save_vw_building_db("L:/지형정보제공2302/브이월드/남한지역(브이월드자료)", conn, cur)
# save_vw_building_recursive("L:/지형정보제공2302/브이월드/남한지역(브이월드자료)", "", conn, cur)
# save_vw_building_path_recursive("L:/지형정보제공2302/브이월드/남한지역(브이월드자료)", "", conn, cur)
# save_vw_building_fiona("L:/지형정보제공2302/브이월드/남한지역(브이월드자료)/2018_V월드 자료/3차원가시화모델_경계/서울특별시/은평구/은평구.shp", 1829027, conn, cur)
update_3ds_file_path(126.88811567,126.92231567,37.609765504,37.636765504, conn, cur)

# update_3ds_file_path(126.94660357,126.95640357,37.549053032,37.556503032, conn, cur)
# crs_wkt = ""
# test_file = "L:/지형정보제공2302/브이월드/남한지역(브이월드자료)/2018_V월드 자료/3차원가시화모델_경계/서울특별시/마포구/마포구.shp"
# file = shapefile.Reader(test_file, encoding='CP949')
# first = file.shapeRecords()[0] #첫번째 객체 불러오기
# element = first.shape.__geo_interface__ #객체를 dict 타입으로 불러오기
# test = gpd.read_file(test_file, encoding='CP949')
# print(test.crs)



# tm60 = pyproj.Proj("EPSG:5186")

# # Define the WGS84 (latitude and longitude) projection
# wgs84 = pyproj.Proj("EPSG:4326")

# # Perform the coordinate transformation from TM60 to WGS84
# longitude, latitude = pyproj.transform(tm60, wgs84, 574179.3125, 365579.6253)

# print(str(longitude) + " , " + str(latitude))

# longitude, latitude = pyproj.transform(wgs84, tm60, 35.81630287332682 , 131.13927579891472)
# print(str(longitude) + " , " + str(latitude))

# longitude, latitude = pyproj.transform(wgs84, tm60, 37.549053032, 126.94660357)
# print(str(longitude) + " , " + str(latitude))

# Image.MAX_IMAGE_PIXELS = None

# save_map_recursive("L:/지형정보제공2302/영상/항공사진(해상도0.25m급)/2021년촬영", "", "map_25", conn, cur)
# save_map_recursive("L:/지형정보제공2302/영상/북한위성영상(해상도0.35~0.5m급)/NK_영상DB_2022-1", "", "map_50", conn, cur)
# save_map_recursive("L:/지형정보제공2302/영상/K2(해상도1m급)/K2_2021/한반도_모자이크_1m_TIle", "", "map_100", conn, cur)


        
# test_file = "L:/지형정보제공2302/영상/항공사진(해상도0.25m급)/2021년촬영/01_25cm_Trans_Output_Gyeonggi/Cell24_03/38713100.tif"
# src = rasterio.open(test_file)
# print(src.bounds)
# test_file = "L:/지형정보제공2302/브이월드/남한지역(브이월드자료)/2018_V월드 자료/3차원가시화모델_경계/경기도/남양주시/남양주시.shp"
# test = gpd.read_file(test_file, encoding='CP949')
# print(test.crs)
# test_file1 = "L:/지형정보제공2302/영상/북한위성영상(해상도0.35~0.5m급)/NK_영상DB_2022-1/CELL01/tile_CELL01_15.tif"
# test_file2 = "L:/지형정보제공2302/영상/북한위성영상(해상도0.35~0.5m급)/NK_영상DB_2022-1/CELL01/tile_CELL01_16.tif"
# test_file3 = "L:/지형정보제공2302/고도자료/Lv4/한반도 고도자료(5M급)2019_ED2/nk_5m_CELL01.tif"


# test = gpd.read_file(test_file, encoding='CP949')
# for i in range(len(test.BDG_TM60_X)):
#     sql = "INSERT INTO vw_building (TRN3D_TYPE, UTL3D_TTE, BDG_BOTTOM, BDG_TOP, BDG_HEIGHT, BDG_TM60_X, BDG_TM60_Y, TRN3D_FNM, 3DS_FILE) VALUES ({}, '{}', {}, {}, {}, {}, {}, '{}', '{}')".format(test.TRN3D_TYPE[i], test.UTL3D_TTE[i], test.BDG_BOTTOM[i], test.BDG_TOP[i], test.BDG_HEIGHT[i], test.BDG_TM60_X[i], test.BDG_TM60_Y[i], test.TRN3D_FNM[i], "")
#     # sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES (" + str(moa_id[0]) + ", " + z_value + ", '" + time_str + "')"
#     cur.execute(sql)
#     conn.commit()

# test.to_csv("d:/test.csv", encoding='utf8', index = False)
# print(test.crs)
# ax = test.convex_hull.plot(color = 'yellow', edgecolor = 'black')
# plt.show()

# # test = gpd.GeoDataFrame.from_file(test_file, encoding='utf8')
# # test.info()
# # test.tail()
# # test.to_csv("d:/test.csv", encoding='utf8', index = False)
# # del test

# # img = rasterio.open(test_file1)
# # show(img)

# get_point = lambda gcp: np.array([gcp.x, gcp.y, gcp.z])
# # Load a raster
# src = rasterio.open(test_file3)
# print(src.bounds)
# # Grab the Groung Control Points
# # points = np.array([get_point(gcp) for gcp in src.gcps[0]])
# # # Now Grab the three corners of their bounding box
# # # -- This guarantees we grab the right points
# # bounds = pv.PolyData(points).bounds
# # origin = [bounds[0], bounds[2], bounds[4]]  # BOTTOM LEFT CORNER
# # point_u = [bounds[1], bounds[2], bounds[4]]  # BOTTOM RIGHT CORNER
# # point_v = [bounds[0], bounds[3], bounds[4]]  # TOP LEFT CORNER
