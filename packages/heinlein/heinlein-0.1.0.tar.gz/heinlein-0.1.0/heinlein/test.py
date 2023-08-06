

from heinlein.dataset import load_dataset
from heinlein.region import Region
import astropy.units as u

ds = load_dataset("des")
points = [(13.4, -20.2), (13.42, -20.2), (13.42, -20.22), (13.4, -20.22)]
reg = Region(points)
data = ds.get_data_from_region(reg)
cat = data['catalog']
import matplotlib.pyplot as plt

ra = cat['ra'].value
dec = cat['dec'].value
print(len(cat._skycoords))
print(len(cat._cartesian_points))
print(len(cat))
plt.scatter(ra, dec)
plt.show()