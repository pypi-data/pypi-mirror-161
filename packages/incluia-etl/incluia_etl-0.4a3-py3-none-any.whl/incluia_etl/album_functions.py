import boto3
import cv2
import matplotlib.image as mpimg
import numpy as np
from tqdm import trange

from .utils.request_functions import s3_file_exists

s3_client = boto3.client('s3')


def find_closest_image_to_point(x=None, y=None, album=None, verbose=True):
    """
    Finding the closest image index to a given coordinate point.
    ----------
    Parameters
        x : float. Longitude of the point of interest.
        y : float. Latitude of the point of interest.
        album: geopandas dataframe. Country album.
        verbose: boolean. Print verbose if True.
    """

    img_index = None

    # epsilon distance to avoid numeric errors.
    epsilon = 1e-5

    x_img_min = np.abs(x - album['centroid_lon'])
    x_img_argmin = list(np.where(np.abs(x_img_min - x_img_min.min()) < epsilon)[0])

    y_img_min = np.abs(y - album['centroid_lat'])
    y_img_argmin = list(np.where(np.abs(y_img_min - y_img_min.min()) < epsilon)[0])

    # index of the image with the closest centroid to the point of interest
    img_index_list = list(set(x_img_argmin) & set(y_img_argmin))
    if len(img_index_list) > 0:
        img_index = img_index_list[0]
    else:
        x_str = str(x)
        y_str = str(y)
        if verbose:
            print(
                f"Input coordinates ({x_str}, {y_str}) out of imagery extraction bounds."
            )
        else:
            pass
    return img_index


def mosaic_around_point_using_album(
    x=None,
    y=None,
    size=None,
    album=None,
    bucket=None,
    x_batch_dim=None,
    y_batch_dim=None,
    pixels_intersect_h=None,
    pixels_intersect_v=None,
    s3_file_dir='002_api_images/',
    local_file_dir='../data/002_api_images/test/',
):
    """
    Displays a mosaic given a point in coordinates x (longitude) and y (latitude).
    size is used to calculate the number of images the mosaic contains.
    size=1 is a single image, size=2 is a 3x3 mosaic, size=3 is a 5x5 mosaic, etc.
    """

    assert '/data/' in local_file_dir, 'local_file_dir must contain /data/'

    # Local path for storing outputs.
    local_file_path = f'{local_file_dir}img_iter.png'

    # image index of the closest point
    img_index = find_closest_image_to_point(x=x, y=y, album=album)

    # save album features from image
    pm_index, batch_x, batch_y, cell_x, cell_y = album.iloc[img_index][
        ['pm_index', 'batch_x', 'batch_y', 'cell_x', 'cell_y']
    ]

    # To create a mosaic img, we will generate horizontal strips of images,
    # and we will concatenate each strip img_h .
    # The outer for is to concatenate horizontal image strips img_h into img.
    img = np.array([])  # OUTPUT: tensor that defines the image

    for j in trange(1 - size, size, desc='Iterative Progress'):
        img_h = np.array([])
        # The inner for is to concatenate vertical single images into a horizontal strip img_h
        for i in range(1 - size, size):
            # set image label for the iteration
            batch_x_iter = batch_x
            batch_y_iter = batch_y
            cell_x_iter = cell_x + i
            cell_y_iter = cell_y + j

            # adjust batch and cell labels if the image is outside the current batch
            if cell_x_iter < 0:
                cell_x_iter = cell_x_iter + x_batch_dim
                batch_x_iter = batch_x - 1
            if cell_x_iter > x_batch_dim - 1:
                cell_x_iter = cell_x_iter - x_batch_dim
                batch_x_iter = batch_x + 1
            if cell_y_iter < 0:
                cell_y_iter = cell_y_iter + y_batch_dim
                batch_y_iter = batch_y - 1
            if cell_y_iter > y_batch_dim - 1:
                cell_y_iter = cell_y_iter - y_batch_dim
                batch_y_iter = batch_y + 1

            # define iteration image path
            pm_dir = str(pm_index) + '/'
            batch_x_label = '{:02d}'.format(batch_x_iter)
            batch_y_label = '{:02d}'.format(batch_y_iter)
            batch_path_iter = f'{batch_x_label}_{batch_y_label}/'
            cell_x_label = '{:02d}'.format(cell_x_iter)
            cell_y_label = '{:02d}'.format(cell_y_iter)
            img_iter_path = f'{cell_x_label}_{cell_y_label}.png'
            s3_file_path = f'{s3_file_dir}{pm_dir}{batch_path_iter}{img_iter_path}'

            # check if the image is currently saved in S3
            img_exists = s3_file_exists(bucket=bucket, s3_file_path=s3_file_path)
            if img_exists:
                # if the simage exists, download it to locally to local_img_path and the read it.
                s3_client.download_file(bucket, s3_file_path, local_file_path)
                img_iter = (mpimg.imread(local_file_path) * 255).astype(np.uint8)
            else:
                # if the image does not exist, define a blanc picture in its place.
                img_iter = np.ones((375, 400, 4)).astype(np.uint8)

            # In the first iteration of the inner for, img_h is empty.
            # Therefore, Else applies and the image is copied.
            # For the following iterations an image is concatenated.
            if len(img_h) > 0:
                img_h = cv2.hconcat([img_h, img_iter[:, (pixels_intersect_v + 1):, :]])
            else:
                img_h = img_iter

        # Analogous routine for the joining horizontal straps.
        if j > -size + 1:
            img = cv2.vconcat([img_h[: (pixels_intersect_h - 1), :, :], img])
        else:
            img = img_h

    # img_index is useful for the other routine.
    return img


def corners_coordinates(lat=None, lon=None):
    """
    Returns a 4 coordinate points--latitude and longitude--where the corners
    of a satellite image are.
    ------------------------------------------------
    parameters:
        lat: float. Centroid of image latitude
        lon: float. Centroid of image longitude
        out: lat1, lat2, lon1, lon2: floats. Coordinates of corners.
    """
    # Earth Modelled as a Sphere
    lat_r = lat / 180 * np.pi
    # lon_r = lon / 180 * np.pi

    r1 = 6378137.0  # radius at equator
    r2 = 6356752.3  # radius at pole

    # https://rechneronline.de/earth-radius/
    numerator = (r1**2 * np.cos(lat_r)) ** 2 + (r2**2 * np.sin(lat_r)) ** 2
    denominator = (r1 * np.cos(lat_r)) ** 2 + (r2 * np.sin(lat_r)) ** 2
    earth_radius = np.sqrt(numerator / denominator)
    # https://groups.google.com/g/google-maps-js-api-v3/c/hDRO4oHVSeM?pli=1
    metersperpx = earth_radius / (128 / np.pi) * np.cos(lat_r) / 2**20
    mts = metersperpx * np.array(
        [400, 400]
    )  # each pixel how many meters they represent

    # Wikipedia's formulas on pages latitude and longitude
    # Earth Modelled as an Ellipsoid

    e2 = 1 - r2**2 / r1**2  # squared excentricity
    # Obtaining latitude and longitude of corners of an image given centroid

    ################################################
    lat_grad_mts = np.pi * r1 * (1 - e2) / (180 * (1 - e2 * np.sin(lat_r) ** 2) ** 1.5)
    lat_dif = mts[0] / lat_grad_mts  # album cte

    lat1 = lat - lat_dif / 2  # image corners
    lat2 = lat + lat_dif / 2  # image corners
    lon_grad_mts = (
        np.pi * r1 * np.cos(lat_r) / (180 * (1 - e2 * np.sin(lat_r) ** 2) ** 0.5)
    )
    lon_dif = mts[1] / lon_grad_mts  # album cte

    lon1 = lon - lon_dif / 2  # image corners
    lon2 = lon + lon_dif / 2  # image corners

    return lat1, lat2, lon1, lon2
