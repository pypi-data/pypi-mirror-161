import abc
import numpy as np 
import scipy as sp 
from cdopt.manifold import basic_manifold
from ..manifold_np import complex_basic_manifold_np


class complex_stiefel_np(complex_basic_manifold_np):
    def __init__(self, var_shape) -> None:
        if len(var_shape) >= 2:
            self._n = var_shape[-2]
            self._p = var_shape[-1]
            self.dim = var_shape[:-2]
        else:
            print("The length of var_shape should be no less than 2.")
            raise TypeError


        super().__init__('Complex Stiefel',var_shape, (*self.dim, self._p,self._p))
        
        self.Ip = np.reshape(np.outer(np.ones(self.dim), np.eye(self._p)),(*self.dim, self._p,self._p))


        
    # def array2tensor(self, X_array):
    #     dim = len(X_array)
    #     X_real = np.as_tensor(X_array[:int(dim/2)])
    #     X_imag = np.as_tensor(X_array[int(dim/2):])
    #     X =  np.complex(X_real, X_imag).to(device=self.device, dtype=self.dtype)
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
        return np.matmul(X.swapaxes(-2,-1).conj(), X) - self.Ip

    def A(self, X):
        XX = np.matmul(X.swapaxes(-2,-1).conj(), X)
        return 1.5 * X - np.matmul(X , (XX /2))


    def JA(self, X, G):
        return np.matmul(G , ( self.Ip - 0.5 * self.C(X) ))  - np.matmul(X , self.Phi(np.matmul(X.swapaxes(-2,-1).conj(), G)) )

    def JA_swapaxes(self,X,G):
        # JA is self-adjoint
        return self.JA(X,G)

    def hessA(self, X, gradf, D):
        return - np.matmul(D , self.Phi( np.matmul(X.swapaxes(-2,-1).conj(), gradf)  )) - np.matmul(X , self.Phi( np.matmul(D.swapaxes(-2,-1).conj() , gradf)  )) - np.matmul(gradf , self.Phi( np.matmul(D.swapaxes(-2,-1).conj() , X) ))


    def JC(self, X, Lambda):
        return np.matmul(2*X , self.Phi(Lambda))

    
    

    # def C_quad_penalty(self, X):
    #     CX = self.C(X)
    #     return np.sum(CX * CX.conj())


    def hess_feas(self, X, D):
        return np.matmul(4*X , self.Phi( np.matmul(X.swapaxes(-2,-1).conj(), D) )  ) + 2* np.matmul(D , self.C(X))

    



    # def Feas_eval(self, X):
    #     return np.linalg.norm( self.C(X).flatten() , 2)

    def Init_point(self, Xinit = None):
        Xinit = super().Init_point(Xinit = Xinit)
        UX, SX, VX = np.linalg.svd(Xinit, full_matrices= False)
        Xinit = np.matmul(UX, VX.swapaxes(-2,-1).conj())
        
        return Xinit

    def Post_process(self,X):
        UX, SX, VX = np.linalg.svd(X, full_matrices= False)
        return np.matmul(UX, VX.swapaxes(-2,-1).conj())



    def generate_cdf_fun(self, obj_fun, beta):
        def local_obj_fun(X):
            CX = self.C(X)
            AX = X - 0.5 * X@ CX
            return (obj_fun(AX) + (beta/2) * np.sum(CX *CX.conj())).real

        



        return local_obj_fun  




    def generate_cdf_grad(self, obj_grad, beta):
        def local_grad(X):
            CX = self.C(X)
            AX = X - 0.5 * np.matmul(X,CX)
            gradf = obj_grad(AX)
            XG = self.Phi( np.matmul(X.swapaxes(-2,-1).conj() , gradf) )

            # local_JA_gradf = gradf @ (np.eye(self._p) - 0.5 * CX) - X @ XG 
            
            # local_JC_CX = 2 * X @(CX)

            return np.matmul(gradf , (self.Ip - 0.5 * CX)) +  np.matmul(X ,  ( 2* beta * CX - XG))

        return local_grad  



    def generate_cdf_hess(self, obj_grad, obj_hess, beta):
        def local_hess(X, D):
            CX = self.C(X)
            AX = X - 0.5 *  np.matmul(X,CX)
            gradf = obj_grad(AX)
            XG = self.Phi( np.matmul(X.swapaxes(-2,-1).conj() , gradf) )
            XD = self.Phi( np.matmul(X.swapaxes(-2,-1).conj() , D) )

            local_JAT_D = np.matmul(D , (self.Ip - 0.5 * CX)) - np.matmul(X , XD)
            local_objhess_JAT_D = obj_hess(AX, local_JAT_D)
            # local_JA_objhess_JAT_D = local_objhess_JAT_D @ (np.eye(self._p) - 0.5 * CX) -  X @ self.Phi( X.T @ local_objhess_JAT_D )

            # local_hessA_objgrad_D = - D @ XG - X @ self.Phi(D.T @ gradf) - gradf @ XD

            # local_hess_feas = 4*X @ XD + 2*D @ CX
            # return local_JA_objhess_JAT_D + local_hessA_objgrad_D + beta * local_hess_feas

            return (   np.matmul(local_objhess_JAT_D , (self.Ip - 0.5 * CX)) 
                    -  np.matmul(X , self.Phi( np.matmul(X.swapaxes(-2,-1).conj() , local_objhess_JAT_D) + self.Phi(np.matmul(D.swapaxes(-2,-1).conj() , gradf)) - 4* beta * XD) )
                    + np.matmul(D , (2*beta*CX - XG) - np.matmul(gradf , XD)  )   )



        return local_hess