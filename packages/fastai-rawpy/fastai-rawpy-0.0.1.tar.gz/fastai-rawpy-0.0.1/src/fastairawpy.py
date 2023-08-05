import fastai
from fastai.vision.all import *
from fastai.vision.data import *
#from fastai.callback import *

#from fastai.torch_core import *
#from fastcore.transform import DisplayedTransform
#from pathlib import Path

import rawpy
import fastai
from fastai import *

class RAWPYobj:
    "This is to copy class Image.Image but actually support RAW image files"
    def __init__(self, fn: Path, pr: rawpy.Params):
        # exposure=findall('[a-zA-Z]+',fn.parents[0].name)[0] # Retrieces "Long" or "Short" exposure
        fn = str(fn)
        try:
            with rawpy.imread(fn) as RAWobj:
                self.obj = RAWobj
                self.ndarr = np.array(RAWobj.postprocess(pr)).astype(np.float32)
                self._size = self.ndarr.shape[:2]
                self.mode = "RGB" if self.ndarr.shape[2] == 3 else self.ndarr.shape[2]
        except rawpy._rawpy.LibRawIOError:
            print("Error. LibRawIOError: This file didn't open: --- ", fn)

    def Update_Size(self):
        self._size = self.ndarr.shape[:2]

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def size(self):
        return self._size

    @property
    def shape(self):
        return self._size


class RAWImage(RAWPYobj):
    "basic Image class made of Rawpy"

    @classmethod
    def create(cls, fn: Path, pr: rawpy.Params) -> None:
        # print("RAWImage.create(): pr", pr)
        return cls(fn, pr)

    def __repr__(
            self): return f'{self.__class__.__name__} mode={self.mode} size={"x".join([str(d) for d in self.size])}'

    def show(self, ctx=None, **kwargs): return show_raw_image(self, ctx=ctx, verbose=True, **kwargs)


# Cell
def RawImageBlock(**kwargs):
    "A `TransformBlock` for RAWImage"
    # print("RawImageBlock: ", kwargs.items())
    parameters = rawpy.Params(**kwargs)
    openFileMethod = partial(RAWImage.create, pr=parameters)
    return TransformBlock(type_tfms=openFileMethod, batch_tfms=IntToFloatTensor)

# Cell
# def ImageBlock(cls=RAWImage,**kwargs):
#    "A `TransformBlock` for images of `cls`"
#    return TransformBlock(type_tfms=cls.create(**kwargs), batch_tfms=IntToFloatTensor)

###################################################################################################################################################

from matplotlib.pyplot import imshow

# Cell
class TensorRawImage(TensorBase):
    def show(self, ctx=None, **kwargs):
        return show_raw_image(self, ctx=ctx, verbose=True, **kwargs)

# Cell
class RAWImageInput(RAWImage): pass
class TensorRawImageInput(TensorRawImage): pass
RAWImageInput._tensor_cls = TensorRawImageInput #TensorBase

# Cell
#class TensorRawImage(TensorRawImageBase): pass

# vision.transforms
# Cell
class IntToFloatTensor(DisplayedTransform):
    "Transform image to float tensor, optionally dividing by 255 (e.g. for images)."
    order = 10 #Need to run after PIL transforms on the GPU
    def __init__(self, div=65535., div_mask=1): store_attr()
    def encodes(self, o:TensorRawImage): return o.float().div_(self.div)
    def decodes(self, o:TensorRawImage): return ((o.clamp(0., 1.) * self.div).long()) if self.div else o

# Cell
def broadcast_vec(dim, ndim, *t, cuda=True):
    "Make a vector broadcastable over `dim` (out of `ndim` total) by prepending and appending unit axes"
    v = [1]*ndim
    v[dim] = -1
    f = to_device if cuda else noop
    return [f(tensor(o).view(*v)) for o in t]

# Cell
@docs
class Normalize(DisplayedTransform):
    "Normalize/denorm batch of `TensorRawImage`"
    parameters,order = L('mean', 'std'),99
    def __init__(self, mean=None, std=None, axes=(0,2,3)): store_attr()

    @classmethod
    def from_stats(cls, mean, std, dim=1, ndim=4, cuda=True): return cls(*broadcast_vec(dim, ndim, mean, std, cuda=cuda))

    def setups(self, dl:DataLoader):
        if self.mean is None or self.std is None:
            x,*_ = dl.one_batch()
            self.mean,self.std = x.mean(self.axes, keepdim=True),x.std(self.axes, keepdim=True)+1e-7

    def encodes(self, x:TensorRawImage): return (x-self.mean) / self.std
    def decodes(self, x:TensorRawImage):
        f = to_cpu if x.device.type=='cpu' else noop
        return (x*f(self.std) + f(self.mean))

    _docs=dict(encodes="Normalize batch", decodes="Denormalize batch")

# vision.data
# Cell
@typedispatch
def show_batch(x:TensorRawImage, y:TensorRawImage, samples, ctxs=None, max_n=10, nrows=None, ncols=None, figsize=None, **kwargs):
    if ctxs is None: ctxs = get_grid(min(len(samples), max_n), nrows=nrows, ncols=ncols, figsize=figsize, double=True)
    for i in range(2):
        ctxs[i::2] = [b.show(ctx=c, **kwargs) for b,c,_ in zip(samples.itemgot(i),ctxs[i::2],range(max_n))]
    return ctxs

# vision.learner
# Cell
@typedispatch
def show_results(x:TensorRawImage, y:TensorRawImage, samples, outs, ctxs=None, max_n=10, figsize=None, **kwargs):
    if ctxs is None: ctxs = get_grid(3*min(len(samples), max_n), ncols=3, figsize=figsize, title='Input/Target/Prediction')
    for i in range(2):
        ctxs[i::3] = [b.show(ctx=c, **kwargs) for b,c,_ in zip(samples.itemgot(i),ctxs[i::3],range(max_n))]
    ctxs[2::3] = [b.show(ctx=c, **kwargs) for b,c,_ in zip(outs.itemgot(0),ctxs[2::3],range(max_n))]
    return


# Cell
def _fig_bounds(x):
    r = x//32
    return min(5, max(1,r))

# Cell
@delegates(plt.Axes.imshow, keep=True, but=['shape', 'imlim'])
def show_raw_image(im, ax=None, figsize=None, title=None, ctx=None,verbose=False,**kwargs):
    "Show a Rawpy or PyTorch image on `ax`."
    # Handle pytorch axis order
    #pv("show_raw_image: begins",verbose)
    if hasattrs(im, ('data','cpu','permute')): # for Pytorch objects
        #pv("show_raw_image: (step in) hasattrs of Tensor",verbose)
        im = im.data.cpu()
        im=((im/65535)*255) # Converting from 16bits to 8bits because stupid "imshow" can only show 8bits
        #im=im*255
        if im.shape[0]<5: im=im.permute(1,2,0)
    elif isinstance(im,RAWPYobj):
        #pv("show_raw_image: (step in) isinstance of RAWPYobj",verbose)
        im=im.ndarr # For Rawpy objects
        im=((im/65535)*255)
    elif not isinstance(im,np.ndarray):
        #pv("show_raw_image: (step in) isinstance of nd.array",verbose)
        im=array(im) # for PIL objects?
   # print(type(im))
    #print(im.shape)
    ax = ifnone(ax,ctx) # returns None if a graph wasn't initialized already
    if figsize is None: figsize = (_fig_bounds(im.shape[0]), _fig_bounds(im.shape[1]))
    if ax is None: _,ax = plt.subplots(figsize=figsize)
    #pv("show_raw_image: ax.imshow()",verbose)
    ax.imshow(np.uint8(im), vmin=0,vmax=255, **kwargs) # prints the images on the figure
    if title is not None: ax.set_title(title)
    ax.axis('off')
    return ax

RAWImage._tensor_cls = TensorRawImage #TensorBase

@ToTensor
def encodes(self, o:RAWImage): return o._tensor_cls(image2tensor(o.ndarr))

RAWImageCreate = Transform(RAWImage.create)

# Cell
@patch(as_prop=True)
def shape(x: RAWImage): return x.sizes[1],x.sizes[0]


######################################################################################################################################

from cv2 import resize as cv2resize
from cv2 import INTER_LINEAR, INTER_AREA, INTER_LANCZOS4

# vision.augment

import torch.nn.functional as F

TensorRawImage.register_func(F.grid_sample, TensorRawImage)
TensorBase.register_func(F.grid_sample, TensorRawImage)

TensorBase.register_func(Tensor.__getitem__, TensorRawImage)
"""
# Cell
for o in Tensor.__getitem__, Tensor.__ne__,Tensor.__eq__,Tensor.add,Tensor.sub,Tensor.mul,Tensor.div,Tensor.__rsub__,Tensor.__radd__,Tensor.matmul,Tensor.bmm:
    TensorBase.register_func(o, TensorRawImage)
"""
# Cell
for o in Tensor.__getitem__, Tensor.__ne__, Tensor.__eq__, Tensor.add, Tensor.sub, Tensor.mul, Tensor.div, Tensor.__rsub__, Tensor.__radd__, Tensor.matmul, Tensor.bmm:
    TensorRawImage.register_func(o, TensorRawImage)

TensorTypes = (TensorImage, TensorMask, TensorPoint, TensorBBox, TensorRawImage)


# Cell
def _process_sz(size):
    if isinstance(size, int): size = (size, size)
    return fastuple(size[1], size[0])


def _get_sz(x):
    if isinstance(x, tuple): x = x[0]
    if not isinstance(x, Tensor): return fastuple(x.size)
    return fastuple(getattr(x, 'img_size', getattr(x, 'sz', (x.shape[-1], x.shape[-2]))))


# Cell
@delegates()
class RandomResizedCrop(RandTransform):
    "Picks a random scaled crop of an image and resize it to `size`"
    split_idx, order = None, 1

    def __init__(self, size, min_scale=0.08, ratio=(3 / 4, 4 / 3),  # resamples=(Image.BILINEAR),
                 val_xtra=0.14, max_scale=1., **kwargs):
        size = _process_sz(size)
        store_attr()
        super().__init__(**kwargs)
        random.seed(2022)
        # self.min_scale=random.triangular(low=0.25, high=0.5, mode=0.49)
        # self.mode = resamples
        self.p

    def before_call(self, b, split_idx):
        w, h = self.orig_sz = _get_sz(b)
        if split_idx:
            xtra = math.ceil(max(*self.size[:2]) * self.val_xtra / 8) * 8
            self.final_size = (self.size[0] + xtra, self.size[1] + xtra)
            self.tl, self.cp_size = (0, 0), self.orig_sz
            return
        self.final_size = self.size
        # self.p=random.uniform(0,1)
        self.p = random.choice([0, 1])
        if self.p:
            self.tl = random.randint(0, w - self.size[0]), random.randint(0, h - self.size[1])
        else:
            for attempt in range(10):
                area = random.uniform(self.min_scale, self.max_scale) * w * h
                # area =random.triangular(low=self.min_scale, high=self.max_scale, mode=self.max_scale)*w*h
                ratio = math.exp(random.uniform(math.log(self.ratio[0]), math.log(self.ratio[1])))
                nw = int(round(math.sqrt(area * ratio)))
                nh = int(round(math.sqrt(area / ratio)))
                if nw <= w and nh <= h:
                    self.cp_size = (nw, nh)
                    self.tl = random.randint(0, w - nw), random.randint(0, h - nh)
                    return
            if w / h < self.ratio[0]:
                self.cp_size = (w, int(w / self.ratio[0]))
            elif w / h > self.ratio[1]:
                self.cp_size = (int(h * self.ratio[1]), h)
            else:
                self.cp_size = (w, h)
            self.tl = ((w - self.cp_size[0]) // 2, (h - self.cp_size[1]) // 2)

    def encodes(self, x: RAWPYobj):
        if self.p:
            x.ndarr = x.ndarr[self.tl[0]:self.tl[0] + self.size[0], self.tl[1]:self.tl[1] + self.size[1]]
        else:
            x.ndarr = x.ndarr[self.tl[0]:self.tl[0] + self.cp_size[0], self.tl[1]:self.tl[1] + self.cp_size[1]]
            # print(x.ndarr.shape)
            if min(self.cp_size[0], self.cp_size[1]) > self.size[
                0]:  # Case 1: Making it smaller == Cropped Patch is bigger than the desired cropped size
                x.ndarr = cv2resize(x.ndarr, dsize=(self.size[0], self.size[0]), interpolation=INTER_AREA)
            elif max(self.cp_size[0], self.cp_size[1]) < self.size[
                0]:  # Case 2: Making it bigger == Cropped Patch is smaller than the desired cropped size
                x.ndarr = cv2resize(x.ndarr, dsize=(self.size[0], self.size[0]), interpolation=INTER_LANCZOS4)
            else:  # Case 2: Making it slightly the same == Cropped Patch's one of the edges is smaller, while another is bigger == Just squeezing it somehow ### Needs to be checked though
                x.ndarr = cv2resize(x.ndarr, dsize=(self.size[0], self.size[0]), interpolation=INTER_LINEAR)
            # print(x.ndarr.shape)
        x.Update_Size()
        return x


"""
Crucial Affine classes for augmentation support
"""


# Cell
def _init_mat(x):
    mat = torch.eye(3, device=x.device).float()
    return mat.unsqueeze(0).expand(x.size(0), 3, 3).contiguous()


# Cell
def _grid_sample(x, coords, mode='bilinear', padding_mode='reflection', align_corners=None):
    "Resample pixels in `coords` from `x` by `mode`, with `padding_mode` in ('reflection','border','zeros')."
    # coords = coords.permute(0, 3, 1, 2).contiguous().permute(0, 2, 3, 1) # optimize layout for grid_sample
    if mode == 'bilinear':  # hack to get smoother downwards resampling
        mn, mx = coords.min(), coords.max()
        # max amount we're affine zooming by (>1 means zooming in)
        z = 1 / (mx - mn).item() * 2
        # amount we're resizing by, with 100% extra margin
        d = min(x.shape[-2] / coords.shape[-2], x.shape[-1] / coords.shape[-1]) / 2
        # If we're resizing up by >200%, and we're zooming less than that, interpolate first
        if d > 1 and d > z:
            x = F.interpolate(x, scale_factor=1 / d, mode='area', recompute_scale_factor=True)
    return F.grid_sample(x, coords, mode=mode, padding_mode=padding_mode, align_corners=align_corners)


# Internal Cell
@patch
def affine_coord(x: TensorRawImage, mat=None, coord_tfm=None, sz=None, mode='bilinear', pad_mode=PadMode.Reflection,
                 align_corners=True):
    if mat is None and coord_tfm is None and sz is None: return x
    size = tuple(x.shape[-2:]) if sz is None else (sz, sz) if isinstance(sz, int) else tuple(sz)
    if mat is None: mat = _init_mat(x)[:, :2]
    coords = affine_grid(mat, x.shape[:2] + size, align_corners=align_corners)
    if coord_tfm is not None: coords = coord_tfm(coords)
    return TensorRawImage(_grid_sample(x, coords, mode=mode, padding_mode=pad_mode, align_corners=align_corners))


# Cell
def _prepare_mat(x, mat):
    h, w = getattr(x, 'img_size', x.shape[-2:])
    mat[:, 0, 1] *= h / w
    mat[:, 1, 0] *= w / h
    return mat[:, :2]


# Cell
class AffineCoordTfm(RandTransform):
    "Combine and apply affine and coord transforms"
    order, split_idx = 30, None

    def __init__(self, aff_fs=None, coord_fs=None, size=None, mode='bilinear', pad_mode=PadMode.Reflection,
                 mode_mask='nearest', align_corners=None, **kwargs):
        store_attr(but=['aff_fs', 'coord_fs'])
        super().__init__(**kwargs)
        self.aff_fs, self.coord_fs = L(aff_fs), L(coord_fs)
        self.cp_size = None if size is None else (size, size) if isinstance(size, int) else tuple(size)

    def before_call(self, b, split_idx):
        while isinstance(b, tuple): b = b[0]
        self.split_idx = split_idx
        self.do, self.mat = True, self._get_affine_mat(b)
        for t in self.coord_fs: t.before_call(b)

    def compose(self, tfm):
        "Compose `self` with another `AffineCoordTfm` to only do the interpolation step once"
        # TODO: keep `name` up to date with the combination
        # TODO: have option to only show a subset of the attrs, e.g. for `Flip`
        self.aff_fs += tfm.aff_fs
        self.coord_fs += tfm.coord_fs

    def _get_affine_mat(self, x):
        aff_m = _init_mat(x)
        if self.split_idx: return _prepare_mat(x, aff_m)
        ms = [f(x) for f in self.aff_fs]
        ms = [m for m in ms if m is not None]
        for m in ms: aff_m = aff_m @ m
        return _prepare_mat(x, aff_m)

    def _encode(self, x, mode, reverse=False):
        coord_func = None if len(self.coord_fs) == 0 or self.split_idx else partial(compose_tfms, tfms=self.coord_fs,
                                                                                    reverse=reverse)
        return x.affine_coord(self.mat, coord_func, sz=self.size, mode=mode, pad_mode=self.pad_mode,
                              align_corners=self.align_corners)

    def encodes(self, x: TensorRawImage):
        return self._encode(x, self.mode)


"""Flip Augumentation"""


# Cell
class Flip(AffineCoordTfm):
    "Randomly flip a batch of images with a probability `p`"

    def __init__(self, p=0.5, draw=None, size=None, mode='bilinear', pad_mode=PadMode.Reflection, align_corners=True,
                 batch=False):
        aff_fs = partial(flip_mat, p=p, draw=draw, batch=batch)
        super().__init__(aff_fs, size=size, mode=mode, pad_mode=pad_mode, align_corners=align_corners, p=p)


"""Dihedral Augumentation"""


@patch
def dihedral(x: TensorRawImage, k):
    if k in [1, 3, 4, 7]: x = x.flip(-1)
    if k in [2, 4, 5, 7]: x = x.flip(-2)
    if k in [3, 5, 6, 7]: x = x.transpose(-1, -2)
    return x


# Internal Cell
@patch
def dihedral_batch(x: TensorRawImage, p=0.5, draw=None, size=None, mode=None, pad_mode=None, batch=False,
                   align_corners=True):
    x0, mode, pad_mode = _get_default(x, mode, pad_mode)
    mat = _prepare_mat(x, dihedral_mat(x0, p=p, draw=draw, batch=batch))
    return x.affine_coord(mat=mat, sz=size, mode=mode, pad_mode=pad_mode, align_corners=align_corners)


# Cell
class Dihedral(AffineCoordTfm):
    "Apply a random dihedral transformation to a batch of images with a probability `p`"

    def __init__(self, p=0.5, draw=None, size=None, mode='bilinear', pad_mode=PadMode.Reflection, align_corners=None,
                 batch=False):
        f = partial(dihedral_mat, p=p, draw=draw, batch=batch)
        super().__init__(aff_fs=f, size=size, mode=mode, pad_mode=pad_mode, align_corners=align_corners)


"""Warp Augumentation"""

from torch import stack, zeros_like as t0, ones_like as t1


# Cell
def _draw_mask(x, def_draw, draw=None, p=0.5, neutral=0., batch=False):
    "Creates mask_tensor based on `x` with `neutral` with probability `1-p`. "
    if draw is None: draw = def_draw
    if callable(draw):
        res = draw(x)
    elif is_listy(draw):
        assert len(draw) >= x.size(0)
        res = tensor(draw[:x.size(0)], dtype=x.dtype, device=x.device)
    else:
        res = x.new_zeros(x.size(0)) + draw
    return TensorBase(mask_tensor(res, p=p, neutral=neutral, batch=batch))


class _WarpCoord():
    def __init__(self, magnitude=0.2, p=0.5, draw_x=None, draw_y=None, batch=False):
        store_attr()
        self.coeffs = None

    def _def_draw(self, x):
        if not self.batch: return x.new_empty(x.size(0)).uniform_(-self.magnitude, self.magnitude)
        return x.new_zeros(x.size(0)) + random.uniform(-self.magnitude, self.magnitude)

    def before_call(self, x):
        x_t = _draw_mask(x, self._def_draw, self.draw_x, p=self.p, batch=self.batch)
        y_t = _draw_mask(x, self._def_draw, self.draw_y, p=self.p, batch=self.batch)
        orig_pts = torch.tensor([[-1, -1], [-1, 1], [1, -1], [1, 1]], dtype=x.dtype, device=x.device)
        self.orig_pts = orig_pts.unsqueeze(0).expand(x.size(0), 4, 2)
        targ_pts = stack([stack([-1 - y_t, -1 - x_t]), stack([-1 + y_t, 1 + x_t]),
                          stack([1 + y_t, -1 + x_t]), stack([1 - y_t, 1 - x_t])])
        self.targ_pts = targ_pts.permute(2, 0, 1)

    def __call__(self, x, invert=False):
        coeffs = find_coeffs(self.targ_pts, self.orig_pts) if invert else find_coeffs(self.orig_pts, self.targ_pts)
        return apply_perspective(x, coeffs)


# Internal Cell
@patch
@delegates(_WarpCoord.__init__)
def warp(x: TensorRawImage, size=None, mode='bilinear', pad_mode=PadMode.Reflection, align_corners=True, **kwargs):
    x0, mode, pad_mode = _get_default(x, mode, pad_mode)
    coord_tfm = _WarpCoord(**kwargs)
    coord_tfm.before_call(x0)
    return x.affine_coord(coord_tfm=coord_tfm, sz=size, mode=mode, pad_mode=pad_mode, align_corners=align_corners)


# Cell
class Warp(AffineCoordTfm):
    "Apply perspective warping with `magnitude` and `p` on a batch of matrices"

    def __init__(self, magnitude=0.2, p=0.5, draw_x=None, draw_y=None, size=None, mode='bilinear',
                 pad_mode=PadMode.Reflection, batch=False, align_corners=True):
        store_attr()
        coord_fs = _WarpCoord(magnitude=magnitude, p=p, draw_x=draw_x, draw_y=draw_y, batch=batch)
        super().__init__(coord_fs=coord_fs, size=size, mode=mode, pad_mode=pad_mode, align_corners=align_corners)


"""Rotate Augumentation"""


# Internal Cell
@patch
@delegates(rotate_mat)
def rotate(x: TensorRawImage, size=None, mode=None, pad_mode=None, align_corners=True, **kwargs):
    x0, mode, pad_mode = _get_default(x, mode, pad_mode)
    mat = _prepare_mat(x, rotate_mat(x0, **kwargs))
    return x.affine_coord(mat=mat, sz=size, mode=mode, pad_mode=pad_mode, align_corners=align_corners)


# Cell
class Rotate(AffineCoordTfm):
    "Apply a random rotation of at most `max_deg` with probability `p` to a batch of images"

    def __init__(self, max_deg=10, p=0.5, draw=None, size=None, mode='bilinear', pad_mode=PadMode.Reflection,
                 align_corners=True, batch=False):
        aff_fs = partial(rotate_mat, max_deg=max_deg, p=p, draw=draw, batch=batch)
        super().__init__(aff_fs=aff_fs, size=size, mode=mode, pad_mode=pad_mode, align_corners=align_corners)


"""Zoom Augumentation """


# Internal Cell
@patch
@delegates(zoom_mat)
def zoom(x: TensorRawImage, size=None, mode='bilinear', pad_mode=PadMode.Reflection,
         align_corners=True, **kwargs):
    x0, mode, pad_mode = _get_default(x, mode, pad_mode)
    return x.affine_coord(mat=zoom_mat(x0, **kwargs)[:, :2], sz=size, mode=mode, pad_mode=pad_mode,
                          align_corners=align_corners)


# Cell
class Zoom(AffineCoordTfm):
    "Apply a random zoom of at most `max_zoom` with probability `p` to a batch of images"

    def __init__(self, min_zoom=1., max_zoom=1.1, p=0.5, draw=None, draw_x=None, draw_y=None, size=None,
                 mode='bilinear',
                 pad_mode=PadMode.Reflection, batch=False, align_corners=True):
        aff_fs = partial(zoom_mat, min_zoom=min_zoom, max_zoom=max_zoom, p=p, draw=draw, draw_x=draw_x, draw_y=draw_y,
                         batch=batch)
        super().__init__(aff_fs, size=size, mode=mode, pad_mode=pad_mode, align_corners=align_corners)


""" Brightness and Contrast Augumentation """


# Cell
@patch
def lighting(x: TensorRawImageInput, func): return torch.sigmoid(func(logit(x)))


# Cell
class SpaceTfm(RandTransform):
    "Apply `fs` to the logits"
    order = 40

    def __init__(self, fs, space_fn, **kwargs):
        super().__init__(**kwargs)
        self.space_fn = space_fn
        self.fs = L(fs)

    def before_call(self, b, split_idx):
        self.do = True
        while isinstance(b, tuple): b = b[0]
        for t in self.fs: t.before_call(b)

    def compose(self, tfm):
        "Compose `self` with another `LightingTransform`"
        self.fs += tfm.fs

    def encodes(self, x: TensorRawImageInput):
        return self.space_fn(x, partial(compose_tfms, tfms=self.fs))


# Cell
class LightingTfm(SpaceTfm):
    "Apply `fs` to the logits"
    order = 40

    def __init__(self, fs, **kwargs):
        super().__init__(fs, TensorRawImageInput.lighting, **kwargs)


# Cell
class _BrightnessLogit():
    def __init__(self, max_lighting=0.2, p=0.75, draw=None, batch=False): store_attr()

    def _def_draw(self, x):
        if not self.batch: return x.new_empty(x.size(0)).uniform_(0.5 * (1 - self.max_lighting),
                                                                  0.5 * (1 + self.max_lighting))
        return x.new_zeros(x.size(0)) + random.uniform(0.5 * (1 - self.max_lighting), 0.5 * (1 + self.max_lighting))

    def before_call(self, x):
        self.change = _draw_mask(x, self._def_draw, draw=self.draw, p=self.p, neutral=0.5, batch=self.batch)

    def __call__(self, x): return x.add_(logit(self.change[:, None, None, None]))


# Internal Cell
@patch
@delegates(_BrightnessLogit.__init__)
def brightness(x: TensorRawImageInput, **kwargs):
    func = _BrightnessLogit(**kwargs)
    func.before_call(x)
    return x.lighting(func)


# Cell
class Brightness(LightingTfm):
    def __init__(self, max_lighting=0.2, p=0.75, draw=None, batch=False):
        "Apply change in brightness of `max_lighting` to batch of images with probability `p`."
        store_attr()
        super().__init__(_BrightnessLogit(max_lighting, p, draw, batch))


# Cell
class _ContrastLogit():
    def __init__(self, max_lighting=0.2, p=0.75, draw=None, batch=False):
        store_attr()

    def _def_draw(self, x):
        if not self.batch:
            res = x.new_empty(x.size(0)).uniform_(math.log(1 - self.max_lighting), -math.log(1 - self.max_lighting))
        else:
            res = x.new_zeros(x.size(0)) + random.uniform(math.log(1 - self.max_lighting),
                                                          -math.log(1 - self.max_lighting))
        return torch.exp(res)

    def before_call(self, x):
        self.change = _draw_mask(x, self._def_draw, draw=self.draw, p=self.p, neutral=1., batch=self.batch)

    def __call__(self, x):
        return x.mul_(self.change[:, None, None, None])


# Internal Cell
@patch
@delegates(_ContrastLogit.__init__)
def contrast(x: TensorRawImageInput, **kwargs):
    func = _ContrastLogit(**kwargs)
    func.before_call(x)
    return x.lighting(func)


# Cell
class Contrast(LightingTfm):
    "Apply change in contrast of `max_lighting` to batch of images with probability `p`."

    def __init__(self, max_lighting=0.2, p=0.75, draw=None, batch=False):
        store_attr()
        super().__init__(_ContrastLogit(max_lighting, p, draw, batch))


class RandNoisyTransform(Transform):
    order = 100  # After Normalize

    def __init__(self, noise_factor=0.5):
        self.noise_factor = noise_factor

    def __call__(self, b, **kwargs):
        x, y = b
        return x + self.noise_factor * torch.randn(x.shape), y


class RandomGaussianNoise(RandTransform):
    "Add noise to image"
    order = 99

    def __init__(self, p=0.5, noise_factor=0.3):
        store_attr()
        super().__init__(p=p)

    def encodes(self, x: TensorRawImageInput): return x + (self.noise_factor * torch.randn(*x.shape).to(x.device))


""" Random Erasing """

from torchvision.transforms.functional import gaussian_blur


# Cell
def cutout_gaussian(x, areas):
    "Replace all `areas` in `x` with N(0,1) noise"
    # print("cutout:", x.shape)
    # a=detuplify(x)[0]
    # b=detuplify(x)[1]
    # print(a.shape)
    # print(a,b)
    chan, img_h, img_w = x.shape[-3:]
    # for rl,rh,cl,ch in areas: x[...,rl:rh, cl:ch]=x[...,rl:rh, cl:ch]+(0.4*torch.randn(*x[...,rl:rh, cl:ch].shape).to(x.device))
    chance = random.choice([0, 1])
    if chance:
        for rl, rh, cl, ch in areas:
            to_be_kernel_sz = min(abs(rh - rl), abs(ch - cl))
            if to_be_kernel_sz <= 1:
                ch += 2
                rh += 2
                to_be_kernel_sz = 2
            to_be_kernel_sz = ((to_be_kernel_sz - 1) * 2) - 1
            # if to_be_kernel_sz % 2 == 0:
            #   to_be_kernel_sz=to_be_kernel_sz-1
            x[..., rl:rh, cl:ch] = gaussian_blur(x[..., rl:rh, cl:ch], to_be_kernel_sz)
    else:
        for rl, rh, cl, ch in areas: x[..., rl:rh, cl:ch] = x[..., rl:rh, cl:ch] + (
                    0.05 * torch.randn(*x[..., rl:rh, cl:ch].shape).to(x.device))
    return x


# Cell
def _slice(area, sz):
    bound = int(round(math.sqrt(area)))
    loc = random.randint(0, max(sz - bound, 0))
    return loc, loc + bound


# Cell
class RandomErasing(RandTransform):
    "Randomly selects a rectangle region in an image and randomizes its pixels."
    order = 100  # After Normalize

    def __init__(self, p=0.5, sl=0., sh=0.3, min_aspect=0.3, max_count=1):
        store_attr()
        super().__init__(p=p)
        self.log_ratio = (math.log(min_aspect), math.log(1 / min_aspect))

    def _bounds(self, area, img_h, img_w):
        r_area = random.uniform(self.sl, self.sh) * area
        aspect = math.exp(random.uniform(*self.log_ratio))
        return _slice(r_area * aspect, img_h) + _slice(r_area / aspect, img_w)

    def encodes(self, x: TensorRawImageInput):  # TensorRawImageInput
        count = random.randint(1, self.max_count)
        _, img_h, img_w = x.shape[-3:]
        area = img_h * img_w / count
        areas = [self._bounds(area, img_h, img_w) for _ in range(count)]
        return cutout_gaussian(x, areas)


""" Preparing aug_transforms function for btch_tfms"""


# Cell
def _compose_same_tfms(tfms):
    tfms = L(tfms)
    if len(tfms) == 0: return None
    res = tfms[0]
    for tfm in tfms[1:]: res.compose(tfm)
    return res


# Cell
def setup_aug_tfms(tfms):
    "Go through `tfms` and combines together affine/coord or lighting transforms"
    aff_tfms = [tfm for tfm in tfms if isinstance(tfm, AffineCoordTfm)]
    lig_tfms = [tfm for tfm in tfms if isinstance(tfm, LightingTfm)]
    others = [tfm for tfm in tfms if tfm not in aff_tfms + lig_tfms]
    lig_tfm = _compose_same_tfms(lig_tfms)
    aff_tfm = _compose_same_tfms(aff_tfms)
    res = [aff_tfm] if aff_tfm is not None else []
    if lig_tfm is not None: res.append(lig_tfm)
    return res + others


# Cell
def aug_transforms(mult=1.0, do_flip=True, flip_vert=False, max_rotate=10., min_zoom=1., max_zoom=1.1,
                   max_lighting=0.2, max_warp=0.2, p_affine=0.75, p_lighting=0.75, xtra_tfms=None, size=None,
                   mode='bilinear', pad_mode=PadMode.Reflection, align_corners=True, batch=False, min_scale=1.):
    "Utility func to easily create a list of flip, rotate, zoom, warp, lighting transforms."
    res, tkw = [], dict(size=size if min_scale == 1. else None, mode=mode, pad_mode=pad_mode, batch=batch,
                        align_corners=align_corners)
    max_rotate, max_lighting, max_warp = array([max_rotate, max_lighting, max_warp]) * mult
    if do_flip: res.append(Dihedral(p=0.5, **tkw) if flip_vert else Flip(p=0.5, **tkw))
    if max_warp:   res.append(Warp(magnitude=max_warp, p=p_affine, **tkw))
    if max_rotate: res.append(Rotate(max_deg=max_rotate, p=p_affine, **tkw))
    if min_zoom < 1 or max_zoom > 1: res.append(Zoom(min_zoom=min_zoom, max_zoom=max_zoom, p=p_affine, **tkw))
    if max_lighting:
        res.append(Brightness(max_lighting=max_lighting, p=p_lighting, batch=batch))
        res.append(Contrast(max_lighting=max_lighting, p=p_lighting, batch=batch))
    if min_scale != 1.: xtra_tfms = RandomResizedCropGPU(size, min_scale=min_scale, ratio=(1, 1)) + L(xtra_tfms)
    return setup_aug_tfms(res + L(xtra_tfms))