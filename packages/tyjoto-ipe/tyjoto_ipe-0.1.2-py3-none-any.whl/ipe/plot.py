import numpy as np
import matplotlib.pyplot as plt

def save_fig(ax,/,title=None,save=False,close=True):
    fig = plt.figure(1)
    # figure tightV
    fig.tight_layout()
    ax.grid(True)
    #fig.set_size_inches(24, 8, forward=True)
    if save is True:
        sname = 'pics/'+title+'.png'
        print("saving %s..."%(sname))
        plt.savefig(sname)
    elif save is None:
        pass
    elif save is not None and save is not False:
        print("saving %s..."%(save))
        plt.savefig(save)
    else:
        plt.show()
    # close fif
    if close:
        plt.close()
    else:
        return ax

def setup_standard(x,y,/,xerr=None,yerr=None,label=None,\
        title=None,xlabel=None,ylabel=None,\
        color=None,marker=None,linestyle='-',
        mfc=None,\
        save=False,close=True):
    ### PLOT IT ###
    # declare figure
    fig = plt.figure(1)
    # get axis of fig
    ax = plt.gca()

    # set title
    ax.set(title=title)


    # ACTUAL PLOT
    if xerr is None and yerr is None:
        axplt = ax.plot(x,y,label=label,\
                c=color,marker=marker,ls=linestyle,mfc=mfc)
    else:
        axplt = ax.errorbar(x,y,xerr=xerr,yerr=yerr,\
                label=label,\
                c=color,marker=marker,ls=linestyle,\
                mfc=mfc,capsize=2)


    # OTHER PARTS
    # set axis labels, legend, etc.
    ax.set(xlabel=xlabel)#'Time [ms]')
    ax.set(ylabel=ylabel)#r'$omega$ [$s^{-1}$]')


    # lgd show
    lgd = plt.legend()

    save_fig(ax,title=title,save=save,close=close)
    return ax



def setup_lgd_outside(x,y,/,xerr=None,yerr=None,label=None,\
        title=None,xlabel=None,ylabel=None,\
        save=False,close=True):
    fig = setup_standard(x,y,xerr,yerr,label,title,xlabel,ylabel,save=False,close=False)
    #plt.figure(fig)
    fig
    # get axis of fig
    ax = plt.gca()

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    #    # Put a legend to the right of the current axis
    lgd = ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # figure tight
    fig.tight_layout()
    ax.grid()
    fig.set_size_inches(24, 8, forward=True)
    if save is True:
        sname = 'pics/'+title+'.png'
        print("saving %s..."%(sname))
        plt.savefig(sname,\
                bbox_extra_artists=(lgd,),\
                bbox_inches='tight')
    else:
        plt.show()
    # close fif
    if close:
        plt.close()
    else:
        return fig

def add_data(ax,x,y,/,xerr=None,yerr=None,label=None,\
        linestyle="--",marker=None,color=None,\
        title=None,save=False,close=True):


    if xerr is None and yerr is None:
        axplt = ax.plot(x,y,color=color,linestyle=linestyle,marker=marker,label=label)
    else:
        axplt = ax.errorbar(x,y,xerr=xerr,yerr=yerr,fmt=linestyle,color=color,capsize=2,label=label)

    lgd = plt.legend()
    save_fig(ax,title=title,save=save,close=close)
    return ax

def add_vertical(ax,x,/,ymin=0,ymax=1,label=None,\
        linestyle="--",marker=None,color=None,\
        title=None,save=False,close=True):

    axplt = ax.axvline(x=x,ymin=ymin,ymax=ymax,label=label,\
            ls=linestyle,color=color)

    lgd = plt.legend()
    save_fig(ax,title=title,save=save,close=close)
    return ax

def change_xscale(ax,scale,/,title=None,save=False,close=True):
    ax.set_xscale(scale)
    lgd = plt.legend()
    save_fig(ax,title=title,save=save,close=close)
    return ax

def change_yscale(ax,scale,/,title=None,save=False,close=True):
    ax.set_yscale(scale)
    lgd = plt.legend()
    save_fig(ax,title=title,save=save,close=close)
    return ax

def change_limits(ax,/,xlim=None,ylim=None,\
        title=None,save=False,close=True):
    if xlim is not None:
        ax.set(xlim=xlim)
    if ylim is not None:
        ax.set(ylim=ylim)
    save_fig(ax,title=title,save=save,close=close)
    return ax 
    
def change_title(ax,title,/,save=False,close=True):
    ax.set(title=title)
    save_fig(ax,title=None,save=save,close=close)
    return ax

def change_xlabel(ax,xlabel,/,save=False,close=True):
    ax.set(xlabel=xlabel)
    save_fig(ax,title=None,save=save,close=close)
    return ax

def change_ylabel(ax,ylabel,/,save=False,close=True):
    ax.set(ylabel=ylabel)
    save_fig(ax,title=None,save=save,close=close)
    return ax
