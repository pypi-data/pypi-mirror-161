import torch
import torch.nn as nn
import torch.nn.functional as F

from torch import Tensor
from torch.nn import Module, Parameter, init, UninitializedParameter
from ...manifold import basic_manifold
from ...manifold_torch import euclidean_torch
import torch.nn.utils.parametrize as P
from ...nn.modules.utils import wvt_transp, wvt_identical, wvt_flatten2d, wvt_flatten2d_transp
from .modified_apply import modified_apply
import types

def set_constraint_dissolving(module: Module, attr_name:str, manifold_class:basic_manifold = euclidean_torch, weight_var_transfer = None, manifold_args = {}, penalty_param = 0):
    weight = getattr(module, attr_name)
#     print(weight.size())

    weight_size=  weight.size()
    if len(weight_size) == 1:
        weight_var_transfer = wvt_identical
    elif len(weight_size) == 2:
        if weight_size[0] >= weight_size[1]:
            weight_var_transfer = wvt_identical
        else: 
            weight_var_transfer = wvt_transp
    else:
        if 'Transpose' in module._get_name():
            weight_var_transfer = wvt_flatten2d_transp
        else:
            weight_var_transfer = wvt_flatten2d

    weight_to_var, var_to_weight, var_shape = weight_var_transfer(weight.size())
    # A = lambda X_tensor: var_to_weight(manifold.A( weight_to_var(X_tensor) ))

    if 'dtype' not in manifold_args.keys():
        manifold_args['dtype'] = torch.float32
    manifold = manifold_class(var_shape, **manifold_args)
    
    

    setattr(module, attr_name,  Parameter(var_to_weight(manifold.Init_point(Xinit = weight_to_var(weight)))) )

    A = lambda X_tensor: var_to_weight(manifold.A( X_tensor ))
    C = lambda X_tensor: manifold.C( X_tensor )

    

    class manifold_module(nn.Module):
        def forward(self, X):
            return A(X)

        def right_inverse(self, AX):
            return weight_to_var(AX)

    P.register_parametrization(module, attr_name, manifold_module())
    

    setattr(module.parametrizations[attr_name],'manifold', manifold)
    setattr(module.parametrizations[attr_name], 'A', lambda X_tensor: A(X_tensor))
    setattr(module.parametrizations[attr_name], 'C', lambda X_tensor: C(X_tensor))

    # module.parametrizations[attr_name]._apply = my_modified_module._apply
    module.parametrizations[attr_name]._apply = types.MethodType(modified_apply, module.parametrizations[attr_name])

    for key, param in module.parametrizations[attr_name].manifold._parameters.items():
        module.parametrizations[attr_name].register_buffer(key, param, persistent = False)
        # module.parametrizations[attr_name]._buffers[key] = param

    # module.parametrizations[attr_name]._buffers.update(module.parametrizations[attr_name].manifold._parameters)
    
    setattr(module.parametrizations[attr_name], 'penalty_param', penalty_param)
    setattr(module.parametrizations[attr_name], 'feasibility', lambda : torch.linalg.norm( C(module.parametrizations.weight.original).flatten() ))
    setattr(module.parametrizations[attr_name], 'quad_penalty', lambda : torch.sum( C(module.parametrizations.weight.original) **2 ))