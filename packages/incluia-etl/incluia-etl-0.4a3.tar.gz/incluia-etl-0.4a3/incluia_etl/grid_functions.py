import os

import boto3
import cv2
import numpy as np
from matplotlib import image as mpimg

from incluia_etl.album_functions import find_closest_image_to_point

from .utils.request_functions import s3_file_exists

s3_client = boto3.client('s3')


def mosaic_around_point_using_batches(
    x=None,
    y=None,
    size=None,
    batch_dict=None,
    local_batches_dir='../data/003_batches/',
    album=None,
    bucket=None,
    lat_difference=None,
    lon_difference=None,
    pixel_size_y=None,
    pixel_size_x=None,
    y_batch_dim=None,
    pixels_intersect_h=None,
    pixels_intersect_v=None,
    verbose=True,
    max_batches=4,
):
    """
    Generates a mosaic around a point using batches.
    A batch is a large mosaic previously stored in S3.
    ----------
    Parameters
        x : float. Longitude of the point of interest.
        y : float. Latitude of the point of interest.
        size: int. Number of pixels of square's side output.
        batch_dict: dictionary of matrices. Initially, in the jupyter-notebook,
        batch_dict is initialized as batch_dict={}. Then on each mosaic_around_point iteration,
        the dictionary, which is sent back as an output, adds if necessary the batches
        that were necessary for producing the mosaic from that iteration. Since the whole
        city imagery is to memory expensive, the dictionary stores only a number
        of batches that the machine can store in RAM. Therefore, to generate mosaics fast,
        it is highly recommended that when using it iteratively for a list of coordinates,
        the coordinates are ordered.
        album: geopandas dataframe. Country album.
        lon_difference: float. Longitude difference between two album images centroids.
        lat_difference: float. Latitude difference between two album images centroids.
        y_batch_dim: Number of images within a batch in y-axis.
        verbose: boolean. Prints verbose
        max_batches: Maximum number of batches dict can store, each batch uses around 120Mb.
    """

    img_out = None
    wld = None

    # Starts by identifying the image id which is closest to the coordinate x,y input.
    img_index = find_closest_image_to_point(x, y, album=album, verbose=verbose)
    if img_index is None:
        return img_out, wld, batch_dict

    # Loads the image features that are necessary for this routine using its id.
    img_cols = [
        'batch_label',
        'batch_x',
        'batch_y',
        'cell_x',
        'cell_y',
        'centroid_lon',
        'centroid_lat',
    ]
    (
        batch_label,
        batch_x,
        batch_y,
        cell_x,
        cell_y,
        centroid_lon,
        centroid_lat,
    ) = album.loc[img_index][img_cols]
    # Particularly, it loads the batch where the image is and gets
    # loaded in the variable img_batch.
    batch_dict = load_batch_to_dict(
        batch_label, batch_dict, bucket=bucket, local_batches_dir=local_batches_dir
    )
    img_batch = batch_dict[batch_label]

    # We wish to calculate the pixel of the image that corresponds to the centroid x,y.
    # First, we calculate the offset of centroid of the image it falls in with respect x,y.
    image_xmove = (x - centroid_lon) / lon_difference  # -0.5 < image_xmove < 0.5
    image_ymove = (y - centroid_lat) / lat_difference  # -0.5 < image_ymove < 0.5

    # To calculate the pixel we start in the centroid of the first image (400/2)
    # and then add the number of pixels a single picture represents using
    # cell_x *  (400 - pixels_intersect_v - 1), where cell_x is an integer.
    # Then image_xmove offsets at least -0.5 and at most 0.5.
    # As an example 3.75 is attained as 4 - 0.25 instead of
    # 3 + 0.75. The centroid pixels are stored in image_centroid_pixel_[x,y].
    image_xmove_aux = 400 / 2 + (cell_x + image_xmove) * (400 - pixels_intersect_v - 1)
    image_centroid_pixel_x = int(round(image_xmove_aux))
    image_ymove_aux = 375 / 2 + (((y_batch_dim - 1) - cell_y) - image_ymove) * (
        375 + pixels_intersect_h
    )
    image_centroid_pixel_y = int(round(image_ymove_aux))

    # Then we simply crop the batch image according to the number of desired pixels.
    if size % 2 == 1:
        range_x_min = image_centroid_pixel_x - int((size - 1) / 2)
        range_x_max = image_centroid_pixel_x + int((size + 1) / 2)
        range_y_min = image_centroid_pixel_y - int((size - 1) / 2)
        range_y_max = image_centroid_pixel_y + int((size + 1) / 2)
    else:
        range_x_min = image_centroid_pixel_x - int(size / 2)
        range_x_max = image_centroid_pixel_x + int(size / 2)
        range_y_min = image_centroid_pixel_y - int(size / 2)
        range_y_max = image_centroid_pixel_y + int(size / 2)

    # Before cropping the batch, we need to know how much of the mosaic
    # required is contained in this batch or else, we require neighboring
    # batches to complete the mosaic.
    ########################################################################################
    #########################################################################################
    #                      Procedure for cropping and concatenating batches.
    # Let (0,0) be the image we have cropped so far
    # but not we require to concatenate a vertical/horizontal strips and even some corners.
    # In any case we only need to consider its 8 images around the image (0,0).
    # We begin by labeling them as follows:

    ################################
    # (-1,  1) # (0,  1) # (1,  1) #
    ################################
    # (-1,  0) # (0,  0) # (1,  0) #
    ################################
    # (-1, -1) # (0, -1) # (1, -1) #
    ################################

    # In this procedure we first crop images (0, 1) or (0, -1) and add a vertical
    # strip above or below (0,0). Then, we generate as a separate strip to the left
    # or to the right. This strip has exactly the same height of the image saved in
    # the first step. Finally, we concatenate this image horizontally.
    # The code is done pretty much case-wise. Perhaps some code could be recycled but the
    # independency of the cases make the code quite clear.

    # batch_[x,y]_aux can take values in [-1, 1] and correspond to the
    # batch label its working with. The default values are 0,0.
    batch_x_aux = 0
    batch_y_aux = 0

    # The default values are the ranges previously stored, which we know they
    # exceeded the limits of the 0,0 batch.
    range_x_min_iter, range_x_max_iter = range_x_min, range_x_max
    range_y_min_iter, range_y_max_iter = range_y_min, range_y_max

    # We begin by identifying which is the range that exceeded its dimensions,
    # so then we can load the corresponding batch that contains the missing mosaic.
    # There are four cases: left, bottom right, top, respectively.
    if range_x_min < 0:
        batch_x_aux = -1
        range_x_min_iter = 0
    if range_x_max > img_batch.shape[1]:
        batch_x_aux = 1
        range_x_max_iter = img_batch.shape[1]
    if range_y_min < 0:
        batch_y_aux = 1
        range_y_min_iter = 0
    if range_y_max > img_batch.shape[0]:
        batch_y_aux = -1
        range_y_max_iter = img_batch.shape[0]

    # We crop all the mosaic contained in the batch 0,0.
    img_out = img_batch[
        range_y_min_iter:range_y_max_iter, range_x_min_iter:range_x_max_iter, :
    ]

    # From here below, only IF clauses appear which correspond to the different
    # cases when we require other batches to complete the mosaic.
    # We start by adding only top and bottom images there are two possible cases.
    # We call the batch, and concatenate
    # its vertical strip below or above, respectively.
    if batch_y_aux in [-1, 1]:
        batch_x_iter = '{:02d}'.format(batch_x)
        batch_y_iter = '{:02d}'.format(batch_y + batch_y_aux)
        batch_iter_label = batch_x_iter + '_' + batch_y_iter
        batch_dict = load_batch_to_dict(
            batch_iter_label,
            batch_dict,
            bucket=bucket,
            local_batches_dir=local_batches_dir,
        )
        img_iter = batch_dict[batch_iter_label]
        if batch_y_aux == -1:
            range_y_min_iter = 0
            range_y_max_iter = range_y_max - img_batch.shape[0] - pixels_intersect_h + 1
            img_iter = img_iter[
                range_y_min_iter:range_y_max_iter, range_x_min_iter:range_x_max_iter, :
            ]
            img_out = cv2.vconcat([img_out[: (pixels_intersect_h - 1), :, :], img_iter])
        if batch_y_aux == 1:
            range_y_min_iter = range_y_min + img_batch.shape[0] + pixels_intersect_h - 1
            range_y_max_iter = img_batch.shape[0]
            img_iter = img_iter[
                range_y_min_iter:range_y_max_iter, range_x_min_iter:range_x_max_iter, :
            ]
            img_out = cv2.vconcat([img_iter[: (pixels_intersect_h - 1), :, :], img_out])

    # Then we generate left or right strips.
    img_v = np.array([])  # Initialize vertical Strip
    # We start by generating the batch labels,
    # the x is constant and the y can be one single image or two if we
    # need to concatenate a corner. Depending on the case the different ranges get calculated.
    if batch_x_aux in [-1, 1]:
        if batch_x_aux == -1:
            range_x_min_iter = range_x_min + img_batch.shape[1] - pixels_intersect_v - 1
            range_x_max_iter = img_batch.shape[1]
        else:
            range_x_min_iter = 0
            range_x_max_iter = range_x_max - img_batch.shape[1] + pixels_intersect_v + 1
        batch_x_iter = '{:02d}'.format(batch_x + batch_x_aux)

        # First we visit image [-1,0] or [1,0],
        # then we add vertical or horizontal strip. Just as above.
        range_y_list = [0]
        if batch_y_aux == -1:
            range_y_list.append(-1)
        if batch_y_aux == 1:
            range_y_list.append(1)

        # reset range-y values as in image (0,0)
        range_y_min_iter, range_y_max_iter = range_y_min, range_y_max
        if range_y_min < 0:
            range_y_min_iter = 0
        if range_y_max > img_batch.shape[0]:
            range_y_max_iter = img_batch.shape[0]

        for j in range_y_list:
            batch_y_iter = '{:02d}'.format(batch_y + j)
            batch_iter_label = batch_x_iter + '_' + batch_y_iter
            batch_dict = load_batch_to_dict(
                batch_iter_label,
                batch_dict,
                bucket=bucket,
                local_batches_dir=local_batches_dir,
            )
            img_iter = batch_dict[batch_iter_label]
            if j == -1:
                range_y_min_iter = 0
                range_y_max_iter = (
                    range_y_max - img_batch.shape[0] - pixels_intersect_h + 1
                )
            if j == 1:
                range_y_min_iter = (
                    range_y_min + img_batch.shape[0] + pixels_intersect_h - 1
                )
                range_y_max_iter = img_batch.shape[0]

            img_iter = img_iter[
                range_y_min_iter:range_y_max_iter, range_x_min_iter:range_x_max_iter, :
            ]

            if j == 0:
                img_v = img_iter
            if j == -1:
                img_v = cv2.vconcat([img_v[: (pixels_intersect_h - 1), :, :], img_iter])
            if j == 1:
                img_v = cv2.vconcat([img_iter[: (pixels_intersect_h - 1), :, :], img_v])

        if batch_x_aux == -1:
            img_out = cv2.hconcat([img_v, img_out[:, (pixels_intersect_v + 1) :, :]])
        else:
            img_out = cv2.hconcat([img_out, img_v[:, (pixels_intersect_v + 1) :, :]])

    # Eliminates excess of stored batches in dict
    batch_keys = list(batch_dict.keys())
    batch_keys.reverse()
    batch_keys_len = len(batch_keys)
    if batch_keys_len > max_batches:
        for i in range(max_batches, batch_keys_len):
            batch_dict.pop(batch_keys[i], None)
            local_batches_path = local_batches_dir + batch_keys[i] + '.png'
            if os.path.exists(local_batches_path):
                os.remove(local_batches_path)

    # Wld file for georeferencing an image. USE EPSG:4326
    wld = np.zeros(6)

    wld[0] = pixel_size_x
    wld[3] = -pixel_size_y
    wld[4] = x - pixel_size_x * size / 2
    wld[5] = y + pixel_size_y * size / 2

    return img_out, wld, batch_dict


def load_batch_to_dict(
    batch_label=None,
    batch_dict=None,
    bucket=None,
    local_batches_dir='../data/003_batches/',
):
    """
    Adds the batch 'batch_label' into the dictionary 'batch_dict' which
    contains the session's loaded batches.
    The batch is loaded from AWS.
    ----------
    Parameters
        batch_label : str. Batch label to load into dictionary.
        batch_dict : dict of matroids: Dictionary which contains batches and
        batch label as keys.
        bucket: str. Bucket name in AWS.
        local_batches_dir: str. Local directory where batches are stored.
    """
    assert '/data/' in local_batches_dir, 'local_batches_dir must contain "/data/"'

    # if batch_label is in dictionary, there is nothing to do
    if batch_label in batch_dict.keys():
        return batch_dict

    local_batches_path = local_batches_dir + batch_label + '.png'
    # if file exists locally
    if not os.path.exists(local_batches_path):
        s3_batches_path = local_batches_path.split('/data/')[-1]
        exists = s3_file_exists(bucket=bucket, s3_file_path=s3_batches_path)
        if exists:
            s3_client.download_file(bucket, s3_batches_path, local_batches_path)
            img = (mpimg.imread(local_batches_path) * 255).astype(np.uint8)
            batch_dict[batch_label] = img

        # If else, then generate an auxiliary batch as a blank image of the appropriate size.
        # Size is given by any batch, specifically we take the size of the first batch in dict.
        else:
            batch_label_zero = list(batch_dict.keys())[0]
            batch_shape = batch_dict[batch_label_zero].shape
            batch_dict[batch_label] = np.ones(batch_shape, dtype=np.uint8)
    return batch_dict


def initialize_batch(batch_list, local_batches_dir='../data/003_batches/'):
    """
    Initializes batch_dict with current batches in local_batches_dir folder.
    ----------
    Parameters
        batch_list: list str. All album's batch labels as a list of strings.
    """
    assert '/data/' in local_batches_dir, 'local_batches_dir must contain "/data/"'

    batch_dict = {}

    for batch_label in batch_list:
        local_batches_path = local_batches_dir + batch_label + '.png'
        batch_stored = os.path.exists(local_batches_path)
        if batch_stored:
            img = (mpimg.imread(local_batches_path) * 255).astype(np.uint8)
            batch_dict[batch_label] = img

    return batch_dict
