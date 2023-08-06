import numpy as np
import torch
from scipy import ndimage
from skimage import filters
from skimage.measure import label, regionprops
from skimage.morphology import closing, disk, square
from skimage.segmentation import clear_border, expand_labels


def segment(image):
    # apply threshold
    thresh = filters.threshold_otsu(image)
    bw = closing(image > thresh, square(3))
    # remove artifacts connected to image border
    cleared = clear_border(bw)
    # label image regions
    return label(cleared, return_num=True)


def scale(x):
    if x.max() > x.min():
        return (x - x.min()) / (x.max() - x.min())
    else:
        return x


def project_correct(zstack, max_area, nc):
    max_proj = zstack.max(axis=0)
    if nc < 2:
        return max_proj
    # Background correction
    r = int(np.sqrt(max_area/np.pi))
    corrected = max_proj - filters.median(max_proj, disk(r))
    return corrected


def per_z(y):
    nc = 0
    labels = []
    max_area = 0
    for image in y:
        label_image, i = segment(image)
        labels.append(label_image)
        if i > nc:
            nc = i
        try:
            area = max([r.area for r in regionprops(label_image)])
        except ValueError:
            # TODO log error
            area = 0
        if area > max_area:
            max_area = area
    return np.stack(labels), nc, max_area


def centroid(image):
    empty = np.ones_like(image)
    for obj in regionprops(image):
        y0, x0 = obj.centroid
        empty[int(y0), int(x0)] = 0
    return empty


def outline(label_image):
    outline_image = expand_labels(label_image) - label_image
    return 1 - outline_image.astype(bool)


def centers(label_image):
    # Get distance transform
    distance = ndimage.distance_transform_edt(label_image)
    # Create empty
    empty = np.ones_like(label_image)
    # For each region
    for obj in regionprops(label_image):
        # Extract the region mask
        masked = distance*(label_image == obj.label)
        empty[masked == masked.max()] = 0
    return empty


def local_scale(label_image, distance):
    empty = np.zeros_like(distance)
    max_value = distance.max()
    for obj in regionprops(label_image):
        masked = distance*(label_image == obj.label)
        empty += max_value * masked / masked.max()
    return empty


def preprocess_target(target, test=False):
    # z, nc, max_area = per_z(target)
    max_proj = target.sum(axis=0).astype(float)
    # project_correct(target, max_area, nc)
    proj_seg, nc_proj = segment(max_proj)
    distance = ndimage.distance_transform_edt(proj_seg)
    distance = local_scale(proj_seg, distance)
    # distance -= ndimage.distance_transform_edt(1 - proj_seg.astype(bool))
    target = scale(distance)
    if isinstance(target, np.ndarray):
        target = torch.from_numpy(target).float()
    if test:
        return max_proj, proj_seg, target
    else:
        return target[None, ...]
