import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import PurePath
from struct import unpack
from matplotlib.colors import LinearSegmentedColormap
import os
from PIL import Image
import pymysql

def dbconnect():
    conn = pymysql.connect(host='127.0.0.1',user='root',passwd='opt6176',db='rams',charset='utf8')
    return conn

def save_building(inFile, conn, cur, moa_id):
    inFile = PurePath(inFile)
    dirname = inFile.parent
    basename = inFile.stem
    
    file = open(inFile, "r")
    strings = file.readlines()
    print(strings)
    file.close()
    
    for str_line in strings:
        str_values = str_line.replace("\n", "").strip().split(" ")
        if len(str_values) > 0:
            h0 = int(str_values[0])
            count = (int)((len(str_values) - 1) / 2)
            sql = "INSERT INTO moa_building (height, count, moa_id) VALUES ({}, {}, {})".format(h0, count, moa_id)
            cur.execute(sql)
            conn.commit()
            
            sql = "SELECT max(id) from moa_building"
            cur.execute(sql)
            results = cur.fetchall()
            
            if len(results) > 0:
                current_id = int(results[0][0])
                for i in range(count):
                    x0 = float(str_values[i*2+1])
                    y0 = float(str_values[i*2+2])
                    sql = "INSERT INTO moa_building_polygon (x0, y0, building_id) VALUES ({}, {}, {})".format(x0, y0, current_id)
                    cur.execute(sql)
                    conn.commit()

def save_dem(inFile, conn, cur, moa_id):
    inFile = PurePath(inFile)
    dirname = inFile.parent
    basename = inFile.stem
    
    file = open(inFile, "r")
    strings = file.readlines()
    print(strings)
    file.close()
    
    line_no = 0
    for str_line in strings:
        if line_no == 0:
            str_values = str_line.split(" ")
            if len(str_values) < 6:
                break
            else:
                x0 = float(str_values[0])
                y0 = float(str_values[1])
                x1 = float(str_values[2])
                y1 = float(str_values[3])
                x_count = int(str_values[4])
                y_count = int(str_values[5])
                x_diff = round((x1-x0)/(float)(x_count-1), 8)
                y_diff = round((y1-y0)/(float)(y_count-1), 8)
                x_index = 0
                y_index = 0
        else:
            h0 = float(str_line)            
            
            sql = "INSERT INTO moa_dem (x0, y0, h0, xi, yi, moa_id) VALUES ({}, {}, {}, {}, {}, {})".format(x0 + (x_diff * (float)(x_index)), y0 + (y_diff * (float)(y_index)), h0, x_index, y_index, moa_id)
            cur.execute(sql)
            conn.commit()
            
            y_index = y_index + 1
            if(y_index > y_count - 1):
                x_index = x_index + 1
                y_index = 0
            
        line_no = line_no + 1
    
def save_moa(inFile, conn, cur):
    inFile = PurePath(inFile)
    dirname = inFile.parent
    basename = inFile.stem
    file_info = basename.split('_')
    date_str = "20" + file_info[2][:2] + "-" + file_info[2][2:4] + "-" + file_info[2][4:]
    print(date_str)
    
    sql = "INSERT INTO moa (date) VALUES ('" + date_str + "')"
    cur.execute(sql)
    conn.commit()
    
    sql = "SELECT max(id) from moa"
    cur.execute(sql)
    results = cur.fetchall()
    
    if len(results) > 0:
        return results[0], conn
    
    return -1, 0
    
    
def save_value(inFile, moa_id, conn, cur):
    with open(inFile, "rb") as fp:
        inFile = PurePath(inFile)
        dirname = inFile.parent
        basename = inFile.stem
        file_info = basename.split('_')
        z_value = file_info[1][3:]
        time_str = file_info[3][:2] + ":" + file_info[3][2:4] + ":" + file_info[3][4:]

        header = _parseHeader(fp)
        x0 = header["x0"]
        y0 = header["y0"]
        dX = header["dX"]
        dY = header["dY"]
        vMax = header['vMax']
        vMin = header['vMin']

        sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES ({}, {}, '{}', {}, {}, {})".format(str(moa_id[0]), z_value, time_str, dX, dY, vMax)
        # sql = "INSERT INTO moa_level (moa_id, z0, time, dx, dy, vMax) VALUES (" + str(moa_id[0]) + ", " + z_value + ", '" + time_str + "')"
        cur.execute(sql)
        conn.commit()
        
        sql = "SELECT max(id) from moa_level"
        cur.execute(sql)
        results = cur.fetchall()
        
        level_id = results[0]

        for _ in range(header["nP"]):
            i = unpack("<i", fp.read(4))[0]
            x = x0 + i * dX
            j = unpack("<i", fp.read(4))[0]
            y = y0 + j * dY
            v = unpack("<d", fp.read(8))[0]
            current_value = v * vMax / 100.0
            sql = "INSERT INTO moa_value (moa_level_id, x, y, value) VALUES (" + str(level_id[0]) + ", " + str(x) + ", " + str(y) + ", " + str(current_value) + ")"
            cur.execute(sql)
            conn.commit()

    
def _parseHeader(fp):
    first4 = unpack("<4c", fp.read(4))
    desc = b"".join(list(first4)).decode("utf-8")

    if desc != "BGSP":
        raise UnknownBinaryFormatError(desc)

    return {
        "desc": desc,
        "vMax": unpack("<d", fp.read(8))[0],
        "vMin": unpack("<d", fp.read(8))[0],
        "dT": unpack("<d", fp.read(8))[0],
        "x0": unpack("<d", fp.read(8))[0],
        "y0": unpack("<d", fp.read(8))[0],
        "z0": unpack("<d", fp.read(8))[0],
        "dX": unpack("<d", fp.read(8))[0],
        "dY": unpack("<d", fp.read(8))[0],
        "nX": unpack("<i", fp.read(4))[0],
        "nY": unpack("<i", fp.read(4))[0],
        "nP": unpack("<i", fp.read(4))[0],
    }


def _printHeader(h):
    print(f"desc: {h['desc']}")
    print(f"(vMax, vMin): ({h['vMax']}, {h['vMin']})")
    print(f"dT: {h['dT']}")
    print(f"(x0, y0, z0): ({h['x0']}, {h['y0']}, {h['z0']})")
    print(f"(dX, dY): ({h['dX']}, {h['dY']})")
    print(f"(nX, nY): ({h['nX']}, {h['nY']})")
    print(f"# of points: {h['nP']}")


def _parseArgs():
    parser = argparse.ArgumentParser(
        description="Generates .plt(ascii) from .bgr(binary)."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="input file full path",
    )

    parser.add_argument(
        "--output",
        required=False,
        help="output file full path(if omitted, same as input except extension)",
    )

    # parser.add_argument("--verbose", action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--verbose", action="store_true", help="print header information"
    )
    parser.add_argument("--no-verbose", action="store_false")
    parser.set_defaults(verbose=False)

    args = parser.parse_args()

    if args.output is None:
        inFile = PurePath(args.input)
        dirname = inFile.parent
        basename = inFile.stem
        args.output = PurePath.joinpath(dirname, basename)

    return args

def save_rams(rams_folder):
    
    conn = dbconnect()
    cur = conn.cursor()

    # bgr 파일로 부터 오염 정보 저장
    # 처음 저장할 경우, moa id 생성
    is_first = True
    path_dir = rams_folder
    folder_list = os.listdir(path_dir)
    for folder_name in folder_list:
        if folder_name[-4:] == "_moa":
            moa_folder_list = os.listdir(path_dir + "//" + folder_name)
            for moa_folder_name in moa_folder_list:
                file_list = os.listdir(path_dir + "//" + folder_name + "//" + moa_folder_name)
                for file_name in file_list:
                    file_ext = os.path.splitext(file_name)[1]
                    if file_ext == '.bgr' :
                        if is_first :
                            moa_id, conn = save_moa(path_dir + "//" + folder_name + "//" + moa_folder_name + "//" + file_name, conn, cur)
                            is_first = False
                            if moa_id[0] == -1:
                                exit
                        
                        save_value(path_dir + "//" + folder_name + "//" + moa_folder_name + "//" + file_name, moa_id, conn, cur)

    # 오염 정보를 통한 전체 오염 영역 확인
    sql = "SELECT min(x), min(y), max(x), max(y), max(value), min(value) from moa_value where moa_level_id IN (SELECT id FROM moa_level WHERE moa_id = " + str(moa_id[0]) + ")"
    cur.execute(sql)
    results = cur.fetchall()        
    min_x = results[0][0]
    min_y = results[0][1]
    max_x = results[0][2]
    max_y = results[0][3]
    max_v = results[0][4]
    min_v = results[0][5]
    
    sql = "SELECT min(z0), max(z0), min(dx), min(dy) from moa_level WHERE moa_id = " + str(moa_id[0])
    cur.execute(sql)
    results = cur.fetchall()
    min_z = results[0][0]
    max_z = results[0][1]
    dx = results[0][2]
    dy = results[0][3]
    
    sql = "SELECT z0 from moa_level WHERE moa_id = " + str(moa_id[0]) + " ORDER BY z0"
    cur.execute(sql)
    results = cur.fetchall()
    
    dz = 100000000
    find_dz = False
    prev_z = 1
    for index, value in enumerate(results):
        if index == 0:
            prev_z = value[0]
        else:
            diff_z = (value[0] - prev_z)
            if diff_z > 1 and diff_z < dz:
                dz = diff_z
                find_dz = True
    if find_dz == False:
        dz = 0
        
    sql = "UPDATE moa SET x0 = {}, y0 = {}, z0 = {}, x1 = {}, y1 = {}, z1 = {}, vMax = {}, vMin = {}, dx = {}, dy = {}, dz = {} WHERE id = {}".format(min_x, min_y, min_z, max_x, max_y, max_z, max_v, min_v, dx, dy, dz, moa_id[0])
    cur.execute(sql)
    conn.commit()
        
    # save dem
    dem_folder = rams_folder + "//dump//dem"
    file_list = os.listdir(dem_folder)
    for file_name in file_list:
        save_dem(dem_folder + "//" + file_name, conn, cur, moa_id[0])
        
    # save building
    building_folder = rams_folder + "//dump//building"
    file_list = os.listdir(building_folder)
    for file_name in file_list:
        save_building(building_folder + "//" + file_name, conn, cur, moa_id[0])


class UnknownBinaryFormatError(Exception):
    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        return f"Error: Unknown binary format {self.desc}"


if __name__ == "__main__":
    try:
        args = _parseArgs()

        save_rams("F:/project/2. 시뮬레이터/4. ADD/화생방/2023/01.ADD DATA/230310_NBC-RAMS/case_mountain")
        # save_building("F:/project/2. 시뮬레이터/4. ADD/화생방/2023/01.ADD DATA/230310_NBC-RAMS/case_building/dump/building/building_210809_154755_0_0")
        # save_dem("F:/project/2. 시뮬레이터/4. ADD/화생방/2023/01.ADD DATA/230310_NBC-RAMS/case_building/dump/dem/dem_210809_154755_0_0")
        # is_first = True
        # path_dir = args.input
        # folder_list = os.listdir(path_dir)
        # for folder_name in folder_list:
        #     file_list = os.listdir(path_dir + "//" + folder_name)
        #     for file_name in file_list:
        #         file_ext = os.path.splitext(file_name)[1]
        #         if file_ext == '.bgr' :
        #             if is_first :
        #                 moa_id, conn = save_moa(path_dir + "//" + folder_name + "//" + file_name)
        #                 is_first = False
        #                 if moa_id[0] == -1:
        #                     exit
                    
        #             save_value(path_dir + "//" + folder_name + "//" + file_name, moa_id, conn)

        # moa_id = [1]
        # conn = dbconnect()
        # cur = conn.cursor()
        # sql = "SELECT min(x), min(y), max(x), max(y), max(value), min(value) from moa_value where moa_level_id IN (SELECT id FROM moa_level WHERE moa_id = " + str(moa_id[0]) + ")"
        # cur.execute(sql)
        # results = cur.fetchall()        
        # min_x = results[0][0]
        # min_y = results[0][1]
        # max_x = results[0][2]
        # max_y = results[0][3]
        # max_v = results[0][4]
        # min_v = results[0][5]
        
        # sql = "SELECT min(z0), max(z0), min(dx), min(dy) from moa_level WHERE moa_id = " + str(moa_id[0])
        # cur.execute(sql)
        # results = cur.fetchall()
        # min_z = results[0][0]
        # max_z = results[0][1]
        # dx = results[0][2]
        # dy = results[0][3]
        
        # sql = "SELECT z0 from moa_level WHERE moa_id = " + str(moa_id[0]) + " ORDER BY z0"
        # cur.execute(sql)
        # results = cur.fetchall()
        
        # dz = 100000000
        # find_dz = False
        # prev_z = 1
        # for index, value in enumerate(results):
        #     if index == 0:
        #         prev_z = value[0]
        #     else:
        #         diff_z = (value[0] - prev_z)
        #         if diff_z > 1 and diff_z < dz:
        #             dz = diff_z
        #             find_dz = True
        # if find_dz == False:
        #     dz = 0
            
        # sql = "UPDATE moa SET x0 = {}, y0 = {}, z0 = {}, x1 = {}, y1 = {}, z1 = {}, vMax = {}, vMin = {}, dx = {}, dy = {}, dz = {} WHERE id = {}".format(min_x, min_y, min_z, max_x, max_y, max_z, max_v, min_v, dx, dy, dz, moa_id[0])
        # cur.execute(sql)
        # conn.commit()

        # bgr2image(args.input, args.output, args.verbose)
    except (FileNotFoundError, UnknownBinaryFormatError) as e:
        print(e)
