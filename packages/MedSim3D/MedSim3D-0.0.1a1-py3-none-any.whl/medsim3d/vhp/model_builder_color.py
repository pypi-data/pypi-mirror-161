import cv2
from tqdm import tqdm
import numpy as np
import os
from PIL import Image
from shapely.geometry import Point, Polygon
import pickle
from quickcsv import *

class ModelBuilderWithColor:
    def __init__(self,polygon_file,dataset_folder,use_color=True):
        list_points=pickle.load(open(polygon_file,'rb'))
        self.coords = []
        for item in list_points:
            print(item)
            self.coords.append((item[0], item[1]))
        self.dataset_folder=dataset_folder
        self.MalePNGRangeDict = {
            "abdomen": [1455, 1997],
            "head": [1001, 1377],
            "legs": [2265, 2878],
            "pelvis": [1732, 2028],
            "thighs": [1732, 2411],
            "thorax": [1280, 1688]
        }
        self.FemalePNGRangeDict={
            "abdomen": [1432, 1909],
            "head": [1001, 1285],
            "legs": [2200, 2730],
            "pelvis": [1703, 1953],
            "thighs": [1703, 2300],
            "thorax": [1262, 1488]
        }
        self.use_color=use_color

        self.MalePNGPrefix = "a_vm"
        self.FeMalePNGPrefix = "avf"

    def is_in_area(self,x,y):

        # Create Point objects
        p1 = Point(x, y)

        # Create a square
        # coords = [(24.89, 60.06), (24.75, 60.06), (24.75, 60.30), (24.89, 60.30)]
        poly = Polygon(self.coords)

        # PIP test with 'within'
        return p1.within(poly) # True

    def show_edges(self,img_path, t=120):
        image = cv2.imread(img_path, 0)
        edges = cv2.Canny(image, t, 3*t)

        cv2.imshow("canny", edges)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save_edges(self,img_path, save_path, t=120):
        image = cv2.imread(img_path, 0)
        edges = cv2.Canny(image, t, 3 * t)

        cv2.imwrite(save_path,edges)

    def get_edges(self,img_path,  t=120):
        image = cv2.imread(img_path, 0)
        edges = cv2.Canny(image, t, 3 * t)

        return edges

    def detect_colored_points(self,idx,img_path,save_path,z,original_img_path=None):
        # img_path = 'test.png'
        if original_img_path!=None:
            im = Image.open(original_img_path)  # Can be many different formats.
            original_img = im.load()
        else:
            original_img=None
        img = cv2.imread(img_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 色彩空间转换为hsv，分离.

        # 色相（H）是色彩的基本属性，就是平常所说的颜色名称，如红色、黄色等。
        # 饱和度（S）是指色彩的纯度，越高色彩越纯，低则逐渐变灰，取0-100%的数值。
        # 明度（V），取0-100%。
        # OpenCV中H,S,V范围是0-180,0-255,0-255
        low = np.array([0, 0, 0])
        high = np.array([180, 255, 46])

        dst = cv2.inRange(src=hsv, lowerb=low, upperb=high)  # HSV高低阈值，提取图像部分区域

        # 寻找白色的像素点坐标。
        # 白色像素值是255，所以np.where(dst==255)
        xy = np.column_stack(np.where(dst == 0))
        # print(xy)

        # 在原图的红色数字上用 金黄色 描点填充。
        list_useful_points=[]
        for c in xy:
            x=c[1]
            y=c[0]
            if self.is_in_area(x,y):
            # print(c)
            # 注意颜色值是(b,g,r)，不是(r,g,b)
            # 坐标:c[1]是x,c[0]是y
                cv2.circle(img=img, center=(int(c[1]), int(c[0])), radius=1, color=(0, 0, 255), thickness=1)
                if original_img_path==None:
                    model = {
                        "id": idx,
                        "x": round(x * 0.33, 2),
                        "y": round(y * 0.33, 2),
                        "z": z

                    }
                else:
                    pix_color=original_img[x,y]
                    model = {
                        "id": idx,
                        "x": round(x * 0.33,2),
                        "y": round(y * 0.33,2),
                        "z": z,
                        "r":pix_color[0],
                        "g": pix_color[1],
                        "b": pix_color[2],
                    }
                # print("color = ",)
                list_useful_points.append(model)

        cv2.imwrite(save_path,img)
        return list_useful_points


    def build(self,gender,body_part,save_edges_folder,save_detected_folder,output_model_file,t=100):
        # img_path = 'datasets/Male-Images/PNG_format/radiological/mri_converted/mvm11501.png'
        # show_edges(img_path=img_path)

        prefix = self.MalePNGPrefix
        affix = ""
        if gender == "Female":
            prefix = self.FeMalePNGPrefix
            affix = "a"
        if not os.path.exists(save_edges_folder):
            os.mkdir(save_edges_folder)
        if not os.path.exists(save_detected_folder):
            os.mkdir(save_detected_folder)
        current_range = self.MalePNGRangeDict
        if gender == "Female":
            current_range = self.FemalePNGRangeDict
        rr = current_range[body_part]
        min_v = rr[0]
        max_v = rr[1]

        width=2048
        height=1216 # 0.33mm
        current_z=0 # 1mm
        size_x=width*0.33
        size_y=height*0.33
        d_z=0
        list_all_points=[]
        for idx in tqdm(range(min_v, max_v + 1)):
            print(idx)
            img_path = f'{self.dataset_folder}/{prefix}{idx}{affix}.png'
            save_path = f'{save_edges_folder}/{prefix}{idx}{affix}.png'
            save_path_detect = f'{save_detected_folder}/{prefix}{idx}{affix}.png'

            if not os.path.exists(img_path):
                continue

            if not os.path.exists(save_path):
                self.save_edges(img_path=img_path, save_path=save_path, t=t)
            if not self.use_color:
                img_path=None
            list_useful_points=self.detect_colored_points(idx=idx,img_path=save_path, save_path=save_path_detect,z=d_z,original_img_path=img_path)
            d_z+=1
            list_all_points+=list_useful_points

        write_csv(output_model_file, list_all_points)
