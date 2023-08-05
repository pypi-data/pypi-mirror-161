This package lets you use "RawImageBlock" in fast.ai so now you can read high quality images of RAW files.
This class inherits RawPy library and creates the interface between the fastai and Rawpy.

How to use:

Just pick RawImageBlock instead of ImageBlock. If you want to pass in paramters for postprocessing, you can easily do so right through "RawImageBlock".

In instance: RawImageBlock(paramterA=a,parameterB=b,...)

for more information, here:
https://letmaik.github.io/rawpy/api/rawpy.Params.html