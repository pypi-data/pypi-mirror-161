.. _mosaic:

Mosaic
======

Reading 4D data `encoded as mosaics`_ is supported natively, and
:class:`~dicom_parser.image.Image` instances will, by default, return a 3D
stacked volume. The same applies for :class:`~dicom_parser.series.Series`
instances, which simply stack the images' data.

Example
-------

.. code:: python

    >>> fmri_series = Series('/path/to/dicom/fmri/')
    >>> fmri_series.data.shape
    (96, 96, 64, 200)

The associated :class:`~dicom_parser.utils.siemens.mosaic.Mosaic` instance and
underlying attributes are avialble through the
:attr:`~dicom_parser.image.Image.mosaic` property.

.. code-block:: python

    >>> type(image.mosaic)
    dicom_parser.utils.siemens.mosaic.Mosaic
    >>> image.mosaic.volume_shape
    (96, 96, 64)

.. _encoded as mosaics:
   https://nipy.org/nibabel/dicom/dicom_mosaic.html
