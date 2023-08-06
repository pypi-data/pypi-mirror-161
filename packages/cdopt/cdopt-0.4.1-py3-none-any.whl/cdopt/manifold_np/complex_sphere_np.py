import abc
import numpy as np 
import scipy as sp 
from cdopt.manifold import basic_manifold
from ..manifold_np import complex_basic_manifold_np


class complex_sphere_np(complex_basic_manifold_np):
    def __init__(self, var_shape):
        
        super().__init__('complex_sphere',var_shape, (1,))



    def A(self, X):
        return (2*X)/( 1 + np.sum( X* X.conj() ) )

    def JA(self, X, G):
        XG = np.sum( X*G.conj() ).real
        X_rvec = np.sum( X* X.conj() ) +1
        return (2*G - ( (4*XG)*X )/X_rvec )/X_rvec
        

    def JA_transpose(self, X, D):
        return self.JA(X,D) 

    def hessA(self, X, gradf, D):
        XG = np.sum(X * gradf.conj()).real 
        XD = np.sum(X * D.conj()).real
        GD = np.sum(gradf * D.conj()).real
        X_rvec = np.sum( X * X.conj()  ) +1
        
        return -(4/(X_rvec**2))*( gradf * XD + D * XG + X * GD ) + 16/( X_rvec**3 ) * (X * XG * XD)


    def C(self, X):
        return np.sum( X * X.conj() ) - 1

    def JC(self, X, Lambda):
        return 2*X * Lambda.real

    def hess_feas(self, X, D):
        return 2 * D * self.C(X) + 4 * X * np.sum(X*D.conj()).real


    def Init_point(self, Xinit = None):
        Xinit = super().Init_point(Xinit=Xinit)
        X_rvec = np.sqrt(np.sum( Xinit * Xinit ))
        Xinit = Xinit / X_rvec
        
        return Xinit

    def Post_process(self,X):
        X_rvec = np.sqrt(np.sum( X * X.conj()  ))
        X = X / X_rvec
        return X

    