import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import warnings

from torch import Tensor
import torch
from torch.nn import Parameter, init, UninitializedParameter
from torch.nn.modules.lazy import LazyModuleMixin

from cdopt.manifold_torch import euclidean_torch
from ..utils.modified_apply import modified_apply
from .utils import wvt_identical, wvt_transp




class Linear_cdopt(nn.Module):
    
    __constants__ = ['in_features', 'out_features']
    in_features: int
    out_features: int
    weight: Tensor

    def __init__(self, in_features: int, out_features: int, bias: bool = True,
                 device=None, dtype=None, manifold_class = euclidean_torch, penalty_param = 0, manifold_args = {}) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        super(Linear_cdopt, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.manifold_class = manifold_class
        self.manifold_args = manifold_args
        self.penalty_param = penalty_param

        if self.in_features >= self.out_features:
            self.manifold = manifold_class((self.in_features, self.out_features), device= device, dtype= dtype, **manifold_args)
            self.A = lambda weight: self.manifold.A(weight.T).T
            self.C = lambda weight: self.manifold.C(weight.T).T
        else:
            self.manifold = manifold_class((self.out_features, self.in_features), device= device, dtype= dtype, **manifold_args)
            self.A = self.manifold.A
            self.C = self.manifold.C

        
        
        for key, param in self.manifold._parameters.items():
            self._parameters[key] = param



        self.weight = Parameter(torch.empty((out_features, in_features), **factory_kwargs))
        if bias:
            self.bias = Parameter(torch.empty(out_features, **factory_kwargs))
        else:
            self.register_parameter('bias', None)

        self.feasibility = lambda : torch.linalg.norm(self.C(self.weight).flatten())
        self.quad_penalty = lambda : torch.sum(self.C(self.weight)**2)

        self.reset_parameters()

    def reset_parameters(self) -> None:
        # Setting a=sqrt(5) in kaiming_uniform is the same as initializing with
        # uniform(-1/sqrt(in_features), 1/sqrt(in_features)). For details, see
        # https://github.com/pytorch/pytorch/issues/57109
        init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.in_features >= self.out_features:
            self.weight = Parameter(self.manifold.Init_point(self.weight.T).T)
        else:
            self.weight = Parameter(self.manifold.Init_point(self.weight))
        
        if self.bias is not None:
            fan_in, _ = init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in) if fan_in > 0 else 0
            init.uniform_(self.bias, -bound, bound)

    def reset_manifolds(self) -> None:
        if self.in_features >= self.out_features:
            self.manifold = self.manifold_class((self.in_features, self.out_features), device = self.weight.data.device ,dtype = self.weight.data.dtype, **self.manifold_args)
            self.A = lambda weight: self.manifold.A(weight.T).T
            self.C = lambda weight: self.manifold.C(weight.T).T
        else:
            self.manifold = self.manifold_class((self.out_features, self.in_features), device = self.weight.data.device ,dtype = self.weight.data.dtype, **self.manifold_args)
            self.A = self.manifold.A
            self.C = self.manifold.C

        
        
        for key, param in self.manifold._parameters.items():
            self.register_buffer(key, param, persistent=False)



        self.weight = Parameter(torch.empty((self.out_features, self.in_features), device = self.weight.data.device ,dtype = self.weight.data.dtype,))
        if self.bias is not None:
            self.bias = Parameter(torch.empty(self.out_features, device = self.weight.data.device ,dtype = self.weight.data.dtype,))
        else:
            self.register_parameter('bias', None)

        self.feasibility = lambda : torch.linalg.norm(self.C(self.weight).flatten())
        self.quad_penalty = lambda :  torch.sum(self.C(self.weight)**2)

    def forward(self, input: Tensor) -> Tensor:
        return F.linear(input, self.A(self.weight), self.bias)

    def extra_repr(self) -> str:
        return 'in_features={}, out_features={}, bias={}'.format(
            self.in_features, self.out_features, self.bias is not None
        )


    def _apply(self, fn):
        return modified_apply(self, fn)



class Bilinear_cdopt(nn.Module):
    __constants__ = ['in1_features', 'in2_features', 'out_features']
    in1_features: int
    in2_features: int
    out_features: int
    weight: Tensor

    def __init__(self, in1_features: int, in2_features: int, out_features: int, bias: bool = True, 
                 device=None, dtype=None, manifold_class = euclidean_torch,penalty_param = 0, weight_var_transfer = None, manifold_args = {}) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        super(Bilinear_cdopt, self).__init__()
        self.in1_features = in1_features
        self.in2_features = in2_features
        self.out_features = out_features

        self.manifold_args = manifold_args
        self.penalty_param = penalty_param


        if weight_var_transfer is None:

            def weight_var_transfer(tensor_shape):
                in_feature_total = self.in1_features * self.in2_features
                out_feature_total = self.out_features

                if in_feature_total >= out_feature_total:
                    var_shape = (in_feature_total, out_feature_total)
                    weight_to_var = lambda X_tensor: torch.reshape(X_tensor, var_shape)
                    var_to_weight = lambda X_var: torch.reshape(X_var, tensor_shape)
                else:
                    var_shape = (out_feature_total, in_feature_total)
                    var_transp_shape = (in_feature_total, out_feature_total)
                    weight_to_var = lambda X_tensor: torch.reshape(X_tensor, var_transp_shape).T 
                    var_to_weight = lambda X_var: torch.reshape( X_var.T, tensor_shape )

                return weight_to_var, var_to_weight, var_shape
        

        self.weight_to_var, self.var_to_weight, self.var_shape = weight_var_transfer( (self.out_features, self.in1_features, self.in2_features) )



        self.manifold = manifold_class(self.var_shape , device= device, dtype= dtype, **manifold_args)
        self.A = lambda weight: self.var_to_weight( self.manifold.A( self.weight_to_var(weight) )  )
        self.C = lambda weight: self.var_to_weight( self.manifold.C( self.weight_to_var(weight) )  )

        for key, param in self.manifold._parameters.items():
            self.register_buffer(key, param, persistent=False)
    

        self.weight = Parameter(torch.empty((out_features, in1_features, in2_features), **factory_kwargs))


        self.feasibility = lambda : torch.linalg.norm(self.C(self.weight).flatten())
        self.quad_penalty = lambda : torch.sum(self.C(self.weight)**2)

        if bias:
            self.bias = Parameter(torch.empty(out_features, **factory_kwargs))
        else:
            self.register_parameter('bias', None)
        self.reset_parameters()

    def reset_parameters(self) -> None:
        bound = 1 / math.sqrt(self.weight.size(1))
        init.uniform_(self.weight, -bound, bound)


        self.weight = Parameter(  self.var_to_weight( self.manifold.Init_point( self.weight_to_var(self.weight) ) )  )



        if self.bias is not None:
            init.uniform_(self.bias, -bound, bound)

    def forward(self, input1: Tensor, input2: Tensor) -> Tensor:
        return F.bilinear(input1, input2, self.A(self.weight), self.bias)

    def extra_repr(self) -> str:
        return 'in1_features={}, in2_features={}, out_features={}, bias={}'.format(
            self.in1_features, self.in2_features, self.out_features, self.bias is not None
        )

    def _apply(self, fn):
        return modified_apply(self, fn)


class LazyLinear_cdopt(LazyModuleMixin, Linear_cdopt):

    cls_to_become = Linear_cdopt  # type: ignore[assignment]
    weight: UninitializedParameter
    bias: UninitializedParameter  # type: ignore[assignment]

    def __init__(self, out_features: int, bias: bool = True,
                 device=None, dtype=None, manifold_class = euclidean_torch, penalty_param = 0, manifold_args = {}) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        # bias is hardcoded to False to avoid creating tensor
        # that will soon be overwritten.
        super().__init__(0, 0, False, manifold_class = manifold_class, penalty_param = penalty_param, manifold_args = manifold_args)
        self.weight = UninitializedParameter(**factory_kwargs)
        self.out_features = out_features
        if bias:
            self.bias = UninitializedParameter(**factory_kwargs)

    def reset_parameters(self) -> None:
        if not self.has_uninitialized_params() and self.in_features != 0:

            super().reset_parameters()

    def initialize_parameters(self, input) -> None:  # type: ignore[override]
        if self.has_uninitialized_params():
            with torch.no_grad():
                self.in_features = input.shape[-1]
                self.weight.materialize((self.out_features, self.in_features))
                if self.bias is not None:
                    self.bias.materialize((self.out_features,))
                
                super().reset_manifolds()    
                self.reset_parameters()



                