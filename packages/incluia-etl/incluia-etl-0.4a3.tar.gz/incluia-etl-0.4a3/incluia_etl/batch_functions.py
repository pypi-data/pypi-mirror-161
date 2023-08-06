import boto3
import cv2
import matplotlib.image as mpimg
import numpy as np
from tqdm import trange

from .utils.request_functions import s3_file_exists

s3_client = boto3.client('s3')


def find_pixel_intersection(
    horizontal=None,
    album=None,
    bucket=None,
    x_batch_dim=None,
    y_batch_dim=None,
    local_file_dir='../data/01_raw_images/',
):
    """
    Find the number of horizontal or vertical pixels that share intersection across images.
    ----------
    Parameters
        horizontal: Boolean. If True finds horizontal intersection strip.
                    If False, finds vertical intersection strip.
        album: geopandas dataframe. Country album.
        bucket: str. Bucket name in AWS
    """

    assert '/data/' in local_file_dir, 'local_file_dir must contain /data/'
    local_file_path = local_file_dir + 'test/img_iter.png'

    # Local path for storing outputs.
    max_range = 20  # the maximum width of pixels in which the image intersection can be
    index_list1, index_list2 = find_full_batch_strip(
        horizontal, album=album, x_batch_dim=x_batch_dim, y_batch_dim=y_batch_dim
    )
    idx_range = range(max_range - 1)

    img1, img2 = None, None
    for i in range(len(index_list1)):
        s3_file_path1, s3_file_path2 = (
            album.loc[index_list1[i]]['path'],
            album.loc[index_list2[i]]['path'],
        )
        s3_client.download_file(bucket, s3_file_path1, local_file_path)
        img1_iter = (mpimg.imread(local_file_path) * 255).astype(np.uint8)
        s3_client.download_file(bucket, s3_file_path2, local_file_path)
        img2_iter = (mpimg.imread(local_file_path) * 255).astype(np.uint8)
        if i > 0:
            if horizontal:
                img1 = cv2.hconcat([img1, img1_iter])
                img2 = cv2.hconcat([img2, img2_iter])
            else:
                img1 = cv2.vconcat([img1_iter, img1])
                img2 = cv2.vconcat([img2_iter, img2])
        else:
            img1 = img1_iter
            img2 = img2_iter

    if horizontal:
        img1 = img1[:1, :, :]
        idx_iter = list(-np.array(range(20)))
        idx_iter[0] = None
        idx_min = np.argmin(
            [
                np.sum((img1 - img2[idx_iter[i + 1] : idx_iter[i], :, :]) ** 2)
                for i in idx_range
            ]
        )
        pixel_min = idx_iter[idx_min + 1]
    else:  # vertical
        img1 = img1[:, -1:, :]
        idx_iter = range(max_range)
        idx_min = np.argmin(
            [
                np.sum((img1 - img2[:, idx_iter[i] : idx_iter[i + 1], :]) ** 2)
                for i in idx_range
            ]
        )
        pixel_min = idx_iter[idx_min]

    return pixel_min


def find_full_batch_strip(
    horizontal=None, album=None, x_batch_dim=None, y_batch_dim=None
):
    """
    Finds a batch in which exists a cell row (or column) that contains a full
    range of consecutive horizontal (vertical) images. This is an auxiliary
    function to calculate the pixel intersection across images to make it a constant.
    ----------
    Parameters
        horizontal: Boolean. If True finds intersection strip. If False, finds vertical strip.
        album: geopandas dataframe. Country album.
    """

    # Find all full strips
    if horizontal:
        cell_idx = 'cell_y'
        cell_col = 'cell_x'
        batch_dim = x_batch_dim
    else:
        cell_idx = 'cell_x'
        cell_col = 'cell_y'
        batch_dim = y_batch_dim

    column_list = ['batch_label', 'cell_x', 'cell_y']
    counts_df = album[column_list].groupby(['batch_label', cell_idx], axis=0).count()
    full_strip = counts_df.loc[counts_df[cell_col] == batch_dim].copy()

    if full_strip.shape[0] == 0:
        raise Exception('There is not a single full strip, wrong shape file')

    full_strip.reset_index(['batch_label', cell_idx], inplace=True)
    full_strip.drop(cell_col, axis=1, inplace=True)

    # Two consecutive Full strips
    i = 0
    j = i + 1
    cond1 = full_strip['batch_label'].iloc[i] == full_strip['batch_label'].iloc[j]
    cond2 = full_strip[cell_idx].iloc[i] + 1 == full_strip[cell_idx].iloc[j]
    while j < full_strip.shape[0] and not (cond1 and cond2):
        i += 1
        j += 1
        cond1 = full_strip['batch_label'].iloc[i] == full_strip['batch_label'].iloc[j]
        cond2 = full_strip[cell_idx].iloc[i] + 1 == full_strip[cell_idx].iloc[j]

    batch_label, cell = full_strip.iloc[i]
    cond1 = album['batch_label'] == batch_label
    cond2 = album[cell_idx].isin([cell])

    index_list1 = album.loc[cond1 & cond2].index
    cond2 = album[cell_idx].isin([cell + 1])
    index_list2 = album.loc[cond1 & cond2].index
    return index_list1, index_list2


def batch_generator(
    batch_label=None,
    album=None,
    bucket=None,
    only_wld=False,
    verbose=False,
    pixel_size_y=None,
    pixel_size_x=None,
    x_batch_dim=None,
    y_batch_dim=None,
    pixels_intersect_h=None,
    pixels_intersect_v=None,
    lat_difference=None,
    lon_difference=None,
    local_file_dir='../data/01_raw_images/',
):
    """
    Generate a large mosaic of images that correspond to a batch in the album.
    ----------
    Parameters
        batch_label: str. The batch label for which the mosaic is generated.
        album: geopandas dataframe. Album of incluia's project.
        bucket: str. Bucket name in AWS.
        only_wld: Boolean. If True then only generates wld file.
                  If True then generates wld and batch.
        verbose: Boolean. If True prints verbose.
    """

    assert '/data/' in local_file_dir, 'local_file_dir must contain /data/'
    local_file_path = local_file_dir + 'test/img_iter.png'
    s3_file_dir = local_file_dir.split('/data/')[-1]

    cond = album['batch_label'] == batch_label
    album_batch = album[cond].copy()

    if album_batch.shape[0] == 0:
        raise Exception('Invalid batch_label or batch_label with zero images')

    ###################################################################
    # Wld file for georeferencing batch. USE EPSG:4326
    album_iter = album_batch.iloc[0]
    # Find top right coordinates of batch
    album_iter_lon = float(
        album_iter['centroid_lon'] - album_iter['cell_x'] * lon_difference
    )
    album_iter_lat = float(
        album_iter['centroid_lat']
        + ((y_batch_dim - 1) - album_iter['cell_y']) * lat_difference
    )

    wld = np.zeros(6)
    wld[0] = pixel_size_x
    wld[3] = -pixel_size_y
    wld[4] = album_iter_lon - pixel_size_x * 400 / 2
    wld[5] = (
        album_iter_lat + pixel_size_y * 400 / 2
    )  # Caution: It is not 375! It is 200 pixels above centroid.

    if only_wld:
        return None, wld

    # To create a batch in img:
    # 1. We generate long horizontal strips of images by concatenating
    #    individual cells in img_h.
    # 2. We concatenate these long horizontal strips to
    #    img_h iteratively (outer for) to form the batch.

    # Initalize output: matroid values that defines the image
    img = np.array([])

    for cell_y in trange(y_batch_dim, desc='Iterative Progress'):
        img_h = np.array([])
        # The inner for is to concatenate vertical single images into a horizontal strip img_h
        for cell_x in range(x_batch_dim):
            # set image label for the iteration
            cell_x_label = '{:02d}'.format(cell_x)
            cell_y_label = '{:02d}'.format(cell_y)
            img_iter_path = cell_x_label + '_' + cell_y_label + '.png'
            s3_file_path = s3_file_dir + batch_label + '/' + img_iter_path

            # check if the image is currently saved in S3
            if s3_file_exists(bucket=bucket, s3_file_path=s3_file_path):
                # if the image exists, download it to locally to
                # local_img_path and the read it.
                s3_client.download_file(bucket, s3_file_path, local_file_path)
                img_iter = (mpimg.imread(local_file_path) * 255).astype(np.uint8)
            else:
                # if the image does not exist, define a blank picture in its place.
                img_iter = np.ones((375, 400, 4)).astype(np.uint8)

            # In the first iteration of the inner for, img_h is empty.
            # Therefore, Else applies and the image is copied.
            # For the following iterations an image is concatenated.
            if cell_x > 0:
                strip1 = img_h[:, -1:, 0:3].astype(int)
                strip2 = img_iter[
                    :, pixels_intersect_v : (pixels_intersect_v + 1), 0:3
                ].astype(int)
                union_error = np.sum(np.abs(strip1 - strip2))
                if union_error > 10000 and verbose:
                    print(f'Seams of batch in {s3_file_path} are too inconsistent')
                img_h = cv2.hconcat([img_h, img_iter[:, (pixels_intersect_v + 1) :, :]])

            else:
                img_h = img_iter

        # Analogous routine for the joining horizontal straps.
        if cell_y > 0:
            # If there is non-empty intersection, eat a strip of pixels
            if pixels_intersect_h != 0:
                img = cv2.vconcat([img_h[:pixels_intersect_h, :, :], img])
            # Otherwise, concatenate images directly.
            else:
                img = cv2.vconcat([img_h, img])
        else:
            img = img_h

    return img, wld
