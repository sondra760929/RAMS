import numpy, sys
import mhd_utils_3d
import bgr2DB
import matplotlib.pyplot as plt

def save_mhd(moa_id, file_path):
        conn = bgr2DB.dbconnect()
        cur = conn.cursor()
        
        sql = "SELECT x0, y0, z0, x1, y1, z1, vMax, vMin, dx, dy, dz from moa where id = " + str(moa_id)
        cur.execute(sql)
        results = cur.fetchall()
        min_x = results[0][0]
        min_y = results[0][1]
        min_z = results[0][2]
        max_x = results[0][3]
        max_y = results[0][4]
        max_z = results[0][5]
        max_v = results[0][6]
        min_v = results[0][7]
        dx = results[0][8]
        dy = results[0][9]
        dz = results[0][10]
        
        sql = "SELECT DISTINCT time FROM moa_level WHERE moa_id = {} ORDER BY time".format(str(moa_id))
        cur.execute(sql)
        time_array = cur.fetchall()
        
        x_count = int((max_x - min_x) / dx + 1)
        y_count = int((max_y - min_y) / dy + 1)
        z_count = int((max_z - min_z) / dz + 1)
        
        meta_dict = {}
        meta_dict['ObjectType'] = 'Image'
        meta_dict['NDims'] = '3'
        meta_dict['BinaryData'] = 'True'
        meta_dict['BinaryDataByteOrderMSB'] = 'False'
        meta_dict['CompressedData'] = 'False'
        meta_dict['TransformMatrix'] = '1 0 0 0 1 0 0 0 1'
        meta_dict['Offset'] = '0 0 0'
        meta_dict['CenterOfRotation'] = '0 0 0'
        meta_dict['AnatomicalOrientation'] = 'RAI'
        meta_dict['ElementSpacing'] = '1 1 1'
        meta_dict['DimSize'] = "{} {} {}".format(str(x_count), str(y_count), str(z_count))
        meta_dict['ElementType'] = 'MET_SHORT'
        meta_dict['ElementDataFile'] = 'Image'
        
        for check_time in time_array:
            data = numpy.zeros([z_count, y_count, x_count], dtype=numpy.short)

            sql = "SELECT id, z0 FROM moa_level WHERE moa_id = {} AND time = '{}' ORDER BY z0".format(str(moa_id), str(check_time[0]))
            cur.execute(sql)
            results = cur.fetchall()
            for moa_level in results:
                level_id = moa_level[0]
                level_z0 = moa_level[1]
                z_index = int((level_z0 - min_z) / dz)
                
                sql = "SELECT x, y, value FROM moa_value WHERE moa_level_id = {}".format(str(level_id))
                cur.execute(sql)
                results1 = cur.fetchall()
                for moa_value in results1:
                    x = moa_value[0]
                    y = moa_value[1]
                    value = moa_value[2]
                    
                    x_index = int((x - min_x) / dx)
                    y_index = int((y - min_y) / dy)
                    img_value = value / max_v;
                    
                    data[z_index][y_index][x_index] = int(img_value * 256)
                    if int(img_value * 256) > 0 :
                        print("{},{},{} : {}".format(x_index, y_index, z_index, int(img_value * 256)))
            
            file_name = str(check_time[0]).replace(":", "_")
            meta_dict['ElementDataFile'] = file_name + ".raw"
            mhd_utils_3d.write_meta_header('C:/Users/user/Downloads/vtk-data-master/1/' + file_name + '.mhd', meta_dict)
            mhd_utils_3d.dump_raw_data('C:/Users/user/Downloads/vtk-data-master/1/' + file_name + '.raw', data)

           
class UnknownBinaryFormatError(Exception):
    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        return f"Error: Unknown binary format {self.desc}"


if __name__ == "__main__":
    try:
        # args = _parseArgs()
        # image_array, meta_header = mhd_utils_3d.load_raw_data_with_mhd('C:/Users/user/Downloads/vtk-data-master/1/FullHead.mhd')
        # image_array.shape
        # image_array=image_array**2
        # def func(x):
        #     y=x**2+2*x+500
        #     return y
        # image_array=func(image_array)
        # meta_header
        # meta_header['ElementSpacing']
        # meta_header['ElementSpacing']='2.0 2.0 5.0'
        # meta_header['ElementDataFile']='output.raw'
        # mhd_utils_3d.write_meta_header('C:/Users/user/Downloads/vtk-data-master/1/output.mhd',meta_header)
        # mhd_utils_3d.dump_raw_data('C:/Users/user/Downloads/vtk-data-master/1/output.raw',image_array)
        # plt.imshow(image_array[10,:,:])
        # plt.show()

        save_mhd(1, "")

        # bgr2image(args.input, args.output, args.verbose)
    except (FileNotFoundError, UnknownBinaryFormatError) as e:
        print(e)

    
    
    
    
    
    
    
    

# moa_id = 1

# image_array, meta_header = mhd_utils_3d.load_raw_data_with_mhd('C:/Users/user/Downloads/vtk-data-master/1/FullHead.mhd')
# image_array.shape
# image_array=image_array**2
# def func(x):
#     y=x**2+2*x+500
#     return y
# image_array=func(image_array)
# meta_header
# meta_header['ElementSpacing']
# meta_header['ElementSpacing']='2.0 2.0 5.0'
# meta_header['ElementDataFile']='output.raw'
# mhd_utils_3d.write_meta_header('C:/Users/user/Downloads/vtk-data-master/1/output.mhd',meta_header)
# mhd_utils_3d.dump_raw_data('C:/Users/user/Downloads/vtk-data-master/1/output.raw',image_array)
# plt.imshow(image_array[10,:,:])
# plt.show()
