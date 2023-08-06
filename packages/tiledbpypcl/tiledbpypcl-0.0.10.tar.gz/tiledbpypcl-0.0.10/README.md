# TileDB python pcl bindings

### package bringing some classes and functions from pcl into python

#### see https://github.com/davidcaron/pclpy (packaging issues and out-of-date)

#### WIP

#### get from pypi:
``
pip install tiledbpypcl
``
#### temp pypi account:
    - username: ctiledb
    - password: TileDBPCL

#### example currently working (version 0.0.9)

```
import numpy as np   # need to import numpy before tiledbpypcl, pybind11 issue causes crash in pybind11 packages otherwise
import tiledbpypcl
from tiledbpypcl.vectors import Float // to come: integrates with std::vector
from tiledbpypcl.PointCloud import PointXYZ as PointCloudXYZ
from tiledbpypcl.point_types import PointXYZ

x = 2.0
y = 2.0
z = 2.0

cloudXYZ = PointCloudXYZ()
for _ in range(100):
    pt = PointXYZ(x, y, z)
    cloudXYZ.push_back(pt)
    
print(cloudXYZ.xyz)
```

```
num_pts = 100
pts = np.empty((num_pts, 3), np.float32)
for i in range(num_pts):
    pts[i][0] = x
    pts[i][1] = y
    pts[i][2] = z

cloudXYZ = PointCloudXYZ.from_pts_array(pts)
print(len(cloudXYZ.xyz))
```