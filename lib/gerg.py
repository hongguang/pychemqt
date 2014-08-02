#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################
###  Implementación de la EoS GERG-2004 y ampliaci´on 2008 ###
##########################################

import cPickle, os

from scipy import exp, log, zeros
from scipy.constants import R
from scipy.optimize import fsolve

import unidades
from physics import R_atml
from lib import mEoS
from lib.config import fluid

Tref=298.15
Pref=101325.
#so=0
#ho=0

class GERG(object):
    """Ecuación de estado para gases naturales, GERG 2008
    ref http://dx.doi.org/10.1021/je300655b"""
    kwargs={"componente": [],
                    "fraccion": [], 
                    "T": 0.0,
                    "rho": 0.0, 
                    "P": 0.0,
                    "v": 0.0,
                    "h": None, 
                    "s": None, 
                    "u": None, 
                    "x": None, 
                    "mezcla": None}

    componentes=[mEoS.CH4.CH4, mEoS.N2.N2, mEoS.CO2.CO2, mEoS.C2.C2, mEoS.C3.C3, mEoS.nC4.nC4, mEoS.iC4.iC4, mEoS.nC5.nC5, mEoS.iC5.iC5, mEoS.nC6.nC6, mEoS.nC7.nC7, mEoS.nC8.nC8, mEoS.H2.H2, mEoS.O2.O2, mEoS.CO.CO, mEoS.H2O.H2O, mEoS.He.He, mEoS.Ar.Ar, mEoS.H2S.H2S, mEoS.nC9.nC9, mEoS.nC10.nC10]

    Fij=cPickle.load(open(os.environ["pychemqt"]+"dat/mEoS_Fij.pkl"))
    Prop_c=cPickle.load(open(os.environ["pychemqt"]+"dat/mEoS_Tc.pkl"))

    fir_ij={
        "0-1":{
            "nr1":  [-0.98038985517335e-2, 0.42487270143005e-3],
            "d1": [1, 4],
            "t1": [0.000, 1.850],

            "nr2": [-0.34800214576142e-1, -0.13333813013896, -0.11993694974627e-1, 0.69243379775168e-1, -0.31022508148249, 0.24495491753226, 0.22369816716981],
            "d2": [1, 2, 2, 2, 2, 2, 3],
            "t2": [7.850, 5.400, 0.000, 0.750, 2.800, 4.450, 4.250],
            "n2": [1, 1, 0.25, 0, 0, 0, 0],
            "e2": [0.5]*7,
            "b2": [1, 1, 2.5, 3, 3, 3, 3],
            "g2": [0.5]*7},

        "0-2":{
            "nr1": [-0.10859387354942, 0.80228576727389e-1, -0.93303985115717e-2],
            "d1": [1, 2, 3],
            "t1": [2.6, 1.95, 0],

            "nr2": [0.40989274005848e-1, -0.24338019772494, 0.23855347281124],
            "d2": [1, 2, 3],
            "t2": [3.95, 7.95, 8],
            "n2": [1, 0.5, 0],
            "e2": [0.5]*3,
            "b2": [1, 2, 3],
            "g2": [0.5]*3},

        "0-3":{
            "nr1": [-0.80926050298746e-3, -0.75381925080059e-3],
            "d1": [3, 4],
            "t1": [0.65, 1.55],

            "nr2": [-0.41618768891219e-1, -0.23452173681569, 0.14003840584586, 0.63281744807738e-1, 0-.34660425848809e-1, -0.23918747334251, 0.19855255066891e-2, 0.61777746171555e1, -0.69575358271105e1, 0.10630185306388e1],
            "d2": [1, 2, 2, 2, 2, 2, 2, 3, 3, 3],
            "t2": [3.100, 5.900, 7.050, 3.350, 1.200, 5.800, 2.700, 0.450, 0.550, 1.950],
            "n2": [1, 1, 1, 0.875, 0.75, 0.5, 0, 0, 0, 0],
            "e2": [0.5]*10,
            "b2": [1, 1, 1, 1.25, 1.5, 2, 3, 3, 3, 3],
            "g2": [0.5]*10},

        "0-4":{
            "nr1": [0.13746429958576e-1, -0.74425012129552e-2, -0.45516600213685e-2, -0.54546603350237e-2, 0.23682016824471e-2],
            "d1": [3, 3, 4, 4, 4],
            "t1": [1.85, 3.95, 0, 1.85, 3.85],

            "nr2": [0.18007763721438, -0.44773942932486, 0.19327374888200e-1, -0.30632197804624],
            "d2": [1, 1, 1, 2],
            "t2": [5.25, 3.85, 0.2, 6.5],
            "n2": [0.25, 0.25, 0, 0],
            "e2": [0.5, 0.5, 0.5, 0.5],
            "b2": [0.75, 1, 2, 3],
            "g2": [0.5, 0.5, 0.5, 0.5]},

        "1-2":{
            "nr1": [0.28661625028399, -0.10919833861247],
            "d1": [2, 3],
            "t1": [1.85, 1.4],

            "nr2": [-0.11374032082270e1, 0.76580544237358, 0.42638000926819e-2, 0.17673538204534],
            "d2": [1, 1, 1, 2],
            "t2": [3.2, 2.5, 8, 3.75],
            "n2": [0.25, 0.25, 0, 0],
            "e2": [0.5, 0.5, 0.5, 0.5],
            "b2": [0.75, 1., 2., 3.],
            "g2": [0.5, 0.5, 0.5, 0.5]},

        "1-3":{
            "nr1": [-0.47376518126608, 0.48961193461001, -0.57011062090535e-2],
            "d1": [2, 2, 3],
            "t1": [0, 0.05, 0],

            "nr2": [-0.19966820041320, -0.69411103101723, 0.69226192739021],
            "d2": [1, 2, 2],
            "t2": [3.65, 4.9, 4.45],
            "n2": [1, 1, 0.875],
            "e2": [0.5, 0.5, 0.5],
            "b2": [1, 1, 1.25],
            "g2": [0.5, 0.5, 0.5]},

        "0-12":{
            "nr1": [-0.25157134971934, -0.62203841111983e-2, 0.88850315184396e-1, -0.35592212573239e-1],
            "d1": [1, 3, 3, 4],
            "t1": [2, -1, 1.75, 1.4],
            "nr2": []},

        "0-5":{
            "nr1": [0.25574776844118e1, -0.79846357136353e1, 0.47859131465806e1, -0.73265392369587, 0.13805471345312e1, 0.28349603476365, -0.49087385940425, -0.10291888921447, 0.11836314681968, 0.55527385721943e-4],
            "d1": [1, 1, 1, 2, 2, 3, 3, 4, 4, 4],
            "t1": [1.000, 1.550, 1.700, 0.250, 1.350, 0.000, 1.250, 0.000, 0.700, 5.400],
            "nr2":[]},

        "0-6":{
            "nr1": [0.25574776844118e1, -0.79846357136353e1, 0.47859131465806e1, -0.73265392369587, 0.13805471345312e1, 0.28349603476365, -0.49087385940425, -0.10291888921447, 0.11836314681968, 0.55527385721943e-4],
            "d1": [1, 1, 1, 2, 2, 3, 3, 4, 4, 4],
            "t1": [1.000, 1.550, 1.700, 0.250, 1.350, 0.000, 1.250, 0.000, 0.700, 5.400],
            "nr2":[]},

        "3-4":{
            "nr1": [0.25574776844118e1, -0.79846357136353e1, 0.47859131465806e1, -0.73265392369587, 0.13805471345312e1, 0.28349603476365, -0.49087385940425, -0.10291888921447, 0.11836314681968, 0.55527385721943e-4],
            "d1": [1, 1, 1, 2, 2, 3, 3, 4, 4, 4],
            "t1": [1.000, 1.550, 1.700, 0.250, 1.350, 0.000, 1.250, 0.000, 0.700, 5.400],
            "nr2":[]},

        "3-5":{
            "nr1": [0.25574776844118e1, -0.79846357136353e1, 0.47859131465806e1, -0.73265392369587, 0.13805471345312e1, 0.28349603476365, -0.49087385940425, -0.10291888921447, 0.11836314681968, 0.55527385721943e-4],
            "d1": [1, 1, 1, 2, 2, 3, 3, 4, 4, 4],
            "t1": [1.000, 1.550, 1.700, 0.250, 1.350, 0.000, 1.250, 0.000, 0.700, 5.400],
            "nr2":[]},

        "3-6":{
            "nr1": [0.25574776844118e1, -0.79846357136353e1, 0.47859131465806e1, -0.73265392369587, 0.13805471345312e1, 0.28349603476365, -0.49087385940425, -0.10291888921447, 0.11836314681968, 0.55527385721943e-4],
            "d1": [1, 1, 1, 2, 2, 3, 3, 4, 4, 4],
            "t1": [1.000, 1.550, 1.700, 0.250, 1.350, 0.000, 1.250, 0.000, 0.700, 5.400],
            "nr2":[]},

        "4-5":{
            "nr1": [0.25574776844118e1, -0.79846357136353e1, 0.47859131465806e1, -0.73265392369587, 0.13805471345312e1, 0.28349603476365, -0.49087385940425, -0.10291888921447, 0.11836314681968, 0.55527385721943e-4],
            "d1": [1, 1, 1, 2, 2, 3, 3, 4, 4, 4],
            "t1": [1.000, 1.550, 1.700, 0.250, 1.350, 0.000, 1.250, 0.000, 0.700, 5.400],
            "nr2":[]},

        "4-6":{
            "nr1": [0.25574776844118e1, -0.79846357136353e1, 0.47859131465806e1, -0.73265392369587, 0.13805471345312e1, 0.28349603476365, -0.49087385940425, -0.10291888921447, 0.11836314681968, 0.55527385721943e-4],
            "d1": [1, 1, 1, 2, 2, 3, 3, 4, 4, 4],
            "t1": [1.000, 1.550, 1.700, 0.250, 1.350, 0.000, 1.250, 0.000, 0.700, 5.400],
            "nr2":[]},

        "5-6":{
            "nr1": [0.25574776844118e1, -0.79846357136353e1, 0.47859131465806e1, -0.73265392369587, 0.13805471345312e1, 0.28349603476365, -0.49087385940425, -0.10291888921447, 0.11836314681968, 0.55527385721943e-4],
            "d1": [1, 1, 1, 2, 2, 3, 3, 4, 4, 4],
            "t1": [1.000, 1.550, 1.700, 0.250, 1.350, 0.000, 1.250, 0.000, 0.700, 5.400],
            "nr2":[]}}



    def __init__(self, **kwargs):
        """Los parámetros necesarios para definirla son:
                -componente: lista de indices de fluidos
                -fraccion: fraccion molar 
        
            Dos de las variables de definicion de estado:
                -T: temperatura, K
                -rho: densidad, kg/m3
                -P: presion, Pa
                -v: volumen especifico, m3/kg
                -h: entalpia, J/kg
                -s: entropia, J/kgK
                -u: energia interna, J/kg
                -x: fraccion de vapor
            """
        self.kwargs=GERG.kwargs.copy()
        self.__call__(**kwargs)

    def __call__(self, **kwargs):
        self.kwargs.update(kwargs)
            
        if self.calculable:
            self.status=1
            self.calculo()
            self.msg=""

    @property
    def calculable(self):
        if self.kwargs["componente"] and self.kwargs["fraccion"]:
            self._definition=True
        else:
            self._definition=False
            
        thermo=0
        for key in ("T", "P", "rho", "v"):
            if self.kwargs[key]:
                thermo+=1
        for key in ( "h", "s", "u", "x"):
            if self.kwargs[key]!=None:
                thermo+=1
        return self._definition and thermo>=2


    def calculo(self):
        T=self.kwargs["T"]
        rho=self.kwargs["rho"]
        P=self.kwargs["P"]
        v=self.kwargs["v"]
        h=self.kwargs["h"]
        s=self.kwargs["s"]
        u=self.kwargs["u"]
        x=self.kwargs["x"]

        self.comp=[self.componentes[i](recursion=False, eq="GERG", **self.kwargs) for i in self.kwargs["componente"]]
        self.id=self.kwargs["componente"]
        self.xi=self.kwargs["fraccion"]

        #Propiedades críticas de la mezcla eq. 7.9, 7.10 pag.125, Tabla 7.10 pag 136
        c_T=zeros((len(self.comp), len(self.comp)))
        c_rho=zeros((len(self.comp), len(self.comp)))
        for i, componentei in enumerate(self.comp):
            for j, componentej in enumerate(self.comp):
                c_T[i, j]=2*self.Prop_c["beta_t"][i][j]*self.Prop_c["gamma_t"][i][j]*(componentei.Tc*componentej.Tc)**0.5
                c_rho[i, j]=2*self.Prop_c["beta_v"][i][j]*self.Prop_c["gamma_v"][i][j]/8.*(1./componentei.rhoc**(1./3)+1./componentej.rhoc**(1./3))**3

        f_T=zeros((len(self.comp), len(self.comp)))
        f_rho=zeros((len(self.comp), len(self.comp)))
        dFT_ik=zeros((len(self.comp), len(self.comp)))
        dFT_ki=zeros((len(self.comp), len(self.comp)))
        dFrho_ik=zeros((len(self.comp), len(self.comp)))
        dFrho_ki=zeros((len(self.comp), len(self.comp)))
        for i, x_i in enumerate(self.xi):
            for j, x_j in enumerate(self.xi):
                f_T[i, j]=x_i*x_j*(x_i+x_j)/(self.Prop_c["beta_t"][i][j]**2*x_i+x_j)
                f_rho[i, j]=x_i*x_j*(x_i+x_j)/(self.Prop_c["beta_v"][i][j]**2*x_i+x_j)
                dFT_ik[i, j]=x_j*(x_j+x_i)/(self.Prop_c["beta_t"][i][j]**2*x_i+x_j) + x_j*x_i/(self.Prop_c["beta_t"][i][j]**2*x_i+x_j)*(1-self.Prop_c["beta_t"][i][j]**2*(x_j+x_i)/(self.Prop_c["beta_t"][i][j]**2*x_i+x_j))
                dFrho_ik[i, j]=x_j*(x_j+x_i)/(self.Prop_c["beta_v"][i][j]**2*x_i+x_j) + x_j*x_i/(self.Prop_c["beta_v"][i][j]**2*x_i+x_j)*(1-self.Prop_c["beta_v"][i][j]**2*(x_j+x_i)/(self.Prop_c["beta_v"][i][j]**2*x_i+x_j))
                dFT_ki[j, i]=x_j*(x_j+x_i)/(self.Prop_c["beta_t"][i][j]**2*x_j+x_i)+x_j*x_i/(self.Prop_c["beta_t"][i][j]**2*x_j+x_i)*(1-(x_j+x_i)/(self.Prop_c["beta_t"][i][j]**2*x_j+x_i))
                dFrho_ki[j, i]=x_j*(x_j+x_i)/(self.Prop_c["beta_v"][i][j]**2*x_j+x_i)+x_j*x_i/(self.Prop_c["beta_v"][i][j]**2*x_j+x_i)*(1-(x_j+x_i)/(self.Prop_c["beta_v"][i][j]**2*x_j+x_i))


        sumai_v=sumaij_v=sumai_T=sumaij_T=m=0
        for i, componentei in enumerate(self.comp):
            sumai_v+=self.xi[i]**2/componentei.rhoc
            sumai_T+=self.xi[i]**2*componentei.Tc
            m+=self.xi[i]*componentei.M
            for j, componentej in enumerate(self.comp):
                if j>i:
                    sumaij_v+=c_rho[i, j]*f_rho[i, j]
                    sumaij_T+=c_T[i, j]*f_T[i, j]

        self.rhoc=unidades.Density(1./(sumai_v+sumaij_v))
        self.Tc=unidades.Temperature(sumai_T+sumaij_T)
        self.M=m    #g/mol
        self.R=unidades.SpecificHeat(R/self.M, "kJkgK")

        Tcxi=rhocxi=[]
        for i, componentei in enumerate(self.comp):
            sumav1=sumat1=0
            for k in range(i):
                sumav1+=c_rho[k, i]*dFrho_ki[k, i]
                sumat1+=c_T[k, i]*dFT_ki[k, i]
            sumav2=sumat2=0
            for k in range(i+1, len(self.xi)):
                sumav2+=c_rho[i, k]*dFrho_ik[i, k]
                sumat2+=c_T[i, k]*dFT_ik[i, k]

            Tcxi.append(2*self.xi[i]*componentei.Tc+sumat1+sumat2)
            rhocxi.append(2*self.xi[i]/componentei.rhoc+sumav1+sumav2)
        self.Tcxi=Tcxi
        self.rhocxi=rhocxi

        if v and not rho:
            rho=1./v

        if T and x!=None:
            pass
        else:
            if T and P:
                rhoo=2.
                rho=fsolve(lambda rho: self._solve(rho, T)["P"]-P*1e6, rhoo)
            elif T and rho: pass
            elif T and h!=None:
                rho=fsolve(lambda rho: self._solve(rho, T)["h"]-h, 200)
            elif T and s!=None:
                rho=fsolve(lambda rho: self._solve(rho, T)["s"]-s, 200)
            elif T and u!=None:
                rho=fsolve(lambda rho: self._solve(rho, T)["u"]-u, 200)
            elif P and rho:
                T=fsolve(lambda T: self._solve(rho, T)["P"]-P*1e6, 600)
            elif P and h!=None:
                rho, T=fsolve(lambda par: (self._solve(par[0], par[1])["P"]-P*1e6, self._solve(par[0], par[1])["h"]-h), [200, 600])
            elif P and s!=None:
                rho, T=fsolve(lambda par: (self._solve(par[0], par[1])["P"]-P*1e6, self._solve(par[0], par[1])["s"]-s), [200, 600])
            elif P and u!=None:
                rho, T=fsolve(lambda par: (self._solve(par[0], par[1])["P"]-P*1e6, self._solve(par[0], par[1])["u"]-u), [200, 600])
            elif rho and h!=None:
                T=fsolve(lambda T: self._solve(rho, T)["h"]-h, 600)
            elif rho and s!=None:
                T=fsolve(lambda T: self._solve(rho, T)["s"]-s, 600)
            elif rho and u!=None:
                T=fsolve(lambda T: self._solve(rho, T)["u"]-u, 600)
            elif h!=None and s!=None:
                rho, T=fsolve(lambda par: (self._solve(par[0], par[1])["h"]-h, self._solve(par[0], par[1])["s"]-s), [200, 600])
            elif h!=None and u!=None:
                rho, T=fsolve(lambda par: (self._solve(par[0], par[1])["h"]-h, self._solve(par[0], par[1])["u"]-u), [200, 600])
            elif s!=None and u!=None:
                rho, T=fsolve(lambda par: (self._solve(par[0], par[1])["s"]-s, self._solve(par[0], par[1])["u"]-u), [200, 600])
            else:
                raise IOError

        fio, fiot, fiott, fiod, fiodd, fiodt, fir, firt, firtt, fird, firdd, firdt, firdtt, nfioni, nfirni=self._eq(rho, T)

        #Tabla 7.1 pag 127
        tau=self.Tc/T
        delta=rho/self.rhoc

        self.T=unidades.Temperature(T)
        self.rho=unidades.Density(rho)
        self.v=unidades.SpecificVolume(1./rho)
        self.P=unidades.Pressure((1+delta*fird)*self.R.JkgK*T*rho)
        self.Z=1+delta*fird
        self.s=unidades.SpecificHeat(self.R.kJkgK*(tau*(fiot+firt)-fio-fir))
        self.u=unidades.Enthalpy(self.R.kJkgK*T*tau*(fiot+firt))
        self.h=unidades.Enthalpy(self.R.kJkgK*T*(1+tau*(fiot+firt)+delta*fird), "kJkg")
        self.cp=unidades.SpecificHeat(self.R.kJkgK*(-tau**2*(fiott+firtt)+(1+delta*fird-delta*tau*firdt)**2/(1+2*delta*fird+delta**2*firdd)), "kJkgK")
        self.cv=unidades.SpecificHeat(-self.R.kJkgK*tau**2*(fiott+firtt), "kJkgK")
        self.g=unidades.Enthalpy(self.R.kJkgK*T*(1+fio+fir+delta*fird))
        self.w=unidades.Speed((self.R*T*(1+2*delta*fird+delta**2*firdd-(1+delta*fird-delta*tau*firdt)**2/tau**2/(fiott+firtt)))**0.5)

        f, FI=self.fug(rho, T, nfirni)
        Ki, xi, yi, Q=self.flash()
        self.x=unidades.Dimensionless(Q)
        self.xl=xi
        self.xv=yi
        if self.kwargs["mezcla"]:
            self.Pc=self.kwargs["mezcla"].Pc
        self.Liquido=fluid()
        self.Gas=fluid()
        

    def fug(self, rho, T, nfirni=None):
        if not nfirni:
            tau=self.Tc/T
            delta=rho/self.rhoc
            fir, firt, firtt, fird, firdd, firdt, firdtt, nfirni=self._phir(tau, delta)
        f=[]
        FI=[]
        for xi, dn in zip(self.xi, nfirni):
            f.append(unidades.Pressure(xi*rho/self.M*R_atml*T*exp(dn), "atm"))
            FI.append(dn-log(self.Z))
        return f, FI

#        firn=delta*fird*(1-1./self.rhoc*n*rhodn)+tau*firt/self.Tc*n*Tcdn
#        nfirn=fir+n*dfirn
#        f


#        propiedades["alfap"]=(1-delta*tau*firdt/(1+delta*fird))/T
#        propiedades["betap"]=rho*(1+(delta*fird+delta**2*firdd)/(1+delta*fird))
#        propiedades["fugacity"]=exp(fir+delta*fird-log(1+delta*fird))
#        propiedades["B"]=B
#        propiedades["C"]=C
#        propiedades["dpdrho"]=self.R*T*(1+2*delta*fird+delta**2*firdd)
#        propiedades["dpdT"]=self.R*rho*(1+delta*fird+delta*tau*firdt)
#
#        self.a=unidades.Enthalpy(self.u-self.T*self.s)
#        self.Z=self.P*self.v/self.T/self.R.kJkgK/1000
#        self.alfap=propiedades["alfap"]     #inversa de la temperatura
#        self.betap=unidades.Density(propiedades["betap"])
#
#        self.Tr=T/self.Tc
#
#        self.cp0=self._Cp0(self._constants["cp"])
#        self.gamma=-self.v/self.P.kPa*self.derivative("P", "v", "s")
#        self.fi=propiedades["fugacity"]
#        self.f=unidades.Pressure(self.fi*self.P)
#        self.virialB=propiedades["B"]
#        self.virialC=propiedades["C"]


    def _eq(self, rho, T):
        tau=self.Tc/T
        delta=rho/self.rhoc
        fio, fiot, fiott, fiod, fiodd, fiodt, nfioni=self._phi0(tau, delta)
        fir, firt, firtt, fird, firdd, firdt, firdtt, nfirni=self._phir(tau, delta)
        return fio, fiot, fiott, fiod, fiodd, fiodt, fir, firt, firtt, fird, firdd, firdt, firdtt, nfioni, nfirni

    def _solve(self, rho, T):
        tau=self.Tc/T
        delta=rho/self.rhoc
        fio, fiot, fiott, fiod, fiodd, fiodt, nfioni=self._phi0(tau, delta)
        fir, firt, firtt, fird, firdd, firdt, firdtt, nfirni=self._phir(tau, delta)
        propiedades={}
        propiedades["P"]=(1+delta*fird)*self.R.JkgK*T*rho
        propiedades["s"]=self.R.kJkgK*(tau*(fiot+firt)-fio-fir)
        propiedades["u"]=self.R.kJkgK*T*tau*(fiot+firt)
        propiedades["h"]=self.R.kJkgK*T*(1+tau*(fiot+firt)+delta*fird)
        return propiedades


    def _phi0(self, tau, delta):
        """Contribución ideal de la energía libre de Helmholtz eq. 7.5"""
        fio=fiot=fiott=fiod=fiodd=fiodt=0
        nfioni=[]   #ðnao/ðni
        for i, componente in enumerate(self.comp):
            deltai=delta*self.rhoc/componente.rhoc
            taui=componente.Tc*tau/self.Tc
            fio_, fiot_, fiott_, fiod_, fiodd_, fiodt_=componente._phi0(componente.GERG["cp"], taui, deltai, Tref, Pref)
            fio+=self.xi[i]*(fio_+log(self.xi[i]))
            fiot+=self.xi[i]*fiot_
            fiott+=self.xi[i]*fiott_
            fiod+=self.xi[i]*fiod_
            fiodd+=self.xi[i]*fiodd_
            fiodt+=self.xi[i]*fiodt_
            nfioni.append(fio_+1+log(self.xi[i]))

        return fio, fiot, fiott, fiod, fiodd, fiodt, nfioni

    def _phir(self, tau, delta):
        """Contribución residual de la energía libre de Helmholtz eq. 7.7"""
        fir=firt=firtt=fird=firdd=firdt=firdtt=0
        firxi=[]
        firxixj=zeros((len(self.comp), len(self.comp)))
        firdxi=[]
        firtxi=[]

        for i, componente in enumerate(self.comp):
            deltai=delta*self.rhoc/componente.rhoc
            taui=componente.Tc*tau/self.Tc
            fir_, firt_, firtt_, fird_, firdd_, firdt_, firdtt_, B_, C_=componente._phir(taui, deltai)
            fir+=self.xi[i]*fir_
            firt+=self.xi[i]*firt_
            firtt+=self.xi[i]*firtt_
            fird+=self.xi[i]*fird_
            firdd+=self.xi[i]*firdd_
            firdt+=self.xi[i]*firdt_

            firxi.append(fir_)
            firdxi.append(fird_)
            firtxi.append(firt_)

        #Contribución residual cruzada eq 7.8
        for i, x_i in enumerate(self.xi):
            for j, x_j in enumerate(self.xi):
                if j>i:
                    fir_, firt_, firtt_, fird_, firdd_, firdt_, firdtt_, B_, C_=self._phijr(i, j, tau, delta)
                    fir+=x_i*x_j*self.Fij[self.id[i]][self.id[j]]*fir_
                    firt+=x_i*x_j*self.Fij[self.id[i]][self.id[j]]*firt_
                    firtt+=x_i*x_j*self.Fij[self.id[i]][self.id[j]]*firtt_
                    fird+=x_i*x_j*self.Fij[self.id[i]][self.id[j]]*fird_
                    firdd+=x_i*x_j*self.Fij[self.id[i]][self.id[j]]*firdd_
                    firdt+=x_i*x_j*self.Fij[self.id[i]][self.id[j]]*firdt_

                    firxi[i]+=x_j*self.Fij[self.id[i]][self.id[j]]*fir_
                    firxixj[i, j]=self.Fij[self.id[i]][self.id[j]]*fir_
                    firdxi[i]+=x_j*self.Fij[self.id[i]][self.id[j]]*fird_
                    firtxi[i]+=x_j*self.Fij[self.id[i]][self.id[j]]*firt_


        suma=suma_rho=suma_T=0
        for i, x_i in enumerate(self.xi):
            suma+=x_i*firxi[i]
            suma_rho+=x_i*self.rhocxi[i]
            suma_T+=x_i*self.Tcxi[i]

        n_rhocni=[]
        n_Tcni=[]
        for i, x_i in enumerate(self.xi):
            n_rhocni.append(self.rhocxi[i]-suma_rho)
            n_Tcni.append(self.Tcxi[i]-suma_T)

        n_firni=[]     #ðar/ðni
        nfirni=[]   #ðnar/ðni
        for i, componente in enumerate(self.comp):
            n_firni.append(delta*fird*(1-1./self.rhoc*n_rhocni[i])+tau*firt/self.Tc*n_Tcni[i]+firxi[i]-suma)
            nfirni.append(fir_+n_firni[i])

        return fir, firt, firtt, fird, firdd, firdt, firdtt, nfirni


    def _phijr(self, i, j, tau, delta):
        txt=str(i)+"-"+str(j)
        constants=self.fir_ij.get(txt, 0)
        fir=fird=firdd=firt=firtt=firdt=firdtt=B=C=0
        if constants:
            delta_0=1e-50
            for i in range(len(constants.get("nr1", []))):        #Polinomial terms
                fir+=constants["nr1"][i]*delta**constants["d1"][i]*tau**constants["t1"][i]
                fird+=constants["nr1"][i]*constants["d1"][i]*delta**(constants["d1"][i]-1)*tau**constants["t1"][i]
                firdd+=constants["nr1"][i]*constants["d1"][i]*(constants["d1"][i]-1)*delta**(constants["d1"][i]-2)*tau**constants["t1"][i]
                firt+=constants["nr1"][i]*constants["t1"][i]*delta**constants["d1"][i]*tau**(constants["t1"][i]-1)
                firtt+=constants["nr1"][i]*constants["t1"][i]*(constants["t1"][i]-1)*delta**constants["d1"][i]*tau**(constants["t1"][i]-2)
                firdt+=constants["nr1"][i]*constants["t1"][i]*constants["d1"][i]*delta**(constants["d1"][i]-1)*tau**(constants["t1"][i]-1)
                firdtt+=constants["nr1"][i]*constants["t1"][i]*constants["d1"][i]*(constants["t1"][i]-1)*delta**(constants["d1"][i]-1)*tau**(constants["t1"][i]-2)
                B+=constants["nr1"][i]*constants["d1"][i]*delta_0**(constants["d1"][i]-1)*tau**constants["t1"][i]
                C+=constants["nr1"][i]*constants["d1"][i]*(constants["d1"][i]-1)*delta_0**(constants["d1"][i]-2)*tau**constants["t1"][i]

            for i in range(len(constants.get("nr2", []))):    #Gaussian terms
                fir+=constants["nr2"][i]*delta**constants["d2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))
                fird+=constants["nr2"][i]*delta**constants["d2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))*(constants["d2"][i]/delta-2*constants["n2"][i]*(delta-constants["e2"][i]))
                firdd+=constants["nr2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))*(-2*constants["n2"][i]*delta**constants["d2"][i]+4*constants["n2"][i]**2*delta**constants["d2"][i]*(delta-constants["e2"][i])**2-4*constants["d2"][i]*constants["n2"][i]*delta**2*(delta-constants["e2"][i])+constants["d2"][i]*2*delta)
                firt+=constants["nr2"][i]*delta**constants["d2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))*(constants["t2"][i]/tau-2*constants["b2"][i]*(tau-constants["g2"][i]))
                firtt+=constants["nr2"][i]*delta**constants["d2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))*((constants["t2"][i]/tau-2*constants["b2"][i]*(tau-constants["g2"][i]))**(2)-constants["t2"][i]/tau**2-2*constants["b2"][i])
                firdt+=constants["nr2"][i]*delta**constants["d2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))*(constants["t2"][i]/tau-2*constants["b2"][i]*(tau-constants["g2"][i]))*(constants["d2"][i]/delta-2*constants["n2"][i]*(delta-constants["e2"][i]))
                firdtt+=constants["nr2"][i]*delta**constants["d2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))*((constants["t2"][i]/tau-2*constants["b2"][i]*(tau-constants["g2"][i]))**(2)-constants["t2"][i]/tau**2-2*constants["b2"][i])*(constants["d2"][i]/delta-2*constants["n2"][i]*(delta-constants["e2"][i]))
                B+=constants["nr2"][i]*delta_0**constants["d2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta_0-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))*(constants["d2"][i]/delta_0-2*constants["n2"][i]*(delta_0-constants["e2"][i]))
                C+=constants["nr2"][i]*tau**constants["t2"][i]*exp(-constants["n2"][i]*(delta_0-constants["e2"][i])**2-constants["b2"][i]*(tau-constants["g2"][i])**(2))*(-2*constants["n2"][i]*delta_0**constants["d2"][i]+4*constants["n2"][i]**2*delta_0**constants["d2"][i]*(delta_0-constants["e2"][i])**2-4*constants["d2"][i]*constants["n2"][i]*delta_0**2*(delta_0-constants["e2"][i])+constants["d2"][i]*2*delta_0)

        return fir, firt, firtt, fird, firdd, firdt, firdtt, B, C


    def flash(self):
        """Cálculo de los coeficientes de reparto entre fases"""
        #Estimación inicial de K mediante correlación wilson Eq 5.61 Pag 82
        Ki=[]
        for componente in self.comp:
            Ki.append(componente.Pc/self.P*exp(5.373*(1.+componente.f_acent)*(1.-componente.Tc/self.T)))

        def f(Q):
            sum=0
            for i, x in enumerate(self.xi):
                sum+=x*(Ki[i]-1.)/(1.+Q+Q*Ki[i])
            return sum

        if f(0)>0 and f(1)>0: #x>1, por tanto solo fase vapor
            xi=self.xi
            yi=self.xi
            Q=1
        elif f(0)<0 and f(1)<0:  #x<0, por tanto solo fase vapor
            xi=self.xi
            yi=self.xi
            Q=0
        else:
            Qo=0.5
            while True:
                Q=Qo
                Qo=fsolve(Vr, Q)
                xi=[]
                yi=[]
                for i, fraccion in enumerate(self.xi):
                    xi.append(fraccion/(1+Qo*(Ki[i]-1)))
                    yi.append(fraccion*Ki[i]/(1+Qo*(Ki[i]-1)))

                fi, Fi=self.fug(self.rho, self.T)
                fiv=r_[yi]*r_[self.titaiv]*self.P
                fil=r_[xi]*r_[self.titail]*self.P
                #criterio de convergencia Eq 21
                if sum((fil/fiv-1)**2)< 1e-15 and (Q-Qo)**2 < 1e-15:
                    break
                else:
                    Ki=r_[self.titail]/r_[self.titaiv]
#
        return Ki, xi, yi, Q


id_GERG=[i.id for i in GERG.componentes]


if __name__ == "__main__":
#    import doctest
#    doctest.testmod()

    aire=GERG(componente=[1, 13, 17], fraccion=[0.78, 0.21, 0.01], P=0.1, T=300)
#    print "%0.1f %0.4f %0.3f %0.3f %0.5f %0.4f %0.2f" % (aire.T, aire.rho, aire.h.kJkg, aire.s.kJkgK, aire.cv.kJkgK, aire.cp.kJkgK, aire.w), aire.P.MPa

#    aire=GERG([0], [1.], P=0.1, T=300)
#    print "%0.1f %0.4f %0.3f %0.3f %0.5f %0.4f %0.2f" % (aire.T, aire.rho, aire.h.kJkg, aire.s.kJkgK, aire.cv.kJkgK, aire.cp.kJkgK, aire.w), aire.P.MPa

#    aire=GERG([1], [1.], P=0.1, T=300)
#    print "%0.1f %0.4f %0.3f %0.3f %0.5f %0.4f %0.2f" % (aire.T, aire.rho, aire.h.kJkg, aire.s.kJkgK, aire.cv.kJkgK, aire.cp.kJkgK, aire.w), aire.P.MPa

#    aire=GERG([15], [1.], P=0.1, T=500)
#    print "%0.1f %0.4f %0.3f %0.3f %0.5f %0.4f %0.2f" % (aire.T, aire.rho, aire.h.kJkg, aire.s.kJkgK, aire.cv.kJkgK, aire.cp.kJkgK, aire.w), aire.P.MPa
