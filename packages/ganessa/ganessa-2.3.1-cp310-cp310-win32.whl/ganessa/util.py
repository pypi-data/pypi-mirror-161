# -*- coding: utf-8 -*-
'''Miscellaneous utilities functions and classes for ganessa'''
from __future__ import (unicode_literals, print_function, absolute_import)

from typing import Iterable, List, Tuple, Sequence, Union, Mapping, Callable, AnyStr, Literal
from datetime import date, datetime, tzinfo, timedelta
import sys
import tempfile
from math import sqrt, log
import shutil
import os
import os.path as OP
from time import perf_counter as perfs
import re
import subprocess
import unicodedata
from platform import uname
import json
import locale
import builtins
import numpy as np

ElemType = Literal[0, 1, 2, 3]

_PTN_BLANKS = re.compile(r'\s+')
_PTN_NO_IDSTR = re.compile(r'\W+')
_PTN_NO_IDCHAR = re.compile('[^A-Za-z0-9?_-]')
_PTN_SEQUEN = re.compile(r'(-+_+-*|_+-+_*)+')
# ok for water hardness in french command language : TH
_PTN_WQ_ATTR = re.compile(r'(T|TH|C\d|\$[0-9A-Z])$', re.IGNORECASE)

US_MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

locale.setlocale(locale.LC_ALL, '')
_decimal_point = locale.localeconv()['decimal_point']

PY3 = sys.version_info.major == 3
X64 = sys.maxsize > 2**32
_uname = uname()
WSVERS = _uname.release if _uname.system == 'Windows' else '0'
del _uname

# Following imports may be used by user scripts
izip = zip
unicode23 = builtins.str
byte23 = builtins.bytes
uchr = builtins.chr
copen = builtins.open
file_encoding = 'utf-8'
PICFILE_ENCODING = 'cp1252'

#****g* ganessa.util/About
# PURPOSE
#   The module ganessa.util provides useful functions used by the Ganessa tools.
# REMARK
#   Some of the functions must be preceded by  'import ganessa.sim'
#****
#****g* ganessa.util/functions
#****
#****g* ganessa.util/iterators
#****

#****f* functions/formatting: strf2, strf3, strf2loc, strf3loc, stri, hhmmss, strd
# SYNTAX
#   * txt = strf2(fval)
#   * txt = strf3(fval)
#   * txt = stri(ival)
#   * hms = hhmmss(val [, rounded=False] [, days=False])
#   * dmy = strd(dval)
# ARGUMENT
#   * int or float val: number of seconds
#   * int ival: integer input value
#   * float fval: float input value
#   * date dval: datetime input value
#   * bool rounded: round value to the nearest second value
#   * bool or str days: if True and hours >= 24, then writes d<days>hh:mm:ss
# RESULT
#   * string txt: string representation of the input value
#   * string hms: representation of time in the form 'hh:mm:ss' or 'd<sep>hh:mm:ss'
#     when days=True and fval >= 86400; <sep> is days if days is a str, otherwise ' '.
#   * string dmy: date time in the isoformat except TZ: YYYY-MM-DDTHH:MM:SS
# REMARK
#   * strf2 and strf3: values larger that 1 are written with at most 2 or 3 digits after decimal dot.
#   * strf2loc and strf3loc use the local decimal dot (. or ,).
#   * strd: the value 'val' is rounded to seconds id rounded= True
# HISTORY
#   23/11/2020 (2.1.6): added 'days' keyword to hhmmss.
#****
def hhmmss(seconds: float, rounded: bool = False, days: Union[bool, str] = False) -> str:
    '''formats a time in seconds as hh:mm:ss'''
    if rounded:
        seconds = int(seconds + 0.5)
    sign = ''
    if seconds < 0:
        seconds, sign = -seconds, '-'
    m = int(seconds//60)
    hours = int(m//60)
    if days and hours > 23:
        sign += str(hours//24) + (days if is_text(days) else ' ')
        hours %= 24
    return "{3}{0:02d}:{1:02d}:{2:02d}".format(hours, m%60, int(seconds - 60*m), sign)

def strf3(val: float) -> str:
    "Formate une valeur float avec mantisse de taille raisonnable"
    if val == 0.0:
        return "0.0"
    elif abs(val) >= 1.0:
        strg = "{0:.3f}".format(val)
    elif abs(val) >= 0.01:
        strg = "{0:.5f}".format(val)
    elif abs(val) >= 0.001:
        strg = "{0:.6f}".format(val)
    else:
        return "{0:.7e}".format(val)
    # suppression des 0 finaux
    # if strg[-2:] == "00":
    #     if strg[-4:] == "0000":
    #         return strg[:-3]
    #     return strg[:-2]
    # else:
    #     return strg
    if strg[-1] == '0':
        if strg[-2] == '0':
            if strg[-3] == '0':
                if strg[-4] == '0':
                    return strg[:-3]
                return strg[:-2]
            return strg[:-1]
        if strg[-2] != '.':
            return strg[:-1]
    return strg

def strf2(val: float) -> str:
    "Formate une valeur float avec mantisse de taille raisonnable"
    if val == 0.0:
        return "0.0"
    elif abs(val) >= 1.0:
        strg = "{0:.2f}".format(val)
    elif abs(val) >= 0.01:
        strg = "{0:.4f}".format(val)
        if strg[-2:] == "00":
            return strg[:-2]
        elif strg[-1:] == "0":
            return strg[:-1]
        else:
            return strg
    else:
        return "{0:.7e}".format(val)
    if strg[-3:] == "000":
        return strg[:-3]
    elif strg[-2:] == "00":
        return strg[:-2]
    else:
        return strg

def strf4(val: float) -> str:
    "Formate une valeur float avec mantisse de taille raisonnable"
    if val == 0.0:
        return "0.0"
    elif abs(val) >= 1.0:
        strg = "{0:.4f}".format(val)
    elif abs(val) >= 0.01:
        strg = "{0:.6f}".format(val)
    elif abs(val) >= 0.001:
        strg = "{0:.7f}".format(val)
    else:
        return "{0:.7e}".format(val)
    if strg[-1] == '0':
        if strg[-2] == '0':
            if strg[-3] == '0':
                if strg[-4] == '0':
                    return strg[:-3]
                return strg[:-2]
            return strg[:-1]
        if strg[-2] != '.':
            return strg[:-1]
    return strg

def _strloc(val: float) -> str:
    return _decimal_point.join(str(val).split('.'))

def _strf3loc(val: float) -> str:
    return _decimal_point.join(strf3(val).split('.'))

def _strf2loc(val: float) -> str:
    return _decimal_point.join(strf2(val).split('.'))

strloc: Callable[[float], str] = str if _decimal_point == '.' else _strloc
strf3loc = strf3 if _decimal_point == '.' else _strf3loc
strf2loc = strf2 if _decimal_point == '.' else _strf2loc

def stri(val: int) -> str:
    "Retourne la chaine representant la valeur entiere"
    return '{0:d}'.format(val)

def strii(val: int) -> str:
    "Retourne la chaine representant la valeur entiere"
    return '{0:02d}'.format(val)

def strd(val) -> str:
    'Returns date time as ISO format'
    # return val.isoformat()
    return val.strftime("%Y-%m-%dT%H:%M:%S")

#****f* functions/quotefilename
# SYNTAX
#   * txt = quotefilename(name)
# ARGUMENT
#   * str name: file name
# RESULT
#   * string txt: file name quoted with double quotes if it contains a whitespace.
# HISTORY
#   * added 11/09/2015.
#****
def quotefilename(fname: AnyStr) -> AnyStr:
    '''Quote a filename with doublequotes if not yet quoted and
    if a whitespace character appears in the filename. Added 150911'''
    if isinstance(fname, unicode23):
        if fname[0] not in ('"', "'") and ' ' in fname:
            fname = '"' + fname + '"'
    else:
        if fname[0] not in (b'"', b"'") and b' ' in fname:
            fname = b'"' + fname + b'"'
    return fname

#****f* functions/is_text, myascii, unistr, str2uni, utf2uni, con2uni
# SYNTAX
#   * bret = is_text(input_str)
#   * atxt = myascii(input_str)
#   * utxt = unistr(input_str)
#   * utxt = str2uni(input_str)
#   * utxt = utf2uni(input_str)
#   * utxt = con2uni(input_str)
# ARGUMENT
#   input_str: value to be converted. Can be of any type:
#   non text input are first converted to unicode.
# RESULT
#   * bool bret: indicator telling if the object item is a  string (unicode or byte).
#     Equivalent to isinstance(input_str, basestring) in python 2.7
#   * unicode or string atxt: string of same type as input_str where non-ascii charcacters
#     have been replaced with the best match (i.e. 'é' is replaced with 'e').
#   * unicode utxt: unicode string decoded from input_str (multiple codecs tried in turn);
#     unistr tries 'cp1252', 'utf-8', 'cp850', 'iso-8859-1';
#     str2uni tries 'utf-8', 'cp1252', 'cp850', 'iso-8859-1';
#     tostr acts as unistr in python2 and as str2uni in python3;
#     con2uni tries cp850 then tostr.
# HISTORY
#   * in version 1.9.0, those functions are defined separately for python2 and python3.
#   * since version 1.9.1, the definitions have been merged.
#   * since version 2.1.5 (2020/08/24), 'ascii' replaced with 'myascii'
#   * since version 2.2.0 (2021/05/27) myascii tries several codecs
#****
_ENCODINGS2 = ('cp1252', 'utf-8', 'cp850', 'iso-8859-1')
_ENCODINGS3 = ('utf-8', 'cp1252', 'cp850', 'iso-8859-1')
_TOSTR_ENCODING = _ENCODINGS3 if PY3 else _ENCODINGS2

def is_u(item: AnyStr) -> bool:
    return isinstance(item, unicode23)

def is_b(item: AnyStr) -> bool:
    return isinstance(item, byte23)

def is_text(item: AnyStr) -> bool:
    '''Check arg for being str or byte'''
    return isinstance(item, (unicode23,byte23))

def unistr(input_str: AnyStr) -> str:
    '''Converts to unicode - cp1252 first guess'''
    if isinstance(input_str, unicode23):
        return input_str
    elif isinstance(input_str, byte23):
        for codec in _ENCODINGS2:
            try:
                return unicode23(input_str, codec)
            except UnicodeError:
                continue
    else:
        return unicode23(input_str)

def str2uni(input_str: AnyStr) -> str:
    '''Converts to unicode - utf-8 first guess'''
    if isinstance(input_str, unicode23):
        return input_str
    elif isinstance(input_str, byte23):
        for codec in _ENCODINGS3:
            try:
                return unicode23(input_str, codec)
            except UnicodeError:
                continue
    else:
        return unicode23(input_str)

def utf2uni(input_str: AnyStr) -> str:
    if isinstance(input_str, unicode23):
        return input_str
    elif isinstance(input_str, byte23):
        return unicode23(input_str, 'utf-8')
    else:
        return unicode23(input_str)

def tostr(input_str: AnyStr) -> str:
    '''converts to unicode - guess depends on py2/py3'''
    if isinstance(input_str, unicode23):
        return input_str
    elif isinstance(input_str, byte23):
        for codec in _TOSTR_ENCODING:
            try:
                return unicode23(input_str, codec)
            except UnicodeError:
                continue
    else:
        return unicode23(input_str)

def con2uni(input_str: AnyStr) -> str:
    if isinstance(input_str, unicode23):
        return input_str
    elif isinstance(input_str, byte23):
        try:
            return unicode23(input_str, 'cp850')
        except UnicodeError:
            for codec in _TOSTR_ENCODING:
                try:
                    return unicode23(input_str, codec)
                except UnicodeError:
                    continue
    else:
        return str(input_str)

def myascii(input_str: AnyStr) -> AnyStr:
    '''Converts to ascii (remove accents etc.)'''
    bunistr = isinstance(input_str, unicode23)
    if bunistr:
        ustr = input_str
    elif isinstance(input_str, byte23):
        # ustr = unicode23(input_str, file_encoding)
        for codec in _TOSTR_ENCODING:
            try:
                ustr = unicode23(input_str, codec)
                break
            except UnicodeError:
                continue
    else:
        return unicode23(input_str)
    u_nkfd_form = unicodedata.normalize('NFKD', ustr)
    u_filtred = ''.join([c for c in u_nkfd_form if not unicodedata.combining(c)])
    if isinstance(input_str, unicode23):
        return u_filtred
    else:
        return u_filtred.encode('ascii', 'replace')
ascii = myascii
#****f* functions/is_wq
# SYNTAX
#   * bret = is_wq(attr, lang=None)
# ARGUMENT
#   unicode or byte string attr: attribute
#   str lang: kernel lang (default None)
# RESULT
#   bool bret: true if att in T, C0 .. C9, $0 .. $9, $A .. $Z
# HISTORY
#   * introduced 14.03.2020 - 2.1.1
#   * added water hardness (TH / HD / DU 24.11.2021 - 2.2.7)
#****
def is_wq(attr: AnyStr) -> bool:
    '''Returns True if attr is a WQ attribute '''
    return _PTN_WQ_ATTR.match(attr.upper()) is not None

#****f* functions/winstr, utf, ws, aws, codewinfile
# SYNTAX
#   * out_txt = winstr(input_str)
#   * out_txt = utf(input_str)
#   * out_str = ws(input_str)
#   * out_astr = aws(input_str)
# ARGUMENT
#   unicode or byte string input_str: string value to be encoded to windows-compatible string
# RESULT
#   * out_txt encoded into Windows-1252 or utf-8 (no change if no accent or special character)
#   * out_str: (unicode) string in python3, Windows-1252 encoded string in python2
#   * out_astr: (unicode) string in python3, ascii unicode string in python2
# REMARK
#   codewinfile and winstr are synonyms
# HISTORY
#   * ws has been introduced 30.05.2018 - 1.9.3
#   * aws has been introduced 12.06.2018 - 1.9.5
#****
def winstr(input_str: AnyStr) -> bytes:
    '''Encode to cp1252'''
    return tostr(input_str).encode('cp1252')  # Windows-1252
codewinfile = winstr

def utf(input_str: AnyStr) -> bytes:
    '''Encode to utf8'''
    return tostr(input_str).encode('utf-8')

# ws = tostr if PY3 or WSVERS > 7 else winstr
ws = tostr if PY3 or WSVERS not in ('6', '7',) else winstr
aws = tostr if PY3 else myascii

#****f* functions/toidpic
# SYNTAX
#   out_str = toidpic(input_str)
# ARGUMENT
#   unicode or string input_str: string value to be converted to a Piccolo ID
# RESULT
#   ascii string where blank, comma, equal are replaced with underscore, other
#   non litteral or digit are replaced with minus.
#****
def toidpic(txt: AnyStr) -> AnyStr:
    'Returns a Piccolo/Picalor compatible ID'
    txt = txt.strip()
    if not txt:
        return '_EMPTY_'
    txt = myascii(txt)
    txt = _PTN_BLANKS.sub('_', txt)
    txt = _PTN_NO_IDSTR.sub('-', txt)
    txt = _PTN_SEQUEN.sub('-', txt)
    return txt

def read_as_idpic(txt: AnyStr) -> AnyStr:
    'Returns a Piccolo/Picalor compatible ID'
    txt = txt.strip().upper()
    if not txt:
        return ''
    txt = _PTN_NO_IDCHAR.sub('?', txt)
    return txt

def toidpic_old(txt):
    'Returns a Piccolo/Picalor compatible ID'
    txt = txt.strip()
    if txt == '':
        return '_EMPTY_'
    txt = myascii(txt.replace('  ', '_').replace(' ', '_')
                     .replace(',', '_').replace('=', '_')
                     .replace('.', '-').replace('/', '-')
                     .replace('(', '-').replace(')' '-')
                     .replace('_-_', '-'))
    return txt

#****f* functions/gfloat, gint, gbool
# SYNTAX
#   * fval = gfloat(input_string)
#   * ival = gint(input_string)
#   * bval = gbool(input_string)
# ARGUMENT
#   string input_str: string value to be converted to a float or int or bool.
#   The decimal separator can either be '.' or ','.
# RESULT
#   * float fval or int ival: numerical value after conversion
#   * bool bval: semantic boolean value.
#     Unlike bool builtin, gbool('False'), gbool('n') and gbool('0') return False
# HISTORY
#   171127: gbool added
#****
def gfloat(strg: AnyStr) -> float:
    "Conversion d'une chaine en float avec '.' ou ',' en separateur decimal"
    try:
        return float(strg)
    except ValueError:
        return float(strg.replace(',', '.', 1))

def gint(strg: AnyStr) -> int:
    "Conversion d'une chaine en int avec '.' ou ',' en separateur decimal"
    try:
        return int(strg)
    except ValueError:
        return int(gfloat(strg))

def gbool(val) -> bool:
    '''Custom conversion to bool'''
    if is_text(val):
        val = tostr(val).lower()
    if val in ("true", "oui", "yes", "vrai", "o", "ok", "y", "t", "v", "1"):
        return True
    if val in ("false", "non", "faux", "no", "n", "f", "0"):
        return False
    return bool(val)

#****f* functions/list2file
# SYNTAX
#   fname = list2file(idlist [, header] [, footer] [, folder] [, suffix])
# ARGUMENT
#   * idlist: list of id (unicode str).
#   * header: optional string to be placed before the list
#   * footer: optional string to be placed after the list
#   * folder: optional folder to create the file (default temp folder).
#   * suffix: optional string to be used as a suffix for fname. Defaults to 'IDs.txt'
# RESULT
#   str fname: name of a temporary file containing header if any, elements of idlist,
#   footer if any, one per line.
#****
def list2file(idlist: Sequence[str], header: str = None, footer: str = None,
                folder: str = None, suffix: str = 'IDs.txt') -> str:
    'Converts a str list into a file'
    wconv = winstr
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as fsel:
        if header is not None:
            fsel.write(wconv(header + '\n'))
        fsel.write(wconv('\n'.join(idlist)))
        if footer is not None:
            fsel.write(wconv('\n' + footer))
    if folder is not None and OP.exists(folder):
        name = OP.join(folder, OP.basename(fsel.name))
        shutil.move(fsel.name, name)
        return name
    else:
        return fsel.name

#****f* functions/XMLduration
# SYNTAX
#   ival = XMLduration(input_string)
# ARGUMENT
#   string input_str: XML duration string value to be converted to a number of seconds.
#
#   The input format is [-]PnYnMnDTnHnMnS where:
#   * leading 'P' is mandatory,
#   * at least one duration item must be present
#   * 'T' is mandatory if any hour, minute, second is present
#   * all items are integers except second that may be either int or float.
# RESULT
#   int ival: number of seconds
#****
def XMLduration(arg: str) -> float:
    '''Converts an ISO duration to seconds'''
    # import re
    # from datetime import timedelta
    if not arg:
        return 0.0
    elif arg[0] != 'P':
        raise ValueError
    else:
        regex = re.compile(r'(?P<sign>-?)P(?:(?P<years>\d+)Y)?(?:(?P<months>\d+)M)?(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?')
        # Fetch the match groups with default value of 0 (not None)
        duration = regex.match(arg).groupdict(0)
        # Create the timedelta object from extracted groups
        delta = timedelta(days=int(duration['days']) + (int(duration['months']) * 30) + (int(duration['years']) * 365),
                          hours=int(duration['hours']),
                          minutes=int(duration['minutes']),
                          seconds=int(duration['seconds']))
        if duration['sign'] == "-":
            delta *= -1
        return delta.days * 86400 + delta.seconds

#****f* functions/decode_time, decode_date
# SYNTAX
#   * fval = decode_time(input_tstring [, factor])
#   * dval = decode_date(input_dstring)
# ARGUMENT
#   * string input_tstr: duration in the form of float or hh:mm:ss or XML duration string.
#   * optional float factor: multiplier (default to 1)
#   * string input_dstr: date in a versatile format YYYY/MM/DD hh:mm:ss or DD/MM/YYYY hh:mm:ss
#     or the iso format YYYY-MM-DDThh:mm:ss where 'T' can be replaced with a blank ' '.
# RESULT
#   * float fval: number of seconds. The result is multiplied by factor only if input_string is a float.
#   * date dval: date. The exception 'ValueError' is raised if the date cannot be read.
#****
def decode_time(strg: str, facteur: float = 1.0) -> float:
    "Retourne le nombre de secondes 'hh:mm:ss' or 'nombre' * facteur "
    # if len(strg) < 10:
    champs = strg.split(":")
    if len(champs) == 1:
        # champ numerique ou PTxHyMz.zzS
        try:
            duree = float(strg) * facteur
        except ValueError:
            duree = XMLduration(strg)
    else:
        # hh:mm[:ss]
        duree = 60*(float(champs[1]) + 60*float(champs[0]))
        if len(champs) == 3:
            duree = duree + float(champs[2])
    return duree

def decode_date(strin: str) -> datetime:
    """ Transforme une date ASCII en datetime
        Produit l'exception ValueError si le format n'est pas reconnu"""
    # from datetime import datetime
    strg = strin.replace('/', '-').replace(' ', 'T').rstrip('Z')
    try:
        result = datetime.strptime(strg, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            result = datetime.strptime(strg, "%d-%m-%YT%H:%M:%S")
        except ValueError:
            champs = strg.split('T')
            try:
                jjmmaa = datetime.strptime(champs[0], "%Y-%m-%d")
            except ValueError:
                jjmmaa = datetime.strptime(champs[0], "%d-%m-%Y")
#                try:
#                    jjmmaa = datetime.strptime(champs[0],"%d-%m-%Y")
#                except ValueError:
#                    return datetime(2222,11,22,11,22,11)
            if len(champs) > 1:
                hms = champs[1].split(':')
                result = jjmmaa.replace(hour=int(hms[0]), minute=int(hms[1]))
            else:
                result = jjmmaa
        if len(strin) > 20:
            # decoder le tzinfo
            pass
    return result

class TZ(tzinfo):
    '''memo for getting UTC offset '''
    def utcoffset(self, dt):
        return timedelta(minutes=-dt)

#****f* functions/envoi_msg
# SYNTAX
#   status = envoi_msg(exp, dst, objet, texte [, serveur=smtp.safege.net] [, pwd=None])
# ARGUMENT
#   * string exp: adresse expediteur du message
#   * string dst: adresse destinataire (ou [dst1, dst2 ... ])
#   * string objet: objet
#   * string texte: texte du message
#   * string serveur (optionnel): serveur d'envoi
# RESULT
#   * bool status: True si le message est parti sans erreur
# HISTORY
#   * 171201: added pwd kwarg
#****
def envoi_msg(exp: str, dst: str, objet: str, texte: str,
                serveur: str = 'smtp.safege.net', pwd: str = None) -> bool:
    '''Sends a simple message by smtp'''
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Create the enclosing message
    msg = MIMEMultipart()
    msg['Subject'] = objet
    # if '@' not in exp:
    #     exp += '@safege.com'
    msg['From'] = exp
    if isinstance(dst, (list, tuple)):
        msg['To'] = ";".join(dst)
    else:
        msg['To'] = dst
    msg.preamble = "SUEZ Consulting - DCS 2021"
    # Texte du message
    msg.attach(MIMEText(texte, 'plain', 'utf-8'))

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(timeout=3)
    try:
        s.connect(serveur)
        if pwd is not None:
            s.starttls()
            s.login(exp, pwd)
        s.sendmail(exp, dst, msg.as_string())
        s.close()
        return True
    except:
        return False

def send_report(appli, addl_text: str = '', dst: str = 'piccolo@safege.fr') -> None:
    '''Collect user & computer info and sends report'''
    try:
        vers = ' v' + appli.vers if appli.vers else ''
    except AttributeError:
        vers = ''
    # username - provided as USERPRINCIPALNAME or USERNAME
    try:
        username = os.environ['UserPrincipalName']
    except KeyError:
        try:
            username = os.environ['username']
        except KeyError:
            username = '?'
    try:
        computername = os.environ['computername']
    except KeyError:
        computername = '?'
    try:
        _uname = uname()
        envoi_msg(exp=username, dst=dst,
                objet='[Usage outil Consulting] - ' + appli.nom,
                texte=('\nTool: ' + appli.nom + vers +
                '\nPython: ' + '.'.join(map(str, sys.version_info[0:3])) +
                ' (' + ('64' if X64 else '32') + ' bits)' +
                '\nUser: ' + username +
                '\nComputer: ' + computername +
                '\nSystem: ' + _uname.system + _uname.version +
                '\n\n' + addl_text + '\n'))
        print(' * Usage report sent to:', dst)
    except KeyError:
        pass

#****f* functions/utf8_bom_encoding
# SYNTAX
#   encoding = utf8_bom_encoding(filename=None)
# ARGUMENT
#   * string filename: input file name (defaults to None)
# RESULT
#   string encoding:
#    * 'utf_8_sig' if no file argument passed
#    * 'utf_8_sig' if file exists and encoding is utf8-bom
#    * None if file does not exists or encoding is not utf8-bom
# HISTORY
#   * 210310 (2.1.7): creation
#   * 210423 (2.1.9): fix empty file resulting in StopIteration exception
#****
def utf8_bom_encoding(filename: str = None) -> Union[str, None]:
    '''Guess if fname is encoded as utf8 with BOM'''
    # UBOM = '\ufeff'
    BOM = b'\xef\xbb\xbf'
    UTF8_BOM_ENCODING = 'utf_8_sig'
    if filename is None:
        return UTF8_BOM_ENCODING
    if not OP.exists(filename):
        return None
    with open(filename, 'rb') as fin:
        try:
            line = next(fin)
        except StopIteration:
            return None
        return UTF8_BOM_ENCODING if line.startswith(BOM) else None

#****f* functions/lec_csv
# SYNTAX
#   header, content = lec_csv(filename [, sep=',']
#   [, skip_before=0] [, skip_after=0] [, as_tuple=False])
# ARGUMENT
#   * string filename: input file name
#   * string sep: optional column separator. Default ','.
#   * int skip_before: optional number of lines to be skipped before reading header.
#   * int skip_after: optional number of lines to be skipped after reading header.
#   * bool as_tuple: optional bool indicating if records are lists (default) or tuples.
# RESULT
#   * header: list/tuple of strings read from the 1st line
#   * content: list of lines, each being a list/tuple of text fields
# REMARK
#   The entire file is read into 'content'
#****
def lec_csv(filename: str, sep: str = ',', skip_before: int = 0, skip_after: str = 0,
            as_tuple: bool = False) -> Tuple[List[any], List[Tuple[any, ...]]]:
    '''
Lecture d'un fichier CSV et retour du contenu
    argument:
        fichier: nom complet du ficher
        sep:     separeteur optionnel (defaut virgule)
    retour :
        header: premiere ligne (liste de champs)
        body:  listes des lignes, chacune etant une liste de champs
    '''
    import csv
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=sep)
        headers = [next(reader) for _i in range(1 + skip_before + skip_after)]
        header = headers[skip_before]
        if as_tuple:
            body = [tuple(line) for line in reader]
            header = tuple(header)
        else:
            body = list(reader)
    del csv
    return header, body

#****f* functions/FichInfo, banner
# SYNTAX
#   * fi = FichInfo(filename)
#   * txt = fi.banner()
# ARGUMENT
#   string filename: input file name - expects the name of the caller '__file__'
# RESULT
#   a class member containing the following fields and method:
#   * nom: basename of the input filename without extension
#   * vers: date of last modification of filename in the form 'YYMMDD'
#   * pyvers: current version of python 'x.y.z'
#   * banner() returns a string containing all the elements above
# HISTORY
#   * 180814 (1.9.8): appended '32/64 bits' to banner info
#****
class FichInfo(object):
    """FichInfo:
        nom = nom de fichier
        vers = date de modification au format (AAAAMMJJ)
        pyvers = version de Python
    """
    def __init__(self, nom: str, version:str = ''):
        snom = tostr(nom)
        self.full = snom
        self.nom = OP.splitext(OP.basename(snom))[0]
        self.vers = version + ' ' if version else ''
        self.vers += date.fromtimestamp(os.stat(snom).st_mtime).strftime("(%Y%m%d)")
        self.pyvers = '.'.join(map(str, sys.version_info[0:3]))
        self.wkdir = OP.dirname(snom)

    def banner(self) -> str:
        '''Returns a string with: app name and version, python version, 32/64 bit'''
        bits = '64' if sys.maxsize > 2**32 else '32'
        return ' '.join((self.nom, self.vers, '- Python', self.pyvers, '-', bits, 'bits'))

#****f* functions/IniFile, get, set, getall, setall, save
# SYNTAX
#   * mycfg = IniFile(filename, folder=None)
#   * txt = mycfg.get(group, key, default)
#   * obj = mycfg.getall(group)
#   * mycfg.set(group, key, value)
#   * mycfg.setall(group, obj)
#   * value = mycfg.remove(group, key)
#   * mycfg.save(folder=None)
# ARGUMENT
#   * string filename: input file name - expects the name of the caller '__file__'
#     in order to get the same file path and name with extension .json
#   * string folder: alternate folder to load from / save to
#   * string group: group of keys
#   * string key, value: value of key to be stored/retrieved
#   * object obj: object to be stored; may be a dict of lists.
# RESULT
#   * mycfg = IniFile(filename): loads the init file and returns the groups of keys
#   * val = mycfg.get(group, key, val) allows to update val if the value of group/key
#     is defined.
#   * object obj: object retrieved.
#   * set() allows to set key with value
#   * save() saves the files back. If folder was given and exists, then the file
#     is saved into that folder instead of the filename folder.
#   * remove() returns the mapping or None if not found
# HISTORY
#   * Default format changed from .xml to .json in aug 2017;
#     previous settings will be converted.
#   * getall and setall added in march 2018.
#   * 180705 (1.9.7) Inifile handles non-ascii filenames
#   * 181218 (2.0.4) get returns unicode strings
#   * 200506 (2.1.2) remove method
#   * 210426 (2.1.9) remove trailing '-<maxver><minver>' from the basename
#   * 211012 (2.2.5) add folder kwarg
#****
class _jsonIniFile(object):
    ''' Gestion d'un fichier de parametres initiaux en JSON'''
    def __init__(self, fname: str, folder: str = None):
        pname = OP.splitext(tostr(fname))[0]
        py_vers = '-' + ''.join(sys.version.split('.')[0:2])
        if pname.endswith(py_vers):
            self.old_fname = pname + '.json'
            pname = pname[:-len(py_vers)]
        else:
            self.old_fname = ''
        self.fname = pname + '.json'
        if folder is not None and OP.isdir(folder):
            self.fname = OP.join(folder, OP.basename(self.fname))
        for pname in (self.old_fname, self.fname, pname + '.json'):
            if pname and OP.exists(pname):
                with copen(pname, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                break
            else:
                self.data = dict()

    def get(self, groupname: str, keyname: str, default):
        '''get keyname from groupname, returns default if not found'''
        try:
            retval = self.data[groupname][keyname]
            return tostr(retval) if is_b(retval) else retval
        except KeyError:
            return default

    def getall(self, groupname: str) -> Mapping:
        '''get all items from groupname'''
        try:
            return self.data[groupname]
        except KeyError:
            return {}

    def set(self, groupname: str, keyname: str, value) -> None:
        '''sets keyname of groupname'''
        try:
            self.data[groupname][keyname] = value
        except KeyError:
            self.data[groupname] = {keyname: value}

    def setall(self, groupname: str, value) -> None:
        '''sets groupname'''
        self.data[groupname] = value

    def remove(self, groupname: str, keyname: str):
        '''Removes keyname from groupname if present'''
        return self.data[groupname].pop(keyname, None)

    def save(self, encoding: str = 'utf-8', folder: str = None) -> None:
        '''Save param file - remove old -<maxvers><minvers> in any
        if folder is provided and exists, then save in folder'''
        if folder is not None and OP.isdir(folder):
            self.fname = OP.join(folder, OP.basename(self.fname))
        with copen(self.fname, 'w', encoding='utf-8') as f:
            encode = {} if PY3 else dict(encoding=encoding)
            json.dump(self.data, f, indent=2, **encode) #, encoding=encoding)
        if self.old_fname and OP.exists(self.old_fname):
            print('Old parameter file:', OP.basename(self.old_fname),
                  'has been replaced with:', OP.basename(self.fname))
            os.remove(self.old_fname)

class _xmlIniFile(object):
    ''' Gestion d'un fichier de parametres initiaux en XML'''
    def __init__(self, fname):
        from xml.etree.ElementTree import parse, Element, ElementTree
        pname = OP.splitext(fname)[0]
        self.fname = pname + '.xml'
        if OP.exists(self.fname):
            self.tree = parse(self.fname)
            self.root = self.tree.getroot()
        else:
            self.root = Element(OP.basename(pname))
            self.tree = ElementTree(self.root)
        del parse, Element, ElementTree, pname

    def get(self, groupname, keyname, default):
        return self.root.findtext(groupname + '/' + keyname, default)

    def set(self, groupname, keyname, value):
        from xml.etree.ElementTree import SubElement
        rgroup = self.root.find(groupname)
        if rgroup is None:
            rgroup = SubElement(self.root, groupname)
        item = rgroup.find(keyname)
        if item is None:
            item = SubElement(rgroup, keyname)
        item.text = value

    def save(self, encoding='utf-8', xml_declaration=True):
        self.tree.write(self.fname, encoding, xml_declaration)

class IniFile(_jsonIniFile):
    ''' Gestion d'un fichier de parametres initiaux en XML /JSON
    Conversion en JSON'''
    def __init__(self, fname: str, folder: str = None):
        sfname = tostr(fname)
        # print('initialisation file:', sfname)
        _jsonIniFile.__init__(self, sfname, folder)
        pname, ext = OP.splitext(sfname)
        TYPES = ('.json', '.xml')
        if ext.lower() not in TYPES:
            for ext in TYPES:
                if OP.exists(pname + ext):
                    break
            else:
                ext = '.json'
        if ext.lower() != '.json':
            xml = _xmlIniFile(sfname)
            # conversion XML en dict --> JSON
            self.data = dict()
            for xgroup in xml.root:
                self.data[xgroup.tag] = dict(((item.tag, item.text) for item in xgroup))
            del xml
        del pname, ext

#****f* functions/IniFile1L, get, set, remove, save
# SYNTAX
#   * mycfg = IniFile1L(filename)
#   * txt = mycfg.get(key, default)
#   * mycfg.set(key, value)
#   * value = mycfg.remove(key)
#   * mycfg.save()
# ARGUMENT
#   * string filename: input file name - expects the name of the caller '__file__'
#     in order to get the same file path and name with extension .json
#   * string key, value: value of key to be stored/retrieved
# RESULT
#   * mycfg = IniFile1L(filename): loads the init file and returns the keys
#   * val = mycfg.get(key, val) allows to update val if the value of key is defined.
#   * set() allows to set key with value
#   * save() saves the files back
#   * remove() returns the mapping or None if not found
# HISTORY
#   * 210426 (2.1.9) remove trailing '-<maxver><minver>' from the basename
#   * 210708 (2.2.4) getall and setall
#****
class IniFile1L(_jsonIniFile):
    ''' Gestion d'un fichier de parametres initiaux en JSON
    version a un seul niveau - init et save inchanges'''
    def get(self, keyname: str, default):
        '''getter'''
        if keyname not in self.data:
            self.data[keyname] = default
        retval = self.data[keyname]
        return tostr(retval) if is_b(retval) else retval

    def getall(self):
        '''Returns the entire dict'''
        return self.data

    def set(self, keyname: str, value):
        '''setter'''
        self.data[keyname] = value

    def setall(self, dictvals):
        '''Reset the entire dict'''
        self.data = dictvals

    def remove(self, keyname: str):
        '''Removes keyname if present'''
        return self.data.pop(keyname, None)

VectF = Union[Sequence[float], np.ndarray]
def tsadd(t1: VectF, v1: VectF, n1: int,
          t2: VectF, v2: VectF, n2: int) -> Tuple[np.ndarray, np.ndarray, int]:
    '''Adds two TS considering asynchronous times'''
    t, v = [], []
    k1, k2 = 0, 0
    p1, p2 = v1[0], v2[0]
    while True:
        if t1[k1] < t2[k2]:
            t.append(t1[k1])
            p1 = v1[k1]
            k1 += 1
        elif t1[k1] > t2[k2]:
            t.append(t2[k2])
            p2 = v2[k2]
            k2 += 1
        else:
            t.append(t1[k1])
            p1, p2 = v1[k1], v2[k2]
            k1 += 1
            k2 += 1
        v.append(p1+p2)
        if k1 == n1 or k2 == n2:
            break
    return np.array(t), np.array(v), len(t)

#****f* functions/roundval, scaladjust
# PURPOSE
#   Computes a rounded approximation of a float number
# SYNTAX
#   * rmin, rbest, rmax = roundval(val, reltol= 0.01)
#   * rval = scaladjust(val)
# ARGUMENT
#   * float val: value to be rounded
# RESULT
#   * float rmin, rmax: lower and upper values approximations (rmax - rmin < reltol*|val|)
#   * float rbest: best approximation (one of rmin, rmax)
#   * float rval: value rounded at 1., 2. or 5. in the order of magnitude of val.
# REMARK
#   scaladjust is used to determine the grid interval for plots as scaladjust(0.25*(ymax-ymin))
# HISTORY:
#   * 20.03.13 (2.1.1) fixed rounding when val < 1
#****
def roundval(val: float, reltol: float = 0.01) -> Tuple[float, float, float]:
    'Calcul d\'une valeur arrondie proche a reltol pres'
    tol = reltol * abs(val)
    d = log(tol, 10.) + 0.0001
    n = int(d)
    if n < 0:
        n -= 1
    base = 10**n
    rest = tol / base + 0.0001
    for x in (7.5, 5.0, 4.0, 2.5, 2.0, 1.5, 1.0):
        if x <= rest:
            break
    rest = base*x
    r1 = rest * (val//rest)
    if val >= 0.0:
        r2 = r1 + rest
    else:
        r1, r2 = r1-rest, r1
    r3 = r1 if r2-val > val-r1 else r2
    return (r1, r3, r2)

def scaladjust(val: float) -> float:
    'Renvoi d\'une valeur arrondie a 1 2 5 pres'
    val = abs(val)
    n = int(log(val, 10.) + 99) - 99
    e = 10.0**n
    m = val / e
    if m < 1.5:
        m = 1.0
    elif m < 3.0:
        m = 2.0
    elif m < 7.5:
        m = 5.0
    else:
        m = 10.0
    return m * e

#****f* functions/dist_to_poly, dist_p_seg, dist, split_poly_at
# PURPOSE
#   Computes the distance of a point (xn, yn) to a polyline or a segment
# SYNTAX
#   * d, s1, s2 = dist_to_poly(xn, yn, nbpoly, xpoly, ypoly)
#   * d, s1, s2 = dist_to_poly(xn, yn, points)
#   * d, s, slength = dist_p_seg(xn, yn, x1, y1, x2, y2)
#   * d = dist(x1, y1, x2, y2)
#   * k, xsplit, ysplit, totlen = split_poly_at(xpoly, ypoly, s, nbpoly)
# ARGUMENTS
#   * double xn, yn: point coordinates
#   * int nbpoly: number of points
#   * double[] xpoly, ypoly: vertices of the polyline
#     (number of vertices in the polyline >= 2; 2 for a plain segment)
#   * sequence points: sequence of pairs of float or double
#   * double x1, y1, x2, y2: coordinates of a segment extremities
#   * double s: curvilinear position to split at
# RESULT
#   * double d: distance of point to the polyline or segment
#   * double s1, s2: curvilinear position of the point projection on the polyline, from each extremity
#   * double s: curvilinear position of the point projection on the segment, starting from (x1, y1)
#   * double slength: length of the segment (x1, y1), (x2, y2)
#   * int k: rank of splitted segment (0: before or at start; nb: after or at end)
#   * double xsplit, ysplit: coordinates of the scurvilinear position s on the plyline
#   * double totlen: total length of the polyline before splitting
# REMARKS
#   * d= 0 means that the point is on the polyline.
#   * s1>0 and s2>0 means that the point projection is at least on one of the segments.
#  HISTORY
#   * 1.7.1 (170223) introduced compiled versions of these 3 functions;
#                    pure python versions names are prefixed with '_'
#   * 2.1.6 (210126) added split_poly_at
#   * 2.1.7 (210324) fix split_poly_at 'ValueError: not enough values to unpack (expected 3, got 2)'
#****
def _dist(x1 : float, y1 : float, x2 : float, y2 : float) -> float:
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def _dist_p_seg(px : float, py : float,
                x1 : float, y1 : float,
                x2 : float, y2 : float) -> Tuple[float, float, float]:
    '''computes minimum distance from a point and a line segment '''
    # adapted from:
    # http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/source.vba
    seglen = _dist(x1, y1, x2, y2)

    if seglen < 0.00001:
        distpseg = _dist(px, py, x1, y1)
        return distpseg, 0.0, seglen

    u1 = (((px - x1) * (x2 - x1)) + ((py - y1) * (y2 - y1)))
    u = u1 / (seglen * seglen)

    if (u < 0.00001) or (u > 1):
        #// closest point does not fall within the line segment, take the shorter distance
        #// to an endpoint
        ix = _dist(px, py, x1, y1)
        iy = _dist(px, py, x2, y2)
        if ix > iy:
            distpseg = iy
            abscisse = seglen
        else:
            distpseg = ix
            abscisse = 0.0
    else:
        # Intersecting point is on the line, use the formula
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        distpseg = _dist(px, py, ix, iy)
        abscisse = _dist(x1, y1, ix, iy)
    return distpseg, abscisse, seglen

def _dist_to_poly(xn : float, yn : float, nb : int,
                  xpoly : VectF, ypoly : VectF) -> Tuple[float, float, float]:
    '''computes minimum distance from a point and a polyline
    i.e. browsing consecutive segments of the polyline.
    Returns the distance, and curvilinear position from extremities'''
    x1, y1 = xpoly[0], ypoly[0]
    dmin = _dist(xn, yn, x1, y1)
    smin, totlen = 0.0, 0.0
    # Browse the segments
    for x2, y2 in izip(xpoly[1:], ypoly[1:]):
        d, s, curlen = dist_p_seg(xn, yn, x1, y1, x2, y2)
        if d < dmin:
            # closest segment: remember the abscisse and distance
            smin = totlen + s
            dmin = d
        # update the total length
        totlen += curlen
        x1, y1 = x2, y2
    return dmin, smin, totlen-smin

def _split_poly_at(xpoly : VectF, ypoly : VectF, s : float,
                   size_poly : int = None) -> Tuple[int, float, float, float]:
    '''Returns the segment index, x, y pos of the curvilinear
    position s on polyline xpoly, ypoly; and the total lenght of polyline'''
    nb = size_poly
    x1, y1, totlen = xpoly[0], ypoly[0], 0
    for x2, y2 in izip(xpoly[:nb], ypoly[:nb]):
        totlen += dist(x1, y1, x2, y2)
        x1, y1 = x2, y2
    #
    x1, y1, curlen = xpoly[0], ypoly[0], 0
    if s <= curlen:
        return 0, x1, y1, totlen
    # Browse the segments
    if nb is None:
        nb = len(xpoly)
    for k, (x2, y2) in enumerate(izip(xpoly[:nb], ypoly[:nb])):
        slength = dist(x1, y1, x2, y2)
        curlen += slength
        if s <= curlen:
            frac = (totlen - s) / slength
            xsplit = x2 + frac *(x1 - x2)
            ysplit = y2 + frac *(y1 - y2)
            return k, xsplit, ysplit, totlen
        x1, y1 = x2, y2
    return nb, x1, y1, totlen

try:
    import ganessa._pyganutl as _utl
except ImportError:
    dist = _dist
    dist_p_seg = _dist_p_seg
    dist_to_poly = _dist_to_poly
    split_poly_at = _split_poly_at
else:
    dist = _utl.dist
    dist_p_seg = _utl.dist_p_seg
    def dist_to_poly(x, y, n, xp, yp):
        return _utl.dist_to_poly(x, y, xp, yp, n)
    try:
        split_poly_at = _utl.split_poly_at
    except AttributeError:
        split_poly_at = _split_poly_at

#****k* iterators/group
# SYNTAX
#   for items in group(iterable, count= 2):
# ARGUMENT
#   * iterable: iterable
#   * int count: group size
# RESULT
#   this iterator allows to return the elements of iterable grouped
#   by lists of size count. The last list may contain less than group elements
# HISTORY
#   * 1.7.6 (170613): iterator added
#   * 2.0.0 (180816): python 3.7 compatibility
#****
def group(iterable: Iterable, count: int) -> Iterable:
    '''returns elements from the iterable grouped by count
    The last set, possibly incomplete, is also returned'''
    itr = iter(iterable)
    while True:
        # yield tuple([itr.next() for i in range(count)])
        chunk = []
        for _i in range(count):
            try:
                chunk.append(next(itr))
            except StopIteration:
                if chunk:
                    yield chunk
                return
        yield chunk

#****f* functions/call_until_false
# PURPOSE
#   Calls a function with args until return is false
# SYNTAX
#   * res = call_until_false(func, args [, maxcount= -1])
# ARGUMENT
#   * callable func: function to be called with args
#   * args: *args to func
#   * int maxcount: optional max count (defaults to -1:
#     infinite sequence)
# RESULT
#   * tuple of sucessive return values
# REMARK
#   Use of this function is meaningful with side-effect functions.
#   The function is repeatedly called with the same argument list; the result
#   is not just duplicated.
# HISTORY
#   * introduced 2.0.3 (1801011)
#****
def call_until_false(func: Callable, args, maxcount: int = 99) -> Tuple[any, ...]:
    '''Repeteadly calls func'''
    count, ret, retvals = maxcount, func(*args), []
    while ret and count:
        retvals.append(ret)
        ret = func(*args)
        count -= 1
    return tuple(retvals)

def copyright_years(startyear: Union[int, str], sep: str = '-') -> str:
    '''Returns the years interval from start year'''
    syear = int(startyear)
    cyear = date.today().year
    ret = str(syear)
    if cyear != syear:
        ret += sep + str(cyear)
    return ret

def version_as_tuple(version: Union[str, List, Tuple]) -> Tuple[int, ...]:
    if isinstance(version, list):
        return tuple(version)
    if isinstance(version, tuple):
        return version
    return tuple(map(int, version.split('.')[0:3]))

def cmp_version(actual : Union[str, List, Tuple], target : Union[str, List, Tuple]) -> int:
    '''Compares version numbers'''
    act = version_as_tuple(actual)
    tgt = version_as_tuple(target)
    return (act > tgt) - (act < tgt)

#****f* functions/piccolo_context
# PURPOSE
#   Reads Context.pic and return colorset and tresholds for given attribute
# SYNTAX
#   * attr, cname, tvals, cvals = piccolo_context(fcontext, attr=None, verbose=False)
# ARGUMENT
#   * str fcontext: name of context file
#   * str attr: attribute to find colorset and thresholds
#   * bool verbose: for printing lookup messages
# RESULT
#   * str attr: attribute found
#   * str cname: name of colorset
#   * list tvals: str list of values / float list of thresholds
#   * list cvals: str list of colors
# REMARK
#   Returns as many colors as str thresholds if attr is alphanumeric;
#   one more color than float thresholds if attr is numeric.
#
#   A tuple of None is returned in case of failure
# HISTORY
#   * introduced 2.2.6 (211117)
#****
def piccolo_context(fcontext: str, attr: str = None, verbose: bool = False) -> Tuple[str, str, Union[List[float], List[str]], List[str]]:
    '''Reads *french* Piccolo context file and retrieve color set and thresholds for 'attr'
    Returns a tuple:
     - attribute (last attribute seen if attr is None)
     - name of colorset
     - list of threshold values
     - list of colors (one more than tresholds for non alphanumerical attribs)'''
    # patterns
    pcoldef = re.compile(r'DEFINIR\s+COULEUR\s+([-\w]+)?')
    ppaldef = re.compile(r'PALETTE\s+(ARC|NOEUD)\s+([-\w]{3,}\s+)?(\w{1,2})\s+([- \+\w\.\*]+)')
    # conversion functions
    def _to_RGB(color):
        '''Converts a Piccolo color name to RGB'''
        HALF, MOST, FULL = 127, 191, 255
        CMAP = {'BLANC': (MOST, MOST, MOST), 'BLANC BLINK': (FULL, FULL, FULL),
                'NOIR': (0, 0, 0), 'NOIR BLINK': (3, 3, 3),
                'ROUGE': (MOST, 0, 0), 'ROUGE BLINK': (FULL, 0, 0),
                'VERT': (0, MOST, 0), 'VERT BLINK': (0, FULL, 0),
                'BLEU': (0, 0, MOST), 'BLEU BLINK': (0, 0, FULL),
                'JAUNE': (MOST, MOST, 0), 'JAUNE BLINK': (FULL, FULL, 0),
                'ROSE': (MOST, 0, MOST), 'ROSE BLINK': (FULL, 0, FULL),
                'CIEL': (0, MOST, MOST), 'CIEL BLINK': (0, FULL, FULL)}
        if is_text(color):
            try:
                return CMAP[color]
            except KeyError:
                return (HALF, HALF, HALF)
        else:
            return color
    def _to_hex(RGB):
        '''Converts a RGB tuple into HTML color'''
        return '#{:02x}{:02x}{:02x}'.format(*RGB)

    # Default color set for Piccolo
    colorsets = {'standard': ('BLANC', 'CIEL', 'CIEL BLINK', 'VERT BLINK', 'JAUNE',
                              'JAUNE BLINK', 'ROSE BLINK', 'ROUGE BLINK', 'ROUGE')}
    palets = {}
    alphanum_attr = {'ZN', 'ZP', 'M', 'CD', 'DN', 'A', 'N', 'PA', 'DI'}
    attrib = 'D'
    if not OP.exists(fcontext):
        if verbose:
            print('Not found:', fcontext)
        return None, None, None, None
    # Read context.pic content
    with open(fcontext, 'r') as fpic:
        for ligne in fpic:
            ligne = tostr(ligne.strip().upper())
            # find colorsets definitions
            m = pcoldef.search(ligne)
            if m is not None:
                colorset = m[1]
                if colorset.startswith('INIT'):
                    continue
                colorsets[colorset] = []
                while ligne != 'FIN':
                    ligne = tostr(next(fpic)).strip().upper()
                    if ligne.startswith('RGB'):
                        colorsets[colorset].append(list(map(int, ligne.split()[1:])))
                    elif ligne.startswith('COULEUR'):
                        colorsets[colorset].append(ligne.split(' ', 1)[1])
                continue
            # finds palettes definitions
            m = ppaldef.search(ligne)
            if m is not None:
                # groups are: PALETTE ARC|NOEUD [colorset] attrib values ...
                typ = m[1].upper()
                attrib = m[3].split()[-1]
                # skip node palette if already defined
                if typ == 'NOEUD' and attrib in palets:
                    continue
                if attrib in alphanum_attr:
                    palets[attrib] = (m[2], m[4].split())
                else:
                    try:
                        palets[attrib] = (m[2], list(map(float, m[4].split())))
                    except ValueError:
                        continue
    #if attr not define, use last define
    if attr is None:
        attr = attrib
    # select color parameters for attr: first from palette the colorset if any
    try:
        colorset, thresholds = palets[attr.upper()]
    except KeyError:
        if verbose:
            print(f'Attribute "{attr}" not found in', fcontext)
        return None, None, None, None
    else:
        if colorset is None:
            colorset = 'standard'
        try:
            colorset = colorset.strip()
            colors = colorsets[colorset]
        except KeyError:
            colorset = f'standard ({colorset} non defini dans le context.pic)'
            colors = colorsets['standard']
        t2c = 0 if attr in alphanum_attr else 1
        colors = list(map(_to_hex, map(_to_RGB, colors)))[0:len(thresholds) + t2c]
    if verbose:
        print(f'Using attribute "{attr}" from', fcontext)
    return attr, colorset, thresholds, colors

#****f* functions/get_python_exe
# SYNTAX
#   name = get_python_exe()
# RESULT
#   str name: path/name to the python executable in use, possibly without extension
# HISTORY
#   2.0.7 (190821) created
#****
def get_python_exe() -> str:
    '''Returns the python.exe full path'''
    if sys.executable is not None:
        return sys.executable
    pyroot = sys.prefix
    if pyroot == getattr('sys', 'base_prefix', pyroot):
        return OP.join(pyroot, 'python')
    return OP.join(pyroot, 'Scripts', 'python')

#****f* functions/update_package
# SYNTAX
#   stat = update_package(package_name [, minvers=''] [, pypi_name=None]
#   [, deps= False] [, https_proxy= None] [, verbose= True])
# ARGUMENT
#   * string package_name: name of the package as used in the import statement
#   * optional string minvers: minimum version required, in the form x.y[.z]
#   * optional string pypi_name: package name in pypi, if different from package_name
#   * optional bool deps: set to True to install the dependencies
#   * optional string https_proxy: url and port of the proxy if required.
# RESULT
#   bool stat: true if the package has been installed or updated
# REMARKS
#   * minvers can also be provided as a list or tuple of ints
#   * proxy lookup starts with HTTPS_PROXY environment variable, then
#     configuration files lookup using get_proxy() function.
# HISTORY
#   * 1.8.1 (171009) added
#   * 1.8.7 (171208) revised to allow ganessa to update itself
#   * 1.8.8 (171212) proxy config .json files lookup added
#   * 1.9.1 (180502) python3
#   * 1.9.2 (180518) use tempfile for testing access (MT compatibility)
#   * 2.0.0 (180818) added verbose parameter
#   * 2.0.5 (190109) remove testing access
#   * 2.0.7 (190821) modified python exe lookup for venv compatibility
#   * 2.0.9 (200205) minor fix in version_as_tuple: remove 4th level (post)
#   * 2.1.5 (210929) exit in embed mode if version inappopriate
#   * 2.2.9 (220214) replace -only-binary with -prefer-binary; add --trusted-host pypi.org

#****
def update_package(package_name, minvers='', pypi_name=None, deps=False,
                   https_proxy=None, verbose=True) -> bool:
    '''Update package using pip if too old - returns True if updated'''
    from importlib import import_module
    try:
        pkg = import_module(package_name)
    except ImportError:
        vers = ''
    else:
        try:
            vers = pkg.__version__
        except AttributeError:
            try:
                vers = pkg.__VERSION__
            except AttributeError:
                try:
                    vers = pkg.version
                except AttributeError:
                    try:
                        vers = pkg.VERSION
                    except AttributeError:
                        vers = '0.0'
        if is_text(vers):
            vers = tostr(vers)
        del pkg
    if pypi_name is None:
        pypi_name = package_name
    # do no try to modify package from embedded call
    try:
        from ganessa_emb_ import full_path
    except ImportError:
        pass
    else:
        del full_path
        reason = 'is missing'
        if vers:
            if not minvers:
                # installed
                return False
            if version_as_tuple(vers) >= version_as_tuple(minvers):
                # installed and >= minvers
                return False
            reason = 'version < ' + str(minvers)
        msg = f'Exiting because package "{pypi_name}" {reason}.'
        sys.exit(msg)

    # Do nothing if already installed or match version
    cmd = [get_python_exe(), '-m', 'pip', 'install']
    # add --user if python root folder not writeable
    user_fold_warn = ''
    # wok = os.access(pyroot, os.W_OK)
    try:
        tmp = OP.join(sys.prefix, 'Lib/site-packages', 'tmpcheck.tmp')
        with open(tmp, 'w') as ftest:
            ftest.write('Folder available for writing!')
    except:     # PermissionError
        cmd.append('--user')
        user_fold_warn = 'Not allowed to write into root folder: installing in user folder'
    else:
        os.remove(tmp)
    cmd += ['--timeout', '2', '--retries', '2']
    cmd += ['--trusted-host', 'pypi.org', '--prefer-binary']
    cmd += ['--find-links', '.']
    # This proprietary build of pyproj is now useless
    # wheel_fold = '//2015329srv/storage$/Logiciels/python'
    # if OP.exists(wheel_fold):
    #     cmd += ['--find-links', wheel_fold]
    if not deps:
        cmd.append('--no-deps')
    if vers:
        if not minvers:
            if verbose:
                print(package_name, vers, 'is already installed')
            return False
        if version_as_tuple(vers) < version_as_tuple(minvers):
            print(package_name, vers, 'is being updated')
        else:
            if verbose:
                print(package_name, vers, 'is already installed and >= ', minvers)
            return False
        cmd.append('--upgrade')
    else:
        print(package_name, 'is being installed')
    cmd.append(pypi_name)
    if user_fold_warn and verbose:
        print(user_fold_warn)

    proxy_ev = 'HTTPS_PROXY' if PY3 else b'HTTPS_PROXY'
    envir = dict(os.environ)
    if https_proxy is None:
        if proxy_ev in envir:
            if verbose:
                print('  Using current proxy settings')
        else:
            # try proxy file if environment variable not set
            https_proxy = get_proxy(OP.dirname(get_caller(False)))
    if https_proxy:
        envir[proxy_ev] = str(https_proxy)
        if verbose:
            print('  Using proxy:', https_proxy)
    else:
        if proxy_ev in envir:
            del envir[proxy_ev]
        if verbose:
            print('  Connection without proxy')
    if verbose:
        print('  running pip')
    if package_name == 'ganessa':
        subprocess.Popen(cmd, env=envir)
        sys.exit()
    else:
        subprocess.call(cmd, env=envir)
    return True

#****f* functions/get_proxy
# SYNTAX
#   proxy = get_proxy([folder=None] [, default=''])
# ARGUMENTS
#   * optional string folder: folder to search for proxy .json file
#   * optional string default: default value for proxy
# RESULT
#   string proxy: value of the proxy, False if not found
# REMARKS
#   The .json configuration files are searched for either a "proxy" key
#   or the first element of the first list. Files names are:
#   'https_proxy', 'Mise_a_jour_packages', 'proxy'.
# HISTORY
#   1.8.8 (171212) created get_proxy
#   2.1.0 (200214) fix urllib3 requiring proxy scheme (http[s]://)
#   2.1.5 (210927) fix kwarg name default in doc; fix return value
#****
def get_caller(direct: bool = True) -> str:
    '''Utility function for getting caller'''
    import inspect
    frame = inspect.stack()[1 if direct else 2]
    try:
        fname = frame[1]
    finally:
        del frame
    return fname

def get_proxy(folder: str = None, default: str = '') -> str:
    '''Lookup for a proxy file configuration'''
    # get the caller folder if not provider
    if folder is None:
        folder = OP.dirname(get_caller(False))
    # file lookup
    for name in ('https_proxy', 'proxys', 'proxy', 'Mise_a_jour_packages'):
        pname = OP.join(folder, name + '.json')
        if OP.exists(pname):
            with copen(pname, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except:
                    continue
                else:
                    try:
                        proxys = data['proxy']
                    except (TypeError, KeyError):
                        try:
                            proxys = data[0]
                        except:
                            continue
            if proxys and not proxys.lower().startswith('http'):
                proxys = 'http://' + proxys
            return proxys
    return default

def is_same_file_by_handle(f1, f2):
    'Memo for comparing files by handles'
    s1 = os.fstat(f1.fileno())
    s2 = os.fstat(f2.fileno())
    return s1.st_ino == s2.st_ino and s1.st_dev == s2.st_dev

_smallest_img_b64 = 'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
_logo_SUEZ_b64 = '''
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
'''

def logo_SUEZ_b64() -> str:
    'Returns Suez logo as b64 image'
    return _logo_SUEZ_b64
    