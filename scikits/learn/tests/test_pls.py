import numpy as np
from numpy.testing import assert_array_almost_equal

from scikits.learn.datasets import load_linnerud
from scikits.learn import pls

d=load_linnerud()
X = d['data_exercise']
Y = d['data_physiological']

###
def test_pls():
    n_components = 2
    
    # 1) Canonical (symetric) PLS (PLS 2 blocks canonical mode A)
    # ===========================================================    
    # Compare 2 algo.: nipals vs. svd
    # ------------------------------
    pls_bynipals = pls.PLS(deflation_mode="canonical")
    pls_bynipals.fit(X,Y, n_components=n_components)
    pls_bysvd = pls.PLS(deflation_mode="canonical",algorithm="svd")
    pls_bysvd.fit(X,Y, n_components=n_components)
    # check that the loading vectors are highly correlated
    assert_array_almost_equal(
        [np.abs(np.corrcoef(pls_bynipals.x_loadings_[:,k],
                               pls_bysvd.x_loadings_[:,k])[1,0]) 
                           for k in xrange(n_components)],np.ones(n_components),
                           err_msg="nipals and svd implementation lead to\
                                    different x loadings")
    assert_array_almost_equal(
        [np.abs(np.corrcoef(pls_bynipals.y_loadings_[:,k],
                               pls_bysvd.y_loadings_[:,k])[1,0]) 
                           for k in xrange(n_components)],np.ones(n_components),
                           err_msg="nipals and svd implementation lead to\
                                    different y loadings")

    # Check PLS properties (with n_components=X.shape[1])
    # ---------------------------------------------------
    plsca = pls.PLS(deflation_mode="canonical")
    plsca.fit(X, Y, n_components=X.shape[1])
    T  = plsca.x_scores_
    P  = plsca.x_loadings_
    Wx = plsca.x_weights_
    U  = plsca.y_scores_
    Q  = plsca.y_loadings_
    Wy = plsca.y_weights_
    
    def check_ortho(M, err_msg):
        MtM = np.dot(M.T,M)
        MtM_rmdiag = MtM - np.diag(np.diag(MtM))
        zero_mat = np.zeros(MtM.size).reshape(MtM.shape)
        assert_array_almost_equal(MtM_rmdiag, zero_mat, err_msg=err_msg)
    
    # Orthogonality of weights 
    # ~~~~~~~~~~~~~~~~~~~~~~~~ 
    check_ortho(Wx, "x weights are not orthogonal")
    check_ortho(Wy, "y weights are not orthogonal")

    # Orthogonality of latent scores
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    check_ortho(T, "x scores are not orthogonal")
    check_ortho(U, "y scores are not orthogonal")

    # Check X = TP' and Y = UQ' (with (p == q) components)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    # center scale X, Y
    Xc, Yc, x_mean, y_mean, x_std, y_std =\
         pls.center_scale_xy(X.copy(), Y.copy(), scale=True)
    assert_array_almost_equal(Xc, np.dot(T, P.T),
        err_msg="X != TP'")
    assert_array_almost_equal(Yc, np.dot(U, Q.T),
            err_msg="Y != UQ'")

    # Check that rotations on training data lead to scores
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Xr, Yr = plsca.transform(X, Y)
    assert_array_almost_equal(Xr, plsca.x_scores_,
        err_msg="rotation on X failed")
    assert_array_almost_equal(Yr, plsca.y_scores_,
        err_msg="rotation on Y failed")


    # "Non regression test" on canonical PLS
    # --------------------------------------
    pls_bynipals = pls.PLS(deflation_mode="canonical")
    pls_bynipals.fit(X,Y, n_components=n_components)

    pls_ca = pls_bynipals
    x_loadings = np.array(
          [[-0.66591531,  0.77356014],
           [-0.67602366, -0.62873035],
           [ 0.35892139, -0.11993352]])
    assert_array_almost_equal(pls_ca.x_loadings_,x_loadings)

    y_loadings = np.array(
          [[ 0.6147046 ,  0.37877736],
           [ 0.65625787,  0.01196607],
           [ 0.51733043, -0.93984895]])
    assert_array_almost_equal(pls_ca.y_loadings_,y_loadings)

    x_weights = np.array(
          [[-0.58989082,  0.78900159],
           [-0.77134081, -0.61352087],
           [ 0.23887693, -0.03269003]])
    assert_array_almost_equal(pls_ca.x_weights_,x_weights)

    y_weights = np.array(
          [[ 0.61330742,  0.25616374],
           [ 0.74697171,  0.11930342],
           [ 0.25668516, -0.95924284]])
    assert_array_almost_equal(pls_ca.y_weights_,y_weights)


    # 2) Regression PLS (PLS2): "Non regression test" 
    # ===============================================
    pls2 = pls.PLS(deflation_mode="regression")
    pls2.fit(X, Y, n_components=n_components)

    x_loadings = np.array(
          [[-0.66591531, -0.01976472],
           [-0.67602366, -0.35471175],
           [ 0.35892139, -1.19418263]])
    assert_array_almost_equal(pls2.x_loadings_,x_loadings)
     
    y_loadings = np.array(
          [[ 0.34163079,  0.33638156],
           [ 0.41608584,  0.29078321],
           [ 0.1429814 ,  0.0651935 ]])
    assert_array_almost_equal(pls2.y_loadings_,y_loadings)
    
    x_weights = np.array(
          [[-0.58989082,  0.46882134],
           [-0.77134081, -0.56802033],
           [ 0.23887693, -0.67643141]])
    assert_array_almost_equal(pls2.x_weights_,x_weights)
    
    y_weights = np.array(
          [[ 0.61330742,  0.74851767],
           [ 0.74697171,  0.64705202],
           [ 0.25668516,  0.14506885]])
    assert_array_almost_equal(pls2.y_weights_,y_weights)
    