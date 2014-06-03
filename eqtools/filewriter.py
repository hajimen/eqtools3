import scipy 
import warnings
import time
import core


def gfile(obj, tin, nw=None, nh=None, shot=None, name=None, tunit = 'ms', title='EQTOOLS'):
 
    if shot is None:
        shot = obj._shot

    timeConvertDict = {'ms':1000.,'s':1.}
    stin = str(int(float(tin)*timeConvertDict[tunit]/timeConvertDict[obj._defaultUnits['_time']]))

    if name is None:
        name = 'g'+str(shot)+'.'+stin

    if nw is None:
        nw = len(obj.getRGrid())

    if nh is None:
        nh = len(obj.getZGrid())

    if len(title) > 10:
        raise ValueError('title is too long')

    header = title+ (11-len(title))*' '+ \
                         time.strftime('%m/%d/%Y')+ \
                         '   '+str(shot)+' '+ stin + tunit + '\n'
                     
    header = header + (51-len(header))*' '+ '3 '+str(nw)+' '+str(nh)
   
    rgrid = scipy.linspace(obj.getRGrid()[0],obj.getRGrid()[-1],nw)
    zgrid = scipy.linspace(obj.getZGrid()[0],obj.getZGrid()[-1],nh)

    print(header)

    gfile =open(name, 'wb')
    gfile.write(header)
    gfile.write(fmt([obj.getRGrid()[-1]-obj.getRGrid()[0],
                     obj.getZGrid()[-1]-obj.getZGrid()[0],
                     0.,
                     obj.getRGrid()[0],
                     obj.getZGrid()[-1]/2.+obj.getZGrid()[0]/2.]))
    gfile.write(fmt([obj.getMagRSpline(tin),
                     obj.getMagZSpline(tin),
                     obj.getPsi0Spline(tin),
                     obj.getPsiLCFSSpline(tin),
                     0.]))
    gfile.write(fmt([obj.getIpCalc(tin),
                     obj.getPsi0Spline(tin),
                     0.,
                     obj.getMagRSpline(tin),
                     0.]))
    gfile.write(fmt([obj.getMagZSpline(tin),
                     0.,
                     obj.getPsiLCFSSpline(tin),
                     0.,
                     0.,
                     0.]))
    gfile.write(fmt([obj.getMagZSpline(tin),
                     0.,
                     obj.getPsiLCFSSpline(tin),
                     0.,
                     0.,
                     0.]))

    #dump = [obj.getFpol().flatten(),
    #        obj.getFluxPres().flatten(),
    #        obj.getFFPrime().flatten()]
    #if obj._tricub:
    #    dump
            
    
def fmt(val):
    try:
        temp = '0{ 0.9E}'.format(val*10)
        out =''.join([temp[1],temp[0],temp[4],temp[2],temp[4:]])
    except ValueError:
        out = []
        temp = []
        idx = 0
        for i in val:
            temp += fmt(i)
            idx += 1
            if idx ==5:
                temp+='\n'
                out += [temp[:]]
                idx = 0
                temp = []

    return out