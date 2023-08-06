Movici Geo Query
================

Movici Geo Query is a library for creating geospatial indexes (rtrees) and querying those trees. It
is targeted and optimized to work together with other Movici libaries. It works natively with numpy
arrays, where multi-point geometries (such as linestrings and polygons) are accepted using Movici's
`csr` format.

Getting Started
---------------

.. code-block:: python

  import numpy as np
  from movici_geo_query import GeoQuery, PointGeometry

  points_a = PointGeometry(np.array([[0, 1], [0.5, 1]]))
  points_b = PointGeometry(np.array([[0.6, 0.9]]))

  gq = GeoQuery(points_a)


  result = gq.nearest_to(points_b)
  
  # for each point in point_b, gq.nearest returns the index of the nearest point in points_a. The
  # result will have the same length as points_b and contains indexes to the points_a array
  
  print(result.indices) # np.array([1])


Installation
------------
Movici Geo Query binaries are currently only available for Linux (manylinux), but Windows and Mac
builds are coming up soon. Installation can be done using ``pip install movici-geo-query``


.. _Building from source:
 
Building from source
^^^^^^^^^^^^^^^^^^^^^
Building from source requires a C compiler that supports C++17, such as Clang>=5. To build 
movici-geo-query from source you also need a version of Boost.geometry that contains the 
``boost::geometry::index::rtree`` headers (eg. boost > 1.74.0). These can be installed using your
favorite package manager, `downloaded from the Boost website <https://www.boost.org/>`_, or taken
directly from `GitHub <https://github.com/boostorg/geometry>`_. When downloading manually,
make sure the boost header files can be found by pip by placing them in pythons ``include`` 
directory:

.. code-block:: bash
  
  BOOST_VERSION=1.79.0
  INCLUDE_DIR=$(python3 -c "import sysconfig as sc; print(sc.get_paths()['include'])")
  TMP_DIR=/tmp/boost_geometry
  mkdir -p ${TMP_DIR}
  git clone --depth 1 --branch boost-${BOOST_VERSION} https://github.com/boostorg/geometry.git ${TMP_DIR}
  cp ${TMP_DIR}/include/boost ${INCLUDE_DIR}

Now you can clone, compile and install from source:

.. code-block:: bash

  git clone https://github.com/nginfra/movici-geo-query.git
  pip3 install movici-geo-query/



Developing Movici Geo Query
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Developing Movici Geo Query assumes you're developing on Linux using a modern C++ compiler that
support C++17, such as Clang>=5. We have tests both in C++ and in Python. Supported Python versions
are 3.8 and higher. It also requires Boost.geometry (see `Building from source`_)

.. code-block:: bash
  
  # install the dev requirements
  pip3 install -r requirements-dev.txt

  # install the package in editable mode
  pip3 install -e -v .

  # run the c test suite
  mkdir build
  cd build
  cmake ..
  make -j
  ./test
  cd ..

  # run the python test suite
  pytest tests/python
