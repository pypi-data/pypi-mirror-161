import math
import warnings

import torch
import torch.nn as nn
import torch.nn.functional as F

from torch import Tensor
import torch
from torch.nn import Parameter, init, UninitializedParameter
from torch.nn.modules.lazy import LazyModuleMixin


from ...manifold_torch import euclidean_torch

from typing import Optional, List, Tuple, Union
from torch.nn.modules.utils import _single, _pair, _triple, _reverse_repeat_tuple
# from torch._torch_docs import reproducibility_notes
from torch.nn.common_types import _size_1_t, _size_2_t, _size_3_t

from ..utils.modified_apply import modified_apply


def wvt_conv_flatten(tensor_shape):
    tensor_shape_ref = (tensor_shape[1], tensor_shape[0], *tensor_shape[2:]  )
    var_shape = (torch.prod(torch.tensor( tensor_shape_ref[1:] )), torch.tensor(tensor_shape_ref[0]))
    var_shape_ref = (var_shape[1], var_shape[0])
    
    # var_shape_transp = ( torch.tensor(tensor_shape[0]), torch.prod(torch.tensor(tensor_shape[1:])))
    weight_to_var = lambda X_tensor : torch.reshape(X_tensor.transpose(0,1), var_shape_ref).T
    var_to_weight = lambda X_var: torch.reshape(X_var.T, tensor_shape_ref).transpose(0,1)
    return weight_to_var, var_to_weight, var_shape


def wvt_conv_flatten_transp(tensor_shape):
    var_shape = (torch.prod(torch.tensor( tensor_shape[1:] )), torch.tensor(tensor_shape[0]))
    var_shape_ref = (var_shape[1], var_shape[0])
    
    # var_shape_transp = ( torch.tensor(tensor_shape[0]), torch.prod(torch.tensor(tensor_shape[1:])))
    weight_to_var = lambda X_tensor : torch.reshape(X_tensor, var_shape_ref).T
    var_to_weight = lambda X_var: torch.reshape(X_var.T, tensor_shape)
    return weight_to_var, var_to_weight, var_shape


def wvt_conv_identical(tensor_shape):
    var_shape = tensor_shape
    weight_to_var = lambda X_tensor : X_tensor
    var_to_weight = lambda X_var: X_var 
    return weight_to_var, var_to_weight, var_shape




class _ConvNd_cdopt(nn.Module):

    __constants__ = ['stride', 'padding', 'dilation', 'groups',
                     'padding_mode', 'output_padding', 'in_channels',
                     'out_channels', 'kernel_size']
    __annotations__ = {'bias': Optional[torch.Tensor]}

    def _conv_forward(self, input: Tensor, weight: Tensor, bias: Optional[Tensor]) -> Tensor:
        ...

    _in_channels: int
    _reversed_padding_repeated_twice: List[int]
    out_channels: int
    kernel_size: Tuple[int, ...]
    stride: Tuple[int, ...]
    padding: Union[str, Tuple[int, ...]]
    dilation: Tuple[int, ...]
    transposed: bool
    output_padding: Tuple[int, ...]
    groups: int
    padding_mode: str
    weight: Tensor
    bias: Optional[Tensor]

    def __init__(self,
                 in_channels: int,
                 out_channels: int,
                 kernel_size: Tuple[int, ...],
                 stride: Tuple[int, ...],
                 padding: Tuple[int, ...],
                 dilation: Tuple[int, ...],
                 transposed: bool,
                 output_padding: Tuple[int, ...],
                 groups: int,
                 bias: bool,
                 padding_mode: str,
                 device=None,
                 dtype=None, manifold_class = euclidean_torch, penalty_param = 0, weight_var_transfer = wvt_conv_flatten, manifold_args = {}) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        super(_ConvNd_cdopt, self).__init__()
        if in_channels % groups != 0:
            raise ValueError('in_channels must be divisible by groups')
        if out_channels % groups != 0:
            raise ValueError('out_channels must be divisible by groups')
        valid_padding_strings = {'same', 'valid'}
        if isinstance(padding, str):
            if padding not in valid_padding_strings:
                raise ValueError(
                    "Invalid padding string {!r}, should be one of {}".format(
                        padding, valid_padding_strings))
            if padding == 'same' and any(s != 1 for s in stride):
                raise ValueError("padding='same' is not supported for strided convolutions")

        valid_padding_modes = {'zeros', 'reflect', 'replicate', 'circular'}
        if padding_mode not in valid_padding_modes:
            raise ValueError("padding_mode must be one of {}, but got padding_mode='{}'".format(
                valid_padding_modes, padding_mode))
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation
        self.transposed = transposed
        self.output_padding = output_padding
        self.groups = groups
        self.padding_mode = padding_mode
        self.penalty_param = penalty_param
        # `_reversed_padding_repeated_twice` is the padding to be passed to
        # `F.pad` if needed (e.g., for non-zero padding types that are
        # implemented as two ops: padding + conv). `F.pad` accepts paddings in
        # reverse order than the dimension.
        if isinstance(self.padding, str):
            self._reversed_padding_repeated_twice = [0, 0] * len(kernel_size)
            if padding == 'same':
                for d, k, i in zip(dilation, kernel_size,
                                   range(len(kernel_size) - 1, -1, -1)):
                    total_padding = d * (k - 1)
                    left_pad = total_padding // 2
                    self._reversed_padding_repeated_twice[2 * i] = left_pad
                    self._reversed_padding_repeated_twice[2 * i + 1] = (
                        total_padding - left_pad)
        else:
            self._reversed_padding_repeated_twice = _reverse_repeat_tuple(self.padding, 2)

        if transposed:
            self.weight = Parameter(torch.empty(
                (in_channels, out_channels // groups, *kernel_size), **factory_kwargs))
        else:
            self.weight = Parameter(torch.empty(
                (out_channels, in_channels // groups, *kernel_size), **factory_kwargs))
        if bias:
            self.bias = Parameter(torch.empty(out_channels, **factory_kwargs))
        else:
            self.register_parameter('bias', None)


        # if weight_var_transfer == None:
        #     def weight_var_transfer(tensor_shape):
        #         var_shape = (torch.prod(torch.tensor(tensor_shape[:-1])), torch.tensor(tensor_shape[-1]))
        #         weight_to_var = lambda X_tensor: torch.reshape(X_tensor, var_shape)
        #         var_to_weight = lambda X_var: torch.reshape(X_var, tensor_shape)
        #         return weight_to_var, var_to_weight, var_shape


                
        self.weight_to_var, self.var_to_weight, self.var_shape = weight_var_transfer(self.weight.size())
        
        
        self.manifold = manifold_class(self.var_shape, device=device, dtype= dtype, **manifold_args)
        self.A = lambda X_tensor: self.var_to_weight(self.manifold.A( self.weight_to_var(X_tensor) ))
        self.C = lambda X_tensor: self.manifold.C( self.weight_to_var(X_tensor) )
        self.feasibility = lambda : torch.linalg.norm( self.C(self.weight).flatten() )
        self.quad_penalty = lambda : torch.sum( self.C(self.weight) **2 )
        for key, param in self.manifold._parameters.items():
            # self._parameters[key] = param
            self.register_buffer(key, param, persistent=False)

        self.reset_parameters()

    def reset_parameters(self) -> None:
        # Setting a=sqrt(5) in kaiming_uniform is the same as initializing with
        # uniform(-1/sqrt(k), 1/sqrt(k)), where k = weight.size(1) * prod(*kernel_size)
        # For more details see: https://github.com/pytorch/pytorch/issues/15314#issuecomment-477448573
        init.kaiming_uniform_(self.weight, a=math.sqrt(5))

        self.weight = Parameter(  self.var_to_weight( self.manifold.Init_point( self.weight_to_var(self.weight) ) )  )


        if self.bias is not None:
            fan_in, _ = init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            init.uniform_(self.bias, -bound, bound)

    def extra_repr(self):
        s = ('{in_channels}, {out_channels}, kernel_size={kernel_size}'
             ', stride={stride}')
        if self.padding != (0,) * len(self.padding):
            s += ', padding={padding}'
        if self.dilation != (1,) * len(self.dilation):
            s += ', dilation={dilation}'
        if self.output_padding != (0,) * len(self.output_padding):
            s += ', output_padding={output_padding}'
        if self.groups != 1:
            s += ', groups={groups}'
        if self.bias is None:
            s += ', bias=False'
        if self.padding_mode != 'zeros':
            s += ', padding_mode={padding_mode}'
        return s.format(**self.__dict__)

    def __setstate__(self, state):
        super(_ConvNd_cdopt, self).__setstate__(state)
        if not hasattr(self, 'padding_mode'):
            self.padding_mode = 'zeros'

    def _apply(self, fn):
        return modified_apply(self, fn)
    



class Conv1d_cdopt(_ConvNd_cdopt):

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_1_t,
        stride: _size_1_t = 1,
        padding: Union[str, _size_1_t] = 0,
        dilation: _size_1_t = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = 'zeros',  # TODO: refine this type
        device=None,
        dtype=None, manifold_class = euclidean_torch, penalty_param = 0,  
        weight_var_transfer = wvt_conv_flatten, manifold_args = {}
    ) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        # we create new variables below to make mypy happy since kernel_size has
        # type Union[int, Tuple[int]] and kernel_size_ has type Tuple[int]
        kernel_size_ = _single(kernel_size)
        stride_ = _single(stride)
        padding_ = padding if isinstance(padding, str) else _single(padding)
        dilation_ = _single(dilation)
        super(Conv1d_cdopt, self).__init__(
            in_channels, out_channels, kernel_size_, stride_, padding_, dilation_,
            False, _single(0), groups, bias, padding_mode, **factory_kwargs, 
            manifold_class = manifold_class, penalty_param=penalty_param,  
            weight_var_transfer = weight_var_transfer, manifold_args = manifold_args)



    def _conv_forward(self, input: Tensor, weight: Tensor, bias: Optional[Tensor]):
        if self.padding_mode != 'zeros':
            return F.conv1d(F.pad(input, self._reversed_padding_repeated_twice, mode=self.padding_mode),
                            weight, bias, self.stride,
                            _single(0), self.dilation, self.groups)
        return F.conv1d(input, weight, bias, self.stride,
                        self.padding, self.dilation, self.groups)

    def forward(self, input: Tensor) -> Tensor:
        return self._conv_forward(input, self.A(self.weight), self.bias)




class Conv2d_cdopt(_ConvNd_cdopt):

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_2_t,
        stride: _size_2_t = 1,
        padding: Union[str, _size_2_t] = 0,
        dilation: _size_2_t = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = 'zeros',  # TODO: refine this type
        device=None,
        dtype=None, manifold_class = euclidean_torch, penalty_param = 0, 
        weight_var_transfer = wvt_conv_flatten, manifold_args = {}
    ) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        kernel_size_ = _pair(kernel_size)
        stride_ = _pair(stride)
        padding_ = padding if isinstance(padding, str) else _pair(padding)
        dilation_ = _pair(dilation)
        super(Conv2d_cdopt, self).__init__(
            in_channels, out_channels, kernel_size_, stride_, padding_, dilation_,
            False, _pair(0), groups, bias, padding_mode, **factory_kwargs, 
            manifold_class = manifold_class, penalty_param = penalty_param,  
            weight_var_transfer = weight_var_transfer, manifold_args = manifold_args)

    def _conv_forward(self, input: Tensor, weight: Tensor, bias: Optional[Tensor]):
        if self.padding_mode != 'zeros':
            return F.conv2d(F.pad(input, self._reversed_padding_repeated_twice, mode=self.padding_mode),
                            weight, bias, self.stride,
                            _pair(0), self.dilation, self.groups)
        return F.conv2d(input, weight, bias, self.stride,
                        self.padding, self.dilation, self.groups)

    def forward(self, input: Tensor) -> Tensor:
        return self._conv_forward(input, self.A(self.weight), self.bias)



class Conv3d_cdopt(_ConvNd_cdopt):

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_3_t,
        stride: _size_3_t = 1,
        padding: Union[str, _size_3_t] = 0,
        dilation: _size_3_t = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = 'zeros',
        device=None,
        dtype=None, manifold_class = euclidean_torch, penalty_param = 0, 
        weight_var_transfer = wvt_conv_flatten, manifold_args = {}
    ) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        kernel_size_ = _triple(kernel_size)
        stride_ = _triple(stride)
        padding_ = padding if isinstance(padding, str) else _triple(padding)
        dilation_ = _triple(dilation)
        super(Conv3d_cdopt, self).__init__(
            in_channels, out_channels, kernel_size_, stride_, padding_, dilation_,
            False, _triple(0), groups, bias, padding_mode, **factory_kwargs, 
            manifold_class = manifold_class, penalty_param = penalty_param,  
            weight_var_transfer = weight_var_transfer, manifold_args = manifold_args)

    def _conv_forward(self, input: Tensor, weight: Tensor, bias: Optional[Tensor]):
        if self.padding_mode != "zeros":
            return F.conv3d(
                F.pad(
                    input, self._reversed_padding_repeated_twice, mode=self.padding_mode
                ),
                weight,
                bias,
                self.stride,
                _triple(0),
                self.dilation,
                self.groups,
            )
        return F.conv3d(
            input, weight, bias, self.stride, self.padding, self.dilation, self.groups
        )

    def forward(self, input: Tensor) -> Tensor:
        return self._conv_forward(input, self.A(self.weight), self.bias)




class _ConvTransposeNd_cdopt(_ConvNd_cdopt):
    def __init__(self, in_channels, out_channels, kernel_size, stride,
                 padding, dilation, transposed, output_padding,
                 groups, bias, padding_mode, device=None, dtype=None, 
                 manifold_class = euclidean_torch, penalty_param = 0,  weight_var_transfer = wvt_conv_flatten_transp, manifold_args = {}) -> None:
        if padding_mode != 'zeros':
            raise ValueError('Only "zeros" padding mode is supported for {}'.format(self.__class__.__name__))

        factory_kwargs = {'device': device, 'dtype': dtype}
        super(_ConvTransposeNd_cdopt, self).__init__(
            in_channels, out_channels, kernel_size, stride,
            padding, dilation, transposed, output_padding,
            groups, bias, padding_mode, **factory_kwargs, 
            manifold_class=manifold_class, penalty_param = penalty_param, 
            weight_var_transfer=weight_var_transfer, manifold_args = manifold_args)

    # dilation being an optional parameter is for backwards
    # compatibility
    def _output_padding(self, input: Tensor, output_size: Optional[List[int]],
                        stride: List[int], padding: List[int], kernel_size: List[int],
                        num_spatial_dims: int, dilation: Optional[List[int]] = None) -> List[int]:
        if output_size is None:
            ret = _single(self.output_padding)  # converting to list if was not already
        else:
            has_batch_dim = input.dim() == num_spatial_dims + 2
            num_non_spatial_dims = 2 if has_batch_dim else 1
            if len(output_size) == num_non_spatial_dims + num_spatial_dims:
                output_size = output_size[num_non_spatial_dims:]
            if len(output_size) != num_spatial_dims:
                raise ValueError(
                    "ConvTranspose{}D: for {}D input, output_size must have {} or {} elements (got {})"
                    .format(num_spatial_dims, input.dim(), num_spatial_dims,
                            num_non_spatial_dims + num_spatial_dims, len(output_size)))

            min_sizes = torch.jit.annotate(List[int], [])
            max_sizes = torch.jit.annotate(List[int], [])
            for d in range(num_spatial_dims):
                dim_size = ((input.size(d + num_non_spatial_dims) - 1) * stride[d] -
                            2 * padding[d] +
                            (dilation[d] if dilation is not None else 1) * (kernel_size[d] - 1) + 1)
                min_sizes.append(dim_size)
                max_sizes.append(min_sizes[d] + stride[d] - 1)

            for i in range(len(output_size)):
                size = output_size[i]
                min_size = min_sizes[i]
                max_size = max_sizes[i]
                if size < min_size or size > max_size:
                    raise ValueError((
                        "requested an output size of {}, but valid sizes range "
                        "from {} to {} (for an input of {})").format(
                            output_size, min_sizes, max_sizes, input.size()[2:]))

            res = torch.jit.annotate(List[int], [])
            for d in range(num_spatial_dims):
                res.append(output_size[d] - min_sizes[d])

            ret = res
        return ret



class ConvTranspose1d_cdopt(_ConvTransposeNd_cdopt):
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_1_t,
        stride: _size_1_t = 1,
        padding: _size_1_t = 0,
        output_padding: _size_1_t = 0,
        groups: int = 1,
        bias: bool = True,
        dilation: _size_1_t = 1,
        padding_mode: str = 'zeros',
        device=None,
        dtype=None, manifold_class = euclidean_torch, penalty_param = 0, 
        weight_var_transfer = wvt_conv_flatten_transp, manifold_args = {}
    ) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        kernel_size = _single(kernel_size)
        stride = _single(stride)
        padding = _single(padding)
        dilation = _single(dilation)
        output_padding = _single(output_padding)
        super(ConvTranspose1d_cdopt, self).__init__(
            in_channels, out_channels, kernel_size, stride, padding, dilation,
            True, output_padding, groups, bias, padding_mode, **factory_kwargs, 
            manifold_class=manifold_class, penalty_param = penalty_param, 
            weight_var_transfer=weight_var_transfer, manifold_args = manifold_args)

    def forward(self, input: Tensor, output_size: Optional[List[int]] = None) -> Tensor:
        if self.padding_mode != 'zeros':
            raise ValueError('Only `zeros` padding mode is supported for ConvTranspose1d')

        assert isinstance(self.padding, tuple)
        # One cannot replace List by Tuple or Sequence in "_output_padding" because
        # TorchScript does not support `Sequence[T]` or `Tuple[T, ...]`.
        num_spatial_dims = 1
        output_padding = self._output_padding(
            input, output_size, self.stride, self.padding, self.kernel_size,  # type: ignore[arg-type]
            num_spatial_dims, self.dilation)  # type: ignore[arg-type]
        return F.conv_transpose1d(
            input, self.A(self.weight), self.bias, self.stride, self.padding,
            output_padding, self.groups, self.dilation)



class ConvTranspose2d_cdopt(_ConvTransposeNd_cdopt):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_2_t,
        stride: _size_2_t = 1,
        padding: _size_2_t = 0,
        output_padding: _size_2_t = 0,
        groups: int = 1,
        bias: bool = True,
        dilation: _size_2_t = 1,
        padding_mode: str = 'zeros',
        device=None,
        dtype=None, manifold_class = euclidean_torch, penalty_param = 0, 
        weight_var_transfer = wvt_conv_flatten_transp, manifold_args = {}
    ) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        kernel_size = _pair(kernel_size)
        stride = _pair(stride)
        padding = _pair(padding)
        dilation = _pair(dilation)
        output_padding = _pair(output_padding)
        super(ConvTranspose2d_cdopt, self).__init__(
            in_channels, out_channels, kernel_size, stride, padding, dilation,
            True, output_padding, groups, bias, padding_mode, **factory_kwargs, 
            manifold_class=manifold_class, penalty_param = penalty_param, 
            weight_var_transfer=weight_var_transfer, manifold_args = manifold_args)

    def forward(self, input: Tensor, output_size: Optional[List[int]] = None) -> Tensor:
        if self.padding_mode != 'zeros':
            raise ValueError('Only `zeros` padding mode is supported for ConvTranspose2d')

        assert isinstance(self.padding, tuple)
        # One cannot replace List by Tuple or Sequence in "_output_padding" because
        # TorchScript does not support `Sequence[T]` or `Tuple[T, ...]`.
        num_spatial_dims = 2
        output_padding = self._output_padding(
            input, output_size, self.stride, self.padding, self.kernel_size,  # type: ignore[arg-type]
            num_spatial_dims, self.dilation)  # type: ignore[arg-type]

        return F.conv_transpose2d(
            input, self.A(self.weight), self.bias, self.stride, self.padding,
            output_padding, self.groups, self.dilation)


class ConvTranspose3d_cdopt(_ConvTransposeNd_cdopt):

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: _size_3_t,
        stride: _size_3_t = 1,
        padding: _size_3_t = 0,
        output_padding: _size_3_t = 0,
        groups: int = 1,
        bias: bool = True,
        dilation: _size_3_t = 1,
        padding_mode: str = 'zeros',
        device=None,
        dtype=None, manifold_class = euclidean_torch, penalty_param = 0, 
        weight_var_transfer = wvt_conv_flatten_transp, manifold_args = {}
    ) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        kernel_size = _triple(kernel_size)
        stride = _triple(stride)
        padding = _triple(padding)
        dilation = _triple(dilation)
        output_padding = _triple(output_padding)
        super(ConvTranspose3d_cdopt, self).__init__(
            in_channels, out_channels, kernel_size, stride, padding, dilation,
            True, output_padding, groups, bias, padding_mode, **factory_kwargs, 
            manifold_class=manifold_class, penalty_param = penalty_param, 
            weight_var_transfer=weight_var_transfer, manifold_args= manifold_args)

    def forward(self, input: Tensor, output_size: Optional[List[int]] = None) -> Tensor:
        if self.padding_mode != 'zeros':
            raise ValueError('Only `zeros` padding mode is supported for ConvTranspose3d')

        assert isinstance(self.padding, tuple)
        # One cannot replace List by Tuple or Sequence in "_output_padding" because
        # TorchScript does not support `Sequence[T]` or `Tuple[T, ...]`.
        num_spatial_dims = 3
        output_padding = self._output_padding(
            input, output_size, self.stride, self.padding, self.kernel_size,  # type: ignore[arg-type]
            num_spatial_dims, self.dilation)  # type: ignore[arg-type]

        return F.conv_transpose3d(
            input, self.A(self.weight), self.bias, self.stride, self.padding,
            output_padding, self.groups, self.dilation)


