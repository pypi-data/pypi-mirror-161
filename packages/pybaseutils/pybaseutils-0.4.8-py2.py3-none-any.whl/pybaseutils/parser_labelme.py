# -*-coding: utf-8 -*-
"""
    @Author : panjq
    @E-mail : pan_jinquan@163.com
    @Date   : 2022-06-29 18:31:12
    @Brief  :
"""
import os
import numpy as np
import cv2
import glob
import random
import numbers
import torch
import json
from tqdm import tqdm
from pybaseutils import image_utils, file_utils, coords_utils


class LabelMeDataset(object):

    def __init__(self,
                 filename=None,
                 data_root=None,
                 anno_dir=None,
                 image_dir=None,
                 class_name=None,
                 use_rgb=True,
                 shuffle=False,
                 check=False,
                 **kwargs):
        """
        :param filename:
        :param data_root:
        :param anno_dir:
        :param image_dir:
        :param transform:
        :param use_rgb:
        :param shuffle:
        """
        self.min_area = 1 / 1000  # 如果前景面积不足0.1%,则去除
        self.use_rgb = use_rgb
        self.class_name, self.class_dict = ["Grid"], {"Grid": 0}
        parser = self.parser_paths(filename, data_root, anno_dir, image_dir)
        self.data_root, self.anno_dir, self.image_dir, self.image_id = parser
        self.postfix = self.get_image_postfix(self.image_dir, self.image_id)
        self.classes = list(self.class_dict.values()) if self.class_dict else None
        self.num_classes = max(list(self.class_dict.values())) + 1 if self.class_dict else None
        self.class_weights = None
        if check:
            self.image_id = self.checking(self.image_id)
        if shuffle:
            random.seed(200)
            random.shuffle(self.image_id)
        self.num_images = len(self.image_id)
        self.scale_rate = 1.0
        self.target_type = 'gaussian'
        self.sigma = 2
        print("GridDataset class_name    :{}".format(class_name))
        print("GridDataset class_dict    :{}".format(self.class_dict))
        print("GridDataset num images    :{}".format(len(self.image_id)))
        print("GridDataset num_classes   :{}".format(self.num_classes))

    def get_image_postfix(self, image_dir, image_id):
        """
        获得图像文件后缀名
        :param image_dir:
        :return:
        """
        if "." in image_id[0]:
            postfix = ""
        else:
            image_list = glob.glob(os.path.join(image_dir, "*"))
            postfix = os.path.basename(image_list[0]).split(".")[1]
        return postfix

    def get_image_anno_file(self, index):
        """
        :param index:
        :return:
        """
        image_id = self.index2id(index)
        image_file, annotation_file = self.__get_image_anno_file(self.image_dir, self.anno_dir, image_id, self.postfix)
        return image_file, annotation_file

    def __get_image_anno_file(self, image_dir, anno_dir, image_id: str, img_postfix):
        """
        :param image_dir:
        :param anno_dir:
        :param image_id:
        :param img_postfix:
        :return:
        """
        if not img_postfix and "." in image_id:
            image_id, img_postfix = image_id.split(".")
        image_file = os.path.join(image_dir, "{}.{}".format(image_id, img_postfix))
        annotation_file = os.path.join(anno_dir, "{}.json".format(image_id))
        return image_file, annotation_file

    def checking(self, image_ids: list, ignore_empty=True):
        """
        :param image_ids:
        :param ignore_empty : 是否去除一些空数据
        :return:
        """
        print("Please wait, it's in checking")
        dst_ids = []
        # image_ids = image_ids[:100]
        # image_ids = image_ids[100:]
        for image_id in tqdm(image_ids):
            image_file, annotation_file = self.get_image_anno_file(image_id)
            if not os.path.exists(annotation_file):
                continue
            if not os.path.exists(image_file):
                continue
            points = self.load_annotations(annotation_file)
            if points.size == 0:
                continue
            dst_ids.append(image_id)
        print("have nums image:{},legal image:{}".format(len(image_ids), len(dst_ids)))
        return dst_ids

    def parser_paths(self, filename=None, data_root=None, anno_dir=None, image_dir=None):
        """
        :param filename:
        :param data_root:
        :param anno_dir:
        :param image_dir:
        :return:
        """
        if isinstance(data_root, str):
            anno_dir = os.path.join(data_root, "json") if not anno_dir else anno_dir
            image_dir = os.path.join(data_root, "images") if not image_dir else image_dir
        image_id = []
        if isinstance(filename, str):
            image_id = self.read_files(filename, split=",")
            data_root = os.path.dirname(filename)
        if not anno_dir:  # 如果anno_dir为空，则自动搜寻可能存在图片目录
            image_sub = ["json"]
            anno_dir = self.search_path(data_root, image_sub)
        if not image_dir:
            image_dir = self.search_path(data_root, ["JPEGImages", "images"])
        if anno_dir and not image_id:
            image_id = self.get_file_list(anno_dir, postfix=["*.png"], basename=True)
        elif image_dir and not image_id:
            image_id = self.get_file_list(anno_dir, postfix=["*.jpg"], basename=True)
        # assert os.path.exists(image_dir), Exception("no directory:{}".format(image_dir))
        # assert os.path.exists(anno_dir), Exception("no directory:{}".format(anno_dir))
        return data_root, anno_dir, image_dir, image_id

    def __getitem__(self, index):
        """
        :param index: int or str
        :return:rgb_image
        """
        image_id = self.index2id(index)
        image_file, annotation_file = self.get_image_anno_file(image_id)
        image = self.read_image(image_file, use_rgb=self.use_rgb)
        points = self.load_annotations(annotation_file)
        image, points = self.select_points(image, points, index=-1)
        data = {"image": image, "points": points}
        return data

    def select_points(self, image, points, index=-1, nearest=1, scale=2.0):
        """
        :param image: 图像
        :param points: 点集合
        :param index: 选择points[index]作为基准点，若index<0则表示随机选择一个
        :param nearest: 选择第K个最近点作为有效区域
        :param scale: 有效区域缩放比例
        :return:
        """
        assert len(points) + 1 > nearest
        # 随机选择一个点作为基准点p1
        index = random.randint(0, len(points) - 1) if index < 0 else index
        p1 = points[index, :]
        distance = np.linalg.norm(points - p1, ord=2, axis=1, keepdims=False)  # 计算欧式距离
        distance[index] = np.inf
        indexes = np.argsort(distance)
        p2 = points[indexes[nearest], :]  # 选择第K个最近点作为第二个基准点
        c12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)  # p1,p2的中心点
        # 选择p1,p2的中心点作为第三个基准点p3
        w, h = abs(p1[0] - p2[0]), abs(p1[1] - p2[1])
        if w < h:  # 如果 w< h
            h = h if random.random() < 0.5 else -h
            p3 = (c12[0] + h, c12[1])
        else:
            w = w if random.random() < 0.5 else -w
            p3 = (c12[0], c12[1] + w)
        # 计算三个基准点的有效区域valid_range
        base = np.asarray([p1, p2, p3])
        xmin, ymin, xmax, ymax = min(base[:, 0]), min(base[:, 1]), max(base[:, 0]), max(base[:, 1])
        valid_range = np.asarray([[xmin, ymin, xmax, ymax]])
        valid_range = image_utils.extend_xyxy(valid_range, scale=(scale, scale))[0]
        # 获得在有效区域valid_range所有点
        # image, points = self.get_points_valid_range(image, select, valid_range, crop=True)
        image, points = self.get_points_valid_range(image, points, valid_range, crop=True)
        return image, points

    def get_points_valid_range(self, image, points, valid_range, crop=True):
        """
        获得在valid_range范围的points
        :param image: 图像
        :param points: 点集合
        :param valid_range: 有效范围(xmin,ymin,xmax,ymax)
        :param crop: 是否采裁剪图像在valid_range有效区域
        :return:
        """
        xmin, ymin, xmax, ymax = valid_range
        contour = [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]
        out_points = []
        for pt in points:
            dist = image_utils.pointPolygonTest(pt, contour)
            if dist > 0: out_points.append(pt)
        out_points = np.asarray(out_points)
        if crop:
            image = image_utils.get_bbox_crop_padding(image, valid_range, color=(255, 255, 255))
            out_points = out_points - (valid_range[0], valid_range[1])
        return image, out_points

    def index2id(self, index):
        """
        :param index: int or str
        :return:
        """
        if isinstance(index, numbers.Number):
            image_id = self.image_id[index]
        else:
            image_id = index
        return image_id

    def __len__(self):
        return len(self.image_id)

    @staticmethod
    def get_files_id(file_list):
        """
        :param file_list:
        :return:
        """
        image_idx = []
        for path in file_list:
            basename = os.path.basename(path)
            id = basename.split(".")[0]
            image_idx.append(id)
        return image_idx

    def read_image(self, image_file: str, use_rgb=True):
        """
        :param image_file:
        :param use_rgb:
        :return:
        """
        image = cv2.imread(image_file, cv2.IMREAD_COLOR)
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 4:
            image = image[:, :, 0:3]
        if use_rgb:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    def load_annotations(self, ann_file: str):
        with open(ann_file, "r") as f:
            annotation = json.load(f)
        points = [data['points'][0] for data in annotation['shapes']]
        points = np.asarray(points, np.float32)
        return points


def show_target_image(image, points, normal=False, transpose=False):
    import numpy as np
    image = np.asarray(image)
    points = np.asarray(points)
    if normal:
        image = np.asarray(image * 255)
    image = np.asarray(image, np.uint8)
    print("image:{},points:{}".format(image.shape,  points.shape))
    if transpose:
        image = image_utils.untranspose(image)
    image = image_utils.draw_landmark(image, [points], radius=2, thickness=4, color=(255, 0, 0))
    image_utils.cv_show_image("image", image, use_rgb=True)


if __name__ == "__main__":
    import torch

    # filename = "/home/dm/nasdata/dataset/handwriting/zitie/train.txt"
    # filename = "/home/dm/nasdata/dataset-dmai/handwriting/grid-det/grid_cross_points/train.txt"
    # filename = "/home/dm/nasdata/dataset-dmai/handwriting/grid-det/grid_cross_points_v2/trainval.txt"
    filename = "/home/dm/nasdata/dataset-dmai/handwriting/grid-det/grid_cross_points_v3/trainval.txt"
    input_size = [160, 160]

    dataset = LabelMeDataset(filename=filename,
                             data_root=None,
                             anno_dir=None,
                             image_dir=None,
                             class_name=None,
                             check=False,
                             phase="val",
                             resample=False,
                             shuffle=False)
    print("have num:{}".format(len(dataset)))
    for i in range(len(dataset)):
        print(i)  # i=20
        data = dataset.__getitem__(0)
        image, points = data["image"], data["points"]
        show_target_image(image, points, normal=False, transpose=False)
