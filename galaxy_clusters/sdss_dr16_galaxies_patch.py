# Query SDSS DR16 for galaxies in a 10°x10° patch
# Saves positions, magnitudes, photo-z to CSV

from astroquery.sdss import SDSS
from astropy import coordinates as coords
import astropy.units as u
import pandas as pd
import numpy as np

# --- 1. Define patch center (change as needed) ---
# Example: Centered on RA=180°, Dec=0° (equatorial)
center_ra = 180.0   # degrees
center_dec = 0.0    # degrees
width = 10.0        # degrees

# Compute bounds
ra_min = center_ra - width / 2.0
ra_max = center_ra + width / 2.0
dec_min = center_dec - width / 2.0
dec_max = center_dec + width / 2.0

print(f"Querying SDSS DR16 for galaxies in [{ra_min:.1f}, {ra_max:.1f}] x [{dec_min:.1f}, {dec_max:.1f}] deg")

# --- 2. Construct SQL query ---
# Uses PhotoObjAll to get magnitudes; joins with Photoz for photo-z
# Filters:
#   - type = 3 → galaxy
#   - clean photometry flags
#   - primary objects only
query = f"""
SELECT
    p.ra, p.dec,
    p.u, p.g, p.r, p.i, p.z,
    pz.z AS photoz,
    pz.zErr AS photoz_err
FROM
    PhotoObjAll AS p
JOIN
    Photoz AS pz ON p.objID = pz.objID
WHERE
    p.type = 3
    AND p.clean = 1
    AND p.mode = 1
    AND p.ra BETWEEN {ra_min} AND {ra_max}
    AND p.dec BETWEEN {dec_min} AND {dec_max}
"""

# --- 3. Execute query via SDSS CasJobs ---
print("Executing query via SDSS CasJobs (may take 10-60 seconds)...")
try:
    result = SDSS.query_sql(query, data_release=16)
except Exception as e:
    print(f"Query failed: {e}")
    raise

if result is None or len(result) == 0:
    raise ValueError("No galaxies found in the specified region.")

print(f"Downloaded {len(result)} galaxies.")

# --- 4. Convert to pandas DataFrame and clean ---
df = result.to_pandas()

# Replace -9999 or invalid photo-z with NaN
df['photoz'] = df['photoz'].replace(-9999.0, np.nan)
df['photoz_err'] = df['photoz_err'].replace(-9999.0, np.nan)

# Optional: drop rows with no photo-z
initial_len = len(df)
df = df.dropna(subset=['photoz'])
print(f"Dropped {initial_len - len(df)} rows with missing photo-z.")

# --- 5. Save to CSV ---
output_file = "sdss_dr16_galaxies_10deg_patch.csv"
df.to_csv(output_file, index=False)
print(f"Saved to '{output_file}'")

# --- 6. Summary stats ---
print("\n--- Summary ---")
print(f"Total galaxies: {len(df)}")
print(f"Photo-z range: {df['photoz'].min():.3f} – {df['photoz'].max():.3f}")
print(f"Magnitude (r) range: {df['r'].min():.2f} – {df['r'].max():.2f}")