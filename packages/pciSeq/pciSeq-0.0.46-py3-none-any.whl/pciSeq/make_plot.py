import pandas as pd
import numpy as np
import skimage.io
import matplotlib.pyplot as plt
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


def gaussian_ellipsoid(cov, mu, sdwidth=None):
    """
    Draws an ellipsoid for a given covariance matrix cov
    and mean vector mu

    Example
    cov_1 = [[1, 0.5], [0.5, 1]]
    means_1 = [1, 1]

    cov_2 = [[1, -0.7], [-0.7, 1]]
    means_2 = [2, 1.5]

    cov_3 = [[1, 0], [0, 1]]
    means_3 = [0, 0]

    ellipsis_1 = gaussian_ellipsoid(cov_1, means_1)
    ellipsis_2 = gaussian_ellipsoid(cov_2, means_2)
    ellipsis_3 = gaussian_ellipsoid(cov_3, means_3)
    ellipsis_3b = gaussian_ellipsoid(cov_3, means_3, sdwidth=2)
    ellipsis_3c = gaussian_ellipsoid(cov_3, means_3, sdwidth=3)

    plt.plot(ellipsis_1[0], ellipsis_1[1], c='b')
    plt.plot(ellipsis_2[0], ellipsis_2[1], c='r')
    plt.plot(ellipsis_3[0], ellipsis_3[1], c='g')
    plt.plot(ellipsis_3b[0], ellipsis_3b[1], c='g')
    plt.plot(ellipsis_3c[0], ellipsis_3c[1], c='g')
    """
    if sdwidth is None:
        sdwidth = 3

    mu = np.array(mu)

    npts = 40
    tt = np.linspace(0, 2 * np.pi, npts)
    ap = np.zeros((2, npts))
    x = np.cos(tt)
    y = np.sin(tt)
    ap[0, :] = x
    ap[1, :] = y

    eigvals, eigvecs = np.linalg.eig(cov)
    eigvals = sdwidth * np.sqrt(eigvals)
    eigvals = eigvals * np.eye(2)

    vd = eigvecs.dot(eigvals)
    out = vd.dot(ap) + mu.reshape(2, -1)

    return out



def run():
    dapi_path = r"D:\Home\Dimitris\OneDrive - University College London\dev\Matlab\cell calling\iss-Redundant-codes\iss-Redundant-codes\data\background_boundaries.tif"
    dapi = skimage.io.imread(dapi_path)

    # read the spots and the gene colours
    iss_spots = pd.read_csv('https://github.com/acycliq/pciSeq/blob/dev/pciSeq/data/mouse/ca1/iss/spots.csv?raw=true')
    gene_colours = pd.read_csv('gene_colours.csv')

    cov_2279 = np.load('cov_2279.npz')['arr_0']
    centroid_2279 = np.load('centroid_2279.npz')['arr_0']
    assert len(cov_2279) == len(centroid_2279)

    cov_2259 = np.load('cov_2259.npz')['arr_0']
    centroid_2259 = np.load('centroid_2259.npz')['arr_0']
    assert len(cov_2259) == len(centroid_2259)

    cov_2308 = np.load('cov_2308.npz')['arr_0']
    centroid_2308 = np.load('centroid_2308.npz')['arr_0']
    assert len(cov_2308) == len(centroid_2308)

    my_dpi = 72
    f = plt.figure(0, figsize=(2 * 7602 / my_dpi, 2 * 5471 / my_dpi), dpi=my_dpi)
    for i, d in enumerate(zip(cov_2279, centroid_2279), 0):
        # f = plt.figure(i, figsize=(2 * 7602 / my_dpi, 2 * 5471 / my_dpi), dpi=my_dpi)
        skimage.io.imshow(dapi)
        for row in gene_colours.itertuples():
            gene = row.Gene
            df = iss_spots[iss_spots.Gene == gene]
            hex_code = row.hex
            plt.scatter(df.x, df.y, s=10, c=hex_code)

        cov = d[0]
        mu = d[1]
        outline = gaussian_ellipsoid(cov, mu, sdwidth=3)
        outline_2259 = gaussian_ellipsoid(cov_2259[i], centroid_2259[i], sdwidth=3)
        outline_2308 = gaussian_ellipsoid(cov_2308[i], centroid_2308[i], sdwidth=3)
        plt.plot(outline[0], outline[1], c='#00B3FF')
        plt.plot(outline_2259[0], outline_2259[1], c='#FF00E6')
        plt.plot(outline_2308[0], outline_2308[1], c='g')
        f.savefig('my_fig_%d.jpg' % i)

        image = Image.open('my_fig_%d.jpg' % i)
        cropped = image.crop((2*4460, 2*402, 2*4892, 2*688))
        cropped = cropped.resize((cropped.width * 2, cropped.height * 2))
        cropped.save('crop_' + 'my_fig_%d.jpg' % i)


if __name__ == "__main__":
    run()