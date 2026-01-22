# Download Abell Catalog and plot with healpy

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

# --- 2. Optional: Filter to likely real Abell clusters ---
# Original Abell catalog has ~4,073 clusters; V/114 includes many duplicates/artifacts.
# We can filter by richness (RICH >= 0) and distance class (DIST <= 7) if columns exist.
if 'RICH' in abell.colnames and 'DIST' in abell.colnames:
    mask = (abell['RICH'] >= 0) & (abell['DIST'] <= 7)
    ra_deg = ra_deg[mask]
    dec_deg = dec_deg[mask]
    print(f"After filtering: {len(ra_deg)} clusters.")

# --- 3. Convert to HEALPix coordinates ---
theta = np.radians(90.0 - dec_deg)  # colatitude
phi = np.radians(ra_deg)

# --- 4. Create HEALPix map (nside=64) ---
nside = 64
npix = hp.nside2npix(nside)
hpx_map = np.zeros(npix, dtype=float)  # Use float to allow NaN

for t, p in zip(theta, phi):
    ipix = hp.ang2pix(nside, t, p)
    hpx_map[ipix] += 1.0

# --- 5. Replace zeros with NaN for log-scale plotting ---
hpx_plot = np.where(hpx_map > 0, hpx_map, np.nan)

# --- 6. Plot Mollweide projection ---
plt.figure(figsize=(12, 8))
hp.mollview(
    hpx_plot,
    title="Abell Cluster Catalog (V/114) – Sky Distribution",
    unit="Clusters per pixel",
    norm="log",
    cmap="magma",
    cbar=True,
    hold=False,
    min=np.nanmin(hpx_plot),  # Avoid issues with all-NaN
)
hp.graticule()
plt.savefig("abell_v114_healpy.png", dpi=150, bbox_inches="tight")
plt.show()

# --- 7. Summary ---
total_clusters = np.nansum(hpx_plot)
pixels_with_clusters = np.count_nonzero(~np.isnan(hpx_plot))
print(f"Total clusters plotted: {int(total_clusters)}")
print(f"Pixels with clusters: {pixels_with_clusters}")