import abc
import numpy as np 
import scipy as sp 
import jax 
import jax.numpy as jnp 
from cdopt.manifold import basic_manifold, complex_basic_manifold
from jax import random


import functools
from cdopt.core import backbone_jax
from zmq import device
from ..manifold import basic_manifold
class basic_manifold_jax(basic_manifold):
    def __init__(self,name,variable_shape, constraint_shape,  regularize_value = 0.01, safeguard_value = 0, device = None) -> None:
        self.name = name
        self.shape = (variable_shape,) 
        self.var_shape = variable_shape
        self.con_shape = constraint_shape
        self.regularize_value = regularize_value
        self.safeguard_value = safeguard_value
        self.device = device


        
        # self.manifold_type = 'S'
        # self.backbone = 'torch'
        # self.var_type = 'torch'

        # self.Ip = torch.eye()

        
        super().__init__(self.name,self.var_shape, self.con_shape,  backbone = backbone_jax, regularize_value = self.regularize_value, safeguard_value = self.safeguard_value, device = self.device)

        
    

    # In class basic_manifold, only the expression for C(X) is required.
    # Only accepts single blocks of variables. 
    # For multiple blocks of variables, please uses product_manifold class. 
    # The generating graph can be expressed as 
    #  C -> JC -> JC_transpose -> hess_feas ----
    #  |                                        |-> generate_cdf_fun, generate_cdf_grad, generate_cdf_hess
    #  --> A -> JA -> JA_transpose -> hessA ----


    def _raise_not_implemented_error(method):
        """Method decorator which raises a NotImplementedError with some meta
        information about the manifold and method if a decorated method is
        called.
        """
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            raise NotImplementedError(
                "Manifold class '{:s}' provides no implementation for "
                "'{:s}'".format(self._get_class_name(), method.__name__))
        return wrapper



    @_raise_not_implemented_error
    def C(self,X):
        """Returns the expression of the constraints
        """

    # self.constraint_shape = np.shape(self.C(np.random.randn(*self.shape )))


    def v2m(self,x):
        return jnp.reshape(x, self.var_shape)



    def m2v(self,X):
        return X.flatten()



    def Init_point(self, Xinit = None, seed = 0):
        key = random.PRNGKey(seed)
        Xinit = random.normal(key, self.var_shape)
        Xinit = jax.device_put(Xinit, self.device)
        return Xinit





class complex_basic_manifold_jax(complex_basic_manifold):
    def __init__(self,name,variable_shape, constraint_shape,  regularize_value = 0.01, safegurad_value = 0, device = None) -> None:
        self.name = name
        self.shape = (variable_shape,) 
        self.var_shape = variable_shape
        self.con_shape = constraint_shape
        self.regularize_value = regularize_value
        self.safegurad_value = safegurad_value
        self.device = device

        
        # self.manifold_type = 'S'
        # self.backbone = 'torch'
        # self.var_type = 'torch'

        # self.Ip = torch.eye()

        
        super().__init__(self.name,self.var_shape, self.con_shape,  backbone = backbone_jax, regularize_value = self.regularize_value, safegurad_value = self.safegurad_value, device = self.device)

        
    

    # In class basic_manifold, only the expression for C(X) is required.
    # Only accepts single blocks of variables. 
    # For multiple blocks of variables, please uses product_manifold class. 
    # The generating graph can be expressed as 
    #  C -> JC -> JC_transpose -> hess_feas ----
    #  |                                        |-> generate_cdf_fun, generate_cdf_grad, generate_cdf_hess
    #  --> A -> JA -> JA_transpose -> hessA ----


    def _raise_not_implemented_error(method):
        """Method decorator which raises a NotImplementedError with some meta
        information about the manifold and method if a decorated method is
        called.
        """
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            raise NotImplementedError(
                "Manifold class '{:s}' provides no implementation for "
                "'{:s}'".format(self._get_class_name(), method.__name__))
        return wrapper



    @_raise_not_implemented_error
    def C(self,X):
        """Returns the expression of the constraints
        """

    # self.constraint_shape = np.shape(self.C(np.random.randn(*self.shape )))


    def v2m(self,x):
        return jnp.reshape(x, self.var_shape)



    def m2v(self,X):
        return X.flatten()


    def array2tensor(self, X_array):
        dim = len(X_array)
        X_real = X_array[:int(dim/2)]
        X_imag = X_array[int(dim/2):]

        return jnp.asarray(X_real + 1j * X_imag)


    def tensor2array(self, X_tensor, np_dtype = np.float64):
        X_real = X_tensor.real.to_py()
        X_imag = X_tensor.imag.to_py()

        return np.concatenate((np_dtype(X_real), np_dtype(X_imag) ) )




    def Init_point(self, Xinit = None, seed = 0):
        key1 = random.PRNGKey(seed)
        key2, key3 = random.split(key1)
        Xinit_real = random.normal(key1, self.var_shape)
        Xinit_imag = random.normal(key3, self.var_shape)
        Xinit = jax.device_put((Xinit_real + 1j * Xinit_imag), self.device)
        return Xinit
