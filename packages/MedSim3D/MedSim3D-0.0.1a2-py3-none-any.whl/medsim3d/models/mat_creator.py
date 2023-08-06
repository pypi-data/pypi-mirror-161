import numpy as np
import quickcsv

class MatCreator:

    def __init__(self,point_csv_file):
        self.point_csv_file=point_csv_file

    def create(self,save_mat_path,MIN_VALUE=10000,key_name="instance",dim=64,size_scale=1.2):

        # 64 x 64 x 64
        # read points and create world of 64x64x64
        points = quickcsv.read_csv(csv_path=self.point_csv_file)
        min_value = MIN_VALUE

        for p in points:
            if float(p["x"]) < min_value:
                min_value = float(p["x"])
            if float(p["y"]) < min_value:
                min_value = float(p["y"])
            if float(p["z"]) < min_value:
                min_value = float(p["z"])

        if min_value < 0:
            for idx, p in enumerate(points):
                points[idx]["x"] = abs(min_value) + float(points[idx]['x'])
                points[idx]["y"] = abs(min_value) + float(points[idx]['y'])
                points[idx]["z"] = abs(min_value) + float(points[idx]['z'])

        max_value = 0

        for p in points:
            if float(p["x"]) > max_value:
                max_value = float(p["x"])
            if float(p["y"]) > max_value:
                max_value = float(p["y"])
            if float(p["z"]) > max_value:
                max_value = float(p["z"])

        size = max_value * size_scale

        d = dim / size

        # create an empty matrix
        matrix = []
        for z in range(dim):
            list_x = []
            for x in range(dim):
                list_y = [0 for _ in range(dim)]
                list_x.append(list_y)
            matrix.append(list_x)

        print(np.asarray(matrix).shape)

        # fill 3D points with 1
        points_revised = []
        for idx, p in enumerate(points):
            x = int(d * float(p["x"]))
            y = int(d * float(p["y"]))
            z = int(d * float(p["z"]))
            # print(x,y,z)
            points_revised.append(p)
            matrix[z][x][y] = 1

        # save mat file
        from scipy.io import loadmat, savemat
        x = {}
        x[key_name] = matrix
        savemat(save_mat_path, x)