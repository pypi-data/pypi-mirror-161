from tqdm import tqdm
import requests
import os

class VHPDownloader:

    def __init__(self):
        self.root_url="https://data.lhncbc.nlm.nih.gov/public/Visible-Human"

        self.GenderItem="Male"
        self.ResItem=['70mm','FullColor','PNG_format','radiological','INDEX','INDEX.Z','README']
        self.FullcolorItem=['abdomen','fullbody','head','legs','pelvis','thighs','thorax','README']
        self.PNG_formatItem=['abdomen','head','legs','pelvis','radiological','thighs','thorax']
        self.MalePNGRangeDict={
            "abdomen":[1455,1997],
            "head":[1001,1377],
            "legs":[2265,2878],
            "pelvis":[1732,2028],
            "thighs":[1732,2411],
            "thorax":[1280,1688]
        }
        self.MalePNGPrefix="a_vm"

    def get_all_male_body_parts(self):
        return list(self.MalePNGRangeDict.keys())

    def download_image(self,pic_url, save_path):

        if os.path.exists(save_path):
            return

        response = requests.get(pic_url, stream=True)

        if not response.ok:
            print(response)
            return

        with open(save_path, 'wb') as handle:
            if response.ok:
                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

    def download_datasets(self,gender,body_part,save_folder):
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
        rr=self.MalePNGRangeDict[body_part]
        min_v=rr[0]
        max_v=rr[1]

        for idx in tqdm(range(min_v, max_v + 1)):
            url = f"{self.root_url}/{gender}-Images/PNG_format/{body_part}/{self.MalePNGPrefix}{idx}.png"
            print(url)
            self.download_image(pic_url=url, save_path=f'{save_folder}/{self.MalePNGPrefix}{idx}.png')
        print("Finished!")
