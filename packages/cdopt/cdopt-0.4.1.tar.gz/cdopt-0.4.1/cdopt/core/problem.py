import numpy as np
from typing import Union, Tuple, List



class problem:
    def __init__(self, manifold, obj_fun, obj_grad=None, obj_hvp=None, beta = 'auto', enable_autodiff: bool = True, backbone = None, enable_jit:bool = True, autobeta_args = {}, Xinit = None, **kwargs):
        
        self.manifold = manifold
        self.obj_fun = obj_fun 

        self.Xinit = manifold.Init_point(Xinit = Xinit)
        self.Xinit_vec_np = manifold.tensor2array(manifold.m2v(self.Xinit))

        if beta == 'auto':
            if 'max_samples' in autobeta_args.keys():
                max_samples = autobeta_args['max_samples']
            else:
                max_samples = 30

            if 'sample_dist' in autobeta_args.keys():
                sample_dist = autobeta_args['sample_dist']
            else:
                sample_dist = 1e0

            if 'thresholding' in autobeta_args.keys():
                thresholding = autobeta_args['thresholding']
            else:
                thresholding = 1e-5

            if 'coeffs' in autobeta_args.keys():
                coeffs = autobeta_args['coeffs']
            else:
                coeffs = 2.5

            X_ref = manifold.tensor2array(manifold.m2v(self.Xinit))
            fval_feas_list = []

            for jjj in range(max_samples):
                D = np.random.randn(manifold.var_num)
                D = (D/ np.linalg.norm(D,2)) * np.random.rand()
                
                X_ref_tmp = manifold.v2m(manifold.array2tensor(  X_ref + sample_dist * D  ))
                A_X_ref_tmp = manifold.A(X_ref_tmp)
                if manifold.manifold_type == 'P':
                    diff_fval = -abs(float(obj_fun( *A_X_ref_tmp )) - float(obj_fun( *manifold.A(A_X_ref_tmp) )))
                else:
                    diff_fval = -abs(float(obj_fun( A_X_ref_tmp )) - float(obj_fun( manifold.A(A_X_ref_tmp) )))
                    # diff_fval = obj_fun( X_ref_tmp ) - obj_fun( A_X_ref_tmp )
                diff_CX =  manifold.Feas_eval(X_ref_tmp) - manifold.Feas_eval( A_X_ref_tmp )
                fval_feas_list.append( (float(diff_fval), float(diff_CX) ) )

            fval_processed = [max( -data_local[0]/(data_local[1]**2), thresholding ) for data_local in fval_feas_list     ]   
            beta = coeffs * max(fval_processed)
        

        self.beta = beta


        if enable_autodiff:
            if obj_grad is None   or   obj_hvp is None:
                if backbone == None:
                    self.backbone = manifold.backbone
                elif backbone == 'jax':
                    # from core.autodiff_jax import autodiff
                    # raise NotImplementedError
                    from ..core.backbone_jax import backbone_jax
                    self.backbone = backbone_jax()
                elif backbone == 'autograd':
                    # from core.autodiff_ag import autodiff
                    from ..core.backbone_autograd import backbone_autograd
                    self.backbone = backbone_autograd()
                elif backbone == 'torch':
                    from ..core.backbone_torch import backbone_torch
                    self.backbone = backbone_torch(**kwargs)
                else: 
                    self.backbone = backbone(**kwargs)
                
                autodiff = self.backbone.autodiff
                    
                if  obj_hvp is None:
                    self.obj_grad, self.obj_hvp = autodiff(obj_fun, obj_grad, manifold.manifold_type)
                else:
                    self.obj_grad,  = autodiff(obj_fun,obj_grad, manifold.manifold_type)
                
            else:
                self.obj_grad = obj_grad 
                self.obj_hvp = obj_hvp 


            

            self.cdf_fun = self.manifold.generate_cdf_fun(self.obj_fun, beta)
            self.cdf_grad = self.manifold.generate_cdf_grad(self.obj_grad, beta)
            self.cdf_hvp = self.manifold.generate_cdf_hess(self.obj_grad, self.obj_hvp, beta)

            if enable_jit and (backbone is not None):
                self.cdf_fun = self.backbone.jit(self.cdf_fun)
                self.cdf_grad = self.backbone.jit(self.cdf_grad)
                self.cdf_hvp = self.backbone.jit(self.cdf_hvp)




            self.cdf_fun_vec = lambda y: self.cdf_fun(self.manifold.v2m(y))
            self.cdf_grad_vec= lambda y: self.manifold.m2v( self.cdf_grad(self.manifold.v2m(y)) )
            self.cdf_hvp_vec = lambda y,p: self.manifold.m2v( self.cdf_hvp(self.manifold.v2m(y), self.manifold.v2m(p)) )


            # self.cdf_fun_vec_np = lambda y: float(self.manifold.tensor2array(self.cdf_fun_vec( self.manifold.array2tensor(y)) ))
            self.cdf_fun_vec_np = lambda y: float(self.cdf_fun_vec( self.manifold.array2tensor(y)) )
            self.cdf_grad_vec_np = lambda y: self.manifold.tensor2array(self.cdf_grad_vec( self.manifold.array2tensor(y)) )
            self.cdf_hvp_vec_np = lambda y,p: self.manifold.tensor2array(self.cdf_hvp_vec(self.manifold.array2tensor(y), self.manifold.array2tensor(p))   )

        else:

            def _raise_not_implemented_error(*args, **kwargs):
                raise NotImplementedError("Automatical differentiation not enabled")


            self.obj_fun = obj_fun
            self.obj_grad = obj_grad
            self.obj_hvp = obj_hvp

            self.cdf_fun = self.manifold.generate_cdf_fun(self.obj_fun, beta)
            if enable_jit:
                self.cdf_fun = self.backbone.jit(self.cdf_fun)
            
            
            self.cdf_fun_vec = lambda y: self.cdf_fun(self.manifold.v2m(y))

            

            if obj_grad is not None:
                self.cdf_grad = self.manifold.generate_cdf_grad(self.obj_grad, beta)
                if enable_jit:
                    self.cdf_grad = self.backbone.jit(self.cdf_grad)

                self.cdf_grad_vec = lambda y: self.manifold.m2v( self.cdf_grad(self.manifold.v2m(y)) )

            else:
                self.cdf_grad = _raise_not_implemented_error
                self.cdf_grad_vec= _raise_not_implemented_error



            if obj_hvp is not None:
                self.cdf_hvp = self.manifold.generate_cdf_hess(self.obj_grad, self.obj_hvp, beta)
                if enable_jit:
                    self.cdf_hvp = self.backbone.jit(self.cdf_hvp)

                self.cdf_hvp_vec = lambda y,p: self.manifold.m2v( self.cdf_hvp(self.manifold.v2m(y), self.manifold.v2m(p)) )

            else:
                self.cdf_hvp = _raise_not_implemented_error
                self.cdf_hvp_vec = _raise_not_implemented_error




        
            


        