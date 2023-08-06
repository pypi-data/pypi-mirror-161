"""Linear modules."""

import abc
import dataclasses
from typing import (Any, Callable, Iterable, List, Optional, Sequence, Tuple,
                    Union)
from dataclasses import dataclass, field

from flax.linen.initializers import lecun_normal
from flax.linen.initializers import variance_scaling
from flax.linen.initializers import zeros
from flax.linen.module import compact
from flax.linen.module import Module
from flax.linen.dtypes import promote_dtype
from jax import eval_shape
from jax import lax
from jax import ShapedArray
import jax.numpy as jnp
import numpy as np
from cdopt.manifold_jax import euclidean_jax, sphere_jax, stiefel_jax

from typing_extensions import \
    dataclass_transform  # pytype: disable=not-supported-yet

from flax import (config, core, errors, serialization, traceback_util,
                  traverse_util)
from flax.core import Scope
from flax.core.frozen_dict import FrozenDict
from flax.core.scope import (  # pylint: disable=g-multiple-import
    CollectionFilter, DenyList, FrozenVariableDict, Variable, VariableDict,
    union_filters)
from flax.linen import summary 

from typing import (Any, Callable, Dict, Generic, Iterable, List, Optional,
                    Sequence, Set, Tuple, Type, TypeVar, Union, overload)

PRNGKey = Any  # pylint: disable=invalid-name
RNGSequences = Dict[str, PRNGKey]


Shape = Tuple[int, ...]
Dtype = Any  # this could be a real type?
Array = Any
PrecisionLike = Union[None, str, lax.Precision, Tuple[str, str],
                      Tuple[lax.Precision, lax.Precision]]

default_kernel_init = lecun_normal()


def _normalize_axes(axes: Tuple[int, ...], ndim: int) -> Tuple[int, ...]:
  # A tuple by convention. len(axes_tuple) then also gives the rank efficiently.
  return tuple(sorted(ax if ax >= 0 else ndim + ax for ax in axes))


def _canonicalize_tuple(x: Union[Sequence[int], int]) -> Tuple[int, ...]:
  if isinstance(x, Iterable):
    return tuple(x)
  else:
    return (x,)


def weight_var_transfer(tensor_shape):
  
  var_shape = (np.prod( np.array(tensor_shape[:-1])) , tensor_shape[-1])
#   var_shape = tensor_shape
#   print(var_shape)
  weight_to_var = lambda X_tensor: jnp.reshape(X_tensor, var_shape)
  var_to_weight = lambda X_var: jnp.reshape(X_var, tensor_shape)
  return weight_to_var, var_to_weight, var_shape


def wvt_conv_flatten_transp(tensor_shape):
  
  var_shape = (np.prod( np.array(tensor_shape[:-1])) , tensor_shape[-1])
#   var_shape = tensor_shape
#   print(var_shape)
  weight_to_var = lambda X_tensor: jnp.reshape(X_tensor, var_shape)
  var_to_weight = lambda X_var: jnp.reshape(X_var, tensor_shape)
  return weight_to_var, var_to_weight, var_shape


def wvt_conv_flatten(tensor_shape):
  tensor_shape_ref = ( *tensor_shape[:-2], tensor_shape[-1], tensor_shape[-2] )
  var_shape = (np.prod( np.array(tensor_shape_ref[:-1])) , tensor_shape_ref[-1])
  weight_to_var = lambda X_tensor: jnp.reshape(  X_tensor.swapaxes(-2,-1), var_shape )
  var_to_weight = lambda X_var: jnp.reshape(X_var, tensor_shape_ref).swapaxes(-2,-1)
  return weight_to_var, var_to_weight, var_shape


def wvt_identity(tensor_shape):
  return lambda X_tensor: X_tensor, lambda X_var: X_var, tensor_shape







class Dense_cdopt(Module):
  """A linear transformation applied over the last dimension of the input.

  Attributes:
    features: the number of output features.
    use_bias: whether to add a bias to the output (default: True).
    dtype: the dtype of the computation (default: infer from input and params).
    param_dtype: the dtype passed to parameter initializers (default: float32).
    precision: numerical precision of the computation see `jax.lax.Precision`
      for details.
    kernel_init: initializer function for the weight matrix.
    bias_init: initializer function for the bias.
  """
  features: int
  use_bias: bool = True
  dtype: Optional[Dtype] = None
  param_dtype: Dtype = jnp.float32
  precision: PrecisionLike = None
  kernel_init: Callable[[PRNGKey, Shape, Dtype], Array] = default_kernel_init
  bias_init: Callable[[PRNGKey, Shape, Dtype], Array] = zeros
  manifold_class:Any = euclidean_jax
  weight_var_transfer:Any = weight_var_transfer
  manifold_args: Dict[str, int] = field(default_factory=dict)


#   def __init__(self,
#                 features: int,
#   use_bias: bool = True,
#   dtype: Optional[Dtype] = None,
#   param_dtype: Dtype = jnp.float32,
#   precision: PrecisionLike = None,
#   kernel_init: Callable[[PRNGKey, Shape, Dtype], Array] = default_kernel_init,
#   bias_init: Callable[[PRNGKey, Shape, Dtype], Array] = zeros,
#   manifold_class = euclidean_jax,
#   weight_var_transfer_tmp = weight_var_transfer,
#   manifold_args = {}):
#     self.features = features
#     self.use_bias = use_bias
#     self.dtype = dtype
#     self.param_dtype = param_dtype
#     self.precision = precision
#     self.kernel_init = kernel_init
#     self.bias_init = bias_init
#     self.manifold_class = manifold_class
#     self.weight_var_transfer_tmp = weight_var_transfer_tmp
#     self.manifold_args = manifold_args


  @compact
  def __call__(self, inputs: Array) -> Array:
    """Applies a linear transformation to the inputs along the last dimension.

    Args:
      inputs: The nd-array to be transformed.

    Returns:
      The transformed input.
    """
    kernel = self.param('kernel',
                        self.kernel_init,
                        (jnp.shape(inputs)[-1], self.features),
                        self.param_dtype)
    if self.use_bias:
      bias = self.param('bias', self.bias_init, (self.features,),
                        self.param_dtype)
    else:
      bias = None
    inputs, kernel, bias = promote_dtype(inputs, kernel, bias, dtype=self.dtype)
    
#     print(kernel.shape)
    weight_to_var, var_to_weight, var_shape = self.weight_var_transfer(kernel.shape)
    manifold = self.manifold_class(var_shape, train_mode = True, **self.manifold_args)
    
    A = lambda kernel : var_to_weight( manifold.A(weight_to_var(kernel)))
    C = lambda kernel : manifold.C(weight_to_var(kernel))
    quad_penalty = jnp.sum( C(kernel) **2  )

    # kernel = var_to_weight( manifold.Init_point(Xinit = weight_to_var(kernel)))
#     self.quad_penalty = lambda kernel: manifold.C_quad_penalty(weight_to_var(kernel))

    y = lax.dot_general(inputs, A(kernel),
                        (((inputs.ndim - 1,), (0,)), ((), ())),
                        precision=self.precision)
    if bias is not None:
      y += jnp.reshape(bias, (1,) * (y.ndim - 1) + (-1,))
    return y, quad_penalty






def _conv_dimension_numbers(input_shape):
  """Computes the dimension numbers based on the input shape."""
  ndim = len(input_shape)
  lhs_spec = (0, ndim - 1) + tuple(range(1, ndim - 1))
  rhs_spec = (ndim - 1, ndim - 2) + tuple(range(0, ndim - 2))
  out_spec = lhs_spec
  return lax.ConvDimensionNumbers(lhs_spec, rhs_spec, out_spec)


PaddingLike = Union[str, int, Sequence[Union[int, Tuple[int, int]]]]
LaxPadding = Union[str, Sequence[Tuple[int, int]]]


def canonicalize_padding(padding: PaddingLike, rank: int) -> LaxPadding:
  """"Canonicalizes conv padding to a jax.lax supported format."""
  if isinstance(padding, str):
    return padding
  if isinstance(padding, int):
    return [(padding, padding)] * rank
  if isinstance(padding, Sequence) and len(padding) == rank:
    new_pad = []
    for p in padding:
      if isinstance(p, int):
        new_pad.append((p, p))
      elif isinstance(p, tuple) and len(p) == 2:
        new_pad.append(p)
      else:
        break
    if len(new_pad) == rank:
      return new_pad
  raise ValueError(
    f'Invalid padding format: {padding}, should be str, int,'
    f' or a sequence of len {rank} where each element is an'
    f' int or pair of ints.')


def weight_var_transfer_conv(tensor_shape):
  '''
  untested
  '''
  var_shape = (np.prod( np.array(tensor_shape[:-1])) , tensor_shape[-1])
#   var_shape = tensor_shape
#   print(var_shape)
  weight_to_var = lambda X_tensor: jnp.reshape(X_tensor, var_shape)
  var_to_weight = lambda X_var: jnp.reshape(X_var, tensor_shape)
  return weight_to_var, var_to_weight, var_shape

class _Conv_cdopt(Module):
  features: int
  kernel_size: Sequence[int]
  strides: Union[None, int, Sequence[int]] = 1
  padding: PaddingLike = 'SAME'
  input_dilation: Union[None, int, Sequence[int]] = 1
  kernel_dilation: Union[None, int, Sequence[int]] = 1
  feature_group_count: int = 1
  use_bias: bool = True
  mask: Optional[Array] = None
  dtype: Optional[Dtype] = None
  param_dtype: Dtype = jnp.float32
  precision: PrecisionLike = None
  kernel_init: Callable[[PRNGKey, Shape, Dtype], Array] = default_kernel_init
  bias_init: Callable[[PRNGKey, Shape, Dtype], Array] = zeros  
  manifold_class:Any = euclidean_jax
  weight_var_transfer:Any = wvt_conv_flatten
  manifold_args: Dict[str, int] = field(default_factory=dict)
    
  @property
  def shared_weights(self) -> bool:
    """Defines whether weights are shared or not between different pixels.

    Returns:
      `True` to use shared weights in convolution (regular convolution).
      `False` to use different weights at different pixels, a.k.a.
      "locally connected layer", "unshared convolution", or "local convolution".

    """
    ...

  @compact
  def __call__(self, inputs: Array) -> Array:
    """Applies a (potentially unshared) convolution to the inputs.

    Args:
      inputs: input data with dimensions (batch, spatial_dims..., features).
        This is the channels-last convention, i.e. NHWC for a 2d convolution
        and NDHWC for a 3D convolution. Note: this is different from the input
        convention used by `lax.conv_general_dilated`, which puts the spatial
        dimensions last.

    Returns:
      The convolved data.
    """

    if isinstance(self.kernel_size, int):
      raise TypeError('Expected Conv kernel_size to be a'
                      ' tuple/list of integers (eg.: [3, 3]) but got'
                      f' {self.kernel_size}.')
    else:
      kernel_size = tuple(self.kernel_size)

    def maybe_broadcast(x: Optional[Union[int, Sequence[int]]]) -> (
        Tuple[int, ...]):
      if x is None:
        # backward compatibility with using None as sentinel for
        # broadcast 1
        x = 1
      if isinstance(x, int):
        return (x,) * len(kernel_size)
      return tuple(x)

    is_single_input = False
    if inputs.ndim == len(kernel_size) + 1:
      is_single_input = True
      inputs = jnp.expand_dims(inputs, axis=0)

    # self.strides or (1,) * (inputs.ndim - 2)
    strides = maybe_broadcast(self.strides)
    input_dilation = maybe_broadcast(self.input_dilation)
    kernel_dilation = maybe_broadcast(self.kernel_dilation)

    padding_lax = canonicalize_padding(self.padding, len(kernel_size))
    if padding_lax == 'CIRCULAR':
      kernel_size_dilated = [
          (k - 1) * d + 1 for k, d in zip(kernel_size, kernel_dilation)
      ]
      zero_pad: List[Tuple[int, int]] = [(0, 0)]
      pads = (zero_pad + [((k - 1) // 2, k // 2) for k in kernel_size_dilated] +
              [(0, 0)])
      inputs = jnp.pad(inputs, pads, mode='wrap')
      padding_lax = 'VALID'
    elif padding_lax == 'CAUSAL':
      if len(kernel_size) != 1:
        raise ValueError(
            'Causal padding is only implemented for 1D convolutions.')
      left_pad = kernel_dilation[0] * (kernel_size[0] - 1)
      pads = [(0, 0), (left_pad, 0), (0, 0)]
      inputs = jnp.pad(inputs, pads)
      padding_lax = 'VALID'

    dimension_numbers = _conv_dimension_numbers(inputs.shape)
    in_features = jnp.shape(inputs)[-1]

    if self.shared_weights:
      # One shared convolutional kernel for all pixels in the output.
      assert in_features % self.feature_group_count == 0
      kernel_shape = kernel_size + (
          in_features // self.feature_group_count, self.features)

    else:
      if self.feature_group_count != 1:
        raise NotImplementedError(
            f'`lax.conv_general_dilated_local` does not support '
            f'`feature_group_count != 1`, got `{self.feature_group_count}`.'
        )

      # Need to know the spatial output shape of a standard convolution to
      # create the unshared convolution kernel.
      conv_output_shape = eval_shape(
          lambda lhs, rhs: lax.conv_general_dilated(  # pylint: disable=g-long-lambda
              lhs=lhs,
              rhs=rhs,
              window_strides=strides,
              padding=padding_lax,
              dimension_numbers=dimension_numbers,
              lhs_dilation=input_dilation,
              rhs_dilation=kernel_dilation,
          ),
          inputs,
          ShapedArray(kernel_size + (in_features, self.features), inputs.dtype)
      ).shape

      # One (unshared) convolutional kernel per each pixel in the output.
      kernel_shape = conv_output_shape[1:-1] + (np.prod(kernel_size) *
                                                in_features, self.features)

    if self.mask is not None and self.mask.shape != kernel_shape:
      raise ValueError('Mask needs to have the same shape as weights. '
                       f'Shapes are: {self.mask.shape}, {kernel_shape}')

    kernel = self.param('kernel', self.kernel_init, kernel_shape,
                        self.param_dtype)

    if self.mask is not None:
      kernel *= self.mask

    if self.use_bias:
      if self.shared_weights:
        # One bias weight per output channel, shared between pixels.
        bias_shape = (self.features,)
      else:
        # One bias weight per output entry, unshared betwen pixels.
        bias_shape = conv_output_shape[1:]

      bias = self.param('bias', self.bias_init, bias_shape, self.param_dtype)
    else:
      bias = None

    inputs, kernel, bias = promote_dtype(inputs, kernel, bias, dtype=self.dtype)
    
    weight_to_var, var_to_weight, var_shape = self.weight_var_transfer(kernel.shape)
    manifold = self.manifold_class(var_shape, train_mode = True, **self.manifold_args)
    
    A = lambda kernel : var_to_weight( manifold.A(weight_to_var(kernel)))
    C = lambda kernel : manifold.C(weight_to_var(kernel))
    quad_penalty = jnp.sum( C(kernel) **2  )
    # kernel = var_to_weight( manifold.Init_point(Xinit = weight_to_var(kernel)))
    
    if self.shared_weights:
      y = lax.conv_general_dilated(
          inputs,
          A(kernel),
          strides,
          padding_lax,
          lhs_dilation=input_dilation,
          rhs_dilation=kernel_dilation,
          dimension_numbers=dimension_numbers,
          feature_group_count=self.feature_group_count,
          precision=self.precision
      )
    else:
      y = lax.conv_general_dilated_local(
          lhs=inputs,
          rhs=A(kernel),
          window_strides=strides,
          padding=padding_lax,
          filter_shape=kernel_size,
          lhs_dilation=input_dilation,
          rhs_dilation=kernel_dilation,
          dimension_numbers=dimension_numbers,
          precision=self.precision
      )

    if self.use_bias:
      bias = bias.reshape((1,) * (y.ndim - bias.ndim) + bias.shape)
      y += bias

    if is_single_input:
      y = jnp.squeeze(y, axis=0)
    return y, quad_penalty


class Conv_cdopt(_Conv_cdopt):
  """Convolution Module wrapping `lax.conv_general_dilated`."""

  @property
  def shared_weights(self) -> bool:
    return True


class ConvLocal_cdopt(_Conv_cdopt):
  """Local convolution Module wrapping `lax.conv_general_dilated_local`."""

  @property
  def shared_weights(self) -> bool:
    return False



class ConvTranspose_cdopt(Module):
  features: int
  kernel_size: Union[int, Tuple[int, ...]]
  strides: Optional[Tuple[int, ...]] = None
  padding: PaddingLike = 'SAME'
  kernel_dilation: Optional[Sequence[int]] = None
  use_bias: bool = True
  mask: Optional[Array] = None
  dtype: Dtype = None
  param_dtype: Dtype = jnp.float32
  precision: PrecisionLike = None
  kernel_init: Callable[[PRNGKey, Shape, Dtype], Array] = default_kernel_init
  bias_init: Callable[[PRNGKey, Shape, Dtype], Array] = zeros
  manifold_class:Any = euclidean_jax
  weight_var_transfer:Any = wvt_conv_flatten_transp
  manifold_args: Dict[str, int] = field(default_factory=dict)

  @compact
  def __call__(self, inputs: Array) -> Array:
    """Applies a transposed convolution to the inputs.

    Behaviour mirrors of `jax.lax.conv_transpose`.

    Args:
      inputs: input data with dimensions (batch, spatial_dims..., features).
        This is the channels-last convention, i.e. NHWC for a 2d convolution
        and NDHWC for a 3D convolution. Note: this is different from the input
        convention used by `lax.conv_general_dilated`, which puts the spatial
        dimensions last.

    Returns:
      The convolved data.
    """
    kernel_size: Tuple[int, ...]
    if isinstance(self.kernel_size, int):
      kernel_size = (self.kernel_size,)
    else:
      kernel_size = self.kernel_size

    is_single_input = False
    if inputs.ndim == len(kernel_size) + 1:
      is_single_input = True
      inputs = jnp.expand_dims(inputs, axis=0)

    strides: Tuple[int, ...]
    strides = self.strides or (1,) * (inputs.ndim - 2)

    in_features = jnp.shape(inputs)[-1]
    kernel_shape = kernel_size + (in_features, self.features)

    if self.mask is not None and self.mask.shape != kernel_shape:
      raise ValueError('Mask needs to have the same shape as weights. '
                       f'Shapes are: {self.mask.shape}, {kernel_shape}')

    kernel = self.param('kernel', self.kernel_init, kernel_shape,
                        self.param_dtype)

    if self.mask is not None:
      kernel *= self.mask

    padding_lax = canonicalize_padding(self.padding, len(kernel_size))
    if padding_lax == 'CIRCULAR':
      padding_lax = 'VALID'

    if self.use_bias:
      bias = self.param('bias', self.bias_init, (self.features,),
                        self.param_dtype)
    else:
      bias = None

    inputs, kernel, bias = promote_dtype(inputs, kernel, bias,
                                         dtype=self.dtype)

    weight_to_var, var_to_weight, var_shape = self.weight_var_transfer(kernel.shape)
    manifold = self.manifold_class(var_shape, train_mode = True, **self.manifold_args)
    
    A = lambda kernel : var_to_weight( manifold.A(weight_to_var(kernel)))
    C = lambda kernel : manifold.C(weight_to_var(kernel))
    quad_penalty = jnp.sum( C(kernel) **2  )
    # kernel = var_to_weight( manifold.Init_point(Xinit = weight_to_var(kernel)))
    y = lax.conv_transpose(
        inputs,
        A(kernel),
        strides,
        padding_lax,
        rhs_dilation=self.kernel_dilation,
        precision=self.precision)

    if self.padding == 'CIRCULAR':
      # For circular padding, we need to identify the size of the final output
      # ("period") along each spatial dimension, pad each dimension to an
      # integer number of periods, and wrap the array periodically around each
      # dimension. Padding should be done in such a way that the start of the
      # original input data inside the padded array is located at integer
      # number of periods - otherwise the result would be circularly shifted.

      # Compute period along each spatial dimension - it's input size scaled
      # by the stride.
      scaled_x_dims = [
          x_dim * stride for x_dim, stride in zip(jnp.shape(inputs)[1:-1], strides)
      ]
      # Compute difference between the current size of y and the final output
      # size, and complement this difference to 2 * period - that gives how
      # much we need to pad.
      size_diffs = [
          -(y_dim - x_dim) % (2 * x_dim)
          for y_dim, x_dim in zip(y.shape[1:-1], scaled_x_dims)
      ]
      # Divide the padding equaly between left and right. The choice to put
      # "+1" on the left (and not on the right) represents a convention for
      # aligning even-sized kernels.
      total_pad = [
          ((size_diff + 1) // 2, size_diff // 2) for size_diff in size_diffs
      ]
      y = np.pad(y, [(0, 0)] + total_pad + [(0, 0)])
      # Wrap the result periodically around each spatial dimension,
      # one by one.
      for i in range(1, y.ndim - 1):
        y = y.reshape(y.shape[:i] + (-1, scaled_x_dims[i - 1]) +
                      y.shape[i + 1:])
        y = y.sum(axis=i)

    if is_single_input:
      y = jnp.squeeze(y, axis=0)
    if self.use_bias:
      y += jnp.reshape(bias, (1,) * (y.ndim - 1) + (-1,))
    return y, quad_penalty