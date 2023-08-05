tethys-utils
==================================

This git repository contains the main class Titan and supporting classes and functions for processing data to be put into Tethys.

For gridded data, a good rule of thumb seems to be to make the block_length 10x the grid resolution and subsequently the time_interval being 460.

Improvements
------------
Some optimizations on the querying of datasets that do not exist in the S3 remote could be improved. More specifically, the first time a dataset (or any datasets in the remote bucket) is being processed, some methods in Titan tries to find files that do not exist in the S3 remote. There are several failed attempts to access these files, then it moves on. Knowing early on that there are no existing datasets and not repeatedly querying empty files would be more nicer. Though in most cases, this is not a significant issues as this only affects the first time a dataset is saved.

The current chunking method reliably creates chunks based on only two chunking parameters. But as a consequence, there are many tiny files at the "edges" of chunks especially for large gridded datasets. If this becomes an issue, one solution would be to implement chunking "origins" to the spatial and temporal chunking. The origins should be automatically created and placed at the "lower" bounds of those dimensions. These origins would need to be saved with the dataset metadata. This should halve the number of tiny files and also reduce the total number of results chunks.
