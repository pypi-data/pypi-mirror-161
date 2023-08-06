# -*- coding: UTF-8 -*-
#======================================================
#
# Compatibility function with ganessa.sim
#
#  2020.06.19 - creation
#
import os
import os.path as OP
from collections import defaultdict
import atexit
import numbers
import numpy as np
import ganessa.epanet2 as et
from ganessa.util import ws, tostr, hhmmss, strf3

LINK = BRANCH = ARC = 1
NODE = NOEUD = 2
TANK = RESERVOIR = RSV = 3

__version__ = '1.00'

_emu_folder = None
_emu_object = None
_fresult = ''

class ENmodel(object):
    '''Functions to be called while ENpackage is active
    i.e. between init and close'''
    def __init__(self, fname, hnd, debug=False):
        self.err = []
        self.hnd = hnd
        self.debug = debug
        self.filename = fname
        self.linkcount = 0
        self.nodecount = 0
        self.errcode = 0
        self.coords = {}
        self.vertices = {}
        self.labels = []
        self.backdrop = []
        self.vertices = defaultdict(list)
        self.open(fname)
        self.get_coords()
        self.extra_text = []

    def close(self):
        ''''Terminate'''
        self.linkcount = 0
        self.nodecount = 0
        self.errcode = 0
        et.ENclose()

    def save(self, fname):
        '''Save the model without modifications ?'''
        et.ENsaveinpfile(ws(fname))

    def save_as(self, fname):
        '''Copy the file with current coords / vertices / labels'''
        # with tempfile.NamedTemporaryFile(delete=False, suffix='.inp') as f:
        #     pass
        # self.save(f.name)
        sections = ('[COORD', '[VERTI', '[LABEL', '[BACKD')
        fcopy = True
        with open(self.filename, 'r') as enfile, open(fname, 'w') as fout:
            for text in self.extra_text:
                fout.write('; ' + text + '\n')
            for unstripped_line in enfile:
                line = unstripped_line.strip()
                if not line:
                    fout.write(unstripped_line)
                    continue
                if line[0] == ';':
                    fout.write(unstripped_line)
                    continue
                if line[0] != '[':
                    if fcopy:
                        fout.write(unstripped_line)
                    continue
                # section change
                fcopy = True
                fout.write(unstripped_line)
                for k, section in enumerate(sections):
                    if line.startswith(section):
                        fcopy = False
                        if k == 0:      # coords
                            for node, coords in self.coords.items():
                                x, y = coords
                                fout.write(' {} \t{} \t{}\n'.format(node, strf3(x), strf3(y)))
                        if k == 1:      # vertices
                            for link, points in self.vertices.items():
                                for x, y in points:
                                    fout.write(' {} \t{} \t{}\n'.format(link, strf3(x), strf3(y)))
                        if k == 2:      # labels
                            for x, y, label in self.labels:
                                fout.write(' {} \t{} \t{}\n'.format(strf3(x), strf3(y), label))
                        if k == 3:      # backdrop
                            for cmd in self.backdrop:
                                skip = '; ' if cmd.startswith('DIMEN') else ' '
                                fout.write('{}{}\n'.format(skip, cmd))
        # os.remove(f.name)

    def ENerr(self, ret, showerr=False):
        val = 0
        if isinstance(ret, (list, tuple)):
            ret, val = ret
        if self.errcode == 0:
            self.errcode = ret
        if ret > 0:
            _r, error = et.ENgeterror(ret, 80)
            print(ret, error)
            self.err.append(error)
            # for msg in getENrpt_errors(self.rptd if self.debug else self.rpt):
            #     self.err.append(msg)
            #     if showerr:
            #         print(msg)
        return val

    def open(self, fname):
        os.chdir(OP.dirname(fname))
        base, _ext = OP.splitext(OP.basename(fname))
        # base, ext = OP.splitext(fname)
        self.inp = ws(base + '.inp')
        self.rpt = ws(base + '.rpt')
        if self.debug:
            print('Starting debug simulation...')
            self.rptd = ws(base + '_dbg.rpt')
            self.ENerr(et.ENopen(self.inp, self.rptd, ws('')), True)
            if not self.errcode:
                self.ENerr(et.ENsolveH())
            if not self.errcode:
                self.ENerr(et.ENreport())
            self.close()
            print('Debug simulation done.')
            self.debug = False
        self.ENerr(et.ENopen(self.inp, self.rpt, ws('')), True)
        if not self.errcode:
            self.linkcount = self.ENerr(et.ENgetcount(et.EN_LINKCOUNT))
        if not self.errcode:
            self.nodecount = self.ENerr(et.ENgetcount(et.EN_NODECOUNT))

    def get_coords(self):
        '''Retrieve coords from .inp file'''
        fcoords = fvertices = flabels = fbackdrop = False
        with open(self.filename, 'r') as enfile:
            for line in enfile:
                line = line.strip()
                if not line:
                    continue
                if line[0] == ';':
                    continue
                if line[0] == '[':
                    fcoords = line.startswith('[COORD')
                    fvertices = line.startswith('[VERTI')
                    flabels = line.startswith('[LABEL')
                    fbackdrop = line.startswith('[BACKD')
                    continue
                if fcoords or fvertices:
                    data = line.split()
                    if len(data) < 3:
                        continue
                    coords = float(data[1]), float(data[2])
                    if fcoords:
                        self.coords[data[0]] = coords
                    else:
                        self.vertices[data[0]].append(coords)
                if flabels:
                    data = line.split(maxsplit=2)
                    self.labels.append((float(data[0]), float(data[1]), data[2]))
                if fbackdrop:
                    self.backdrop.append(line)

    def getENerrmsg(self):
        return self.err

    def linknodes(self, link, qavg=0):
        _ret, ix = et.ENgetlinkindex(link)
        _ret, nix, nfx = et.ENgetlinknodes(ix)
        _ret, ni = et.ENgetnodeid(nix)
        _ret, nf = et.ENgetnodeid(nfx)
        return (nf, ni) if qavg < 0 else (ni, nf)

    def getENresults(self):
        '''Runs the simulation and collects all links and nodes results'''
        if self.err:
            return None, None, None, None, []
        linkcount, nodecount = self.linkcount, self.nodecount
        print('Model has', linkcount, 'links and', nodecount, 'nodes.')

        duration = self.ENerr(et.ENgettimeparam(et.EN_DURATION))
        # 8 * nbts * (duration / dt) < 0.5*10**9 -- double avec la transposition !
        dtmin = 8 * (1 + self.nodecount + self.linkcount) * duration / (5*10**8)
        maxsteps = 5*10**8 // (8 * (1 + self.nodecount + self.linkcount))
        print('Running simulation over {} s and collecting results'.format(duration))
        print('Avg sampling interval > {} s'.format(int(dtmin)))
        self.ENerr(et.ENopenH(), True)
        # qfact = self.EN2Picunitfactor()
        qfact = 1.0
        tank_index = [ix for ix in range(1, nodecount+1) if et.ENgetnodetype(ix)[1] == et.EN_TANK]
        tankcount = len(tank_index)
        mapresults = []
        tstep = 1
        show, stepcount, stepskips, step = 0, 0, 0, duration / 24
        self.ENerr(et.ENinitH(0), True)
        while tstep > 0:
            ret, t = et.ENrunH()
            if ret:
                self.err.append(et.ENgeterror(ret, 80)[1] + ' t=' + hhmmss(t))
            if t >= show:
                txt = '\t{:3d}% - t= {}'.format(int(100*show/duration), hhmmss(t))
                if self.hnd:
                    self.hnd.v3.set(txt)
                    self.hnd.update()
                else:
                    print(txt)
                show += step
            # stepcount < t * maxsteps/duration
            if duration*stepcount <= t*maxsteps:
                stepcount += 1
                # Retrieve hydraulic results for time t
                flow = np.zeros(linkcount+1)
                pres = np.zeros(nodecount+1)
                levl = np.zeros(tankcount)
                for ix in range(1, nodecount+1):
                    _ret, v = et.ENgetnodevalue(ix, et.EN_PRESSURE)
                    pres[ix] = v
                for ix in range(1, linkcount+1):
                    _ret, v = et.ENgetlinkvalue(ix, et.EN_FLOW)
                    flow[ix] = v
                for k, ix in enumerate(tank_index):
                    _ret, v = et.ENgetnodevalue(ix, et.EN_HEAD)
                    levl[k] = v
                mapresults.append((t, flow*qfact, pres, levl))
            else:
                stepskips += 1
            _ret, tstep = et.ENnextH()
        _ret = et.ENcloseH()
        if self.err:
            print('\n'.join(self.err))

        # Transpose results by type and object
        steps = np.array([r[0] for r in mapresults])
        tmp = np.array([r[1] for r in mapresults])
        flows = {et.ENgetlinkid(ix)[1]: tmp[:, ix] for ix in range(1, linkcount+1)}
        tmp = np.array([r[2] for r in mapresults])
        press = {et.ENgetnodeid(ix)[1]: tmp[:, ix] for ix in range(1, nodecount+1)}
        tmp = np.array([r[3] for r in mapresults])
        levls = {et.ENgetnodeid(ix)[1]: tmp[:, k] for k, ix in enumerate(tank_index)}
        print('Stored {} - skipped {} steps'.format(stepcount, stepskips))
        if self.hnd:
            tf = steps[-1]
            txt = 'terminée' if tf >= duration else 'interrompue à ' + hhmmss(tf)
            self.hnd.v3.set('Simulation hydraulique ' + txt)
            self.hnd.update()
        sr = stepcount/float(stepcount + stepskips)
        return (steps, flows, press, levls, mapresults, sr)

class Elements(object):
    '''Generic iterator for model elements'''
    def __init__(self, typelt):
        if isinstance(typelt, numbers.Number):
            self.type = typelt
            self.nbmax = nbobjects(self.type)
            self.get_id = {LINK: et.ENgetlinkid, NODE: et.ENgetnodeid}[typelt]
        self.index = 1
    def __iter__(self):
        return self
    def __next__(self):
        if self.index > self.nbmax:
            raise StopIteration
        elem = self.get_id(self.index)[1]
        self.index += 1
        return tostr(elem)
    def __len__(self):
        return self.nbmax
    next = __next__
    len = __len__

class Nodes(Elements):
    '''Node iterator'''
    def __init__(self):
        super(Nodes, self).__init__(NODE)

class Links(Elements):
    '''Links iterator'''
    def __init__(self):
        super(Links, self).__init__(LINK)

class Tanks(Elements):
    '''Tanks iterator'''
    def __init__(self):
        super(Tanks, self).__init__(TANK)    

class GanessaError(Exception):
    '''Error class'''
    def __init__(self, number, reason, text):
        self.number = number
        self.reason = reason
        self.text = tostr(text)
    def __str__(self):
        return __file__ + ' ERROR : ({:d}) : {:s}'.format(self.number, self.text)

def init(folder=None, silent=False, debug=0):
    global _emu_folder, _emu_object
    _emu_folder = folder
    _emu_object = None

def dll_version():
    return '2.00.12'

def _close(*args):
    global _emu_object
    if _emu_object:
        _emu_object.close()
    _emu_object = None

atexit.register(_close)
quit = _close
close = _close

def setlang(new_lang):
    return 'en'

def useExceptions(enable=True):
    pass

def reset():
    _close()

def cmdfile(fname, *args):
    global _emu_object
    _emu_object = ENmodel(fname, None)

def loadbin(fname):
    global _emu_object
    _close()
    _emu_object = ENmodel(fname, None)

def loadres():
    return 0 if _emu_object else 1

def save(fname):
    if _emu_object:
        _emu_object.save_as(fname)
savemodel = save

def nbobjects(objtyp):
    if _emu_object:
        return {LINK: _emu_object.linkcount,
                NODE: _emu_object.nodecount,
                }[objtyp]
    return 0

def nbvertices():
    return len(_emu_object.vertices) if _emu_object else 0

def selectlen(text):
    return 0, LINK

def savemodel(fname):
    if _emu_object:
        _emu_object.save(fname)

def getid(typelt, idx):
    if typelt == LINK:
        fget_id = et.ENgetlinkid
    else:
        fget_id = et.ENgetnodeid
    _, v = fget_id(idx)
    return tostr(v)

def nlinkattr(idx, attr):
    et_attr = {'Q': et.EN_FLOW}[attr]
    _ret, v = et.ENgetlinkvalue(idx, et_attr)
    return v

def nnodeattr(idx, attr):
    if attr in ('X', 'Y'):
        _, nid = et.ENgetnodeid(idx)
        try:
            return _emu_object.coords[nid]
        except (AttributeError, KeyError):
            return 0
    et_attr = {'P': et.EN_PRESSURE,
               'CH': et.EN_HEAD,
               'Z': et.EN_ELEVATION}[attr]
    _, v = et.ENgetnodevalue(idx, et_attr)
    return v

def nodeattr(nid, attr):
    if attr in ('X', 'Y'):
        try:
            return _emu_object.coords[nid][0 if attr == 'X' else 1]
        except (AttributeError, KeyError):
            return 0
    et_attr = {'P': et.EN_PRESSURE,
               'CH': et.EN_HEAD,
               'Z': et.EN_ELEVATION}[attr]
    _, idx = et.ENgetnodeindex(nid)
    _, v = et.ENgetnodevalue(idx, et_attr)
    return v

def linkXYZV(sid, include_nodes=True):
    x, y, z, v, nbp = [], [], [], [], 0
    if not _emu_object:
        return x, y, z, v, nbp
    _, ix = et.ENgetlinkindex(sid)
    _, xni, xnf = et.ENgetlinknodes(ix)
    _, zi = et.ENgetnodevalue(xni, et.EN_ELEVATION)
    _, zf = et.ENgetnodevalue(xnf, et.EN_ELEVATION)
    try:
        vertices = _emu_object.vertices[sid]
    except KeyError:
        if not include_nodes:
            return x, y, z, v, nbp
    else:
        x, y = zip(*vertices) if vertices else ([], [])
        nbp = len(x)
    if include_nodes:
        nbp += 2
    # faux mais bon...
    z = np.linspace(zi, zf, num=nbp)
    v = np.zeros(nbp)
    if include_nodes:
        x[0:0] = nnodeattr(xni, 'X')
        x.append(nnodeattr(xnf, 'X'))
        y[0:0] = nnodeattr(xni, 'Y')
        y.append(nnodeattr(xnf, 'Y'))
    return x, y, z, v, nbp

def get_labels():
    '''Returns the list of (x, y, labels) if any'''
    if not _emu_object:
        return []
    return _emu_object.labels

def set_coordinates(node, x, y):
    '''Resets the node coordinates'''
    if not _emu_object:
        return
    try:
        _emu_object.coords[node] = (x, y)
    except KeyError:
        pass

def set_vertices(link, x, y):
    '''Resets the link vertices'''
    if not _emu_object:
        return
    try:
        _emu_object.vertices[link] = list(zip(x, y))
    except KeyError:
        pass

def clear_labels():
    '''Add a new label'''
    if  _emu_object:
        _emu_object.labels = []

def add_label(x, y, label):
    '''Add a new label'''
    if _emu_object:
        _emu_object.labels.append((x, y, label))

def add_extra_text(text):
    '''Add a new comment'''
    if _emu_object:
        if not text.startswith(';'):
            text = ';' + text
        _emu_object.extra_text.append(text)
