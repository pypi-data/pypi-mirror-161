import abc
import numpy as np 
import scipy as sp 
import jax 
import jax.numpy as jnp 
from cdopt.manifold import basic_manifold
from jax import random
from ..manifold_jax import complex_basic_manifold_jax


class complex_oblique_jax(complex_basic_manifold_jax):
    def __init__(self, var_shape, device = None):
        
        self.dim = var_shape[:-1]
        self._p = var_shape[-1]

        super().__init__('oblique',var_shape, (*self.dim,1 ), device = device )

    


    # def array2tensor(self, X_array):
    #     dim = len(X_array)
    #     X_real = torch.as_tensor(X_array[:int(dim/2)])
    #     X_imag = torch.as_tensor(X_array[int(dim/2):])
    #     X =  torch.complex(X_real, X_imag).to(device=self.device, dtype=self.dtype)
    #     X.requires_grad = True 
    #     return X 


    # def tensor2array(self, X_tensor, np_dtype = np.float64):
    #     X_real = X_tensor.real.detach().cpu().numpy()
    #     X_imag = X_tensor.imag.detach().cpu().numpy()

    #     return np.concatenate((np_dtype(X_real), np_dtype(X_imag)) )



    def A(self, X):
        X_rvec = jnp.sum( X * X.conj(), -1, keepdims=True )
        return (2*X)/( 1 + X_rvec )


    def JA(self, X, G):
        XG = jnp.sum(X*G.conj(), -1, keepdims=True).real
        X_rvec = jnp.sum( X* X.conj() , -1, keepdims=True).real +1
        return (2*G - ( (4*XG)*X )/X_rvec )/X_rvec


    def hessA(self, X, gradf, D):
        XG = jnp.sum(X * gradf.conj(), -1, keepdims=True).real 
        XD = jnp.sum(X * D.conj(), -1, keepdims=True).real
        GD = jnp.sum(gradf * D.conj(), -1, keepdims=True).real
        X_rvec = jnp.sum( X * X.conj() , -1, keepdims=True ) +1
        
        return -(4/(X_rvec**2))*( gradf * XD + D * XG + X * GD ) + 16/( X_rvec**3 ) * (X * XG * XD)



    # def C_quad_penalty(self, X):
    #     CX = self.C(X)
    #     return torch.sum( CX * CX.conj()  )

    # def Feas_eval(self, X):
    #     return torch.sqrt(self.C_quad_penalty(X)).real



    def C(self, X):
        return jnp.sum( X * X.conj(), -1, keepdims=True ) - 1

    def JC(self, X, Lambda):
        return 2*X * Lambda.real

    def hess_feas(self, X, D):
        return 2 * D * self.C(X) + 4 * X * jnp.sum(X*D.conj(), -1, keepdims= True).real



    def Init_point(self, Xinit = None):
        Xinit = super().Init_point(Xinit = Xinit)
        
        X_rvec = jnp.sqrt(jnp.sum( Xinit * Xinit.conj(), -1, keepdims= True ))
        Xinit = Xinit / X_rvec
        Xinit = jax.device_put(Xinit, self.device)
        return Xinit

    def Post_process(self,X):
        X_rvec = jnp.sqrt(jnp.sum( X * X.conj(), -1, keepdims= True ))
        X = X / X_rvec
        return X

    