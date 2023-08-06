
import scipy.integrate 
import pandas as pd
import numpy as np 
import pyvista as pv

def fc_unstruc2poly(mesh_unstruc):
    """
    A function to convert unstructuredgrid to polydata.
    :param mesh_unstruc: unstructured pyvista grid
    :type mesh_unstruc: pv.UnstructuredGrid
    :return: pv.PolyData
    :rtype: pv.PolyData

    """
    vertices=mesh_unstruc.points
    faces=mesh_unstruc.cells
    return pv.PolyData(vertices, faces)


def get_visibility(c1,c2):
    """
    Check if two facets can "see"" each other
    
    :param c1: a facet
    :type c1: PolyData facet (pyvista format)
    :param c2: a facet
    :type c2: PolyData facet (pyvista format)
    :return: the visibility between two facets
    :rtype: boolean

    """
    # les centres des cellules
    center1 = c1.cell_centers().points
    center2 = c2.cell_centers().points
    n21 = center1-center2
    # les normales
    norm1 = c1.cell_normals
    norm2 = c2.cell_normals
    # les produits scalaires
    pd_scal_sup = np.einsum('ij,ij->i',n21, norm2)
    pd_scal_inf = np.einsum('ij,ij->i',n21, norm1)
    # test de visibilite 
    vis=False
    if (pd_scal_sup > 0 and pd_scal_inf < 0):
        vis = True
    return vis

def get_visibility_raytrace(face1,face2,obstacle):
    """
    
    :param face1: face1 to be checked for obstruction 
    :type face1: pv.PolyData
    :param face2: face1 to be checked for obstruction
    :type face2: pv.PolyData
    :param obstacle: the mesh inbetween, composing the potentiel obstruction
    :type obstacle: pv.PolyData
    :return: True=no obstruction, False=obstruction
    :rtype: TYPE

    """
    # Define line segment
    start = face1.cell_centers().points[0]
    stop =  face2.cell_centers().points[0]
    # Perform ray trace
    points, ind = obstacle.ray_trace(start, stop, first_point=False)
    print(ind, len(ind))
    
    # if you work with a single cell
    if obstacle.n_cells==1:
        if ind.size==0:# if intersection: there is an obstruction
            return True 
        else:# if not, the faces can see each other
            return False
    # if face1 and face2 are contained in the obstacle mesh
    else:
        if len(ind)>3: # if intersection: there is an obstruction
            return False
        else: # if not, the faces can see each other
            return True

def trunc(values, decs=0):   
    return np.trunc(values*10**decs)/(10**decs)

def integrand(x , y, norm_q_carree, norm_p_carree, scal_qpq, scal_qpp, scal_pq, norm_qp_carree):
    return np.log(y**2*norm_q_carree + x**2*norm_p_carree - 2*y*scal_qpq + 2*x*scal_qpp - 2*x*y*scal_pq + norm_qp_carree)*scal_pq

def compute_viewfactor(cell_1,cell_2):
    """
    Computes the view factor from cell_2 to cell_1.

    Parameters
    ----------
    cell_1 : float
        PolyData facet (pyvista format)
    cell_2 : float 
        PolyData facet (pyvista format)
    Returns
    -------
    FF : float
        View factor from cell_2 to cell_1.
    """
    FF = 0
    #travail sur la cellule 1
    cell_1_poly = cell_1     
    cell_1 = cell_1.cast_to_unstructured_grid()
    cell_1_points = cell_1.cell_points(0)
    
    cell_1_points_roll = np.roll(cell_1_points, -1, axis=0)
    vect_dir_elts_1 = cell_1_points_roll - cell_1_points
    cell_1_points = trunc(cell_1_points, decs = 4)
    
    #travail sur la cellule 2
    cell_2_poly = cell_2
    cell_2 = cell_2.cast_to_unstructured_grid()
    cell_2_points = cell_2.cell_points(0)
    cell_2_points_roll = np.roll(cell_2_points, -1, axis=0)
    vect_dir_elts_2 = cell_2_points_roll - cell_2_points
    cell_2_points = trunc(cell_2_points, decs = 4)
    
    n_cols      = np.shape(cell_2_points)[0]
    n_rows      = np.shape(cell_1_points)[0]
    
    nb_sommets_1 = n_rows
    nb_sommets_2 = n_cols
    
    #calcul de la dataframe avec tous les vecteurs 
    mat_vectors = np.zeros((n_rows,n_cols))
    vectors     = pd.DataFrame(mat_vectors, dtype = object)
    
    for row in range(n_rows) :
        #on calcule les coordonnées des vecteurs partant du sommet i de la cellule i et allant vers les différents sommets j de la cellule j
        coord_repeat         = np.tile(cell_1_points[row], (nb_sommets_2, 1))
        vect_sommets_1_to_2  = cell_2_points - coord_repeat
        #On transforme les matrices en liste de tuple pour obtenir les coordonnées de vecteurs sous forme de triple
        coord_vect           = list(tuple(map(tuple, vect_sommets_1_to_2)))
        #On stocke ensuite les coord dans le DataFrame
        vectors.at[row]        = pd.Series(coord_vect)
        
    vect_sommets_extra = vectors
    
    vect_sommets_intra_1 = vect_dir_elts_1
    vect_sommets_intra_2 = vect_dir_elts_2                
    
    #calcul des constantes pour lintegrale 
    area = cell_2_poly.compute_cell_sizes(area = True)['Area']
    A_q  = area[0]
    constante = 4*np.pi*A_q
    
    err  = 0
    s_i  = 0
    s_j = 0
    
    arr_test              = np.argwhere((cell_2_points[:,None, :] == cell_1_points[:,:]).all(-1))
    nbre_sommets_partages = np.shape(arr_test)[0]
    
    if nbre_sommets_partages == 0 :
            #dans ce cas il n'y a aucun sommet partage 
                for n in range(nb_sommets_2):
                    p_n_np1       = tuple(vect_sommets_intra_2[n,:])
                    norm_p_carree = np.dot(p_n_np1, p_n_np1)
                    
                    for m in range(nb_sommets_1):
                        q_m_mp1        = tuple(vect_sommets_intra_1[m,:])
                        norm_q_carree  = np.dot(q_m_mp1,q_m_mp1)
                        qm_pn          = vect_sommets_extra.loc[m,n]
                        norm_qp_carree = np.dot(qm_pn,qm_pn)
                        scal_qpq       = np.dot(qm_pn, q_m_mp1)
                        scal_qpp       = np.dot(qm_pn, p_n_np1)
                        scal_pq        = np.dot(q_m_mp1, p_n_np1)
                        
                        s_j, err = scipy.integrate.dblquad(integrand,0,1,lambda x : 0, lambda x : 1, args = (norm_q_carree, norm_p_carree, scal_qpq, scal_qpp, scal_pq, norm_qp_carree,))
                        
                        s_i += round(s_j/constante, 11)
                        err += err/(nb_sommets_1 + nb_sommets_2)
    else : 
    #dans ce cas les cellules ne partagent que 1 côté
    #on décide alors de les 'décoller'
        for sommet_j in cell_2_points[:,:]:
            #on les décale en leur appliquant le vecteur reliant les centroïdes des cellules
            # sommet_j += np.dot(normals[index[0]], 0.001)
            sommet_j += np.dot(cell_1_poly.face_normals[0],0.001) # LE BON
            # sommet_j += np.dot(cell_1_poly.normals,0.001)
            
        #On doit alors réécrire les vecteurs allant d'une cellule à l'autre
        for row in range(n_rows) :
            #on calcule les coordonnées des vecteurs partant du sommet i de la cellule i et allant vers les différents sommets j de la cellule j
            coord_repeat         = np.tile(cell_1_points[row], (n_cols, 1))
            vect_sommets_i_to_j  = cell_2_points - coord_repeat
            #On transforme les matrices en liste de tuple pour obtenir les coordonnées de vecteurs sous forme de triple
            coord_vect           = list(tuple(map(tuple, vect_sommets_i_to_j)))
            #On stocke ensuite les coord dans le DataFrame
            vectors.at[row]        = pd.Series(coord_vect)
        #puis on fait comme ci il n'y avait pas de sommet partagé !
        for n in range(nb_sommets_2):
            p_n_np1       = tuple(vect_sommets_intra_2[n,:])
            norm_p_carree = np.dot(p_n_np1, p_n_np1)
            
            for m in range(nb_sommets_1):
                q_m_mp1        = tuple(vect_sommets_intra_1[m,:])
                norm_q_carree  = np.dot(q_m_mp1,q_m_mp1)
                qm_pn          = vect_sommets_extra.loc[m,n]
                norm_qp_carree = np.dot(qm_pn,qm_pn)
                scal_qpq       = np.dot(qm_pn, q_m_mp1)
                scal_qpp       = np.dot(qm_pn, p_n_np1)
                scal_pq        = np.dot(q_m_mp1, p_n_np1)
                
                s_j, err = scipy.integrate.dblquad(integrand,0,1,lambda x : 0, lambda x : 1, args = (norm_q_carree, norm_p_carree, scal_qpq, scal_qpp, scal_pq, norm_qp_carree,))
                
                s_i += round(s_j/constante, 11)
                err += err/(nb_sommets_1 + nb_sommets_2)
    
    if s_i > 0 :
        FF  = s_i
    
    return FF
