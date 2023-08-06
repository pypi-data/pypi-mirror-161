import abc
import numpy as np 
import scipy as sp 
import jax 
import jax.numpy as jnp 
from cdopt.manifold import basic_manifold
from jax import random
from ..manifold_jax import complex_basic_manifold_jax


class complex_stiefel_jax(complex_basic_manifold_jax):
    def __init__(self, var_shape, device = None) -> None:
        if len(var_shape) >= 2:
            self._n = var_shape[-2]
            self._p = var_shape[-1]
            self.dim = var_shape[:-2]
        else:
            print("The length of var_shape should be no less than 2.")
            raise TypeError


        super().__init__('Complex Stiefel',var_shape, (*self.dim, self._p,self._p), device=device)
        
        self.Ip = jnp.reshape(jnp.outer(jnp.ones(self.dim), jnp.eye(self._p)),(*self.dim, self._p,self._p))
        self.Ip = jax.device_put(self.Ip, self.device)

        
    # def array2tensor(self, X_array):
    #     dim = len(X_array)
    #     X_real = jnp.as_tensor(X_array[:int(dim/2)])
    #     X_imag = jnp.as_tensor(X_array[int(dim/2):])
    #     X =  jnp.complex(X_real, X_imag).to(device=self.device, dtype=self.dtype)
    #     X.requires_grad = True 
    #     return X 


    # def tensor2array(self, X_tensor, np_dtype = np.float64):
    #     X_real = X_tensor.real.detach().cpu().numpy()
    #     X_imag = X_tensor.imag.detach().cpu().numpy()

    #     return np.concatenate((np_dtype(X_real), np_dtype(X_imag)) )



    def Phi(self, M):
        return (M + M.swapaxes(-2,-1).conj() )/2

    def C(self, X):
        # return X.T @ X - self.Ip.to(device=X.device, dtype = X.dtype)
        return jnp.matmul(X.swapaxes(-2,-1).conj(), X) - self.Ip

    def A(self, X):
        XX = jnp.matmul(X.swapaxes(-2,-1).conj(), X)
        return 1.5 * X - jnp.matmul(X , (XX /2))


    def JA(self, X, G):
        return jnp.matmul(G , ( self.Ip - 0.5 * self.C(X) ))  - jnp.matmul(X , self.Phi(jnp.matmul(X.swapaxes(-2,-1).conj(), G)) )

    def JA_swapaxes(self,X,G):
        # JA is self-adjoint
        return self.JA(X,G)

    def hessA(self, X, gradf, D):
        return - jnp.matmul(D , self.Phi( jnp.matmul(X.swapaxes(-2,-1).conj(), gradf)  )) - jnp.matmul(X , self.Phi( jnp.matmul(D.swapaxes(-2,-1).conj() , gradf)  )) - jnp.matmul(gradf , self.Phi( jnp.matmul(D.swapaxes(-2,-1).conj() , X) ))


    def JC(self, X, Lambda):
        return jnp.matmul(2*X , self.Phi(Lambda))

    
    

    # def C_quad_penalty(self, X):
    #     CX = self.C(X)
    #     return jnp.sum(CX * CX.conj())


    def hess_feas(self, X, D):
        return jnp.matmul(4*X , self.Phi( jnp.matmul(X.swapaxes(-2,-1).conj(), D) )  ) + 2* jnp.matmul(D , self.C(X))

    



    # def Feas_eval(self, X):
    #     return jnp.linalg.norm( self.C(X).flatten() , 2)

    def Init_point(self, Xinit = None):
        Xinit = super().Init_point(Xinit = Xinit)
        UX, SX, VX = jnp.linalg.svd(Xinit, full_matrices= False)
        Xinit = jnp.matmul(UX, VX.swapaxes(-2,-1).conj())
        Xinit = jax.device_put(Xinit, self.device)
        return Xinit

    def Post_process(self,X):
        UX, SX, VX = jnp.linalg.svd(X, full_matrices= False)
        return jnp.matmul(UX, VX.swapaxes(-2,-1).conj())



    def generate_cdf_fun(self, obj_fun, beta):
        def local_obj_fun(X):
            CX = self.C(X)
            AX = X - 0.5 * X@ CX
            return (obj_fun(AX) + (beta/2) * jnp.sum(CX *CX.conj())).real

        



        return local_obj_fun  




    def generate_cdf_grad(self, obj_grad, beta):
        def local_grad(X):
            CX = self.C(X)
            AX = X - 0.5 * jnp.matmul(X,CX)
            gradf = obj_grad(AX)
            XG = self.Phi( jnp.matmul(X.swapaxes(-2,-1).conj() , gradf) )

            # local_JA_gradf = gradf @ (np.eye(self._p) - 0.5 * CX) - X @ XG 
            
            # local_JC_CX = 2 * X @(CX)

            return jnp.matmul(gradf , (self.Ip - 0.5 * CX)) +  jnp.matmul(X ,  ( 2* beta * CX - XG))

        return local_grad  



    def generate_cdf_hess(self, obj_grad, obj_hess, beta):
        def local_hess(X, D):
            CX = self.C(X)
            AX = X - 0.5 *  jnp.matmul(X,CX)
            gradf = obj_grad(AX)
            XG = self.Phi( jnp.matmul(X.swapaxes(-2,-1).conj() , gradf) )
            XD = self.Phi( jnp.matmul(X.swapaxes(-2,-1).conj() , D) )

            local_JAT_D = jnp.matmul(D , (self.Ip - 0.5 * CX)) - jnp.matmul(X , XD)
            local_objhess_JAT_D = obj_hess(AX, local_JAT_D)
            # local_JA_objhess_JAT_D = local_objhess_JAT_D @ (np.eye(self._p) - 0.5 * CX) -  X @ self.Phi( X.T @ local_objhess_JAT_D )

            # local_hessA_objgrad_D = - D @ XG - X @ self.Phi(D.T @ gradf) - gradf @ XD

            # local_hess_feas = 4*X @ XD + 2*D @ CX
            # return local_JA_objhess_JAT_D + local_hessA_objgrad_D + beta * local_hess_feas

            return (   jnp.matmul(local_objhess_JAT_D , (self.Ip - 0.5 * CX)) 
                    -  jnp.matmul(X , self.Phi( jnp.matmul(X.swapaxes(-2,-1).conj() , local_objhess_JAT_D) + self.Phi(jnp.matmul(D.swapaxes(-2,-1).conj() , gradf)) - 4* beta * XD) )
                    + jnp.matmul(D , (2*beta*CX - XG) - jnp.matmul(gradf , XD)  )   )



        return local_hess