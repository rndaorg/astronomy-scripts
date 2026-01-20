# Day 3: Download Abell Catalog via astroquery and plot with healpy (FIXED)

import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
from astroquery.vizier import Vizier

# --- 1. Query Abell catalog (V/114) ---
print("Querying Abell catalog from VizieR (V/114)...")
Vizier.ROW_LIMIT = -1
catalogs = Vizier.get_catalogs("V/114")
abell = catalogs[0]

ra_deg = abell['RAJ2000'].data
dec_deg = abell['DEJ2000'].data

print(f"Downloaded {len(ra_deg)} entries.")

# --- 2. Convert to HEALPix coordinates ---
theta = np.radians(90.0 - dec_deg)  # colatitude
phi = np.radians(ra_deg)

# --- 3. Create HEALPix map (nside=64) ---
nside = 64
npix = hp.nside2npix(nside)
hpx_map = np.zeros(npix, dtype=int)

for t, p in zip(theta, phi):
    ipix = hp.ang2pix(nside, t, p)
    hpx_map[ipix] += 1

# --- 4. MASK ZERO VALUES for log-scale plotting ---
# healpy requires positive values for log norm
hpx_masked = hp.ma(hpx_map)
hpx_masked.mask = (hpx_map == 0)  # mask empty pixels

# --- 5. Plot ---
plt.figure(figsize=(12, 8))
hp.mollview(
    hpx_masked,
    title="Abell Cluster Catalog (V/114) – Sky Distribution",
    unit="Clusters per pixel",
    norm="log",          # now safe: zeros are masked
    cmap="magma",
    cbar=True,
    hold=False
)
hp.graticule()
plt.savefig("abell_v114_healpy.png", dpi=150, bbox_inches="tight")
plt.show()

# --- 6. Summary ---
print(f"Total clusters: {hpx_map.sum()}")
print(f"Pixels with clusters: {(hpx_map > 0).sum()}")