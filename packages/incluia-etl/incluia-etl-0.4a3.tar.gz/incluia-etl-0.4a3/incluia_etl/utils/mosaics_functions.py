import math

import boto3
import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision.transforms as T
from shapely.geometry import box
from torchvision.utils import make_grid

s3_client = boto3.client('s3')


def mosaic_models_corners(
    y=None, x=None, img_size=None, pixel_size_y=None, pixel_size_x=None
):
    """
    Given a centroid of an image (y,x), returns a geopandas box of the
    corresponding generated mosaic.
    Args:
        y: y-centroid coordinate (float)
        x: x-centroid coordinate (float)
        img_size: Number of pixels of the length of the squared image.
        pixel_size_y:
        pixel_size_x:

    Returns: Geopandas Polygon box of the corresponding generated mosaic.
    """
    # North
    n = y + pixel_size_y * img_size / 2
    # South
    s = y - pixel_size_y * img_size / 2
    # East
    e = x + pixel_size_x * img_size / 2
    # West
    w = x - pixel_size_x * img_size / 2
    box_out = box(w, s, e, n)
    return box_out


irange = range


def make_grid_with_labels(tensor, labels, nrow=8, limit=64, padding=2, pad_value=0):
    """Make a grid of images.

    Args:
        tensor (Tensor or list): 4D mini-batch Tensor of shape (B x C x H x W)
            or a list of images all of the same size.
        labels (list):  ( [labels_1,labels_2,labels_3,...labels_n]) where
                        labels is Bx1 vector of some labels
        limit (int, optional): Limits number of images and labels to make grid of
        nrow (int, optional): Number of images displayed in each row of the grid.
            The final grid size is ``(B / nrow, nrow)``. Default: ``8``.
        padding (int, optional): amount of padding. Default: ``2``.
        pad_value (float, optional): Value for the padded pixels. Default: ``0``.

    Example:
        See this notebook
        `here <https://gist.github.com/anonymous/bf16430f7750c023141c562f3e9f2a91>`_

    """

    # Opencv configs
    if not isinstance(labels, list):
        raise ValueError
    else:
        labels = np.transpose(np.asarray(labels))  # np.asarray(labels).T[0]
    if limit is not None:
        tensor = tensor[:limit, ::]
        labels = labels[:limit]  # , ::]

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 2
    color = (255, 255, 0)
    thickness = 10

    if not (
        torch.is_tensor(tensor)
        or (isinstance(tensor, list) and all(torch.is_tensor(t) for t in tensor))
    ):
        raise TypeError(
            'tensor or list of tensors expected, got {}'.format(type(tensor))
        )

    # if list of tensors, convert to a 4D mini-batch Tensor
    if isinstance(tensor, list):
        tensor = torch.stack(tensor, dim=0)

    if tensor.dim() == 2:  # single image H x W
        tensor = tensor.unsqueeze(0)
    if tensor.dim() == 3:  # single image
        if tensor.size(0) == 1:  # if single-channel, convert to 3-channel
            tensor = torch.cat((tensor, tensor, tensor), 0)
        tensor = tensor.unsqueeze(0)

    if tensor.dim() == 4 and tensor.size(1) == 1:  # single-channel images
        tensor = torch.cat((tensor, tensor, tensor), 1)

    if tensor.size(0) == 1:
        return tensor.squeeze(0)

    # make the mini-batch of images into a grid
    nmaps = tensor.size(0)
    xmaps = min(nrow, nmaps)
    ymaps = int(math.ceil(float(nmaps) / xmaps))
    height, width = int(tensor.size(2) + padding), int(tensor.size(3) + padding)
    num_channels = tensor.size(1)
    grid = tensor.new_full(
        (num_channels, height * ymaps + padding, width * xmaps + padding), pad_value
    )
    k = 0
    for y in irange(ymaps):
        for x in irange(xmaps):
            if k >= nmaps:
                break
            working_tensor = tensor[k]
            if labels is not None:
                org = (20, 60)
                working_image = cv2.UMat(
                    np.asarray(
                        np.transpose(working_tensor.numpy(), (1, 2, 0)) * 255
                    ).astype('uint8')
                )
                image = cv2.putText(
                    working_image,
                    f'{str(labels[k])}',
                    org,
                    font,
                    fontScale,
                    color,
                    thickness,
                    cv2.LINE_AA,
                )
                working_tensor = T.ToTensor()(image.get())
            grid.narrow(1, y * height + padding, height - padding).narrow(
                2, x * width + padding, width - padding
            ).copy_(working_tensor)
            k = k + 1
    return grid


def show_images(images, y, nmax=64, labels_bool=False, title='', text_dict=None):
    """
    Prints a mosaics of images.
    y: str or int: label.
    nmax: int. Maximum number of images.
    labels_bool: If label appear (True) or not (False) in mosaic.
    title: str. Title of the mosaic.
    text_dict: dictionaty. Example of a text_dict={'Poor': 1, 'Non-Poor': 0}
    """

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title)
    props = dict(boxstyle='round', facecolor='wheat', alpha=1.0)
    if text_dict is None:
        text_dict = {}
    if len(text_dict.keys()) > 0:
        textstr = 'Groundtruth\n'
        for i in text_dict.keys():
            textstr += i + ': ' + str(text_dict[i]) + '\n'

        # place a text box in upper left in axes coords
        ax.text(
            0.87,
            0.98,
            textstr,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment='top',
            bbox=props,
        )

    if labels_bool:
        labels = list(y)
        ax.imshow(
            make_grid_with_labels((images.detach()[:nmax]), labels=labels).permute(
                1, 2, 0
            )
        )
    else:
        ax.imshow(make_grid((images.detach()[:nmax]), nrow=8).permute(1, 2, 0))


def show_batch(dl, labels_bool=False, title='', text_dict=None, nmax=64):
    """
    Example of a text_dict={'Poor': 1, 'Non-Poor': 0}
    """
    if text_dict is None:
        text_dict = {}
    for images, y, _, _ in dl:
        show_images(
            images,
            y,
            nmax=nmax,
            labels_bool=labels_bool,
            title=title,
            text_dict=text_dict,
        )
        break
