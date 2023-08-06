import abc
import numpy as np 
import scipy as sp 
import jax 
import jax.numpy as jnp 
from cdopt.manifold import basic_manifold
from jax import random
from ..manifold_jax import complex_basic_manifold_jax


class complex_sphere_jax(complex_basic_manifold_jax):
    def __init__(self, var_shape, device = None):
        
        super().__init__('complex_sphere',var_shape, (1,), device = device)



    def A(self, X):
        return (2*X)/( 1 + jnp.sum( X* X.conj() ) )

    def JA(self, X, G):
        XG = jnp.sum( X*G.conj() ).real
        X_rvec = jnp.sum( X* X.conj() ) +1
        return (2*G - ( (4*XG)*X )/X_rvec )/X_rvec
        

    def JA_transpose(self, X, D):
        return self.JA(X,D) 

    def hessA(self, X, gradf, D):
        XG = jnp.sum(X * gradf.conj()).real 
        XD = jnp.sum(X * D.conj()).real
        GD = jnp.sum(gradf * D.conj()).real
        X_rvec = jnp.sum( X * X.conj()  ) +1
        
        return -(4/(X_rvec**2))*( gradf * XD + D * XG + X * GD ) + 16/( X_rvec**3 ) * (X * XG * XD)


    def C(self, X):
        return jnp.sum( X * X.conj() ) - 1

    def JC(self, X, Lambda):
        return 2*X * Lambda.real

    def hess_feas(self, X, D):
        return 2 * D * self.C(X) + 4 * X * jnp.sum(X*D.conj()).real


    def Init_point(self, Xinit = None, seed = 0):
        if Xinit is None:
            key = random.PRNGKey(seed)
            Xinit_real = random.normal(key, self.var_shape)
            key = random.PRNGKey(seed+1)
            Xinit_imag = random.normal(key, self.var_shape)
            Xinit = Xinit_real + 1j * Xinit_imag
        X_rvec = jnp.sqrt(jnp.sum( Xinit * Xinit ))
        Xinit = Xinit / X_rvec
        Xinit = jax.device_put(Xinit, self.device)
        return Xinit

    def Post_process(self,X):
        X_rvec = jnp.sqrt(jnp.sum( X * X.conj()  ))
        X = X / X_rvec
        return X

    