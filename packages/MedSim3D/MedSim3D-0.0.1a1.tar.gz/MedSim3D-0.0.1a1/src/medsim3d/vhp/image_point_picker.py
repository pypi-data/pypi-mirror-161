import cv2
import pickle

class ImagePointPicker:
    def __init__(self):
        pass

    def start_to_pick(self,img_path,save_points_file):
        list_points = []

        # stores mouse position in global variables ix(for x coordinate) and iy(for y coordinate)
        # on double click inside the image
        def select_point(event, x, y, flags, param):
            global ix, iy
            if event == cv2.EVENT_LBUTTONDBLCLK:  # captures left button double-click
                ix, iy = x, y
                list_points.append([ix, iy])
                print(ix, iy)

        # img_path = "../datasets/Female-Images/PNG_format/thorax_analysis/edges/avf1405a.png"

        img = cv2.imread(img_path)
        cv2.namedWindow('image')
        # bind select_point function to a window that will capture the mouse click
        cv2.setMouseCallback('image', select_point)
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        pickle.dump(list_points, open(save_points_file, 'wb'))

