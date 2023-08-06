import torch 

def get_quad_penalty(local_module: torch.nn.Module):
    if hasattr(local_module, 'quad_penalty'):
        quad_all = local_module.penalty_param * local_module.quad_penalty()
        
    else:
        quad_all = 0

    for child in local_module.children():
        quad_all += get_quad_penalty(child)

    return quad_all



def wvt_flatten2d(tensor_shape):
    tensor_shape_ref = (tensor_shape[1], tensor_shape[0], *tensor_shape[2:]  )
    var_shape = (torch.prod(torch.tensor( tensor_shape_ref[1:] )), torch.tensor(tensor_shape_ref[0]))
    var_shape_ref = (var_shape[1], var_shape[0])
    
    # var_shape_transp = ( torch.tensor(tensor_shape[0]), torch.prod(torch.tensor(tensor_shape[1:])))
    weight_to_var = lambda X_tensor : torch.reshape(X_tensor.transpose(0,1), var_shape_ref).T
    var_to_weight = lambda X_var: torch.reshape(X_var.T, tensor_shape_ref).transpose(0,1)
    return weight_to_var, var_to_weight, var_shape


def wvt_flatten2d_transp(tensor_shape):
    var_shape = (torch.prod(torch.tensor( tensor_shape[1:] )), torch.tensor(tensor_shape[0]))
    var_shape_ref = (var_shape[1], var_shape[0])
    
    # var_shape_transp = ( torch.tensor(tensor_shape[0]), torch.prod(torch.tensor(tensor_shape[1:])))
    weight_to_var = lambda X_tensor : torch.reshape(X_tensor, var_shape_ref).T
    var_to_weight = lambda X_var: torch.reshape(X_var.T, tensor_shape)
    return weight_to_var, var_to_weight, var_shape


def wvt_identical(tensor_shape):
    var_shape = tensor_shape
    weight_to_var = lambda X_tensor : X_tensor
    var_to_weight = lambda X_var: X_var 
    return weight_to_var, var_to_weight, var_shape