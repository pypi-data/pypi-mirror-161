__author__ = "Vinaya Valsan, Caitlin Rose"
import os
import sys

import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

from matplotlib import rcParams
from glob import glob
from ligo.skymap import plot
from ligo.skymap import postprocess

print('---------------------Creating skymap---------------------')
input_dir = sys.argv[1]
# remove the color codes, because for whatever reason they're included on uwm.
input_dir = input_dir.replace("\x1b[0m", "")
input_dir = input_dir.replace("\x1b[01;34m", "")
input_dir = input_dir.replace("\x1b[K", "")


frac = sys.argv[2]
if len(sys.argv) > 3:
    output_dir = sys.argv[3]
else:
    output_dir = input_dir

namestr = frac.replace(".", "p")
filename = glob(
    input_dir + "/ll_samples_loudest_highweight_" + namestr + ".txt"
)[0]
os.makedirs(os.path.join(input_dir, "summary_plots"), exist_ok=True)

(
    mass1,
    mass2,
    mchirp,
    eta,
    spin1z,
    spin2z,
    distance,
    dec,
    ra,
    inclination,
    phase,
    polarization,
    likelihood,
    prior,
    sampling_function,
    weight,
) = np.loadtxt(filename, skiprows=1, unpack=True)
p = np.asarray(weight)
p /= p.sum()
theta = (np.pi / 2.0) - dec
phi = ra
nside = 256  # 128
npix = hp.pixelfunc.nside2npix(nside)
pixels = hp.pixelfunc.ang2pix(nside, theta, phi, nest=True)
skymap = [0] * npix
index = -1
for i in pixels:
    index = index + 1
    if skymap[i] == 0:
        skymap[i] = p[index]
    else:
        skymap[i] = skymap[i] + p[index]
skymap = skymap / np.sum(skymap)
skymapring = hp.pixelfunc.reorder(skymap, inp="NESTED", out="RING")
sigma = 0.05  # smooting parameter
skymapring = hp.sphtfunc.smoothing(skymapring, sigma=sigma)
skymap = hp.pixelfunc.reorder(skymapring, inp="RING", out="NESTED")
skymap[skymap < 0] = 0
skymap = skymap / np.sum(skymap)
np.savetxt(
    f"{output_dir}/summary_plots/RapidPE_skymap_{namestr}.dat",
    skymap,
)


deg2perpix = hp.nside2pixarea(nside, degrees=True)
probperdeg2 = skymap / deg2perpix
ax = plt.axes(projection="astro hours mollweide")
ax.grid()
vmax = probperdeg2.max()
img = ax.imshow_hpx(
    (probperdeg2, "ICRS"), nested=True, vmin=0.0, vmax=vmax, cmap="cylon"
)
plot.outline_text(ax)

# contour option in ligo-skymap-plot
cls = 100 * postprocess.find_greedy_credible_levels(skymap)
cs = ax.contour_hpx(
    (cls, "ICRS"), nested=True, colors="k", linewidths=0.5, levels=(50, 90)
)
fmt = r"%g\%%" if rcParams["text.usetex"] else "%g%%"
plt.clabel(cs, fmt=fmt, fontsize=6, inline=True)

# annotate option in ligo-skymap-plot
text = []
pp = np.round((50, 90)).astype(int)
ii = np.round(np.searchsorted(np.sort(cls), (50, 90)) * deg2perpix).astype(int)
for i, p in zip(ii, pp):
    text.append("{:d}% area: {:d} deg²".format(p, i, grouping=True))
ax.text(1, 1, "\n".join(text), transform=ax.transAxes, ha="right")

plt.savefig(f"{output_dir}/summary_plots/skymap_{namestr}.png")
