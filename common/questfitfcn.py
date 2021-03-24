import numpy as np
import lmfit
from lmfit.models import ExpressionModel

def blackbody(wave,a,T):

    '''Function defined for fitting a blackbody model
    
    Parameters
    -----
    wave: array
    1-D array of the wavelength to be fit
    a: float
    scale factor for model
    T: float
    temperature of blackbody
    
    returns
    -------
    BB_model: array
    '''
    
    h=6.6261e-27

    c=3.e10

    k=1.3807e-16

    hck = h*c/k
    wave = wave*1e-4
    BB_model = wave**-5*(np.exp(h*c/(k*wave*T))-1)**-1


    return a*BB_model/BB_model.max()

def set_up_fit_blackbody_model(p,p_fixfree,name):
    '''Function defined to set up fitting blackbody_model within lmfit
        
        Parameters
        -----
        p: list
        list of initial guess for the blackbody_model fit
        
        
        
        returns
        -------
        blackbody_model_model: lmfit model
        blackbody_model_paramters: lmfit model parameters
        '''


    model_name = name
    blackbody_model = lmfit.Model(blackbody,independent_vars=['wave'],prefix=model_name+'_')
    blackbody_model_parameters = blackbody_model.make_params()
    print(p_fixfree[0])
    blackbody_model_parameters[model_name+'_a'].set(value=p[0],min=0.,vary=p_fixfree[0])
    blackbody_model_parameters[model_name+'_T'].set(value=p[1],min=1.,vary=p_fixfree[1])

    return blackbody_model,blackbody_model_parameters

def powerlaw(wave,a,b):

    '''Function defined for fitting a powerlaw model
    
    Parameters
    -----
    wave: array
    1-D array of the wavelength to be fit
    a: float
    scale factor for powerlaw
    b: float
    exponent for powerlaw
    
    returns
    -------
    powerlaw_model: array
    '''
    


    powerlaw_model = a*wave**b


    return powerlaw_model

def set_up_fit_powerlaw_model(p,p_fixfree,name):
    '''Function defined to set up fitting powerlaw_model within lmfit
        
        Parameters
        -----
        p: list
        list of initial guess for the powerlaw_model fit
        
        
        
        returns
        -------
        powerlaw_model_model: lmfit model
        powerlaw_model_paramters: lmfit model parameters
        '''


    model_name = name
    powerlaw_model = lmfit.Model(powerlaw,independent_vars=['wave'],prefix=model_name)
    powerlaw_model_parameters = powerlaw_model.make_params()
    powerlaw_model_parameters[model_name+'a'].set(value=p[0],min=0.,vary=p_fixfree[0])
    powerlaw_model_parameters[model_name+'b'].set(value=p[1],min=1.,vary=p_fixfree[1])

    return powerlaw_model,powerlaw_model_parameters


def model_scale(model,a):

    '''Function defined for fitting a continuum model
    
    Parameters
    -----
    wave: array
    1-D array of the wavelength to be fit
    a: float
    scale factor for model_scale

    
    returns
    -------
    powerlaw_model: array
    '''
        
        
        
    model_scale = model*a


    return model_scale




#def screen_exctinction_model(extinction_curve,Av):
#
#    '''Function defined for fitting a screen_exctinction_model
#
#        Parameters
#        -----
#        wave: array
#        1-D array of the wavelength to be fit
#        Av: float
#        scale factor for exctinction_model
#
#
#        returns
#        -------
#        powerlaw_model: array
#        '''
#
#
#
#    model_extinction = 10**-0.4*Av*np.log10(extinction_curve)
#
#
#    return model_extinction


#def mixed_exctinction_model(extinction_curve,Av):
#
#    '''Function defined for fitting a screen_exctinction_model
#
#        Parameters
#        -----
#        wave: array
#        1-D array of the wavelength to be fit
#        Av: float
#        scale factor for exctinction_model
#
#
#        returns
#        -------
#        powerlaw_model: array
#        '''
#
#
#    tau = 0.4*Av*np.log10(extinction_curve)
#
#    model_extinction = 1 - np.exp(-tau)/(tau)
#
#    return model_extinction

def set_up_fit_extinction(p,p_fixfree,model_name,extinction_model,mixed_or_screen):
    '''Function defined to set up fitting model_scale within lmfit
        
        Parameters
        -----
        p: list
        list of initial guess for the model_scale fit
        
        
        
        returns
        -------
        powerlaw_model_model: lmfit model
        powerlaw_model_paramters: lmfit model parameters
        '''
    
    
    model_name = model_name
    if mixed_or_screen == 'M':
        exp = "1 - exp(-0.4*%s_Av*log10(%s))/(0.4*%s_Av*log10(%s))" % (model_name,extinction_model,model_name,extinction_model)
    
    if mixed_or_screen == 'S':
        exp = "power(10,(-0.4*%s_Av*log10(%s)))" % (model_name,extinction_model)

    model_extinction = ExpressionModel(exp,independent_vars=[extinction_model],name = model_name)
    
    #model_scale_model = lmfit.Model(powerlaw,independent_vars=['extinction_curve'],prefix=model_name)
    model_extinction_parameters = model_extinction.make_params()
    print(p_fixfree[0])
    if mixed_or_screen == 'M':
        model_extinction_parameters[model_name+'_Av'].set(value=p[0],min=1.,vary=p_fixfree[0])
    if mixed_or_screen == 'S':
        model_extinction_parameters[model_name+'_Av'].set(value=p[0],min=0.,vary=p_fixfree[0])
    return model_extinction,model_extinction_parameters

def set_up_fit_model_scale(p,p_fixfree,model_name,model):
    '''Function defined to set up fitting model_scale within lmfit
        
        Parameters
        -----
        p: list
        list of initial guess for the model_scale fit
        
        
        
        returns
        -------
        scale_model_model: lmfit model
        scale_model_paramters: lmfit model parameters
        '''
    
    
    exp = "1*%s_amp*1*%s" % (model[:-4],model[:-4])
    model_scale_model = ExpressionModel(exp,independent_vars=[model[:-4]],name=model_name)
    model_scale_parameters = model_scale_model.make_params()
    
    model_scale_parameters[model[:-4]+'_amp'].set(value=p[0],min=0.,vary=p_fixfree[0])#,min=0.

    
    return model_scale_model,model_scale_parameters


def set_up_absorption(p,p_fixfree,model_name,abs_model):
    '''Function defined to set up fitting model_scale within lmfit
        
        Parameters
        -----
        p: list
        list of initial guess for the absorption model
        
        
        
        returns
        -------
        absorption_model: lmfit model
        absorption_paramters: lmfit model parameters
        '''


    exp = "exp(-1*%s_tau*%s)" % (model_name,abs_model)
    model = ExpressionModel(exp,independent_vars=[abs_model],name = model_name)
    abs_model_parameters = model.make_params()
    abs_model_parameters[model_name+'_tau'].set(value=p[0],min=0.,vary=p_fixfree[0])#min=0.


    return model,abs_model_parameters
