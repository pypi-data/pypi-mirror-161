import numpy as np

def linearfit(x,y):
    # linear fit
    y2 = y
    # y2err = np.square(yerr)
    p = np.polyfit(x,y2,1)

    xfit = np.linspace(np.min(x),np.max(x))
    yfit = (np.polyval(p,xfit))

    yp = np.polyval(p,x)
    corr_matrix = np.corrcoef(y2,yp)
    corr = corr_matrix[0,1]
    r2 = corr*corr

    labelfit = "Fit: "+"y=%.2e*x+%.2e;\
            "%(p[0],p[1])+"\n"+r"$R^2$=%.2f; "%(r2)


    return {'xfit':xfit,'yfit':yfit,\
            'coeffs':p,'r-squared':r2,\
            'label':labelfit}

def squarerootfit(x,y):
    # squareroot fit (not tested)
    y2 = np.square(y)
    # y2err = np.square(yerr)
    p = np.polyfit(x,y2,1)

    xfit = np.linspace(np.min(x),np.max(x))
    yfit = (np.polyval(p,xfit))

    yp = np.polyval(p,x)
    corr_matrix = np.corrcoef(y2,yp)
    corr = corr_matrix[0,1]
    r2 = corr*corr

    labelfit = "Fit: "+"y=%.2e*x+%.2e;\
            "%(p[0],p[1])+"\n"+r"$R^2$=%.2f; "%(r2)


    return {'xfit':xfit,'yfit':yfit,\
            'coeffs':p,'r-squared':r2,\
            'label':labelfit}

def semilogyfit(x,y):
    # Semilogy fit 
    y2 = np.log(y)
    #y2err = yerr[istart:iend]
    #y2err = np.log(y2err)
    p = np.polyfit(x,y2,1)

    xfit = np.linspace(np.min(x),np.max(x))
    yfit = np.exp(np.polyval(p,xfit))

    yp = np.polyval(p,x)
    corr_matrix = np.corrcoef(y2,yp)
    corr = corr_matrix[0,1]
    r2 = corr*corr

    labelfit = "Fit: "+r"$\ln(y)$"+"=%.2e*x+%.2e;\
            "%(p[0],p[1])+"\n"+r"$R^2$=%.2f; "%(r2)

    return {'xfit':xfit,'yfit':yfit,\
            'coeffs':p,'r-squared':r2,\
            'label':labelfit}
