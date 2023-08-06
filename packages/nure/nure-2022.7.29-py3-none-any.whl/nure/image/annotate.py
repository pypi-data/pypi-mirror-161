import math

import numpy as np

ESP = np.finfo(np.float32).eps


def to_ndarray(a):
    if not isinstance(a, np.ndarray):
        a = np.array(a)

    return a


def polygon2bbox(polygon):
    xys = np.reshape(polygon, (-1, 2))
    x1, y1 = np.min(xys, axis=0)
    x2, y2 = np.max(xys, axis=0)

    return x1, y1, x2 - x1, y2 - y1


def normalize_bboxes(bboxes, image_size):
    """ normalize the bboxes to [0, 1]
    Args:
        bboxes: array of shape [N, 4]
            each bounding box contains 4 values likes (ymin, xmin, ymax, xmax)
        image_size: tuple of 2 elements
            image size as (width, height)
    """
    bboxes = to_ndarray(bboxes)
    image_size = to_ndarray(image_size)

    width, height = image_size[..., 0], image_size[..., 1]

    normalized = np.stack((
        bboxes[..., 0] / height, bboxes[..., 1] / width,
        bboxes[..., 2] / height, bboxes[..., 3] / width), axis=-1)

    return normalized


def denormalize_bboxes(bboxes, image_size):
    """ inverse the action of normalize_bboxes
    Args:
        bboxes: array of shape [N, 4]
            each bounding box contains 4 values likes (ymin, xmin, ymax, xmax)
        image_size: tuple of 2 elements
            image size as (width, height)
    """
    image_size = to_ndarray(image_size)
    return normalize_bboxes(bboxes, 1 / image_size)


def calibrate_bboxes(boxes, image_size):
    """ calibrate the bounding boxes when the image is padded to sqaure
    """
    boxes = to_ndarray(boxes)
    image_size = to_ndarray(image_size)

    ymin, xmin, ymax, xmax = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]
    width, height = image_size[..., 0], image_size[..., 1]

    if width < height:
        ratio = width / height
        xmin = xmin * ratio
        xmax = xmax * ratio
    else:
        ratio = height / width
        ymin = ymin * ratio
        ymax = ymax * ratio

    return np.stack((ymin, xmin, ymax, xmax), axis=-1)


def xywh2yxyx(boxes):
    xmin, ymin, width, height = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]

    ymax = ymin + height
    xmax = xmin + width

    return np.stack((ymin, xmin, ymax, xmax), axis=-1)


def xywh2xyxy(boxes):
    xmin, ymin, width, height = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]

    ymax = ymin + height
    xmax = xmin + width

    return np.stack((xmin, ymin, xmax, ymax), axis=-1)


def yxyx2xywh(boxes):
    ymin, xmin, ymax, xmax = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]

    height = ymax - ymin
    width = xmax - xmin

    return np.stack((xmin, ymin, width, height), axis=-1)


def xyxy2yxyx(boxes):
    xmin, ymin, xmax, ymax = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]
    return np.stack((ymin, xmin, ymax, xmax), axis=-1)


def yxyx2xyxy(boxes):
    ymin, xmin, ymax, xmax = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]
    return np.stack((xmin, ymin, xmax, ymax), axis=-1)


def boxes_area(boxes):
    ymin, xmin, ymax, xmax = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]
    areas = (xmax - xmin) * (ymax - ymin)
    return areas


def intersect_over_union(boxA, boxB):
    boxA = to_ndarray(boxA)
    boxB = to_ndarray(boxB)
    # determine the (x, y)-coordinates of the intersection rectangle
    y1 = np.maximum(boxA[..., 0], boxB[..., 0])
    x1 = np.maximum(boxA[..., 1], boxB[..., 1])
    y2 = np.minimum(boxA[..., 2], boxB[..., 2])
    x2 = np.minimum(boxA[..., 3], boxB[..., 3])

    # compute the area of intersection rectangle
    inter_area = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    boxA_area = boxes_area(boxA)
    boxB_area = boxes_area(boxB)
    iou = inter_area / (boxA_area + boxB_area - inter_area)

    return iou


def intersect_over_b(boxA, boxB):
    boxA = to_ndarray(boxA)
    boxB = to_ndarray(boxB)
    # determine the (x, y)-coordinates of the intersection rectangle
    y1 = np.maximum(boxA[..., 0], boxB[..., 0])
    x1 = np.maximum(boxA[..., 1], boxB[..., 1])
    y2 = np.minimum(boxA[..., 2], boxB[..., 2])
    x2 = np.minimum(boxA[..., 3], boxB[..., 3])

    # compute the area of intersection rectangle
    interArea = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    boxBArea = (boxB[..., 2] - boxB[..., 0]) * (boxB[..., 3] - boxB[..., 1])
    iob = interArea / (boxBArea + ESP)

    return iob


def clip_boxes_out_of_image(boxes, image_size, threshold=0.4):
    """Clip off parts of the BB box that are outside of the image in-place.
    Parameters
    ----------
    boxes: tuple[N,4]
        bounding box [ymin, xmin, ymax, xmax]
    image_size:
        size of image [height, width]
    Returns
    -------
    tuple[N',4]
        Bounding box, clipped to fall within the image dimensions.
        The object may have been modified in-place.
    """
    boxes = to_ndarray(boxes)
    image_size = to_ndarray(image_size)
    ymin, xmin, ymax, xmax = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]
    height, width = image_size[..., 0], image_size[..., 1]

    xmin = np.clip(xmin, 0, width - ESP)
    xmax = np.clip(xmax, 0, width - ESP)
    ymin = np.clip(ymin, 0, height - ESP)
    ymax = np.clip(ymax, 0, height - ESP)

    new_boxes = np.stack((ymin, xmin, ymax, xmax), axis=-1)
    if threshold is None:
        return new_boxes, np.ones_like(new_boxes)

    old_area = boxes_area(boxes)
    new_area = boxes_area(new_boxes)
    mask = new_area / old_area > threshold

    return new_boxes, mask


def translate_boxes(boxes, yx):
    """ translate boxes [yxyx] with offset yx
    """
    yx = to_ndarray(yx)
    offset_y, offset_x = yx[..., 0], yx[..., 1]
    ymin, xmin, ymax, xmax = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]
    xmin = xmin + offset_x
    xmax = xmax + offset_x
    ymin = ymin + offset_y
    ymax = ymax + offset_y

    return np.stack((ymin, xmin, ymax, xmax), axis=-1)


def expand_bounding_boox(image_sizes, boxes, margin) -> np.ndarray:
    """ expand the bounding box evenly all direction by margin percent
    Paramters:
        image_size: Tuple[int, int]
            height, width of image
        bbox: Tuple[int, int, int, int]
            original bounding box. Format in ymin, xmin, ymax, xmax
        margin: float
            the proportion of expansion of each edge. Ex: 0.1 is 10%
    Returns:
        Tuple[int, int, int, int]
            expanded bounding box accounting for image size
    """
    image_sizes = to_ndarray(image_sizes)
    boxes = to_ndarray(boxes)

    ymin, xmin, ymax, xmax = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]
    w = xmax - xmin
    h = ymax - ymin
    xmin = np.maximum(0, xmin - margin * w)
    ymin = np.maximum(0, ymin - margin * h)
    xmax = np.minimum(image_sizes[..., 1], xmax + margin * w)
    ymax = np.minimum(image_sizes[..., 0], ymax + margin * h)

    return np.stack((ymin, xmin, ymax, xmax), axis=-1)


def cut_instance(image_size, size, bboxes=None, classes=None, overlap=0.1, acceptable_area=0.4):
    """cut image into multiple patch
    Args:
        image_size (tuple(int, int)): original image size (height, width)
        size (int): image patch size
        bboxes (list(4-int,), optional): list of bounding boxes. Defaults to None.
        classes (list(4-int,)), optional): class of boxes. Defaults to None.
        overlap (float, optional): overlap percentage. Defaults to 0.1.
        acceptable_area (float, optional): any cutted boxes whose area is smaller than original one is remove. Defaults to 0.4.
    Returns:
        resolution, new_rects, boxes_list, classes_list
    """
    height, width = image_size
    rows = math.ceil((height - overlap * size) / (size - overlap * size))
    cols = math.ceil((width - overlap * size) / (size - overlap * size))
    resolution = [rows, cols]

    ymin = np.arange(rows) * size * (1 - overlap)
    xmin = np.arange(cols) * size * (1 - overlap)
    ymax = ymin + size
    xmax = xmin + size
    ymax[-1] = height
    xmax[-1] = width

    xx, yy = np.meshgrid(np.arange(cols), np.arange(rows))
    new_rects = np.stack([
        np.take(ymin, yy),
        np.take(xmin, xx),
        np.take(ymax, yy),
        np.take(xmax, xx),
    ], axis=-1).reshape((-1, 4))

    if bboxes is None:
        return resolution, new_rects
    assert classes is not None

    # shape [1, N, 4]
    rects = new_rects.reshape((1, -1, 4))

    # shape [B, 1, 4]
    bboxes = bboxes.reshape((-1, 1, 4))

    # propagate together and get [B, N, 4]
    boxes_to_rects = np.stack([
        bboxes[..., 0] - rects[..., 0],
        bboxes[..., 1] - rects[..., 1],
        bboxes[..., 2] - rects[..., 0],
        bboxes[..., 3] - rects[..., 1]
    ], axis=-1)

    # shape [1, N, 2]
    rects_size = np.stack([
        rects[..., 2] - rects[..., 0],
        rects[..., 3] - rects[..., 1],
    ], axis=-1)

    # clip boxes respect to rects
    # shape [B, N, 4] and [B, N]
    new_boxes, mask = clip_boxes_out_of_image(boxes_to_rects, rects_size, threshold=acceptable_area)

    boxes_list = [new_boxes[mask[:, i], i] for i in range(new_rects.shape[0])]
    classes_list = [classes[mask[:, i]] for i in range(new_rects.shape[0])]

    return resolution, new_rects, boxes_list, classes_list


def _non_maxima_suppression_(boxes, scores=None, threshold=0.7):
    inverted_indices = None
    if scores is not None:
        indices = np.argsort(scores)[::-1]
        boxes = boxes[indices]
        inverted_indices = np.argsort(indices)

    mask = np.ones(boxes.shape[0], dtype=np.bool)
    for i in range(boxes.shape[0]):
        ious = intersect_over_union(boxes[i], boxes[i + 1:])
        suppressed_indices = np.where(ious > threshold)[0] + i + 1
        mask[suppressed_indices] = False

    if scores is None:
        return mask
    return mask[inverted_indices]


def non_maxima_suppression(boxes, scores=None, classes=None, threshold=0.7):
    if classes is None:
        return _non_maxima_suppression_(boxes, scores=scores, threshold=threshold)

    class_uniques = np.unique(classes)
    sup_mask = np.ones(boxes.shape[0], dtype=np.bool)
    for uclass in class_uniques:
        cmask = classes == uclass
        sup_cmask = _non_maxima_suppression_(
            boxes[cmask],
            scores=None if scores is None else scores[cmask], threshold=threshold)
        sup_mask[cmask] = sup_cmask

    return sup_mask
