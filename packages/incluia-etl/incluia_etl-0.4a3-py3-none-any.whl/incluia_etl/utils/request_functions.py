import json
import os
import warnings
from io import StringIO
from os import path

import boto3
import botocore
import geopandas as gpd
import imageio
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
from botocore.exceptions import ClientError
from PIL import Image
from shapely import wkt

warnings.simplefilter(action='ignore', category=FutureWarning)


def upload_object(
    bucket: str = None,
    local_file_path: str = None,
    obj: object = None,
    s3_file_path: str = None,
    profile_name: str = None,
    verbose: bool = True,
    **kwargs,
):
    """
    Upload a file to s3. Source can be a locally written file or
    from memory.

    Parameters
    ----------
    bucket : str, default None
        Bucket name to load from.
    local_file_path : str
        Local path to upload from.
        Must be of the form: "<optional directory>/data/<s3 file path>".
    s3_file_path : str, default None
        s3 path to upload obj.
    obj : object, default None
        Object to be uploaded.
    profile_name : str, default None
        AWS profile name.
    verbose : bool, default True
        Prints verbose if True.
    **kwargs

    Returns
    -------
    flag : bool
        Returns True if file is uploaded, False otherwise.

    Upload from disk.
    -------------------------------------
        Specifications
        --------------
        bucket != None
        local_file_path != None
        s3_file_path = Optional
        obj == None

        Upload a file written in local_file_path to an S3 bucket.
        The destination path s3_file_path is as local_file_path after "data/",
         unless s3_file_path specified.
        File is uploaded into same file path name after "data/".
        The local file path must contain a "data/" folder to save the file.

    Upload from memory.
    -----------------------------------------
        Specifications
        --------------
        bucket != None
        obj != None
        s3_file_path != None
        local_file_path == None
    """

    bucket_in = bucket is not None
    local_file_path_in = local_file_path is not None
    s3_file_path_in = s3_file_path is not None
    obj_in = obj is not None

    if not bucket_in:
        raise Exception('Argument bucket cannot be None')

    # method disk corresponds to upload a locally written file
    method_disk = local_file_path_in and not obj_in
    # method memory corresponds to upload a file directly from memory
    method_memory = obj_in and s3_file_path_in and not local_file_path_in

    if not method_disk and not method_memory:
        raise Exception('Specify either method disk or method memory. Read docstring.')

    if method_disk:
        if '/data/' not in local_file_path:
            raise Exception(f'local_file_path={local_file_path} must contain "/data/"')
        if not s3_file_path_in:
            s3_file_path = local_file_path.split('/data/')[-1]
        # disk method supports all types of formats
        file_format = None
        is_in_supported_formats = True
    else:
        file_format = '.' + s3_file_path.split('.', s3_file_path.count('.'))[-1]
        supported_formats = ['.csv', '.json']
        is_in_supported_formats = file_format in supported_formats

    if profile_name is not None:
        try:
            boto3.setup_default_session(profile_name=profile_name)
        except botocore.exceptions.ClientError as e:
            raise e

    # This print applies when supported format is True,
    # otherwise local file path must be saved first
    if verbose and is_in_supported_formats:
        print(f'Saving file in S3 as: {s3_file_path} ... ', end='')
    s3_resource = boto3.resource('s3')
    s3_obj = s3_resource.Object(bucket_name=bucket, key=s3_file_path)
    if method_disk:
        response = s3_obj.put(Body=open(local_file_path, 'rb'))
    else:
        if file_format == '.json':
            response = s3_obj.put(Body=(bytes(json.dumps(obj).encode('UTF-8'))))
        elif file_format == '.csv':
            csv_buffer = StringIO()
            obj.to_csv(csv_buffer, index=False, **kwargs)
            response = s3_obj.put(Body=csv_buffer.getvalue())
        # To Do: Add new formats to add them directly from memory
        else:
            if verbose:
                print('\nThis type of format must be stored locally first.')

            temp_file_dir = '../data/temp/'
            dir_exists = path.exists(path=temp_file_dir)
            if not dir_exists:
                os.mkdir(path=temp_file_dir)

            file_name, file_format, _, s3_file_dir = file_path_breaker(
                s3_file_path=s3_file_path
            )
            s3_file_dir = s3_file_dir.replace('/', '_')
            temp_file_path = f'{temp_file_dir}{s3_file_dir}{file_name}{file_format}'
            save_object(obj=obj, local_file_path=temp_file_path, verbose=verbose)
            if verbose:
                print(f'Saving file in S3 as: {s3_file_path} ... ', end='')
            response = s3_obj.put(Body=open(temp_file_path, 'rb'))
            os.remove(temp_file_path)

    flag = response.get('ResponseMetadata')
    if verbose:
        if flag.get('HTTPStatusCode') == 200:
            print('done')
        else:
            print('error')

    # This function could be modified to return flag
    return None


def save_object(
    obj=None,
    local_file_path: str = None,
    s3_file_path: str = None,
    bucket: str = None,
    verbose: bool = True,
    **kwargs,
):
    """
    Save a file locally and default option uploads a copy from local to an S3 bucket after.
    The copy is uploaded to S3 under the same path after "data/".

    Parameters
    ----------
    obj: object, default None
        Object to save locally and in s3 or only in s3
    local_file_path : str
        Local path to read csv file from.
        Must be of the form: "<optional directory>/data/<s3 file path>".
    bucket : str, default None
        Bucket name to load from.
    s3_file_path : str, default None
        s3 path to upload obj.
    verbose : bool, default True
        Prints verbose if True.

    Returns
    -------
    flag : bool
        Return True if file is saved, False otherwise.

    Save locally and upload:
        Specifications
        --------------
        obj != None
        local_file_path != None
        s3_file_path = Optional
        bucket != None

    Save locally only:
        Specifications
        --------------
        obj != None
        local_file_path != None
        s3_file_path = None
        bucket = None
    """

    local_file_path_in = local_file_path is not None
    s3_file_path_in = s3_file_path is not None
    obj_in = obj is not None
    bucket_in = bucket is not None

    save_upload = obj_in and local_file_path_in and bucket_in
    save_local_only = (
        obj_in and local_file_path_in and not bucket_in and not s3_file_path_in
    )

    if not save_upload and not save_local_only:
        raise Exception('Specify valid set of inputs. Read docstring.')

    if '/data/' not in local_file_path:
        raise Exception(f'local_file_path={local_file_path} must contain "/data/"')

    # Read file file_format
    file_name, file_format, local_file_dir, _ = file_path_breaker(
        local_file_path=local_file_path
    )

    if not obj_in:
        raise Exception('Object obj cannot be None')

    supported_formats = ['.csv', '.json', '.geojson', '.shp', '.png', '.wld']
    if file_format not in supported_formats:
        if obj_in:
            raise Exception('Only csv, geojson, shp, png and wld formats are supported')

    # Saving local file first
    if verbose:
        print(f'Saving local file: {local_file_path} ... ', end='')
    if file_format == '.json':
        file_formats = ['.json']
        with open(local_file_path, 'w') as fout:
            json.dump(obj, fout)
    elif file_format == '.csv':
        file_formats = ['.csv']
        obj.to_csv(local_file_path, index=False, **kwargs)
    elif file_format == '.geojson':
        file_formats = ['.geojson']
        obj.to_file(filename=local_file_path, driver='GeoJSON', **kwargs)
    elif file_format == '.shp':
        file_formats = ['.cpg', '.dbf', '.prj', '.shp', '.shx']
        obj.to_file(filename=local_file_path, driver='ESRI Shapefile', **kwargs)
    elif file_format == '.png':
        imageio.imwrite(uri=local_file_path, im=obj)
        file_formats = ['.png']
    else:  # file_format == '.wld':
        with open(local_file_path, 'w+') as f:
            for i in obj:
                f.write(f'{i:.20f}\n')
        file_formats = ['.wld']

    if verbose:
        print('done')

    # Uploading object using method-disk: uploads from a locally written file.
    flag = True
    if save_upload:
        # if s3_file_path is not None, get s3_file_dir
        if s3_file_path_in:
            _, _, _, s3_file_dir = file_path_breaker(s3_file_path=s3_file_path)
        # assign s3_file_dir as local_file_dir after /data/
        else:
            s3_file_dir = local_file_dir.split('/data/')[-1]
        # upload as loop, since shapefiles involves saving several files
        for file_format in file_formats:
            local_file_path = f'{local_file_dir}{file_name}{file_format}'
            s3_file_path = f'{s3_file_dir}{file_name}{file_format}'
            flag = upload_object(
                local_file_path=local_file_path,
                s3_file_path=s3_file_path,
                bucket=bucket,
                verbose=verbose,
                **kwargs,
            )

    return flag


def download_object(
    local_file_path: str = None,
    s3_file_path: str = None,
    bucket: str = None,
    profile_name: str = None,
    verbose: bool = True,
):
    """
    Download a file from an S3 bucket to disk.

    Parameters
    ----------
    local_file_path : str, default None
        Local path to read csv file from.
        Must be of the form: "<optional directory>/data/<s3 file path>".
    s3_file_path : str, default None
        s3 path source of object.
    bucket : str, default None
        Bucket name to load from.
    profile_name : str, default None
        AWS profile name.
    verbose : bool, default True
        Prints verbose if True.

    Returns
    -------
    Flag if download was successful.

    Specifications
    --------------
        bucket != None
        local_file_path != None
        s3_file_path = Optional

        If s3_file_path is None, file is downloaded into same path as local_file_path
         path name after "data/".
        The local file path must contain a "data/" folder to save the file.
    """

    local_file_path_in = local_file_path is not None
    s3_file_path_in = s3_file_path is not None
    bucket_in = bucket is not None

    if not local_file_path_in or '/data/' not in local_file_path:
        raise Exception(f'local_file_path={local_file_path} must contain "/data/"')

    if not bucket_in:
        raise Exception('Argument bucket cannot be None')

    if not s3_file_path_in:
        s3_file_path = local_file_path.split('/data/')[-1]

    if profile_name is not None:
        try:
            boto3.setup_default_session(profile_name=profile_name)
        except botocore.exceptions.ClientError as e:
            raise e

    s3_resource = boto3.resource('s3')
    try:
        if verbose:
            print(f'Downloading {s3_file_path} from S3 ... ', end='')
        flag = s3_resource.Bucket(name=bucket).download_file(
            Key=s3_file_path, Filename=local_file_path
        )
        if verbose:
            print('done')
    except botocore.exceptions.ClientError as e:
        flag = False
        if e.response['Error']['Code'] == '404':
            print('The object does not exist.')
        else:
            raise

    return flag


def get_s3_object(
    s3_file_path: str = None,
    bucket: str = None,
    profile_name: str = None,
    verbose: bool = True,
):
    """
    Get a file from an S3 bucket directly into memory.
    Auxiliary function that depends on the get_<file_format> of each file.
    Warning: It is not meant to use this function independently.

    Parameters
    ----------
    s3_file_path : str, default None
        s3 file path to read from.
    bucket : str, default None
        Bucket name to load from.
    profile_name : str, default None
        AWS profile name.
    verbose : bool, default True
        Prints verbose if True.

    Returns
    -------
    Object
    """

    bucket_in = bucket is not None
    s3_file_path_in = s3_file_path is not None

    if not bucket_in:
        raise Exception('Argument bucket cannot be None')

    if not s3_file_path_in:
        raise Exception('Argument s3_file_path cannot be None')

    _, file_format, _, _ = file_path_breaker(s3_file_path=s3_file_path)

    if profile_name is not None:
        try:
            boto3.setup_default_session(profile_name=profile_name)
        except botocore.exceptions.ClientError as e:
            raise e

    s3_client = boto3.client('s3')
    obj = None
    try:
        if verbose:
            print(f'Getting object {s3_file_path} from S3 ... ', end='')
        obj = s3_client.get_object(Bucket=bucket, Key=s3_file_path)
        if verbose:
            print('done')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print('The object does not exist.')
        else:
            raise

    return obj


def get_csv(
    local_file_path: str = None,
    bucket: str = None,
    s3_file_path: str = None,
    force_source_s3: bool = False,
    profile_name: str = None,
    col_names_to_lower: bool = False,
    verbose=True,
    **kwargs,
):
    """
    Read a csv file locally (method disk) or from an S3 bucket (method memory).

    Parameters
    ----------
    bucket : str, default None
        Bucket name to load from.
    s3_file_path : str, default None
        s3 file path to read from.
    local_file_path : str
        Local path to read csv file from.
        Must be of the form: "<optional directory>/data/<s3 file path>".
    force_source_s3 : boolean, default False
        Forces download from s3 even if local file exists and overwrites.
    profile_name : str, default None
        AWS profile name.
    col_names_to_lower : bool.
        If True column names are read as lowercase.
    verbose : bool, default True
        Prints verbose if True.
    **kwargs : options for functions pd.get_csv(). For example, encoding=latin1

    Returns
    -------
    df : pd.DataFrame
        File read as a table.

    method disk: Write and read from locally written file. File is kept in disk.
        Specifications
        --------------
        local_file_path != None
        bucket != None
        s3_file_path Optional

    method memory: Download and read from memory. File is noy kept in disk.
        Specifications
        --------------
        s3_file_path != None
        bucket != None
        local_file_path = None
    """

    local_file_path_in = local_file_path is not None
    bucket_in = bucket is not None
    s3_file_path_in = s3_file_path is not None

    # method disk get from a locally written file
    method_disk = local_file_path_in and bucket_in
    # method memory corresponds to upload a file directly from memory
    method_memory = s3_file_path_in and bucket_in and not local_file_path_in

    if not method_disk and not method_memory:
        raise Exception('Specify either local_file_path or s3_file_path')

    if method_disk:
        if '/data/' not in local_file_path:
            raise Exception(f'local_file_path={local_file_path} must contain "/data/"')

        if not s3_file_path_in:
            s3_file_path = local_file_path.split('/data/')[-1]

        # Read file file_format
        file_name, file_format, _, s3_file_dir = file_path_breaker(
            local_file_path=local_file_path
        )
    else:
        file_name, file_format, _, s3_file_dir = file_path_breaker(
            s3_file_path=s3_file_path
        )

    if file_format != '.csv':
        raise Exception('File file_format invalid. Input must be a csv file.')

    if method_disk:
        # Tries to read from local file first because it is faster.
        local_file_path_exists = path.exists(path=local_file_path)

        # Downloads file from S3.
        if force_source_s3 or not local_file_path_exists:
            download_object(
                local_file_path=local_file_path,
                s3_file_path=s3_file_path,
                bucket=bucket,
                verbose=verbose,
                profile_name=profile_name,
            )
        filepath_or_buffer = local_file_path
        file_path = local_file_path
    else:
        obj = get_s3_object(
            s3_file_path=s3_file_path,
            bucket=bucket,
            profile_name=profile_name,
            verbose=verbose,
        )
        filepath_or_buffer = obj['Body']
        file_path = s3_file_path

    if verbose:
        print(f'Reading file: {file_path} ... ', end='')
    df = pd.read_csv(filepath_or_buffer=filepath_or_buffer, **kwargs)
    if verbose:
        print('done')

    if col_names_to_lower:
        df.columns = df.columns.str.lower()

    return df


def get_csv_as_gpd(
    local_file_path: str = None,
    bucket: str = None,
    s3_file_path: str = None,
    crs='epsg:4326',
    geometry_col: str = 'geometry',
    force_source_s3: bool = False,
    profile_name: str = None,
    col_names_to_lower: bool = False,
    verbose=True,
    **kwargs,
):
    """
    Read a csv file locally (method disk) or from an S3 bucket (method memory) as geopandas.
    method disk: Write and read from locally written file. File is kept in disk.
        Specifications
        --------------
        local_file_path != None
        bucket != None
        s3_file_path = Optional.

    method memory: Download and read from memory. File is noy kept in disk.
        Specifications
        --------------
        s3_file_path != None
        bucket != None
        local_file_path = None

    Parameters
    ----------
    local_file_path : str
        Local path to read csv file from.
        Must be of the form: "<optional directory>/data/<s3 file path>".
    s3_file_path : str, default None
        s3 file path to read from.
    bucket : str, default None
        Bucket name to load from.
    crs : int or str, default epsg:4326
        The Coordinate Reference System (CRS) to read the file as. Default = 4326.
    geometry_col : str, default 'geometry'
        Geometry column name of dataframe
    force_source_s3 : default False
        force downloading file from s3 and overwrites local file if exits.
    profile_name : str, default None
        AWS profile name.
    col_names_to_lower : bool.
        If True column names are read as lowercase.
    verbose : bool, default True
        Prints verbose if True.
    **kwargs : options for functions pd.get_csv(). For example, encoding=latin1

    Returns
    -------
    df : gpd.GeoDataFrame
        File read as a table with geometry column.
    """

    df = get_csv(
        local_file_path=local_file_path,
        bucket=bucket,
        s3_file_path=s3_file_path,
        force_source_s3=force_source_s3,
        profile_name=profile_name,
        col_names_to_lower=col_names_to_lower,
        verbose=verbose,
        **kwargs,
    )
    df[geometry_col] = df[geometry_col].apply(wkt.loads)
    df = gpd.GeoDataFrame(data=df, crs=crs)
    return df


def get_vector_map(
    local_file_path: str = None,
    s3_file_path: str = None,
    bucket: str = None,
    crs=4326,
    profile_name: str = None,
    force_source_s3=False,
    verbose=True,
):
    """
    Read a GeoDataFrame file locally, or from an S3 bucket if specified or file does
     not exist locally.

    Reads any vector-based spatial data in formats ESRI shapefile (.shp) or GeoJSON.
    Can transform the geopandas to Coordinate Reference System given as "crs".

    Parameters
    ----------
    local_file_path : str
        Local path to read vector map file from.
        Must be of the form: "<optional directory>/data/<s3 file path>".
    s3_file_path : str, default None
        s3 file path to read from.
    bucket : str, default None
        Bucket name to load from.
    crs : int, default 4326
        The Coordinate Reference System (CRS) to read the GeoDataFrame as.
    force_source_s3 : boolean, default False
        Forces download from s3 even if local file exists and overwrites.
    profile_name : str, default None
        AWS profile name.
    verbose : bool, default True
        Prints verbose if True.

    Returns
    -------
    vector_map : gpd.GeoDataFrame
        File read as a table with a geometry column.

    Method disk: Read from locally written file. File is kept in disk.
        Specifications
        --------------
        local_file_path != None
        bucket != None
        s3_file_path = Optional.

    Method memory: Download and read from memory. File is noy kept in disk.
        Specifications
        --------------
        s3_file_path != None
        bucket != None
        local_file_path = None
    """

    local_file_path_in = local_file_path is not None
    s3_file_path_in = s3_file_path is not None
    bucket_in = bucket is not None

    # method disk get from a locally written file
    method_disk = local_file_path_in and bucket_in
    # method memory corresponds to upload a file directly from memory
    method_memory = s3_file_path_in and bucket_in and not local_file_path_in

    if not method_disk and not method_memory:
        raise Exception('Specify either method disk or method memory. Read docstring.')

    if method_disk:
        file_path = local_file_path
    else:
        file_path = s3_file_path
    file_format = '.' + file_path.split('.', file_path.count('.'))[-1]

    # Shapefiles must be written in disk first because they are composed of many files
    # Create a temporary folder to save files
    if file_format == '.shp' and method_memory:
        method_disk = True
        local_file_dir = '../data/temp/'
        dir_exists = path.exists(path=local_file_dir)
        if not dir_exists:
            os.mkdir(path=local_file_dir)

    if method_disk:
        if '/data/' not in local_file_path:
            raise Exception(f'local_file_path={local_file_path} must contain "/data/"')

        if not s3_file_path_in:
            s3_file_path = local_file_path.split('/data/')[-1]
            # Read file file_format
            file_name, _, local_file_dir, s3_file_dir = file_path_breaker(
                local_file_path=local_file_path
            )
        else:
            # Read file file_format
            file_name, _, local_file_dir, _ = file_path_breaker(
                local_file_path=local_file_path
            )
            _, _, _, s3_file_dir = file_path_breaker(s3_file_path=s3_file_path)

        filepath_or_buffer = local_file_path
    else:
        filepath_or_buffer = None
        file_name, _, local_file_dir, s3_file_dir = file_path_breaker(
            s3_file_path=s3_file_path
        )

    if file_format == '.geojson':
        file_formats = ['.geojson']
    elif file_format == '.shp':
        file_formats = ['.cpg', '.dbf', '.prj', '.shp', '.shx']
    else:
        raise Exception('File file_format invalid. Must be geojson or shp')

    if method_disk:
        # Tries to read from local file first because it is faster.
        local_file_path_exists = path.exists(path=local_file_path)

        # Downloads file from S3.
        if force_source_s3 or not local_file_path_exists:
            for file_format in file_formats:
                local_file_path_iter = f'{local_file_dir}{file_name}{file_format}'
                s3_file_path_iter = f'{s3_file_dir}{file_name}{file_format}'

                download_object(
                    local_file_path=local_file_path_iter,
                    s3_file_path=s3_file_path_iter,
                    bucket=bucket,
                    verbose=verbose,
                    profile_name=profile_name,
                )
    # method-memory reads from memory
    else:
        obj = get_s3_object(
            s3_file_path=s3_file_path,
            bucket=bucket,
            profile_name=profile_name,
            verbose=verbose,
        )
        filepath_or_buffer = obj['Body']

    if verbose:
        print(f'Reading local file: {file_path} ... ', end='')
    vector_map = gpd.read_file(filename=filepath_or_buffer)
    if verbose:
        print('done')

    # Coordinate Reference Systen maps Python to places on the Earth.
    # For example, one of the most commonly used
    # Coordinate Reference System is the WGS84 latitude-longitude projection.
    # This can be referred to using the authority code "EPSG:4326" or epsg=4326.
    vector_map = vector_map.to_crs(epsg=crs)

    return vector_map


def get_img(
    local_file_path: str = None,
    s3_file_path: str = None,
    bucket: str = None,
    wld: bool = True,
    profile_name: str = None,
    verbose: bool = True,
) -> Image:
    """
    Read an image locally or from an S3 bucket if specified or file does not exist locally.
    Supports option for erasing the image from disk after reading into memory.

    Parameters
    ----------
    local_file_path : str, default None
        Local path to store S3 image.
        Must be of the form: "<optional directory>/data/<s3 image path>".
    s3_file_path : str, default None
        set for downloading file stream directly into memory.
    bucket : str, default None
        Bucket name to load image from.
    wld : bool, default True
        If True, downloads wld file associated to image.
    profile_name : str, default None
        AWS profile name.
    verbose : bool, default True
        Prints verbose if True.

    Returns
    -------
    img: Image. Returns image from file read in bucket.

    Method disk: Read from locally written file. File is kept in disk.
        Specifications
        --------------
        local_file_path != None
        bucket != None
        s3_file_path = Optional.

    Method memory: Download and read from memory. File is noy kept in disk.
        Specifications
        --------------
        s3_file_path != None
        bucket != None
        local_file_path = None
    """

    local_file_path_in = local_file_path is not None
    s3_file_path_in = s3_file_path is not None
    bucket_in = bucket is not None

    # method disk get from a locally written file
    method_disk = local_file_path_in and bucket_in

    # method memory corresponds to upload a file directly from memory
    method_memory = s3_file_path_in and bucket_in and not local_file_path_in

    # Tests for valid input
    if not method_disk and not method_memory:
        raise Exception('Specify either method disk or method memory. Read docstring.')

    if method_disk:
        if '/data/' not in local_file_path:
            raise Exception(f'local_file_path={local_file_path} must contain "/data/"')

        if '.png' not in local_file_path:
            raise Exception(
                f'local_file_path={local_file_path} must be a png format file'
            )

        if s3_file_path_in and '.png' not in s3_file_path:
            raise Exception(f's3_file_path={s3_file_path} must be a png format file')
    else:
        if '.png' not in s3_file_path:
            raise Exception(f'local_file_path={s3_file_path} must be a png format file')

    # Execute disk method
    if method_disk:
        _, _, local_file_dir, _ = file_path_breaker(local_file_path=local_file_path)
        dir_exists = path.exists(path=local_file_dir)
        if not dir_exists:
            os.mkdir(path=local_file_dir)

        if not s3_file_path_in:
            s3_file_path = local_file_path.replace('../data/', '')

        # Download image
        _ = download_object(
            local_file_path=local_file_path,
            s3_file_path=s3_file_path,
            bucket=bucket,
            verbose=verbose,
            profile_name=profile_name,
        )
        file_path_or_stream = local_file_path
        img = (mpimg.imread(file_path_or_stream) * 255).astype(np.uint8)

        if wld:
            wld_local_file_path = local_file_path.replace('png', 'wld')
            wld_s3_file_path = s3_file_path.replace('png', 'wld')
            # Download wld
            _ = download_object(
                local_file_path=wld_local_file_path,
                s3_file_path=wld_s3_file_path,
                bucket=bucket,
                verbose=verbose,
                profile_name=profile_name,
            )
    # Execute memory method
    else:
        # Download image to file_stream
        s3_resource = boto3.resource('s3')
        obj = s3_resource.Object(bucket_name=bucket, key=s3_file_path)
        response = obj.get()
        file_path_or_stream = response['Body']
        img = Image.open(file_path_or_stream)
        img = np.array(img)

    img = img[:, :, :-1]
    # Assumes range [1,255]
    img = Image.fromarray(img)
    return img


def s3_file_exists(
    s3_file_path: str = None, bucket: str = None, profile_name: str = None
) -> bool:
    """
    Check if a file exists in an S3 bucket given its path.

    Parameters
    ----------
    s3_file_path : str, default None
        s3 file path to read from.
    bucket : str, default None
        Bucket name to load from.
    profile_name : str, default None
        AWS profile name.

    Returns
    -------
    exists : bool
        True if file exists and False otherwise.
    """
    if profile_name is not None:
        boto3.setup_default_session(profile_name=profile_name)

    s3_resource = boto3.resource('s3')
    exists = True
    try:
        s3_resource.Object(bucket_name=bucket, key=s3_file_path).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            # The object does not exist.
            exists = False
        else:
            # Something else has gone wrong.
            raise

    return exists


def file_path_breaker(
    local_file_path: str = None,
    s3_file_path: str = None,
) -> tuple[str, str, str, str]:
    """
    Get useful substrings of local_file_path such as file name, format and directory:

    Parameters
    ----------
    local_file_path: str, default None
        The local file path string to break into different substrings.
        Must be of the form: "<optional directory>/data/<s3 file path>".
    s3_file_path : str, default None
        s3 file path to break into different substrings.

    Returns
    -------
    file_name: str
        Substring of local_file_path containing only name of file.
    file_format: str
        Substring of local_file_path containing only format of file.
    local_file_dir: str
        Substring of local_file_path containing only directory of file.
    s3_file_dir: str
        Substring of local_file_path containing only directory of file, after "data/" folder.
    """

    # method disk get from a locally written file
    method_disk = local_file_path is not None and s3_file_path is None
    # method memory corresponds to upload a file directly from memory
    method_memory = s3_file_path is not None and local_file_path is None
    if not method_disk and not method_memory:
        raise Exception('Specify either local_file_path or s3_file_path')

    if method_disk:
        if '/data/' not in local_file_path:
            raise Exception(f'local_file_path={local_file_path} must contain "/data/"')
        s3_file_path = local_file_path.split('/data/')[-1]
    else:
        local_file_path = s3_file_path

    file_name_file_format = local_file_path.split('/', local_file_path.count('/'))[-1]
    file_name = file_name_file_format.split('.', file_name_file_format.count('.'))[0]
    file_format = (
        '.' + file_name_file_format.split('.', file_name_file_format.count('.'))[-1]
    )
    if method_disk:
        local_file_dir = local_file_path.replace(file_name_file_format, '')
    else:
        local_file_dir = ''
    s3_file_dir = s3_file_path.replace(file_name_file_format, '')
    return file_name, file_format, local_file_dir, s3_file_dir


def get_feather(
    local_file_path: str = None,
    bucket: str = None,
    force_source_s3=False,
    profile_name: str = None,
    col_names_to_lower: bool = False,
):
    """
    Read a feather file locally, or from an S3 bucket if specified or file does not exist locally.

    Parameters
    ----------
    local_file_path : str
        Local path to read feather file from.
        Must be of the form: "<optional directory>/data/<s3 file path>".
    bucket : str, default None
        Bucket name to load from.
    force_source_s3: boolean, default False
        Forces download from s3 even if local file exists and overwrites.
    profile_name : str, default None
        AWS profile name.
    col_names_to_lower : bool, default False
        Specifies if column names need to be converted to lower.

    Returns
    -------
    type of object stored in file
    """

    if '/data/' not in local_file_path:
        raise Exception(f'local_file_path={local_file_path} must contain "/data/"')

    # Read file file_format
    file_name, file_format, _, s3_file_dir = file_path_breaker(
        local_file_path=local_file_path
    )

    if file_format != '.feather':
        raise Exception('File file_format invalid. Input must be a feather file.')

    local_file_path_exists = path.exists(path=local_file_path)

    if force_source_s3 or not local_file_path_exists:
        # Downloads object as in method disk, stores file in disk
        download_object(
            local_file_path=local_file_path,
            bucket=bucket,
            profile_name=profile_name,
        )

    feather = pd.read_feather(path=local_file_path)

    if col_names_to_lower:
        feather.columns = feather.columns.str.lower()

    return feather
