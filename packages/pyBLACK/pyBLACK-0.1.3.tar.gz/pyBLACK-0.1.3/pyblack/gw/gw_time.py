import numpy as np
import multiprocessing as mp
from scipy.integrate import solve_ivp
import pickle
import os

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


from .. import constants as cost

#Constants
G3_AU=cost.G_AUMsunyr**3.
c5_AU=cost.c_AUyr**5.

def _dfdt_Peters(t,y,m1,m2,rlo):
    """
    Da/Dt and De/Dt due to gravitational wave from Peters64, the units are AU, Msun, yr
    :param t: Time, this parameters is unused but it is required by some scipy ode integrator.
    :param y: A 2D array or vector containing a and e, a is un AU
    :param m1: Mass of the first star in Msun
    :param m2: Mass of the second star in Msun
    :param rlo: Last stable circular orbit (3xRs) in AU
    :return: Array containing da/dt (AU/yr) and de/dt (AU/yr)
    """
    a,e=y
    if e<0: e=0
    if a<0: a=1e-20

    cost = G3_AU * m1 * m2 * (m1+m2) / c5_AU


    fa=-64./5.* cost /(a*a*a * (1-e*e)**3.5) * (1.+73./24.*e*e+37./96. * e * e * e * e) #AU/yr
    fe=-304./15. * cost * e /(a*a*a*a * (1-e*e)**2.5) * (1.+121./304. * e * e) #/yr

    return np.array([fa,fe])

def _Jacobian_Peters(t,y,m1,m2,rlo):
    """
    Jacobin of the da/dt and de/dt from Peter64, the units are AU, Msun, yr.
    :param t: Time, this parameters is unused but it is required by some scipy ode integrator.
    :param y: A 2D array or vector containing a and e, a is un AU
    :param m1: Mass of the first star in Msun
    :param m2: Mass of the second star in Msun
    :param rlo: Last stable circular orbit (3xRs) in AU
    :return:  2x2 numpy array [[dfa/da, dfa/de],[dfe/da,dfe/de]]
    """

    a,e=y
    if e<0: e=0
    if a<0: a=1e-20

    cost = G3_AU * m1 * m2 * (m1+m2) / c5_AU

    dfa_da = (3/(a*a*a*a)) * ( 64./5.* cost /((1-e*e)**3.5) * (1.+73./24.*e*e+37./96. * e * e * e * e))
    dfa_de =  (  ( (73/12*e + 37/24*e*e*e)/(1-e*e)**3.5 )    +  ( (7*e) * (1.+73./24.*e*e+37./96. * e * e * e * e)/(1-e*e)**4.5 ) ) * (-64/5*cost/(a*a*a))

    dfe_da = (4/(a*a*a*a*a)) * (304./15. * cost * e /((1-e*e)**2.5) * (1.+121./304. * e * e))
    dfe_de =  (e*( ( (121/152*e)/((1-e*e)**2.5) )  + ( (5*e)*(1+121/304*e*e)/((1-e*e)**3.5)  ) ) + ((1.+121./304. * e * e)/(1-e*e)**2.5) ) *  (-304./15. * cost)/(a*a*a*a)

    return np.array([[dfa_da, dfa_de],[dfe_da,dfe_de]])

def _is_outside_rlo(t,y,m1,m2,rlo):
    """
    Event check  used in solve_ivp
    :param t: Time, this parameters is unused but it is required by some scipy ode integrator.
    :param y: A 2D array or vector containing a and e, a is un AU
    :param m1: Mass of the first star in Msun
    :param m2: Mass of the second star in Msun
    :param rlo: Last stable circular orbit (3xRs) in AU
    :return: if inside rlo return 0, else 1
    """

    a=y[0]

    return a>rlo

_is_outside_rlo.terminal=True

def _estimate_tgw_lsoda_single(a,e,m1,m2,rlo, t_integration=1e40, use_Jacobian=False):
    """
    This function integrate the da/dt-de/dt Peters64 system.
    It uses the LSODA method (see scipy documentation) and stop when a is lower than the rlo or if t>t_integration.
    :param a: Initial semi major axis in AU
    :param e:  Initial eccentricity
    :param m1: Mass of the first star in Msun
    :param m2: Mass of the second star in Msun
    :param rlo: Last stable circular orbit (3xRs) in AU
    :param t_integration:  Integration time in yr
    :param use_Jacobian: If True use the Jacobian of the ode system.
    :return:  If something went wrong in the integration return nan,
    if the event a<rlo is triggered return the time of the event otherwise return the integration time.
    """

    if use_Jacobian: J=_Jacobian_Peters
    else: J=None

    intrk = solve_ivp(_dfdt_Peters, [0,t_integration],  [a,e], jac=J, method="LSODA", min_step=cost.cgs_to_yr*1e-3, rtol=1e-8, events=_is_outside_rlo,  args=(m1,m2,rlo), vectorized=False)
    status = intrk.status

    if status==0:   tdel=t_integration
    elif status==1: tdel  = intrk.t_events[0]
    else: tdel=np.nan

    return tdel


def _euler(a,e,m1,m2,h):
    fa,fe=_dfdt_Peters(1,[a,e],m1,m2,1)
    anew = a + fa*h
    enew = e + fe*h

    return anew,enew

def _runge4(a,e,m1,m2,h):
    #runge kutta 4 scheme needs 5 scalar floats:
    # m1: primary mass/Msun
    # m2: secondary mass/Msun
    # a:  semi-major axis /AU
    # e:  eccentricity
    # h:  timestep/yr (timestep is variable)

    fa,fe=_dfdt_Peters(1,[a,e],m1,m2,1)

    k1a=h*fa #0.5*h*fa
    k1e=h*fe #0.5*h*fe

    fa2,fe2=_dfdt_Peters(1,[a+(0.5*k1a),e+(0.5*k1e)],m1,m2,1)

    k2a=h*fa2 #0.5*h*fa2
    k2e=h*fe2 #0.5*h*fe2

    fa3,fe3=_dfdt_Peters(1,[a+(0.5*k2a),e+(0.5*k2e)],m1,m2,1)

    k3a=h*fa3
    k3e=h*fe3

    fa4,fe4=_dfdt_Peters(1,[a+k3a,e+k3e],m1,m2,1)

    k4a=h*fa4
    k4e=h*fe4

    anew=a + (1./6.) * (k1a + 2.*k2a + 2.*k3a + k4a)
    enew=e + (1./6.) * (k1e + 2.*k2e + 2.*k3e + k4e)

    return anew,enew #outputs are semi-major axis, eccentricity at time t+h



def _estimate_tgw_single_adaptiveRK(a,e,m1,m2,rlo,toll=1e-2,h_adaptive_increase=2,h_adaptive_decrease=10):

    t = 0
    h = 3.17098e-8 #1 secondo
    h_adaptive_increase = h_adaptive_increase
    h_adaprive_decrease = h_adaptive_decrease
    toll = toll
    aold=a
    eold=e

    while(aold>=rlo):
        anew,enew=_runge4(aold,eold,m1,m2,h)

        if(abs(anew-aold)/aold<(0.1*toll)): #set adaptive timestep
            h=h*h_adaptive_increase
            anew,enew=_runge4(aold,eold,m1,m2,h)

        elif(abs(anew-aold)/aold>toll):
            while(abs(anew-aold)/aold>toll):
                h=h/h_adaprive_decrease
                anew,enew=_runge4(aold,eold,m1,m2,h)
        t+=h
        aold=anew
        eold=enew

    return t

def _estimate_tgw_single_adaptiveeuler(a,e,m1,m2,rlo,toll=1e-2,h_adaptive_increase=2,h_adaptive_decrease=10):

    t = 0
    h = 3.17098e-8 #1 secondo
    h_adaptive_increase = h_adaptive_increase
    h_adaprive_decrease = h_adaptive_decrease
    toll = toll
    aold=a
    eold=e

    while(aold>=rlo):
        anew,enew=_euler(aold,eold,m1,m2,h)

        if(abs(anew-aold)/aold<(0.1*toll)): #set adaptive timestep
            h=h*h_adaptive_increase
            anew,enew=_euler(aold,eold,m1,m2,h)

        elif(abs(anew-aold)/aold>toll):
            while(abs(anew-aold)/aold>toll):
                h=h/h_adaprive_decrease
                anew,enew=_euler(aold,eold,m1,m2,h)
        t+=h
        aold=anew
        eold=enew

    return t

def fTgw(a,e,m1,m2):

    return 5. / 256. * c5_AU / G3_AU * a * a * a * a * (1. - e * e) ** 3.5 / (
                        m1 * m2 * (m1 + m2))

def fTpeters(a,e,m1,m2):

    return fTgw(a,e,m1,m2)/(1+73./24.*e*e + 37./96.*e*e*e*e)


def _Tzwick(a,e,m1,m2):

    return fTpeters(a,e,m1,m2)*8**(1-np.sqrt(1-e))

def _TIorio(a,e,m1,m2):

    e2=e*e
    exponent = 1.105 - 0.807*e +0.193*e2
    base = 1-e**3.074

    fcorr = e2*(-0.443 + 0.580*base**exponent)

    return fTgw(a,e,m1,m2)/(1+fcorr)

_allowed_methods = ("gw","peters","interpolation","iorio22","zwick20","combined","lsoda","adaptiverk","adaptiveeuler")
def estimate_tgw(a,e,m1,m2, method="combined", nproc=1, a_Rsun=False, use_Jacobian=False, spline=True,toll=1e-2,h_adaptive_increase=2,h_adaptive_decrease=10):
    """
    Estimate the Gravitational Wave time defined as the time needed to a binary system to shrink the semimajor axis
    to value smaller than the last stable circular orbit.
    :param a:  Semi-major axis in AU
    :param e:  Eccentricity
    :param m1: Mass of the first star  in Msun
    :param m2: Mass of the second star in Msun
    :param method: it can be:
        - peters: classic time scale for gw from Peters64
        - gw: Peters 64 time scale without the factor (1+73./24.*e*e + 37./96.*e*e*e*e)
        - interpolation: gw time scale corrected for the eccentricity (tuned on integrated results)
        - iorio22: gw time scale corrected for the eccentricity based on analytic fit of the residuals (tuned on integrated results), see Iorio+22
        - zwick20: peters time scale corrected for the eccentricity based on analytic fit of the residuals (tuned on integrated results), see Zwick+20
        - combined: use iorio22 for e<0.999, otherwise zwick20
        - lsoda: ode integration with LSODA method (Adams/BDF method with automatic stiffness detection and switching) thorugh the scipy solve_ivp
        - adaptiverk: 4th order Runge-Kutta with adaptive time step. If thea variation between two steps is smaller than
        0.1*toll (see below) the time step is increased of the  factor h_adaptive_increase (see below), if the varaition if larger than the tollerance
        the time  step is decreased of the factor h_adaptive_decrease (see below).
    :param options: Options passed to a chosen method. All options available for already implemented methods are listed below.
    :param nproc: Number of processes to be used, available for lsoda and adaptiverk.
    :param a_Rsun: if True a are in Rsun units otherwise AU
    :param use_Jacobian: Use Jacobian instead of finite diffirence, available for lsoda
    :param spline: If True correct the Peters formula using the interpolation for the correcting term, otherwise use  a fitting formula, available for cured_peters
    :param toll: relative tollerance target to use in the a estimate, available for adaptive_rk
    :param h_adaptive_increase: increasing factor for the time step,
    :param h_adaptive_decrease: decreasing factor for the time step.
    :return: Numpy array containing the  time estimate (Myr) when the separation of the two object is smaller than the last stable orbit.
    """

    method = method.lower()
    if method not in _allowed_methods:
        availabe_methods = ", ".join(_allowed_methods)
        raise ValueError("The function estimate_tgw does not implement the method \'%s\'. "
                         "Available methods are: "%method + availabe_methods + ".")

    a=np.atleast_1d(a)
    if a_Rsun: a=a*cost.Rsun_to_AU
    e=np.atleast_1d(e)
    m1=np.atleast_1d(m1)
    m2=np.atleast_1d(m2)

    fRLO     =  lambda mass: 6.*cost.G_AUMsunyr*mass/ (cost.c_AUyr*cost.c_AUyr)

    if method=="peters":

        tdel_array = fTpeters(a,e,m1,m2) # Tpeters in yr

    elif method=="gw":

        tdel_array = fTgw(a,e,m1,m2)

    elif method=="zwick20":

        tdel_array=_Tzwick(a,e,m1,m2)

    elif method=="iorio22":

        tdel_array=_TIorio(a,e,m1,m2)

    elif method=="combined":

        tdel_array=np.where(e>0.999,_Tzwick(a,e,m1,m2),_TIorio(a,e,m1,m2))

    elif method=="interpolation":

        if spline:
            data_file_path = os.path.abspath(os.path.dirname(__file__)) + "/ext_data/"
            with open(data_file_path+'/cured_gw_time.interpolation','rb') as infile:
                cured = pickle.load(infile)
        else:
            pvalue  = [0.00185429, -0.00628489,  0.00704127, -0.0026295]
            escale = 0.10055517
            cured   = lambda x:  (pvalue[0] + pvalue[1]*x + pvalue[2]*x*x + pvalue[3]*x*x*x)*np.exp(x/escale)

        Tpeters = fTgw(a,e,m1,m2)
        tdel_array = Tpeters/(1+cured(e))

    elif method=="lsoda":

        Tpeters = fTgw(a,e,m1,m2)  # Tpeters in yr

        Mmax = np.where(m1>m2, m1,m2)
        RLO =  fRLO(Mmax) #3*Schw. radius of bh in AU

        if nproc==1:
            tdel_array = np.zeros(len(a))
            for i in range(len(a)):
                tdel_array[i] =_estimate_tgw_lsoda_single(a[i], e[i], m1[i], m2[i], RLO[i], t_integration=100*Tpeters[i], use_Jacobian=use_Jacobian)
        else:
            data_arr = np.vstack((a,e,m1,m2,RLO,100*Tpeters)).T
            with mp.Pool(nproc) as pool:
                tdel_array = pool.starmap(_estimate_tgw_lsoda_single, data_arr)

            tdel_array=np.array(tdel_array).flatten()

    elif method=="adaptiverk":

        Mmax = np.where(m1>m2, m1,m2)
        RLO =  fRLO(Mmax) #3*Schw. radius of bh in AU

        if nproc==1:
            tdel_array = np.zeros(len(a))
            for i in range(len(a)):
                tdel_array[i] =_estimate_tgw_single_adaptiveRK(a[i], e[i], m1[i], m2[i],  RLO[i], toll, h_adaptive_increase, h_adaptive_decrease)
        else:
            data_arr = np.vstack((a,e,m1,m2, RLO, toll*np.ones(len(a)), h_adaptive_increase*np.ones(len(a)), h_adaptive_decrease*np.ones(len(a)))).T
            with mp.Pool(nproc) as pool:
                tdel_array = pool.starmap(_estimate_tgw_single_adaptiveRK, data_arr)
            tdel_array=np.array(tdel_array).flatten()

    elif method=="adaptiveeuler":

            Mmax = np.where(m1>m2, m1,m2)
            RLO =  fRLO(Mmax) #3*Schw. radius of bh in AU

            if nproc==1:
                tdel_array = np.zeros(len(a))
                for i in range(len(a)):
                    tdel_array[i] =_estimate_tgw_single_adaptiveeuler(a[i], e[i], m1[i], m2[i],  RLO[i], toll, h_adaptive_increase, h_adaptive_decrease)
            else:
                data_arr = np.vstack((a,e,m1,m2, RLO, toll*np.ones(len(a)), h_adaptive_increase*np.ones(len(a)), h_adaptive_decrease*np.ones(len(a)))).T
                with mp.Pool(nproc) as pool:
                    tdel_array = pool.starmap(_estimate_tgw_single_adaptiveeuler, data_arr)
                tdel_array=np.array(tdel_array).flatten()


    return tdel_array*cost.yr_to_Myr
