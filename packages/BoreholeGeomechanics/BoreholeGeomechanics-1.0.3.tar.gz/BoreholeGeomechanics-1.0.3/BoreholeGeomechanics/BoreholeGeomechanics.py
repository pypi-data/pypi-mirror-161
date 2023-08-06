# Borehole geomechanics library. 
# Lahcene Bellounis and Mai-Linh Doan, ISTerre, May-July 2022
# Contact: Mai-linh.doan@univ-grenoble-alpes.fr

from tkinter import N
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Original geographic : 
#   x : East
#   y : North
#   z : Upwards
# Note : different from Lee 1992, made for the work of Cécile Massiot

# Plane weakness axes
#   x : plunging vector
#   y : cross-product of normal x plunging  (note the order, so that the orientation of the axes are ok)
#   z : normal vector

# Borehole axis
# x : horizontal vector, perpendicular to borehole axis (x= y cross z)
# y : perpendicular to the borehole axis, pointing to the top generatrix of the borehole
# z : borehole axis, pointing to the surface

# Trigonometric functions for angles in degree
def cos(angle_in_degree):
    return np.cos(angle_in_degree*np.pi/180)
def sin(angle_in_degree):
    return np.sin(angle_in_degree*np.pi/180)
def tan(angle_in_degree):
    return np.tan(angle_in_degree*np.pi/180)

# Defining vectors in geographical space
def vector_from_Euler_angles(theta, lamda):
    """
    Unitary vector from the Euler angle of a direction
    """
    return np.array([sin(theta) * cos(lamda), sin(theta)*sin(lamda), cos(theta)] )


# Orienting vector of the plunging line, (well or line of greater slope)
# Trend = azimut of the line projected onto an horizontal plane
# Lambda = Angle 

def Euler_angles_of_line_from_trend_and_plunge(trend, plunge):
    theta = plunge + 90
    lamda=90 - trend
    return [theta, lamda]

def vector_from_trend_and_plunge(trend, plunge):
    """
    Unitary vector from given trend and plunge of an axis 
    """
    euler = Euler_angles_of_line_from_trend_and_plunge(trend, plunge) #return (theta, lambda)
    return vector_from_Euler_angles(euler[0], euler[1])


# Plottting utilities
def plot_Mohr_circle(smin,smax,**kwargs):
    ax=kwargs.pop('axes',np.nan)
    if ax == np.nan:
        fig,ax=plt.subplots()
    center=(smin+smax)/2
    radius=(smax-smin)/2
    ax.add_patch(mpatches.Circle(xy=(center,0),radius=radius,**kwargs))
    return ax
    
def plot_plane_on_Mohr(sigma_n,tau,**kwargs):
    ax=kwargs.pop('axes',np.nan)
    if ax == np.nan:
        fig,ax=plt.subplots()

    marker=kwargs.pop('marker','+')
    ax.scatter(sigma_n,tau,marker,**kwargs)
    return ax


### Stress class 
class Stress:
    """
    A class managing stress and its various representation in several axes family
        - principal axes
            x : S1, maximum principal stress directions. 
                    Plunge (relative to horizontal) and trend (azimut) is specified
            y : S2, intermediate principal stress directions
            z : S3, minimum principal stress directions. 
                    Plunge (relative to horizontal) and trend (azimut) is specified
        - geographic axes
            x : East
            y : North
            z : Upwards
        - planes axes
            x : plunging vector
            y : cross product of x and z
            z : normal vector
            
    Note that by default we work in true stres, not effective stress
    
    Internally, the stress data is stored by the principal components, but for computation
    the pivot axes system is the geographic ones.
    """
    
    def __init__(self,S1=np.nan,S2=np.nan,S3=np.nan,
                 trend1=0,trend3=90,plunge1=0,plunge3=0,
                 Pp=0,unit='',mu=0.6):
        """
        2 ways of defining stress : 
            -  stress(array) where array is a 3x3 matrix
            - from principal stress : 
                S1, S2, S3, trend1,trend3,plunge1,plunge3
        With AGUments Pp you can specify the pore pressure
        mu (friction coefficient) is optionnal.
            It can be used to draw the self polygon (Stress.stress_polygon method)
        """
        # A stress is defined a priori by it internal stress direction
        if type(S1)== np.ndarray:
            self.tensor_principal_from_geographic(S1)
            self.unit=unit
            self.Pp=Pp
            self.mu=mu
        else:
            self.S1=S1
            self.S2=S2
            self.S3=S3
            self.trend1=trend1
            self.trend3=trend3
            self.plunge1=plunge1
            self.plunge3=plunge3
            self.Pp=Pp
            self.unit=unit
            self.mu=mu
        
    def __repr__(self):
        """
        Display the stress tensor attributes
        """
        return 'S1= {} {}  S2= {} {}  S3: {} {}\n'.format(self.S1,self.unit,self.S2,self.unit,self.S3,self.unit)+\
                'Pp= {} {} \n'.format(self.Pp,self.unit)+\
                'Plunge1 = {} degree  Azimut1 = {} degree\n'.format(self.plunge1,self.trend1)+\
                'Plunge3 = {} degree  Azimut3 = {} degree'.format(self.plunge3,self.trend3)
        
    # TODO test consistency of principal stress and principal directions 
    # orthogonality, ordering of S1, S2, S3
    
    def tensor_principal(self):
        """
        Return diagonal matric in principal stress direction
        """
        return np.diag([self.S1,self.S2,self.S3])

    # geographic
    def transfer_principal_to_geographic(self):
        """
        transfer_geographic_to_principal(trend1,plunge1,trend3,plunge3)

        Return the transfer matrix help to get the coefficients in the old (initial, starting) coordinate system
        to from the coefficient in the new (target, final) coordinate system

        We first get the expression of the unit vectors from the new coordinate system, expressed in the old system.

        Input 
            trend1 = azimut of the projection of the maximal principal stress direction (S1) onto an horizontal plane
            plunge1 = dip of the maximum principal stress direction relative to an horizontal plane
            trend3 = azimut of the projection of the minimal principal stress direction (S3) onto an horizontal plane
            plunge3 = dip of the minimum principal stress direction (S3) relative to an horizontal plane

        Return transfer matrix geographic -> principal, L, so that S_geog=L.T dot S_princ L
        columns : vectors in that order : σ1, σ2, σ3 
        """
        #S1, S2, S3 in Euler coordinates defined by the trend and plunge of S1 and S3
        eS1 = vector_from_trend_and_plunge(self.trend1, self.plunge1)
        eS3 = vector_from_trend_and_plunge(self.trend3, self.plunge3)
        eS2 = -np.cross(eS1, eS3)

        #L as in equation 2.99 of Jaeger etc
        self.principal_directions_in_geographic_coords = np.column_stack([eS1,eS2, eS3])
        return self.principal_directions_in_geographic_coords

    def transfer_geographic_to_principal(self): 
        return self.transfer_principal_to_geographic().T

    def tensor_geographic_from_principal(self):
        """
        Two syntaxes : 
        tensor_geographic_from_principal(stress_tensor,trend1,plunge1,trend3,plunge3)
        tensor_geographic_from_principal([S1,S2,S3],trend1,plunge1,trend3,plunge3)

        Return stress tensor in geographic axes (E,N,Up)
        """
        S_princ=self.tensor_principal()
        L_geographic_to_principal=self.transfer_geographic_to_principal()
        self.S_geographic = L_geographic_to_principal.T @ S_princ @ L_geographic_to_principal
        return self.S_geographic
    
    def tensor_principal_from_geographic(self,stress):
        """
        tensor_principal_from_geographic(self,stress)
        Input:
            Stress is an 3x3 matrix 
        Output : none
             Get back principal stress direction from a full stress tensor.
             The S1, S2, S3, plunge1, plunge3,trend1, trend3 are updated
             To define a stress from geographic stress tensor:
                 - First define an empty stress object
                 - Second, use this function
        """
        eigs=np.linalg.eig(stress)
        magnitudes=eigs[0]
        vectors=eigs[1]

        # work on sorted matrix
        increasing_order=np.argsort(magnitudes)
        magnitudes_inc=magnitudes[increasing_order].copy()
        vectors_inc=vectors[:,increasing_order].copy()

        [self.S3,self.S2,self.S1]=magnitudes_inc.copy()

        # maximum is the last (here 2, as there are 3 values and that numbering starts from 0)
        self.trend1=np.arctan2(vectors_inc[2][0],vectors_inc[2][1])*180/np.pi
        self.plunge1=np.arcsin(-vectors_inc[2][2])*180/np.pi

        # minimum is the first (here 0, as numbering starts from 0)
        self.trend3=np.arctan2(vectors_inc[0][0],vectors_inc[0][1])*180/np.pi
        self.plunge3=np.arcsin(-vectors_inc[0][2])*180/np.pi

    def tensor_geographic(self):
        return self.tensor_geographic_from_principal()
    
    
    
    # graphical plots
    def get_S1(self,**kwargs):
        if self.S1 == np.nan:
            stress=kwargs.pop('stress',np.nan*np.ones((3,3)))
            self.tensor_principal_from_geographic(stress)
        return self.S1

    def get_S2(self,**kwargs):
        if self.S2== np.nan:
            stress=kwargs.pop('stress',np.nan*np.ones((3,3)))
            self.tensor_principal_from_geographic(stress)
        return self.S2

    def get_S3(self,**kwargs):
        if self.S3== np.nan:
            stress=kwargs.pop('stress',np.nan*np.ones((3,3)))
            self.tensor_principal_from_geographic(stress)
        return self.S3

    def get_S1_eff(self):
        return self.get_S1-self.Pp

    def get_S2_eff(self):
        return self.get_S2-self.Pp

    def get_S3_eff(self):
        return self.get_S3-self.Pp

    def plot_Mohr_circles(self,effective=False,**kwargs):
        """
        axes : specify axis to use. If not specified, will be created
        color : color
        """
        ax=kwargs.pop('axes',None)
        color=kwargs.pop('color',0.7*np.array([1,1,1]))
        if ax is None:
            fig,ax=plt.subplots()
        print(ax)
            
        if effective:
            S1=self.get_S1_eff()
            S2=self.get_S2_eff()
            S3=self.get_S3_eff()
            ax.set_xlabel(f"$\sigma_n'$ [{self.unit}]")
        else:
            S1=self.get_S1()
            S2=self.get_S2()
            S3=self.get_S3()
            ax.set_xlabel(f'$\sigma_n$ (no pressure added) [{self.unit}]')

        if S2 == np.nan:
            plot_Mohr_circle(S3,S1,axes=ax,ec='k')
        else:
            plot_Mohr_circle(S3,S1,axes=ax,ec='k',fc=color)
            plot_Mohr_circle(S3,S2,axes=ax,ec='k',fc='w')
            plot_Mohr_circle(S2,S1,axes=ax,ec='k',fc='w')
        xl=ax.get_xlim()
        ax.set_xlim(xl[0],max([max(xl),S1*1.1])) # 1.1 : margin for nicer display
        ax.set_aspect('equal')    #,adjustable='datalim')
        ax.set_ylabel(f'$\tau$ [{self.unit}]')
        yl=ax.get_ylim()
        ax.set_ylim(0,max([max(yl),(S1-S3)/2*1.1])) # 1.1 : margin for nicer display
        return ax

    def stress_applied_on_plane(self,plane):
        """
        Input 
            dipdir = azimut of the projection of the plunging plane vector onto an horizontal plane
            dir = dip of the maximum plunging plane vector relative to an horizontale plane        
            
        Output
        [sigma_n, tau]
        """
        sigmaPlane=plane.tensor_plane_from_geographic(self)
        sigma_n=sigmaPlane[2, 2]
        tau = np.sqrt( np.square(sigmaPlane[0, 2]) + np.square(sigmaPlane[1, 2]) )                                     
        return [sigma_n,tau]
    
    def stress_polygon(self,Sv,n_pts=200):
        ## Stress Polygon ##
        #input : Sv, mu, Pp 
        Pp = self.Pp
        mu = self.mu
        f = (np.sqrt(mu**2+1)+mu)**2
        Sh =  Pp + (Sv-Pp)/f
        SH = Pp + f*(Sv-Pp)
        x1 = np.linspace(Sh,SH,n_pts)
        x2 = np.linspace(Sh,Sv,n_pts)
        curve1 = x1                   #SH=Sh
        curve2 = Pp+f*(x2-Pp)         #(SH-Pp)/(Sh-Pp)=f(mu)
        plt.rcParams['font.family']='Times new roman'
        fig, ax = plt.subplots(figsize=(8,8))
        ax.plot(x1,curve1,color='black')
        ax.plot(x2,curve2,color='red')
        ax.vlines(Sv,Sv,SH,linestyle='dashed',color='black')
        ax.vlines(Sh,Sh,Sv,color='black')
        ax.hlines(SH,Sv,SH,color='black')
        ax.hlines(Sv,Sh,Sv,linestyle='dashed',color='black')
        ax.fill_between(x2,Sv,curve2,alpha=0.1)
        ax.fill_between(x2,x2,Sv,alpha=0.1)
        ax.fill_between(np.linspace(Sv,SH,n_pts),np.linspace(Sv,SH,n_pts),SH,alpha=0.1)
        ax.set_xlabel(r'$S_{hmin}$'+f" [{self.unit}]")
        ax.set_ylabel(r'$S_{hmax}$'+f" [{self.unit}]")
        ax.text(0.9*(Sv+SH)/2,1.1*(Sv+SH)/2,'RF')
        ax.text((Sv+Sh)/2,0.9*(Sv+SH)/2,'SS')
        ax.text((Sv+Sh)/2-0.5*(Sv-Sh)/2,(Sv+Sh)/2+0.5*(Sv-Sh)/2,'NF')
        ax.set_ylim(Sh*0.8,SH*1.05)
        ax.set_xlim(Sh*0.8,SH*1.05)
        ax.grid()
        return ax,Sh,SH
    
    
    def lower_hemisphere(self,figsize=(10,10),s=300,ax=None,loc='best',*args,**kwargs):
        """
        stereographic projection of the three principal stress components in the geographic coordinate system
        """
        tr_mat = self.transfer_principal_to_geographic()
        trend2 = np.arctan2(tr_mat[0,1],tr_mat[1,1])
        plunge2 = np.arctan2(-tr_mat[2,1],np.sqrt(tr_mat[0,1]**2+tr_mat[1,1]**2))*(180/np.pi)
        trend1 = self.trend1*(np.pi/180)
        trend3 = self.trend3*(np.pi/180)
        plunge1 = self.plunge1
        plunge3 = self.plunge3
        plt.rcParams['font.size']=16
        if ax is None:
            fig= plt.figure(figsize=figsize)
            ax = plt.subplot(projection='polar')
        ax.scatter(trend1,abs(plunge1),marker='o',s=s,zorder=2,color='red',label=r'$S_1$')
        ax.scatter(trend2,abs(plunge2),marker='o',s=s,zorder=2,color='blue',label=r'$S_2$')
        ax.scatter(trend3,abs(plunge3),marker='o',s=s,zorder=2,color='green',label=r'$S_3$')
        ax.set_rlim(90,0)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rticks([30,60])
        ax.set_yticklabels([])
        ax.set_xticklabels(['N','NE','E','SE','S','SW','W','NW'])
        ax.legend(loc=loc,*args,**kwargs)
        return ax, trend2*(180/np.pi),plunge2

class Borehole:
    """ - borehole axes
            x : horizontal vector, perpendicular to borehole axis (x= y cross z)
            y : perpendicular to the borehole axis, pointing to the top generatrix of the borehole
            z : borehole axis, pointing to the surface
        radius in m    
        alpha : Biot coefficient (default : 1) → Used for Kirch
        nu : Poisson Coefficient (default : 0.25) → Used for Kirch
        Pm : Mud pressure
        Pp: Pore pressure
        mu : Fiction coefficient
        When considering an angle theta, and a position r, we have to retrieve the local srr and s00
        This matrix is a local orientation
    """
       
    inch=0.0254
    def __init__(self,azimuth,inclination,radius=0.1,alpha=1,nu=0.25,Pm=np.nan,Pp=np.nan,mu=np.nan):
        self.azimuth=azimuth
        self.inclination = inclination
        self.radius = radius
        self.biot = alpha
        self.poisson = nu # for stress concentration in deviated hole
        self.Pm=Pm
        self.Pp=Pp # will be read from stress class later
        self.mu = mu # friction coefficient
  
    ### stress applied on a borehole from geographic ###
    # swich from geographic to borehole
    def transfer_borehole_to_geographic(self):
        zb=-vector_from_trend_and_plunge(self.azimuth,90-self.inclination)
        yb=vector_from_trend_and_plunge(self.azimuth,-self.inclination)
        xb=np.cross(yb,zb)
        borehole_directions_in_geographic_coords = np.column_stack([xb,yb,zb])
        return borehole_directions_in_geographic_coords
        
    def transfer_geographic_to_borehole(self):
        return self.transfer_borehole_to_geographic().T

    def tensor_borehole_from_geographic(self,Sgeog):
        """
        tensor_geographic_from_borehole(self,Sgeog):
        Sgeog is a 3x3 matrix, generally built with the tensor_geographic() method of stress class
        """
        L_geographic_to_borehole = self.transfer_geographic_to_borehole()
        S_borehole=L_geographic_to_borehole @ Sgeog @ L_geographic_to_borehole.T
        #stress in the plane coordinate system
        return S_borehole

    def tensor_geographic_from_borehole(self,S_borehole):
        """
        tensor_geographic_from_borehole(self,S_borehole):
        S_borehole is a 3x3 matrix
        """
        L_geographic_to_borehole = self.transfer_geographic_to_borehole()
        S_geographic=L_geographic_to_borehole.T @ S_borehole @ L_geographic_to_borehole
        #stress in the plane coordinate system
        return S_geographic

    # def tensor_borehole(self,stress):
    #     """
    #     """
    #     self.Pp=stress.Pp # get pore pressure from stress data
    #     return self.tensor_borehole_from_geographic(stress.tensor_geographic())

    ### stress applied in the cylindrical system from borehole axes ###
    # swich from borehole to cylindrical

    def transfer_cylindrical_to_borehole(self,theta):
        er=vector_from_trend_and_plunge(90-theta,0)
        et=vector_from_trend_and_plunge(-theta,0)
        ez=np.array([0,0,1])
        cylindrical_directions_in_borehole_coords = np.column_stack([er,et,ez])
        return cylindrical_directions_in_borehole_coords 
    def transfer_borehole_to_cylindrical(self,theta):
        return self.transfer_cylindrical_to_borehole(theta).T
    def tensor_cylindrical_from_borehole(self,Sbor,theta):
        L_borehole_to_cylindrical = self.transfer_borehole_to_cylindrical(theta)
        S_cyl=L_borehole_to_cylindrical @ Sbor @ L_borehole_to_cylindrical.T
        #stress in the plane coordinate system
        return S_cyl
    def tensor_borehole_from_cylindrical(self,S_cyl,theta):
        L_borehole_to_cylindrical = self.transfer_borehole_to_cylindrical(theta)
        S_bor=L_borehole_to_cylindrical.T @ S_cyl@ L_borehole_to_cylindrical
        #stress in the plane coordinate system
        return S_bor

    ###  Stress concentration around a borehole ### 
    def compute_stress_pertubated_by_hole_cyl(self,s_far,r=np.nan,theta=0):
        """
        compute_stress_tensor_around_hole(s_far,r=np.nan,theta=0,Pm=0,Pp=0,alpha=1,nu=0.25)
        Compute stress concentration around a borehole, following Lee, JSPS, 2012
        S_far is a 3x3 matrix, generally built with the tensor_borehole() method of borehole class
        """
        
        out=np.zeros_like(s_far)
        
        alpha=self.biot
        nu=self.poisson
        
        a= self.radius
        if np.isnan(r):
            r = self.radius
    #    if (r<a).any():
    #        return None

        sxx=s_far[0][0];syy=s_far[1][1];szz=s_far[2][2];
        txy=s_far[0][1];txz=s_far[0][2];tyz=s_far[1][2];
        Pm=self.Pm
        Pp=self.Pp

        # srr
        s_r_r = (sxx+syy)/2*(1-np.square(a/r)) + (sxx-syy)/2*(1-4*np.square(a/r)+3*np.power(a/r,4))*cos(2*theta) \
                    + txy*(1-4*np.square(a/r)+3*np.power(a/r,4))*sin(2*theta) \
                    + Pm*np.square(a/r) - alpha* Pp
        out[0][0]=s_r_r

        # s theta theta
        s_theta_theta = (sxx+syy)/2*(1+np.square(a/r)) - (sxx-syy)/2*(1+3*np.power(a/r,4))*cos(2*theta)\
                        - txy*(1+3*np.power(a/r,4))*sin(2*theta) \
                        - Pm*np.square(a/r) - alpha* Pp
        out[1][1]=s_theta_theta
        
        # szz
        s_z_z = szz \
                - 2*nu* (sxx-syy) *np.square(a/r)* cos(2*theta)\
                - 4 * nu * txy * np.square(a/r)* sin(2*theta) \
                - alpha * Pp
        out[2][2]=s_z_z

        # tau r theta
        s_r_theta = ((sxx-syy)/2*sin(2*theta) + txy * cos(2*theta)) * (1+2*np.square(a/r)-3*np.power(a/r,4))
        out[0][1]=s_r_theta
        # tau r z
        s_r_z = (tyz*sin(theta)+txz*cos(theta))* (1-np.square(a/r))
        out[0][2]=s_r_z
        # tau y z
        s_theta_z = (-txz*sin(theta)+tyz*cos(theta))* (1+np.square(a/r))
        out[1][2]=s_theta_z

        # symmetric matrix
        out[1][0] = out[0][1]
        out[2][0] = out[0][2]
        out[2][1] = out[1][2]
        return out

    
    def compute_stress_pertubated_by_hole_geographic(self,stress,r=np.nan,theta=0):
        return self.tensor_geographic_from_borehole(
                self.tensor_borehole_from_cylindrical(
                    self.compute_stress_pertubated_by_hole_cyl(
                                self.tensor_borehole(stress),r,theta),theta))

    def stress_pertubated_by_hole_geographic(self,s0,r=np.nan,theta=0):
        """
        Output is a stress class
        """
        s=Stress(Pp=self.Pp)
        s.tensor_principal_from_geographic(self.compute_stress_pertubated_by_hole_geographic(s0,r,theta))
        return s

    def show_stress_pertubated_by_hole_geographic(self,stress):
        pass # to be implemented
    
    
    def breakout_angle(SHmax,Shmin,UCS,mu,Pw,Pp):
        """
        Compute the breakout angle using Shmin and Shmax
        """
        phi = np.arctan(mu)
        q=(1+np.sin(phi))/(1-np.sin(phi))
        theta = 0.5*np.arccos((SHmax+Shmin-UCS-(1+q)*(Pw-Pp))/(2*(SHmax+Shmin)))
        Wbo = np.pi-2*theta
        return Wbo*(180/np.pi)
    
    def principal_stress_direction(self,trend1,plunge1,trend3,plunge3):
        """
        Contructed rotation matrix in geographic coordinates
        """
        e1 = vector_from_trend_and_plunge(trend1,plunge1)
        e3 = vector_from_trend_and_plunge(trend3,plunge3)
        e2 = np.cross(e3,e1)
        return np.row_stack([e1,e2,e3])
    
    def borehole_directions(self,azimuth, inclination):
        e1 = vector_from_trend_and_plunge(azimuth+90,0)
        e2 = vector_from_trend_and_plunge(azimuth,-inclination)
        e3 = np.cross(e1,e2)
        return np.row_stack([e1,e2,e3])

    def failure_regions(self,S_ics,trend1=90,plunge1=0,trend3=0,
                        plunge3=-90,Si=np.nan,mu=0.6,nu=0,
                        n_r=200,n_theta=400,r_max=0.5):
        """
        Predicts the occurence of breakouts in a region around the borehole.
        Parameters:
            Stress:
            S_ics : Stress tensor in in-situ coordinate system, (diagonal matrix, 
                    with diagonal coefficient sigma_1, sigma_2, sigma_3)    
            trend 1, plunge 1 : sigma_1 orientation
            trend 3, plunge 3 : sigma_3 orientation

            Material rheology:
            Si :  Cohesion of the Mohr-Coulomb failure law (fracture creation)
                   = Intrisic shear strength of the intact rock matrix in Lee, 2012
            mu  :  internal friction coefficient 
            nu : Poisson ratino
            
            The occurence of failure will be checked on a annulus, gridded with 
            n_r : number of layers in the annular grid
            n_theta: number of angles in the annular grid
            r_max : maximum extent (radius) of the annular grid
        Returns
        """
        azimuth = self.azimuth 
        inclination = self.inclination
        a=self.radius
        Pw=self.Pm # Pwell = Pmud
        Pp=self.Pp
        alpha=self.biot
    
        ## Far field

        # Rotation matrix : principal stress direction to geographic 
        E = self.principal_stress_direction(trend1,plunge1,trend3,plunge3)

        # Rotation matrix : geographic to borehole
        B = self.borehole_directions(azimuth,inclination)

        S_ics2ecs = E.T@S_ics@E # In situ to geographic

        S_ecs2bcs = B@S_ics2ecs@B.T # From geographic to borehole.


        sxx=S_ecs2bcs[0,0]
        syy=S_ecs2bcs[1,1]
        szz=S_ecs2bcs[2,2]

        sxy=S_ecs2bcs[0,1]
        sxz=S_ecs2bcs[0,2]
        syz=S_ecs2bcs[1,2]

        ## Initialization
        # S_crit =np.zeros((n_theta, n_r))
        S_1 = np.zeros((n_theta, n_r))
        S_3 = np.zeros((n_theta, n_r))
        rock_failure = np.zeros((n_theta, n_r))
        # S_weakness = np.zeros((n_theta, n_r))
        # S_wn = np.zeros((n_theta, n_r))
        # tau_w = np.zeros((n_theta, n_r))
        srr = np.zeros((n_theta, n_r))
        stt = np.zeros((n_theta, n_r))
        szz_c = np.zeros((n_theta, n_r)) # new name to avoid confusion with stress in cartesian coordinates
        srt = np.zeros((n_theta, n_r))
        srz = np.zeros((n_theta, n_r))
        stz = np.zeros((n_theta, n_r))
        S_c = np.zeros((n_theta, n_r,3,3))
        # S_w = np.zeros((n_theta, n_r,3,3))

        for i in range(n_theta):
            t=(2*np.pi/n_theta)*i # theta in radian
            for j in range(n_r):
                r=a+(a/n_r)*j*r_max
                srr[i,j] =  (1/2)*(sxx+syy)*(1-(a/r)**2)+\
                            (1/2)*(sxx-syy)*(1-4*((a/r)**2)+3*((a/r)**4))*np.cos(2*t)+ \
                            sxy*(1-4*((a/r)**2)+3*((a/r)**4))*np.sin(2*t)+\
                            Pw*((a/r)**2)-alpha*Pp
                stt[i,j] =   (1/2)*(sxx+syy)*(1+(a/r)**2)\
                            -(1/2)*(sxx-syy)*(1+3*((a/r)**4))*np.cos(2*t)\
                            -sxy*(1+3*((a/r)**4))*np.sin(2*t)\
                            -Pw*((a/r)**2)-alpha*Pp
                szz_c[i,j] = szz -2*nu*(sxx-syy)*((a/r)**2)*np.cos(2*t)\
                            -4*nu*sxy*((a/r)**2)*np.sin(2*t)-alpha*Pp
                srt[i,j] = ((1/2)*(sxx-syy)*np.sin(2*t)+sxy*np.cos(2*t))*\
                            (1+2*((a/r)**2)-3*((a/r)**4))
                srz[i,j] = (syz*np.sin(t)+sxz*np.cos(t))*(1-((a/r)**2))
                stz[i,j] = (-sxz*np.sin(t)+syz*np.cos(t))*(1+((a/r)**2))

                # Stress in  cylindrical coordinates
                S_c[i,j] = np.array([[srr[i,j],srt[i,j],srz[i,j]],
                                     [srt[i,j],stt[i,j],stz[i,j]],
                                     [srz[i,j],stz[i,j],szz_c[i,j]]],float)
                # Diagonalisation of the local stress
                val = np.linalg.eig(S_c[i,j])[0]
                S_cp = val[val.argsort()].copy()
                S_3[i,j] = S_cp[0]
                S_1[i,j] = S_cp[2]
                if S_1[i,j]>=S_3[i,j]+2*(mu*S_3[i,j]+Si)*(np.sqrt(mu**2+1)+mu):
                    rock_failure[i,j] = 1
        a=self.radius            
        theta = np.linspace(0,2*np.pi,n_theta)
        r = np.linspace(a,1.5*a,n_r)
        r,t = np.meshgrid(r,theta)

        plt.rcParams['font.family']='times new roman'
        plt.rcParams['font.size']=15
        plt.figure(figsize=(10,10))
        ax1 = plt.subplot(projection='polar')
        b = ax1.pcolormesh(t,r,rock_failure,cmap='jet')
        ax1.set_yticklabels([])
        ax1.set_theta_zero_location('E')
        plt.colorbar(b,orientation = 'horizontal',fraction = 0.03)
        ax1.plot(0,0,'.k',marker = '+')
        
        return [ax1, rock_failure, S_1, S_3]


class Plane:
    def __init__(self,dipdir,dip, mu = 0.6, C0=0,
                 trend1=np.nan,plunge1=np.nan,trend3=np.nan,plunge3=np.nan,azimuth=np.nan,inclination=np.nan,
                radius=np.nan,Pm=np.nan,Pp=np.nan,biot=np.nan):
        """
        Plane(trend,plunge)
        defined from the plunging vector; with dipdir = trend and dip = plunge
        mu and C0 coefficient of Amonton; default mu =0.6 and null cohesion
        """
        self.dipdir = dipdir
        self.dip = dip
        self.mu = mu
        self.C0=C0
        self.trend1=trend1
        self.trend3=trend3
        self.plunge1=plunge1
        self.plunge3=plunge3
        self.azimuth=azimuth
        self.inclination=inclination
        self.radius=radius
        self.Pm=Pm
        self.Pp=Pp
        self.biot=biot
        
    def __repr__(self):
        return f"Plane of dip (=trend) {self.dip:.2f}° and azimut (=plunge) {self.dipdir:.2f}°"
    
    # stress applied on plane
    # note that this operation is not bijective
    def transfer_plane_to_geographic(self):
        """
        transfer_geographic_to_principal(dipdir,dip)

        Input 
            dipdir = azimut of the projection of the plunging plane vector onto an horizontal plane
            dir = dip of the maximum plunging plane vector relative to an horizontale plane

        Plane weakness axes
        #   x : plunging vector
        #   y : cross-product of both 
        #   z : normal vector

        Return transfer matrix enabling to pass from coefficients in the plane axes to to coefficients in the geographical axes
        """
        planePlungingVector = vector_from_trend_and_plunge(self.dipdir, self.dip)
        planeNormalVector = vector_from_trend_and_plunge(self.dipdir, self.dip - 90)
        planeHorVector = np.cross(planeNormalVector, planePlungingVector) #horizontal vector
        plane_directions_in_geographic_coords = np.column_stack([planePlungingVector, 
                                                                 planeHorVector, 
                                                                 planeNormalVector])
        return plane_directions_in_geographic_coords

    def transfer_geographic_to_plane(self):
        return self.transfer_plane_to_geographic().T

    def tensor_plane_from_geographic(self,stress):
        L_geographic_to_plane = self.transfer_geographic_to_plane()
        sigmaPlane=L_geographic_to_plane @ stress.tensor_geographic() @ L_geographic_to_plane.T
        #stress in the plane coordinate system
        return sigmaPlane

    def normal_stress_from_geographic(self,stress):
        sigmaPlane=self.tensor_plane_from_geographic(stress)
        #stress in the fault-normal direction:
        return sigmaPlane[2, 2]

    def shear_stress_from_geographic(self,stress):
        sigmaPlane=self.tensor_plane_from_geographic(stress)
        #eq 2.120: (l, m, n) is the 3rd line of LprincToPlane: vector coord normal to plane in the ref of principal coordinates
        tau = np.sqrt( np.square(sigmaPlane[0, 2]) + np.square(sigmaPlane[1, 2]) )
        #stress in the fault-normal direction:
        return tau

    def stress_applied_on_plane(self,stress):
        """
        Input 
            Stress : stress object 
            
        Output
        [sigma_n, tau]
        """
        sigmaPlane=self.tensor_plane_from_geographic(stress)
        sigma_n=sigmaPlane[2, 2]
        tau = np.sqrt( np.square(sigmaPlane[0, 2]) + np.square(sigmaPlane[1, 2]) )                                     
        return sigma_n,tau
    
    def will_fail(self,stress,n_pts=200,colorbar=False):
        """
        Amonton's law to predict the distance to failure:
        computes the distance to failure (Coulomb stress change)

        Stress = tensor (np.array) with principal stress. (diagonal matrix)

        """
        mu = self.mu
        C0 = self.C0

        sigma_i =self.stress_applied_on_plane(stress)[0]    #coordonnees du plan sur le cercle de mohr
        tau_i = self.stress_applied_on_plane(stress)[1]
        dist_to_fail = np.abs(mu*sigma_i-tau_i+C0)/np.sqrt(np.power(mu,2)+1)
        y_i = mu*sigma_i+C0
        if y_i > tau_i:
            x_intersect = sigma_i - dist_to_fail*np.sin(np.arctan(mu))
            y_intersect = mu*x_intersect+C0
        else:
            x_intersect = sigma_i + dist_to_fail*np.sin(np.arctan(mu))
            y_intersect = mu*x_intersect+C0
        plt.rcParams['font.family']='times new roman'    

        x = np.linspace(0,(stress.S1-stress.Pp)*5,500)
        y1 = np.zeros(np.shape(x))
        y2 = mu*x+C0


        fig, ax=plt.subplots(figsize=(15,20))
        a1 = plt.Circle(((stress.S1+stress.S3)/2-stress.Pp,0),(stress.S1-stress.S3)/2,color='none',ec='k')
        ax.add_patch(a1)
        polygon = ax.fill_between(x, y1, y2, lw=0, color='none')
        ylim = ax.set_ylim()
        verts = np.vstack([p.vertices for p in polygon.get_paths()])
        ymin, ymax = verts[:, 1].min(), verts[:, 1].max()
        gradient = ax.imshow(np.array([np.interp(np.linspace(ymin, ymax, n_pts), [y1i, y2i], np.arange(2))
                                    for y1i, y2i in zip(y1, y2)]).T,
                          cmap='jet', aspect='equal', origin='lower', extent=[x.min(), x.max(), ymin,ymax])
        gradient.set_clip_path(a1)
        a2 = plt.Circle(((stress.S1+stress.S2)/2-stress.Pp,0),(stress.S1-stress.S2)/2,color='white',ec='k')
        a3 = plt.Circle(((stress.S2+stress.S3)/2-stress.Pp,0),(stress.S2-stress.S3)/2,color='white',ec='k')
        ax.add_patch(a2)
        ax.add_patch(a3)
        ax.plot(x,mu*x+C0,label=r'$\tau$'+f"$={mu}\sigma_n'+{C0}$")
        ax.plot(sigma_i-self.Pp,tau_i,marker='o',color='black')
        ax.set_ylim(0,((stress.S1-stress.S3)/2)*1.1)
        ax.set_xlim(0,(stress.S1-stress.Pp)*1.1)
        ax.text(sigma_i-self.Pp,tau_i,f'({self.dipdir},{self.dip})')
        ax.legend(loc='best')
        ax.set_xlabel(f"$\sigma_n'$ [{stress.unit}]")
        ax.set_ylabel(r'$\tau$ '+f"[{stress.unit}]")
        ax.set_title('Normalized slip tendency')
        if colorbar:
            plt.colorbar(gradient,ax=ax,label='slip tendency')
        return bool(y_i < tau_i),dist_to_fail,ax  # to implement; use Amonton's law

    def principal_stress_direction(self,trend1,plunge1,trend3,plunge3):
        e1 = vector_from_trend_and_plunge(trend1,plunge1)
        e3 = vector_from_trend_and_plunge(trend3,plunge3)
        e2 = np.cross(e3,e1)
        return np.row_stack([e1,e2,e3])
    
    def borehole_directions(self,azimuth, inclination):
        e1 = vector_from_trend_and_plunge(azimuth+90,0)
        e2 = vector_from_trend_and_plunge(azimuth,-inclination)
        e3 = np.cross(e1,e2)
        return np.row_stack([e1,e2,e3])
    
    def plane_directions(self):
        yp = vector_from_trend_and_plunge(self.dipdir,self.dip)
        zp = vector_from_trend_and_plunge(self.dipdir,self.dip-90)
        xp = np.cross(yp,zp)
        return np.row_stack([xp,yp,zp])
    
    def failure_regions(self,S_ics,trend1=np.nan,plunge1=np.nan,trend3=np.nan,
                        plunge3=np.nan,Sw=np.nan,UCS=np.nan,nu=np.nan,mu_w=np.nan,inclination=np.nan,azimuth=np.nan,
                        n_theta=400,n_r=200):
        
        self.trend1=trend1
        self.trend3=trend3
        self.plunge1=plunge1
        self.plunge3=plunge3
        a=self.radius
        Pw=self.Pm # Pwell = Pmud
        Pp=self.Pp
        alpha=self.biot
        self.inclination=inclination
        self.azimuth=azimuth
        dipdir=self.dipdir
        dip=self.dip
        
        E = self.principal_stress_direction(trend1,plunge1,trend3,plunge3)
        
        B = self.borehole_directions(azimuth,inclination)
        
        W = self.plane_directions(dipdir,dip)

        S_ics2ecs = E.T@S_ics@E

        S_ecs2bcs = B@S_ics2ecs@B.T


        sxx=S_ecs2bcs[0,0]
        syy=S_ecs2bcs[1,1]
        szz=S_ecs2bcs[2,2]

        sxy=S_ecs2bcs[0,1]
        sxz=S_ecs2bcs[0,2]
        syz=S_ecs2bcs[1,2]

        S_crit =np.zeros((n_theta, n_r))
        S_1 = np.zeros((n_theta, n_r))
        S_3 = np.zeros((n_theta, n_r))
        rock_failure = np.zeros((n_theta, n_r))
        S_weakness = np.zeros((n_theta, n_r))
        S_wn = np.zeros((n_theta, n_r))
        tau_w = np.zeros((n_theta, n_r))
        srr = np.zeros((n_theta, n_r))
        stt = np.zeros((n_theta, n_r))
        szz_c = np.zeros((n_theta, n_r))
        srt = np.zeros((n_theta, n_r))
        srz = np.zeros((n_theta, n_r))
        stz = np.zeros((n_theta, n_r))
        S_c = np.zeros((n_theta, n_r,3,3))
        S_w = np.zeros((n_theta, n_r,3,3))

        for i in range(n_theta):
            t=(2*np.pi/n_theta)*i
            for j in range(n_r):
                r=a+(a/n_r)*j*0.5
                srr[i,j] = (1/2)*(sxx+syy)*(1-(a/r)**2)+(1/2)*(sxx-syy)*(1-4*((a/r)**2)+3*((a/r)**4))*np.cos(2*t)+sxy*(1-4*((a/r)**2)+3*((a/r)**4))*np.sin(2*t)+Pw*((a/r)**2)-alpha*Pp
                stt[i,j] = (1/2)*(sxx+syy)*(1+(a/r)**2)-(1/2)*(sxx-syy)*(1+3*((a/r)**4))*np.cos(2*t)-sxy*(1+3*((a/r)**4))*np.sin(2*t)-Pw*((a/r)**2)-alpha*Pp
                szz_c[i,j] = szz -2*nu*(sxx-syy)*((a/r)**2)*np.cos(2*t)-4*sxy*((a/r)**2)*np.sin(2*t)-alpha*Pp
                srt[i,j] = ((1/2)*(sxx-syy)*np.sin(2*t)+sxy*np.cos(2*t))*(1+2*((a/r)**2)-3*((a/r)**4))
                srz[i,j] = (syz*np.sin(t)+sxz*np.cos(t))*(1-((a/r)**2))
                stz[i,j] = (-sxz*np.sin(t)+syz*np.cos(t))*(1+((a/r)**2))
                S_c[i,j] = np.array([[srr[i,j],srt[i,j],srz[i,j]],[srt[i,j],stt[i,j],stz[i,j]],[srz[i,j],stz[i,j],szz_c[i,j]]],float)
                val = np.linalg.eig(S_c[i,j])[0]
                S_cp = val[val.argsort()].copy()
                S_3[i,j] = S_cp[0]
                S_1[i,j] = S_cp[2]
                C = np.array([[np.cos(t),np.sin(t),0],[-np.sin(t),np.cos(t),0],[0,0,1]],float)
                S_w[i,j] = W@B.T@C.T@S_c[i,j]@C@B@W.T
                S_wn[i,j] = S_w[i,j,2,2]
                tau_w[i,j] = np.sqrt(S_w[i,j,2,0]**2+S_w[i,j,2,1]**2)
                if (tau_w[i,j]>=Sw+mu_w*S_wn[i,j]):
                    S_weakness[i,j]=1
        
        
        a=self.radius            
        theta = np.linspace(0,2*np.pi,n_theta)
        r = np.linspace(a,1.5*a,n_r)
        r,t = np.meshgrid(r,theta)

        plt.rcParams['font.family']='times new roman'
        plt.rcParams['font.size']=15
        plt.figure(figsize=(10,10))
        ax1 = plt.subplot(projection='polar')
        b = ax1.pcolormesh(t,r,S_weakness,cmap='jet')
        ax1.set_yticklabels([])
        ax1.set_theta_zero_location('E')
        plt.colorbar(b,orientation = 'horizontal',fraction = 0.03)
        ax1.plot(0,0,'.k',marker = '+')
        
        return [ax1, S_weakness, S_1, S_3]

    
