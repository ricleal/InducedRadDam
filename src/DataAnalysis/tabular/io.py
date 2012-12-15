"""
Functions for :class:`tabular.tab.tabarray` i/o methods, including to/from 
separated-value (CSV, e.g. ``.tsv``, ``.csv``) and other text files, binary 
files, hierarchical separated-value (HSV) format.

"""

import types
import csv
import cPickle
import os
import shutil
import compiler
import re

import numpy as np
from numpy import int64

import tabular as tb
import tabular.utils as utils
from tabular.utils import uniqify, listunion

__all__ = ['loadSV', 'loadSVcols','loadSVrecs', 'saveSV', 'loadbinary',       
           'savebinary',  'loadHSV', 'saveHSV', 'savecolumns', 'loadHSVlist', 
           'appendHSV', 'appendcolumns', 'typeinfer', 'inferdelimiterfromname', 
           'inferdialect', 'processmetadata', 'inferheader',
           'readstoredmetadata']

DEFAULT_VERBOSITY=5

def loadSV(fname, names=None, dtype=None, shape=None, formats=None,    
           titles=None, aligned=False, byteorder=None,  **kwargs):

    """
    Load a delimited text file to a numpy record array.

    Takes a delimited text file and returns data as a NumPy record array. 
    Basically, calls loadSVcols and combines columns into a record array.
    Also metadata including column names, formats, coloring, &c. if these items 
    are determined during the loading process.

    **Parameters**

            **fname** :  string or file object

                    Path (or file object) corresponding to a separated variable
                    (CSV) text file.
                  
           **names** :  list of strings, or `None`

                    List of column names given in the header of the file
                    (optional).


           **formats** :  list of strings, or `None`

                    List of strings corresponding to type of each column,
                    parsed from the header of the file (if provided).  These
                    may either by strings in `['int', 'str', 'float']` or 
                    describe numpy types, e.g. `'<i4', '<f8', '|S5'`.

    **NumPy Parameters**
    
        The following parametes mimic parameters of the numpy record array construction interface.
			
		    **dtype**
		    
            **shape**
      
            **titles**
          
            **aligned**
            
            **byteorder**

    **kwargs**: keyword argument dictionary of variable length

        Contains various parameters used in loadSVcols.
            
                           
 
    **Returns**

            **R** :  numpy record array

                    record array constructed from data in the SV file

            **metadata** :  dictionary

                    Metadata read and constructed during process of reading 
                    file.


    **See Also:**

            :func:`tabular.io.loadSV`, :func:`tabular.io.saveSV`, 
            :func:`tabular.io.typeinfer`

    """

    [Columns, metadata]  = loadSVcols(fname, **kwargs)

    if names is None and 'names' in metadata.keys():
	      names = metadata['names']

    return [utils.fromarrays(Columns, type = np.ndarray, dtype=dtype, 
    shape=shape, formats = formats, names=names, titles=titles, 
    aligned=aligned, byteorder=byteorder), metadata]

def loadSVcols(fname, usecols=None,valuefixer=None, **kwargs):


    """
    Load a separated value text file to a list of column arrays.

    Takes a tabular text file with a specified delimeter and end-of-line 
    character, and return data as a Python list of either numpy arrays 
    corresponding to columns, each a uniform Python type (int, float, str).
    Also metadata including column names, formats, coloring, &c. if these items 
    are determined during the loading process.

    **Parameters**

            **fname** :  string or file object

                    Path (or file object) corresponding to a separated variable
                    (CSV) text file.
                    
            **usecols** :  list of integers or column names, optional

                    If `usecols` is not `None`, only the columns it lists are
                    loaded, with 0 being the first column.

            **valuefixer** :  lambda function, optional

                    Lambda function to apply to every value in the SV.
                    
            **verbosity** :  integer, optional

                   Sets how much detail from messages will be printed.
             
            **kwargs**: keyword argument dictionary of variable length
             
                    Contains various parameters used in loadSVrecs
            
                           
 
    **Returns**

            **columns** :  list of numpy arrays

                    List of arrays corresponding to columns of data.

            **metadata** :  dictionary

                    Metadata read and constructed during process of reading 
                    file.


    **See Also:**

            :func:`tabular.io.loadSV`, :func:`tabular.io.saveSV`, 
            :func:`tabular.io.typeinfer`

    """

    [records, metadata] = loadSVrecs(fname, **kwargs)
    
    Lens = np.array([len(r) for r in records])
    assert (Lens == Lens[0]).all() , 'Not all records have same number of fields.'

    l0 = Lens[0]
    if not usecols is None:
        getcols = [i if i >= 0 else l0 + i for i in usecols if isinstance(i,int)]
        if 'names' in metadata.keys():
            names = metadata['names']
            getcols += [names.index(c) for c in usecols if c in names]
            if 'coloring' in metadata.keys():
            	coloring = metadata['coloring']
            	for c in usecols:
            		if c in coloring.keys():
            			getcols += [names.index(n) for n in coloring[c]]
        getcols = uniqify(getcols)
        getcols.sort()
        metadatacolthreshold(metadata,getcols)
    else:
        if 'names' in metadata.keys():
            names = metadata['names']
            getcols = range(len(names))
        else:
            getcols = range(l0)
    
    if valuefixer is None:
        if 'formats' in metadata.keys():
            formats = metadata['formats']
            columns = [np.array([rec[j] for rec in records], f) for (j,f) in 
                              zip(getcols,formats)]
        else:
            columns = [typeinfer([rec[j] for rec in records]) for j in getcols]
    else:
        if 'formats' in metadata.keys():
            formats = metadata['formats']
            columns = [np.array([valuefixer(rec[j]) for rec in records], f) 
                              for (j,f) in zip(getcols,formats)]
        else:
            columns = [typeinfer([valuefixer(rec[j]) for rec in records]) for j
                             in getcols]

    return [columns, metadata]


def loadSVrecs(fname, lineterminator = '\n', skiprows=0, linefixer=None,
                          namesinheader=True, verbosity = DEFAULT_VERBOSITY, 
                           **metadata):


    """
    Load a separated value text file to a list of lists of strings of records.

    Takes a tabular text file with a specified delimeter and end-of-line 
    character, and return data as a Python list of 
    Python lists corresponding to records (rows). 
    Also metadata including column names, formats, coloring, &c. if these items 
    are determined during the loading process.

    **Parameters**

            **fname** :  string or file object

                    Path (or file object) corresponding to a separated variable
                    (CSV) text file.

            **lineterminator** :  string, optional

                    The string separating lines of text, e.g. '\\n'.  By 
                    default, this is assumed to be '\\n'. Note that the file is 
                    opened using the "read universal" option::

                            file(fname, 'rU')

            **skiprows** :  non-negative integer, optional

                    The first `skiprows` lines are ignored.

            **namesinheader**:  Boolean, optional

                    If `namesinheader == True` and `metadatadict == None`, then 
                    assume metadatadict = {'names': headerlines-1}, e.g. the 
                    column names are in the last header line.

            **linefixer** :  lambda function, optional

                    Lambda function to apply to every line in the SV.
                    
            **verbosity** :  integer, optional

                   Sets how much detail from messages will be printed.
             
            **metadata**: keyword argument dictionary of variable length
             
                    Contains various parameters for meatadata settings.  These 
                    may include:
            
            **comments** :  string, optional

                    The string denoting the start of a comment, e.g. '#'.  Note
                    that if not supplied and the first line of the input file 
                    begins with a '#', then it is assumed to be '#'.  Lines at 
                    the top of the file beginning with `comments` are assumed 
                    to be the header of the file where metadata can be found 
                    (e.g. column names).

            **delimiter** :  string, optional

                    The string that separates values in each line of text, e.g.
                    '\\t'.  By default, this is inferred from the file 
                    extension:

                    *	if the file ends in `.tsv`, the delimiter is '\\t'

                    *	if the file ends in `.csv`, the delimiter is ','

                    If the delimiter cannot be inferred and is not given, it is
                    assumed to be '\\t'.  Note that this is different from the
                    default for `numpy.loadtxt <http://docs.scipy.org/doc/numpy/reference/generated/numpy.loadtxt.html>`_, which is any whitespace.

                    **See Also:**  :func:`tabular.io.inferdelimiter`
    
            **metametadata**:  dictionary, optional

                    Dictionary mapping one or more special keys in
                    `['names', 'formats', 'types', 'coloring']` each to a line
                    number corresponding to a row in the header (Python style, 
                    starting with 0 rather than 1).  The line number is equal 
                    to the actual line number in the file (starting at 0) minus 
                    `skiprows`.  Negative line numbers allowed, and are counted 
                    from the end of the header.

                    If `None`, look for a string representation of 
                    `metadatadict` in the header, this is a line beginning with 
                    "metadatadict=".  The default settings of 
                    :func:`tabular.io.saveSV` result in writing out this line
                    in the first line of the header.


            **headerlines** :  integer, optional

                    The number of lines at the top of the file (after the first 
                    `skiprows` lines) corresponding to the header of the file 
                    where metadata can be found (e.g. column names).   Lines 
                    after this are the "actual data" lines.



    **CSV Parameters**
    
        The following parameters replicate parameters of Python CSV module interface.  ("delimiter" does as well.)

            **dialect**
             
            **quotechar**
            
            **quoting**
            
            **escapechar**
            
            **doublequote**
            
            **skipinitialspace**

                      
                   
 
    **Returns**

            **records** :  list of lists of strings

                    List of lists corresponding to records (rows) of data.

            **metadata** :  dictionary

                    Metadata read and constructed during process of reading 
                    file.


    **See Also:**

            :func:`tabular.io.loadSV`, :func:`tabular.io.saveSV`, 
            :func:`tabular.io.typeinfer`

    """
   
    if is_string_like(fname):
        fh = file(fname, 'rU')
    elif hasattr(fname, 'readline'):
        fh = fname
    else:
        raise ValueError('fname must be a string or file handle')

    F = fh.read().strip(lineterminator).split(lineterminator)[skiprows:]
    fh.close()

    if linefixer:
        F = map( linefixer, F )
        
    metadata = dict([(k,v) for (k,v) in metadata.items() if v is not None]) 

    if 'comments' not in metadata.keys():
        metadata['comments'] = '#'
        if verbosity > 7:
            print 'Assuming comment character is "#"'
        
    if 'metametadata' in metadata.keys():
        mmd = metadata['metametadata']
    else:
        mmd = None
		
    storedmetadata = readstoredmetadata( data=F, comments=metadata['comments'], metametadata=mmd, verbosity=verbosity)

    if storedmetadata:
        if verbosity > 7:
            print '\n\nStored metadata read from file:', storedmetadata, '\n\n' 
        for name in storedmetadata:
            if name in metadata.keys() and storedmetadata[name] and storedmetadata[name] != metadata[name]:
            	if verbosity >= 4:
                    print "WARNING:  A value for ", name , "was found in metadata read from special-format header in file", fname , "as well as being provided explicitly, and read value differs from provided value.  Using provided value."
            else:
                metadata[name] = storedmetadata[name]
                       
    if 'headerlines' not in metadata.keys():
        metadata['headerlines'] = inferheader(F,metadata=metadata)
        if verbosity >=6:
            print 'Inferring "headerlines" to equal', metadata['headerlines'], '...'
        
    if namesinheader:
        if metadata['headerlines'] == 0:
            metadata['headerlines'] = 1
            if verbosity >= 6:
        	    print '... assuming "headerlines" = 1, since "namesinheader"=True.'

    infdia = inferdialect(fname,F[metadata['headerlines']:],lineterminator)

    if 'dialect' not in metadata.keys():
        if 'delimiter' not in metadata.keys():
            metadata['dialect'] = infdia
            if 8 > verbosity > 2:
                print 'Inferring delimiter to be ' + repr(metadata['dialect'].delimiter)
            elif verbosity >= 8:
        	    print 'Inferring dialect with values:', printdialect(metadata['dialect'])
        else:
            metadata['dialect'] = csv.Sniffer().sniff(metadata['delimiter'])

    processmetadata(metadata,items='dialect',verbosity=verbosity)

    if infdia.delimiter != metadata['dialect'].delimiter:
        if verbosity >= 5:
            if storedmetadata and 'delimiter' in storedmetadata.keys() and infdia.delimiter == storedmetadata['delimiter']:
                print 'Inferred delimiter differs from given delimiter but equals delimiter read from metadata in file.  Are you sure you haven\'t made a mistake?'
            else:
                print 'Inferred delimiter differs from given delimiter.'

    if 'names' not in metadata.keys() and namesinheader and not storedmetadata:
        assert metadata['headerlines'] > 0, 'Trying to set names useing last header line since namesinheader is True, but "headerlines" = 0 indicating no headerline present at all.'
        metadata['names'] = F[metadata['headerlines']-1]
        if verbosity > 1:
            print 'Inferring names from the last header line (line', metadata['headerlines'], ').'

    processmetadata(metadata,items='names,formats',verbosity=verbosity)
     
    return [list(csv.reader(F[metadata['headerlines']:],
                      dialect=metadata['dialect'])),metadata]


def saveSV(fname, X, comments=None, metadata=None, printmetadict=None,
                   dialect = None, delimiter=None, doublequote=True, 
                   lineterminator='\n', escapechar = None, 
                   quoting=csv.QUOTE_MINIMAL, 
                   quotechar='"', skipinitialspace=False, 
                   verbosity=DEFAULT_VERBOSITY):

    """
    Save a tabarray to a separated-variable (CSV) file.

    **Parameters**

            **fname** :  string

                    Path to a separated variable (CSV) text file.

            **X** :  tabarray

                    The actual data in a :class:`tabular.tab.tabarray`.

            **comments** :  string, optional

                    The string denoting the start of a comment, e.g. '#':

                    *	If `metadata` is not specified, the default is ''.

                    *	If  `metadata` is specified, the default is '#'.

            **delimiter** :  string, optional

                    The string that separates values in each line of text, e.g.
                    '\\t'.  By default, this is inferred from the file 
                    extension:

                    *	If the file ends in `.tsv`, the delimiter is '\\t'

                    *	If the file ends in `.csv`, the delimiter is ','

                    If the delimiter cannot be inferred and is not given, it is
                    assumed to be '\\t'.  Note that this is different from the
                    default for :func:`numpy.loadtxt`, which is any whitespace.

            **linebreak** :  string, optional

                    The string separating lines of text, e.g. '\\n'.  By 
                    default, this is assumed to be '\\n'.

            **metadata** :  list of strings or Boolean, optional

                    Allowed header keys are strings in 
                    `['names', 'formats', 'types', 'coloring']`. These keys 
                    indicate what special metadata is printed in the header.

                    *	If `metadata` is not specified, then defaults to 
                    	`['names']`.

                    *	If `True`, this is the same as 
                    	`metadata = ['coloring', 'types', 'names']`.

                    *	If `None`, no metadata is printed, e.g. just the data.

            **printmetadict** :  Boolean, optional

                    Whether or not to print a string representation of the
                    `metadatadict` in the first line of the header.

                    If `printmetadict` is not specified, then:

                    *	If `metadata` is specified and is not `False`, then
                    	`printmetadata` defaults to `True`.

                    *	Else if `metadata` is `False`, then `printmetadata`
                    	defaults to `False`.

                    *	Else `metadata` is not specified, and `printmetadata`
                    	defaults to `False`.

                    See the :func:`tabular.io.loadSV` for more information
                    about `metadatadict`.

    **See Also:**

            :func:`tabular.io.loadSV`

    """
    
    if metadata is None:
        metakeys = ['names']
        if printmetadict is None:
            printmetadict = False
        if comments is None:
            comments = ''
        if verbosity > 7:
            print 'Defaulting to writing out names metadata, with no metametadata dictionary written and empty comments string.'
    elif metadata is True:
        metakeys = ['dialect','coloring', 'types', 'names']
        if printmetadict is None:
            printmetadict = True
        if comments is None:
            comments = ''
        if verbosity >= 5:
            print 'Writing out', metakeys,' metadata, with a corresponding metametadata dictionary, and empty comments string.'
    elif metadata is False:
        metakeys = []
        printmetadict = False
        comments = ''
        if verbosity >= 5:
            print 'Writing out no metadata at all.'
    else:
        metakeys = metadata
        if printmetadict is None:
            if metakeys == []:
                printmetadict = False
            else:
                printmetadict = True
        if comments is None:
            comments = ''
        if verbosity >= 5:
            if len(metakeys) > 0:
                print 'Writing out metadata for ', metakeys
            else:
                print 'Writing out no metadata.'
            

    dialect = getdialect(fname,dialect, delimiter, lineterminator, doublequote, 
                               escapechar, quoting, quotechar, skipinitialspace)
    delimiter = dialect.delimiter     
    
    if 6 > verbosity > 2:
    	print 'Using delimiter ', repr(delimiter)
    elif verbosity >= 6:
        print 'Using dialect with values:', repr(printdialect(dialect))
        
    metadata = getstringmetadata(X,metakeys,dialect)

    metametadata = {}
    v = 1
    for k in metakeys:
        if k in metadata.keys():
            nl = len(metadata[k].split(lineterminator))
            metametadata[k] = v if nl == 1 else (v,v + nl)
            v = v + nl

    F = open(fname,'wb')

    if printmetadict is True:
        line = "metametadata=" + repr(metametadata)
        F.write(comments + line + lineterminator)

    for k in metakeys:
        if k in metadata.keys():
            for line in metadata[k].split(lineterminator):
                F.write(comments + line + lineterminator)

    typevec = []
    ColStr = []
    UseComplex = False
    for name in X.dtype.names:
        typevec.append(X.dtype[name].name.strip('0123456789').rstrip('ing'))
        D = X[name]
        if D.ndim > 1:
            D = D.flatten()
        if typevec[-1] == 'str':
            if sum([delimiter in d for d in D]) > 0:
                print("WARNING: An entry in the '" + name +
                      "' column contains at least one instance of the "
                      "delimiter '" + delimiter + "' and therefore will use "
                      "the Python csv module quoting convention (see online " 
                      "documentation for Python's csv module).  You may want "
                      "to choose another delimiter not appearing in records, " 
                      "for performance reasons.")
                UseComplex = True
                break
            else:
                ColStr.append(D)
        else:
            ColStr.append(str(D.tolist()).strip('[]').split(', '))


    if UseComplex is True:
        csv.writer(F, dialect=dialect).writerows(X)
    else:
        F.write(lineterminator.join([delimiter.join([col[i] for col in ColStr]) 
                                               for i in range(len(ColStr[0]))]))
    F.close()


def printdialect(d):
    return dict([(a,getattr(d,a)) for a in dir(d) if not a.startswith('_')])

def metadatacolthreshold(metadata,getcols):
    getcols = getcols[:]
    getcols.sort()
    if 'names' in metadata.keys():
        n = metadata['names'][:]
        metadata['names'] = [n[i] for i in getcols]
        if 'coloring' in metadata.keys():
            coloring = metadata['coloring']
            metadata['coloring'] = thresholdcoloring(coloring, metadata['names'])
    if 'formats' in metadata.keys():
        f = metadata['formats'][:]
        metadata['formats'] = [f[i] for i in getcols]


def inferdialect(fname = None, datalines = None,lineterminator='\n'):
    """
    Attempts to convert infer dialect from csv file lines. 
    
    Essentially a small extension of the "sniff" function from 
    Python CSV module.   csv.Sniffer().sniff attempts to infer 
    the delimiter from a putative delimited text file by analyzing 
    character frequencies.   This function adds additional analysis 
    in which guesses are checked again the number of entries in
    each line that would result from spliiting relative to that guess. 
    If no plausable guess if found, delimiter is inferred from file 
    name  ('csv' yields ',', everything else yields '\t'.)
    
    **Parameters** 
    
        **fname** : pathstring
        
            name of file
        
        **datalines** : list of strings
        
            list of lines in the data file
            
        **lineterminator** : single-character string
        
           lineterminator to join split/join line strings 
        
    **Returns**
    
        csv.Dialect obejct
        
    
    """
    
    if datalines is None:
        if is_string_like(fname):
            fh = file(fname, 'rU')
        elif hasattr(fname, 'readline'):
            fh = fname
        else:
            raise ValueError('fname must be a string or file handle')

        F = fh.read().strip(lineterminator).split(lineterminator)
        fh.close() 
        
    if not is_string_like(fname):
        fname = None

    tries = [10,30,60,100,200,400,800]

    if len(datalines) > 100:
        starts = [int(len(datalines)/5) * i for i in range(5)]
    else:
        starts = [0,int(len(datalines)/2)]
        
    G = []
    for s in starts:
        for t in [tt for (i,tt) in enumerate(tries) if i == 0 or s + tries[i-1] <= len(datalines)]:
            try:
                g = csv.Sniffer().sniff(lineterminator.join(datalines[s:s+t]))
                G += [g]
            except:
                pass
            else:
                break
                
    delims = [g.delimiter for g in G]       
    G = [g for (i,g) in enumerate(G) if g.delimiter not in delims[:i]]
    V = []
    for g in G:
        lvec = np.array([len(r) for r in
                                        csv.reader(datalines[:1000],dialect=g)])
        V += [lvec.var()]

    if len(G) > 0:
        V = np.array(V)
        return G[V.argmin()]
    else:
        if verbosity > 2:
            print 'dialect inference failed, infering dialect to be', inferdelimiterfromname(fname) , 'from filename extension.'
        return csv.Sniffer().sniff(inferdelimiterfromname(fname))



def readstoredmetadata(data=None, fname=None, lineterminator = '\n',
                                         linenumber=None, comments = '#', 
                                         metametadata=None, 
                                         verbosity=DEFAULT_VERBOSITY):

    """
    Read metadata from a delimited text file.
    
    """

    if data is None:
        if is_string_like(fname):
            fh = file(fname, 'rU')
        elif hasattr(fname, 'readline'):
            fh = fname
        else:
            raise ValueError('fname must be a string or file handle')

        data = fh.read().split(lineterminator)
        
    if not metametadata:
        if linenumber is None:
            if comments:
     	        n = 0
     	        for i in range(len(data)):
     	            if not data[i].startswith(comments):
     	                break
     	        if i == 0:
     	            i = 1
     	            if verbosity >= 10:
     	                print 'Looking for metametadata on line 0 (no comment lines present).'
     	        else:
     	            if verbosity >= 9:
     	                print 'Searching for metametadata lines up to line', i, ', where comments end.'
     	        crange = range(i)
            else:
                crange = [0]
                if verbosity >=9:
                    print 'Looking for metametadata on line 0.'
        else:
            crange = [linenumber]

        metametadata = None
        for ln in crange:
            metametaline = data[ln] 
            s = re.compile(r'metametadata[\s]*=[\s]*{').search(metametaline)
            if s:
                l = s.start()
                if len(uniqify(metametaline[:l])) <= 1:
                    metametaline = metametaline[l:].rstrip()
                    try:
                        X = compiler.parse(metametaline)
                    except SyntaxError:
                        pass
                    else:
                        if IsMetaMetaDict(X):
                            exec metametaline
                            if verbosity > 6:
                                print 'Found valid metametadata at line', ln, 'in file.  Metametadata is:', metametadata
                            break
                            
    if metametadata:
        
        metadata = {}
        metadata['metametadata'] = metametadata
 
        if max([v if isinstance(v,int) else max(v) for v in  metametadata.values()]) < len(data):
            for n in metametadata.keys():
                [s,e] = [metametadata[n],metametadata[n]+1] if isinstance(metametadata[n],int) else [metametadata[n][0],metametadata[n][1]]
                metadata[n] = lineterminator.join(data[s:e])
            processmetadata(metadata,comments = comments,verbosity=verbosity)
        
            return metadata


def processmetadata(metadata,items = None, comments=None, 
                                    verbosity=DEFAULT_VERBOSITY):

    """
    Process Metadata from stored (or "packed") state to functional state.

    Metadata can come be read from a file "packed" in various ways, 
    e.g. with a string representation of a dialect or coloring dictionary.  
    This function "unpacks" the stored metadata into useable Python
    objects.  It consists of a list of quasi-modular parts, one for each 
    type of recognized metadata.

    **Parameters**

        **metadata** : dictionary

             This argument is a dictionary whose keys are strings denoting
             different kinds of metadata (e.g. "names" or "formats") and 
             whose values are the metadata of that type.
             The metadata dictionary is modified IN-PLACE by this function.

        **items** : string or list of strings, optional

            The items arguments specifies which metadata keys are to be 
            processed.  E.g. of items = 'names,formats', then the "names" 
            metadata and "formats" metadata will be processed, but no 
            others  Note however, that sometimes, the processing of one 
            type of metadata requires that another be processed first, e.g. 
            "dialect" must processed into an actual CSV.dialect object 
            before "names"  is processed.   (The processed of "names" 
            metadata involves splitting the names metadat string into a 
            list, using the delmiter.  This delimiter is part of the dialect 
            object.)   In these cases, if you call processmetadata on one 
            item before its requirements are processed, nothing will happen.

        **comments** : single-character string, optional

            The comments character is used to process many pieces of 
            metadata, e.g. it is striped of the left side of names and formats strings
            before splitting on delimiter.

        **verbosity** : integer, optional

            Determines the level of verbosity in the printout of messages
            during the running of the procedure. 


   **Returns**
   
       Nothing

    """


    items = items.split(',') if isinstance(items,str) else items

    if comments is None:
        if 'comments' in metadata.keys():
            comments = metadata['comments']
        else:
            comments = '#'
            if verbosity > 8:
                print 'processing metadata with comments char = #'
    else:
        if 'comments' in metadata.keys() and comments != metadata['comments'] and verbosity > 8:
            print 'comments character specified to process metadata (', repr(comments) ,') is different from comments charcater set in metadata dictionary (', repr(metadata['comments']) , ').'

    if not items or 'dialect' in items:
        if 'dialect' in metadata.keys():
            if isinstance(metadata['dialect'],str):
                D = dialectfromstring(metadata['dialect'].lstrip(comments))
                if D:
                    metadata['dialect'] = D
                    if verbosity > 8:
                        print 'processed dialect from string'
                else:
                    if verbosity > 8:
                        print 'dialect failed to be converted properly from string representation in metadata.'

            if 'delimiter' in dir(metadata['dialect']):
                for a in dir(metadata['dialect']):
                    if not a.startswith('_') and a in metadata.keys():
                        setattr(metadata['dialect'],a, metadata[a])
                        if (verbosity > 2 and a == 'delimiter') or verbosity >= 8:
                            print 'Setting dialect attribute', a ,'to equal specified valued:', metadata[a]


    if (not items or 'names' in items) and 'names' in metadata.keys(): 
        if is_string_like(metadata['names']) and 'dialect' in metadata.keys():      
            if 'delimiter' in dir(metadata['dialect']):
                d=metadata['dialect']
                n=metadata['names']
                metadata['names'] = list(csv.reader([n.lstrip(comments)],      
                               dialect=d))[0]
                if verbosity > 8:
                    print '... splitting "names" metadata from string with delimiter', repr(d.delimiter), '. Resulting names:', metadata['names']

    if (not items or 'formats' in items) and 'formats' in metadata.keys(): 
        if is_string_like(metadata['formats']) and 'dialect' in metadata.keys():      
           if 'delimiter' in dir(metadata['dialect']):
                d=metadata['dialect']
                n=metadata['formats']
                metadata['formats'] = list(csv.reader([n.lstrip(comments)],  
        	                    dialect=d))[0]
                if verbosity > 8:
                    print '... splitting "formats" metadata from string with delimiter', repr(d.delimiter), '. Resulting names:', metadata['formats']        	                  

    if (not items or 'coloring' in items) and 'coloring' in metadata.keys():
        if is_string_like(metadata['coloring']):
            C = coloringfromstring(metadata['coloring'].lstrip(comments))
            if C:
                metadata['coloring'] = C
                if verbosity > 8:  
                    print '... processed coloring from string'
            else:
                if verbosity > 8:
                    print 'coloring failed to be converted properly from string representation in metadata.'

    if (not items or 'headerlines' in items):
        if 'headerlines' in metadata.keys():
            if isinstance(metadata['headerlines'],str):
                try:
                    h = metadata['headerlines']
                    metadata['headerlines'] = int(h.lstrip(comments))
                except (ValueError,TypeError):
                    if verbosity > 6:
                        print 'headerlines metadata failed to convert to an integer.'
                else:
                    pass
                        

            if isinstance(metadata['headerlines'],int):
                if 'metametadata' in metadata.keys():
                    h= metadata['headerlines']
                    mmd = metadata['metametadata']
                    metadata['headerlines'] = max(h,1+max([v if isinstance(v,int) else 
                           max(v) for v in mmd.values()]))
                    if metadata['headerlines'] > h and verbosity > 8:
                        print 'Resetting headerlines from', h, 'to', metadata['headerlines'], 'because of line number indications from metametadata.'


def inferheader(lines,comments=None,metadata=None):

    """
    Infers header from a CSV or other tab-delimited file.
    
    This is essentially small extension of the csv.Sniffer.has_header algorithm.
    provided in the Python csv module.   First, it checks to see whether a 
    metametadata dictionary is present, specifiying the lines numbers of 
    metadata lines in the header, and if so, sets the header lines to include
    at least those lines.  Then iookms to see if a comments character is 
    present, and if so, includes those lines as well.  If either of the above 
    returns a nono-zero number of headerlines, the function returns that 
    number; otherwise, it uses the csv.Sniffer module, checking each line 
    in succession, and stopping at the first line where the sniffer module 
    finds no evidence of a header, and returning that line numner.
    
    **Parameters** 
    
        **lines** : line of strings 
        
            The list of lines representing lines in the file
            
        **comments** : single-character string, optional
        
            Comments character  specification. 
            
        **metadata** : metadata dictionary, optional
        
            used to deterine a comments character and metametadata dicationary, if present, 

    **Returns**
    
        Integer, representing the number of (inferred) header lines at the top of the file
    
    """
	
    if comments is None and metadata and 'comments' in metadata.keys():
        comments = metadata['comments']
    if comments is None:
        comments = '#'	
	
    if 'metametadata' in metadata.keys():
        mmd = metadata['metametadata']
        cc =  1+max([v if isinstance(v,int) else max(v) for v in mmd.values()])
    else:
        cc = 0

    if comments != '':
        for l in xrange(cc,len(lines)):
            if not lines[l].startswith(comments):
                break
          
    if l > 0:
        return l
    else:
        for j in xrange(len(lines)):
            hasheader = 'unset'
            for k in [100,200,400,800,1600]:
                F = '\n'.join(lines[j:j+k])
                try:
                    hasheader = csv.Sniffer().has_header(F)
                except:
                    pass
                else:
                    break
            if not hasheader:
                return j



from compiler.ast import Stmt,Tuple,Assign,AssName,Dict,Const,List,Discard,Name

isctype = lambda x,t : (isinstance(x,Const) and isinstance(x.value,t)) or (t == types.BooleanType and isinstance(x,Name) and x.name in ['False','True']) or (t == types.NoneType and isinstance(x,Name) and x.name == 'None')

def IsMetaMetaDict(AST):

    """
    Checks whether a given AST (abstract syntax tree) 
    object represents a metametadata dictionary.   
    
    """

    isintpair = lambda x : isinstance(x,Tuple) and len(x.asList()) == 2 and isctype(x.asList()[0],int) and isctype(x.asList()[1],int)
    try:
        if len(AST.getChildren()) > 1 and isinstance(AST.getChildren()[1],Stmt):
            if isinstance(AST.getChildren()[1].getChildren()[0],Assign):
                [s,d] = AST.getChildren()[1].getChildren()[0].asList()
    except (TypeError,AttributeError):
        return False
    else:
        if isinstance(s,AssName) and s.name == 'metametadata':     
            if isinstance(d,Dict):
                return all([isctype(k,str) and (isctype(v,int) or isintpair(v)) 
                                                         for (k,v) in d.items])

def dialectfromstring(s):
    """
    Attempts to convert a string representation of a CSV 
    dialect (as would be read from a file header, for instance) 
    into an actual csv.Dialect object.   
    
    """

    try:
        AST = compiler.parse(s)
    except SyntaxError:
        return
    else:
        try:
            if len(AST.getChildren()) > 1:
                ST = AST.getChildren()[1]
                if isinstance(ST,Stmt):
                    if isinstance(ST.getChildren()[0],Discard):
                        d = ST.getChildren()[0].asList()[0]
        except (TypeError,AttributeError):
            pass
        else:
            if isinstance(d,Dict) and len(d.items) > 0:
                if all([isctype(i[0],str) for i in d.items]):
                    testd = csv.Sniffer().sniff('a,b,c')
                    if all([n.value in dir(testd) and 
                        isctype(v,type(getattr(testd,n.value))) for (n,v) in 
                                                          d.items]):
                        D = eval(s)
                        for n in D.keys():
                            setattr(testd,n,D[n])
                        return testd


def coloringfromstring(s):
    """
    Attempts to convert a string representation of a coloring
    dictionary (as would be read from a file header, for instance) 
    into an actual coloring dictionary.
    
    """
    try:
        AST = compiler.parse(s)
    except SyntaxError:
        return
    else:
        try:
            if len(AST.getChildren()) > 1:
                ST = AST.getChildren()[1]
                if isinstance(ST,Stmt) and isinstance(ST.getChildren()[0],
                                                                     Discard):
                    d = ST.getChildren()[0].asList()[0]
        except (TypeError,AttributeError):
            pass
        else:
            if isinstance(d,Dict) and len(d.items) > 0:
                if all([isctype(i[0],str) for i in d.items]):
            	    if all([isinstance(i[1],List) for i in d.items]):
            	        if all([all([isctype(j,str) for j in i[1]]) for i in 
            	                                                      d.items]):
            	            return eval(s)


def getdialect(fname,dialect, delimiter, lineterminator, doublequote, escapechar, 
                        quoting, quotechar, skipinitialspace):
                        
                       
    if dialect is None:
        if delimiter is None:
            dialect = csv.Sniffer().sniff(inferdelimiterfromname(fname))
        else:
            dialect = csv.Sniffer().sniff(delimiter)
           
    dialect.lineterminator = lineterminator
    if doublequote is not None:
        dialect.doublequote = doublequote
    if escapechar is not None:
        dialect.escapechar = escapechar
    if quoting is not None:
        dialect.quoting = quoting
    if quotechar is not None:
        dialect.quotechar = quotechar
    if skipinitialspace is not None:
        dialect.skipinitialspace = skipinitialspace

    return dialect


def getstringmetadata(X,metakeys,dialect):

    metadata = {}
    delimiter = dialect.delimiter

    dialist = ['delimiter', 'lineterminator', 'doublequote', 'escapechar', 
                                      'quoting', 'quotechar','skipinitialspace']

    if 'names' in metakeys:
        metadata['names'] = delimiter.join(X.dtype.names)
    if 'coloring' in metakeys and X.coloring != {}:
        metadata['coloring'] = repr(X.coloring)
    if 'types' in metakeys:
        metadata['types'] = delimiter.join(parsetypes(X.dtype))
    if 'formats' in metakeys:
        metadata['formats'] = delimiter.join(parseformats(X.dtype))
    if 'dialect' in metakeys:
        diakeys = dialist
    else:
        diakeys = list(set(dialist).intersection(set(metakeys)))
    if len(diakeys) > 0:
        metadata['dialect'] = repr(dict([(a,getattr(dialect,a)) 
                                                             for a in diakeys]))

    return metadata


def loadbinary(fname):
    """
    Load a numpy binary file or archive created by tabular.io.savebinary.
    
    Load a numpy binary file (``.npy``) or archive (``.npz``) created by 
    :func:`tabular.io.savebinary`.

    The data and associated data type (e.g. `dtype`, including if given, column 
    names) are loaded and reconstituted.

    If `fname` is a numpy archive, it may contain additional data giving 
    hierarchical column-oriented structure (e.g. `coloring`).  See 
    :func:`tabular.tab.tabarray.__new__` for more information about  
    coloring.

    The ``.npz`` file is a zipped archive created using :func:`numpy.savez` and 
    containing one or more ``.npy`` files, which are NumPy binary files created 
    by :func:`numpy.save`.

    **Parameters**

            **fname** :  string or file-like object

                    File name or open numpy binary file (``.npy``) or archive 
                    (``.npz``) created by :func:`tabular.io.savebinary`.

                    *	When `fname` is a ``.npy`` binary file, it is 
                    	reconstituted as a flat ndarray of data, with 
                    	structured dtype.

                    *	When `fname` is a ``.npz`` archive, it contains at 
                    	least one ``.npy`` binary file and optionally another:

                            *	``data.npy`` must be in the archive, and is
                            	reconstituted as `X`, a flat ndarray of data, 
                            	with structured dtype, `dtype`.

                            *	``coloring.npy``, if present is reconstitued as
                            	`coloring`, a dictionary.

    **Returns**

            **X** :  numpy ndarray with structured dtype

                    The data, where each column is named and is of a uniform 
                    NumPy data type.

            **dtype** :  numpy dtype object

                    The data type of `X`, e.g. `X.dtype`.

            **coloring** :  dictionary, or None

                    Hierarchical structure on the columns given in the header 
                    of the file; an attribute of tabarrays.

                    See :func:`tabular.tab.tabarray.__new__` for more
                    information about coloring.

    **See Also:**

            :func:`tabular.io.savebinary`, :func:`numpy.load`, 
            :func:`numpy.save`, :func:`numpy.savez`

    """

    X = np.load(fname)
    if isinstance(X, np.lib.io.NpzFile):
        if 'coloring' in X.files:
            coloring = X['coloring'].tolist()
        else:
            coloring = None
        if 'data' in X.files:
            return [X['data'], X['data'].dtype, coloring]
        else:
            return [None, None, coloring]
    else:
        return [X, X.dtype, None]

def savebinary(fname, X, savecoloring=True):
    """
    Save a tabarray to a numpy binary file or archive.
    
    Save a tabarray to a numpy binary file (``.npy``) or archive
    (``.npz``) that can be loaded by :func:`tabular.io.savebinary`.

    The ``.npz`` file is a zipped archive created using
    :func:`numpy.savez` and containing one or more ``.npy`` files,
    which are NumPy binary files created by :func:`numpy.save`.

    **Parameters**

            **fname** :  string or file-like object

                    File name or open numpy binary file (``.npy``) or archive 
                    (``.npz``) created by :func:`tabular.io.savebinary`.

            **X** :  tabarray

                    The actual data in a :class:`tabular.tab.tabarray`:

                    *	if `fname` is a ``.npy`` file, then this is the same 
                    	as::

                                    numpy.savez(fname, data=X)

                    *	otherwise, if `fname` is a ``.npz`` file, then `X` is 	
                    	zipped inside of `fname` as ``data.npy``

            **savecoloring** : boolean

                    Whether or not to save the `coloring` attribute of `X`.
                    If `savecoloring` is `True`, then `fname` must be a
                    ``.npz`` archive and `X.coloring` is zipped inside of
                    `fname` as ``coloring.npy``

                    See :func:`tabular.tab.tabarray.__new__` for more
                    information about coloring.

    **See Also:**

            :func:`tabular.io.loadbinary`, :func:`numpy.load`, :func:`numpy.save`, :func:`numpy.savez`

    """

    if fname[-4:] == '.npy':
        np.save(fname, X)
    else:
        if savecoloring is True:
            np.savez(fname, data=X, coloring=X.coloring)
        else:
            np.savez(fname, data=X)

def loadHSV(path, X=None, names=None, rootpath=None, rootheader=None, 
                                        coloring=None, toload=None, Nrecs=None):
    """
    Load a list of columns (numpy arrays) from a HSV directory. 
    
    Load a list of numpy arrays, corresponding to columns of data, from a 
    hierarchical separated variable (HSV) directory (``.hsv``) created by 
    :func:`tabular.io.saveHSV`.

    This function is used by the tabarray constructor
    :func:`tabular.tab.tabarray.__new__` when passed the `HSV` argument.

    Each column of data inside of the ``.hsv`` directory is a separate 
    comma-separated variable text file (``.csv``), whose name includes the 
    column name and data type of the column (e.g. ``name.int.csv``, 
    ``name.float.csv``, ``name.str.csv``).  An ordered list of columns, if 
    provided, is stored in a separate file, ``header.txt``.

    A ``.hsv`` directory can contain ``.hsv`` subdirectories.  This allows for 
    hierarchical structure on the columns, which is mapped to a coloring 
    dictionary. For example, a subdirectory named ``color.hsv`` contains 
    ``.csv`` files corrseponding to columns of data grouped by that color.  
    Note that when the file structure is not flat, :func:`tabular.io.loadHSV` 
    calls itself recursively.

    **Parameters**

            **path** :  string

                    Path to a ``.hsv`` directory or individual ``.csv`` text 
                    files, corresponding to individual columns of data inside 
                    of a ``.hsv`` directory.

            **X** :  list of numpy arrays, optional

                    List of numpy arrays, corresponding to columns of data.  
                    Typically, the `X` argument is only passed when
                    :func:`tabular.io.loadHSV` calls itself recursively, in 
                    which case each element is a column of data that has 
                    already been loaded.

            **names** :  list of strings, optional

                    List of strings giving column names. Typically, the `names` 
                    is only passed when :func:`tabular.io.loadHSV` calls itself 
                    recursively, in which case each element gives the name of 
                    the corresponding array in `X`.

            **rootpath** :  string, optional

                    Path to the top-level file (directory), i.e. the value of
                    `path` the first time :func:`tabular.io.loadHSV` is called.
                    Typically, the `rootpath` argument is only passed when
                    :func:`tabular.io.loadHSV` calls itself recursively.

            **rootheader** :  list of strings, optional

                    Ordered list of column names. Typically, the `rootheader`
                    argument is only passed when :func:`tabular.io.loadHSV`
                    calls itself recursively, in which case `rootheader` is
                    filled by parsing the (optional) ``header.txt`` file in
                    `rootpath`, if it exists.

            **coloring** :  dictionary, optional

                    Hierarchical structure on the columns given in the header
                    of the file; an attribute of tabarrays.

                    Typically, the `coloring` argument is only passed when
                    :func:`tabular.io.loadHSV` calls itself recursively, in 
                    which case it contains coloring, i.e. hierarchical 
                    structure information, on the arrays in `X`.

                    See :func:`tabular.tab.tabarray.__new__` for more
                    information about coloring.

                    **See Also:** :func:`tabular.io.infercoloring`

            **toload** :  list of strings, optional

                    List of strings corresponding to a subset of column names
                    and/or color names; only these columns are loaded.

                    **See Also:**  :func:`tabular.io.thresholdcoloring`

            **Nrecs** :  non-negative integer

                    The number of records in `X`. Typically, the `Nrecs` 
                    argument is only passed when :func:`tabular.io.loadHSV`
                    calls itself recursively, in which case it is set by the 
                    first ``.csv`` file loaded.  Subsequent columns must have 
                    the same number of records; when any subsequent column
                    disagrees, it is not loaded and a warning is issued.

    **Returns**

            **X** :  list of numpy arrays

                    List of numpy arrays, corresponding to columns of data, 
                    each loaded from one ``.csv`` file.

            **names** :  list of strings

                    List of strings giving column names.

            **coloring** :  dictionary

                    Hierarchical structure on the columns given in the header 
                    of the file; an attribute of tabarrays.

                    See :func:`tabular.tab.tabarray.__new__` for more
                    information about coloring.

    **See Also:**

            :func:`tabular.tab.tabarray.__new__`, 
            :func:`tabular.io.saveHSV`

    """

    if os.path.isdir(path):
        path = backslash(path)
    if X is None:
        X = []
    if names is None:
        names = []
    if rootpath is None:
        rootpath = path
    if rootheader is None:
        # If it exists, use the header.txt files to order attributes
        # (this is not required)
        rootheader = []
        if os.path.isdir(path):
            if 'header.txt' in os.listdir(path):
                rootheader =  open(path + 'header.txt', 
                                   'r').read().strip('\n').split('\n')
            else:
                H = [h for h in os.listdir(path) if h.endswith('header.txt')]
                if len(H)>0:
                    rootheader =  open(path + H[0], 
                                       'r').read().strip('\n').split('\n')

    if os.path.isdir(path):
        L = [l for l in os.listdir(path) 
             if l.endswith('.hsv') or l.endswith('.csv')]
        keys = path[len(rootpath):].split('.hsv/')[:-1]
    else:
        L = [path]
        keys = []

    CSVList = []

    for l in L:
        parsed_filename = l.split('.')
        name = '.'.join(parsed_filename[:-2]).split('/')[-1]
        if parsed_filename[-1] == 'csv' and (toload is None or name in toload):
            CSVList += [name]
            if name not in names:
                col = open(path + l if l != path else path, 
                           'r').read().split('\n')
                if Nrecs is None:
                    Nrecs = len(col)
                if len(col) == Nrecs:
                    try:
                        type_data = eval(parsed_filename[-2])
                        col = np.array([type_data(c) for c in col], 
                                       parsed_filename[-2])
                        if len(rootheader) > 0 and name in rootheader:
                            indvec = [names.index(j) for j in 
                                      rootheader[:rootheader.index(name)] 
                                      if j in names]
                            insert_ind = max(indvec) + 1 \
                                         if len(indvec) > 0 else 0
                            X.insert(insert_ind, col)
                            names.insert(insert_ind, name)
                        else:
                            X += [col]
                            names += [name]
                    except:
                        print ("Warning: the data in the .csv file", 
                               path + l if l != path else path, 
                               "does not match the given data type,", 
                               parsed_filename[-2], ", and was not loaded.")
                else:
                    print("Warning: the column", path, 
                          (l if l != path else path), "has", str(len(col)), 
                          "records, which does not agree with the number of " 
                          "records in first column loaded, '" + names[0] + 
                          "', which has", str(Nrecs), "records -- only the " 
                          "first column, as well as all the other columns "
                          "which also have ", str(Nrecs), " records, will be " "loaded.")
        elif parsed_filename[-1] == 'hsv' and os.path.isdir(path):
            colorname = '.'.join(parsed_filename[:-1]).split('/')[-1]
            if toload is None or not colorname in toload:
                [X, names, coloring] = \
                    loadHSV(path + l, X=X, names=names,         
                            rootpath=rootpath, rootheader=rootheader, 
                            coloring=coloring, toload=toload, Nrecs=Nrecs)
            elif colorname in toload:
                [X, names, coloring] = \
                    loadHSV(path + l, X=X, names=names, rootpath=rootpath, 
                            rootheader=rootheader, coloring=coloring, 
                            toload=None, Nrecs=Nrecs)

    if (path == rootpath) & path.endswith('.hsv/'):
        coloring = infercoloring(path)
        if not toload is None:
            coloring = thresholdcoloring(coloring, names)

    return [X, names, coloring]

def saveHSV(fname, X, printheaderfile=True):
    """
    Save a tabarray to a hierarchical separated variable (HSV) directory.  
    
    The tabarray can later be loaded back from the ``.hsv`` by passing `fname` 
    to the `HSV` argument of the tabarray constructor 
    :func:`tabular.tab.tabarray.__new__`.

    This function is used by the tabarray method
    :func:`tabular.tab.tabarray.saveHSV`.

    Each column of data in the tabarray is stored inside of the ``.hsv`` 
    directory to a separate comma-separated variable text file (``.csv``), 
    whose name includes the column name and data type of the column (e.g. 
    ``name.int.csv``, ``name.float.csv``, ``name.str.csv``).

    Coloring information, i.e.  hierarchical structure on the columns, is 
    stored in the file directory structure of the ``.hsv``, where ``.hsv`` 
    subdirectories correspond to colors in the coloring dictionary::

            X.coloring.keys()

    e.g. a subdirectory named ``color.hsv`` contains ``.csv`` files
    corrseponding to columns of data grouped by that color::

            X['color']

    See :func:`tabular.tab.tabarray.__new__` for more information about 
    coloring.

    Note that when the file structure is not flat,
    :func:`tabular.io.loadHSV` calls itself recursively.

    **Parameters**

            **fname** :  string

                    Path to a ``.hsv`` directory or individual ``.csv`` text 
                    files, corresponding to individual columns of data inside 
                    of a ``.hsv`` directory.

            **X** :  tabarray

                    The actual data in a :class:`tabular.tab.tabarray`.

            **printheaderfile** : boolean, optional

                    Whether or not to print an ordered list of columns names in 
                    an additional file ``header.txt`` in all ``.hsv`` 
                    directories. The order is given by::

                            X.dtype.names

                    The ``header.txt`` file is used by 
                    :func:`tabular.io.loadHSV` to load the columns of data in 
                    the proper order, but is not required.

    **See Also:**

            :func:`tabular.tab.tabarray.__new__`, :func:`tabular.io.loadHSV`, :func:`tabular.io.savecolumns`

    """

    fname = backslash(fname)
    makedir(fname)

    keys = X.coloring.keys()
    pairwise = [[set(X.coloring[key1]) > set(X.coloring[key2]) for key1 in 
                 keys] for key2 in keys]
    names = list(X.dtype.names)

    for i in range(len(keys)):
        if sum(pairwise[i]) == 0:
            saveHSV(fname + keys[i] + '.hsv/', X[keys[i]], printheaderfile)
            names = [n for n in names if n not in X[keys[i]].dtype.names]

    savecolumns(fname, X[names])

    if (printheaderfile is True) and (X.dtype.names > 1):
        G = open(fname + 'header.txt', 'w')
        G.write('\n'.join(X.dtype.names))
        G.close()


def savecolumns(fname, X):
    """
    Save columns of a tabarray to an existing HSV directory.

    Save columns of tabarray `X` to an existing HSV directory `fname` (e.g. a 
    ``.hsv`` directory created by :func:`tabular.io.saveHSV`).

    Each column of data in the tabarray is stored inside of the ``.hsv`` 
    directory to a separate comma-separated variable text file (``.csv``), 
    whose name includes the column name and data type of the column (e.g. 
    ``name.int.csv``, ``name.float.csv``, ``name.str.csv``).

    Coloring is lost.

    This function is used by the tabarray method
    :func:`tabular.tab.tabarray.savecolumns`.

    **Parameters**

            **fname** :  string

                    Path to a hierarchical separated variable (HSV) directory
                    (``.hsv``).

            **X** :  tabarray

                    The actual data in a :class:`tabular.tab.tabarray`.

    **See Also:**

            :func:`tabular.io.saveHSV`, :func:`tabular.io.loadHSVlist`

    """

    fname = backslash(fname)
    names = X.dtype.names
    for name in names:
        typestr = X.dtype[name].name.strip('0123456789').rstrip('ing')
        F = open(fname + name + '.' + typestr + '.csv', 'w')
        D = X[name]
        if D.ndim > 1:
            D = D.flatten()
        if typestr == 'str':
            F.write('\n'.join(D))
        else:
            F.write(str(D.tolist()).strip('[]').replace(', ','\n'))
        F.close()

def loadHSVlist(flist):
    """
    Load tabarrays from a list of hierarchical separated variable directories.
    
    Loads tabarrays from a list of  hierarchical separated variable (HSV) 
    paths, assuming they have disjoint columns and identical numbers of rows;  
    then stacks them horizontally, e.g. adding columns side-by-side, aligning 
    the rows.

    Colorings can be lost.

    **Parameters**

            **flist** :  list of strings

                    List of paths to hierarchical separated variable (HSV)
                    directories (``.hsv``) and/or individual ``.csv`` text 
                    files, corresponding to individual columns of data inside 
                    of a ``.hsv`` directory.

    **See Also:**

            :func:`tabular.io.loadHSV`, :func:`tabular.io.savecolumns`

    """

    X = tb.tabarray(HSVfile = flist[0])
    for fname in flist[1:]:
        Y = tb.tabarray(HSVfile = fname)
        X = X.colstack(Y)
    return X

def appendHSV(fname, RecObj, order=None):
    """
    Append records to an on-disk tabarray, e.g. HSV directory.
    
    Function for appending records to an on-disk tabarray, used when one wants 
    to write a large tabarray that is not going to be kept in memory at once.

    If the tabarray is not there already, the function intializes the tabarray 
    using the tabarray `__new__` method, and saves it out.

    **Parameters**

            **fname** :  string

                    Path of hierarchical separated variable (``.hsv``) file to
                    which to append records in `RecObj`.

            **RecObj** :  array or dictionary

            *	Either an array with complex dtype (e.g. tabarray, recarray or 
            	ndarray), or

            *	a dictionary (ndarray with structured dtype, e.g. a tabarray) 
            	where

                    *	keys are names of columns to append to, and
                    *	the value on a column is a list of values to be 
                    	appended to that column.

            **order** :  list of strings

                    List of column names specifying order in which the columns 
                    should be written; only used when the HSV does not exist 
                    and the header specifying order needs to be written.

    **See Also:**

            :func:`tabular.io.appendcolumns`

    """

    if hasattr(RecObj, 'dtype'):
        names = RecObj.dtype.names
    elif hasattr(RecObj, 'keys'):
        names = RecObj.keys()

    if order is None:
        order = names

    if hasattr(RecObj, 'coloring'):
        keys = RecObj.coloring.keys()
        pairwise = [[set(RecObj.coloring[key1]) > set(RecObj.coloring[key2]) for key1 in keys] for key2 in keys]
        names = list(RecObj.dtype.names)
        for i in range(len(keys)):
            if sum(pairwise[i]) == 0:
                appendHSV(fname + keys[i] + '.hsv/', RecObj[keys[i]], order)
                names = [n for n in names if n not in RecObj[keys[i]].dtype.names]

    appendcolumns(fname, RecObj[names])


def appendcolumns(fname, RecObj, order=None):
    """
    Append records to a flat on-disk tabarray, e.g. HSV without subdirectories.
    
    Function for appending columnns a flat on-disk tabarray, (e.g. no colors), 
    used when one wants to write a large tabarray that is not going to be kept 
    in memory at once.

    If the tabarray is not there already, the function intializes the tabarray 
    using the tabarray __new__ method, and saves it out.

    See :func:`tabular.io.appendHSV` for a more general method.

    **Parameters**

            **fname** :  string

                    Path of hierarchical separated variable (.hsv) file of 
                    which to append.

            **RecObj** :  array or dictionary

            *	Either an array with complex dtype (e.g. tabarray, recarray or 
            	ndarray), or

            *	a dictionary (ndarray with structured dtype, e.g. a tabarray) 
            	where

                    *	keys are names of columns to append to, and
                    *	the value on a column is a list of values to be 
                    	appended to that column.

            **order** :  list of strings

                    List of column names specifying order in which the columns 
                    should be written; only used when the HSV does not exist 
                    and the header specifying order needs to be written.

    **See Also:**

            :func:`tabular.io.appendHSV`

    """

    if hasattr(RecObj, 'dtype'):
        names = RecObj.dtype.names
    elif hasattr(RecObj, 'keys'):
        names = RecObj.keys()

    if order is None:
        order = names

    Cols = [RecObj[o] for o in order]
    assert all([len(Cols[0]) == len(a) for a in Cols]), \
           ("In ", funcname(), ":  There are differing numbers of elements in " 
            "the columns, no records appended.")

    if not os.path.exists(fname):
        assert set(names) == set(order), \
               "The names and the order argument conflict."
        tb.tabarray(columns = Cols, names = order).save(fname)
    elif len(Cols[0]) > 0:
        headerfilename = [l for l in os.listdir(fname) if 
                          l.endswith('header.txt')][0]
        header = open(fname + headerfilename,'r').read().split('\n')
        if set(header) != set(names):
            print("Warning:  The header file and names conflict; either some " 
                  "names don't exist in the header or some headers don't "
                  "exist in the column names of the input tabular data" 
                  "structure.  Proceeding anyways.\n")
            print("Names in header (", fname + headerfilename, "): ", header, 
                  "\n")
            print("Names in RecObj: ", names)
                  
        for h in header:
            name = [fname + l for l in os.listdir(fname) if l.startswith(h) and 
                    l.endswith('.csv')]
            if len(name) > 0:
                name = name[0]
                dtype = name.split('.')[-2]
                if dtype == 'str':
                    F = open(name,'a')
                    F.write('\n' + '\n'.join(RecObj[h]))
                    F.close()
                else:
                    F = open(name,'a')
                    F.write('\n' + str(np.array(RecObj[h]).tolist()) \
                                               .strip('[]').replace(', ','\n'))
                    F.close()
    else: 
        pass

def is_string_like(obj):
    """
    Check whether input object behaves like a string.

    From:  _is_string_like in numpy.lib._iotools

    **Parameters**

        **obj** :  string or file object

                Input object to check.

    **Returns**

        **out** :  bool

                Whether or not `obj` behaves like a string.

    """
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True

def typeinfer(column):
    """
    Infer the data type (int, float, str) of a list of strings.

    Take a list of strings, and attempts to infer a numeric data type that fits 
    them all.

    If the strings are all integers, returns a NumPy array of integers.

    If the strings are all floats, returns a NumPy array of floats.

    Otherwise, returns a NumPy array of the original list of strings.

    Used to determine the datatype of a column read from a separated-variable 
    (CSV) text file (e.g. ``.tsv``, ``.csv``) of data where columns are 
    expected to be of uniform Python type.

    This function is used by tabular load functions for SV files, e.g. by 
    :func`tabular.io.loadSV` when type information is not provided in the 
    header, and by :func:`tabular.io.loadSVsafe`.

    **Parameters**

            **column** :  list of strings

                    List of strings corresponding to a column of data.

    **Returns**

            **out** :  numpy array

                    Numpy array of data from `column`, with data type
                    int, float or str.

    """
    try:
        return np.array([int(x) for x in column], 'int')
    except:
        try:
            return np.array([float(x) if x != '' else np.nan for x in column], 
                            'float')
        except:
            return np.array(column, 'str')

def infercoloring(path, rootpath = None, coloring = None):
    """
    Infer the coloring from the file structure of a HSV directory.

    Infer the coloring of a tabarray saved as a hierarchical separated variable 
    ('.hsv') directory by looking at file directory substructure.  Note that 
    when the file structure is not flat, :func:`tabular.io.infercoloring` calls 
    itself recursively.

    Used by loadHSV() because when 'toload' is not None, the complete coloring 
    must be known to threshold it properly.

    **Parameters**

            **path** :  string

                    Path to a ``.hsv`` directory or individual ``.csv`` text 
                    files, corresponding to individual columns of data inside 
                    of a ``.hsv`` directory.

            **rootpath** :  string, optional

                    Path to the top-level file (directory), i.e. the value of
                    `path` the first time :func:`tabular.io.loadHSV` is called.
                    Typically, the `rootpath` argument is only passed when
                    :func:`tabular.io.infercoloring` calls itself recursively.

            **coloring** :  dictionary, optional

                    Hierarchical structure on the columns.  See below.

    **Returns**

            **coloring** :  dictionary

                    Hierarchical structure on the columns given in the header
                    of the file; an attribute of tabarrays.

                    Typically, the `coloring` argument is only passed when
                    :func:`tabular.io.loadHSV` calls itself recursively, in 
                    which case it contains coloring, i.e. hierarchical 
                    structure information, on the arrays in `X`.

                    See :func:`tabular.tab.tabarray.__new__` for more
                    information about coloring.

    **See Also:**

            :func:`tabular.io.loadHSV`

    """
    path = backslash(path)
    if rootpath is None:
        rootpath = path
    if coloring is None:
        coloring = {}
    L = [l for l in os.listdir(path) if l.endswith('.hsv') or 
         l.endswith('.csv')]

    tabarray = [L[i] for i in xrange(len(L)) if L[i].split('.')[-1] == 'hsv']
    for dd in tabarray:
        coloring = infercoloring(path+dd, rootpath, coloring)

    if path !=      rootpath:
        DotCSV = [L[i] for i in xrange(len(L)) if L[i].split('.')[-1] == 'csv']
        names = [DotCSV[i].split('.')[:-2][0] for i in xrange(len(DotCSV))]
        keysfrompath = path[len(rootpath):].strip('.hsv/').split('.hsv/')
        for key in keysfrompath:
            if key in coloring.keys():
                coloring[key] = utils.uniqify(coloring[key] + names)
            else:
                coloring[key] = names

    return coloring

def inferdelimiterfromname(fname):
    """
    Infer delimiter from file extension.

    *       If *fname* ends with '.tsv', return '\\t'.

    *       If *fname* ends with '.csv', return ','.

    *       Otherwise, return '\\t'.

    **Parameters**

            **fname** :  string

                    File path assumed to be for a separated-variable file.

    **Returns**

            **delimiter** :  string

                    String in ['\\t', ','], the inferred delimiter.

    """
    
    if not is_string_like(fname):
        return '\t'
        
    if fname.endswith('.tsv'):
        return '\t'
    elif fname.endswith('.csv'):
        return ','
    else:
        return '\t'


def parseformats(dtype):
    """
    Parse the formats from a structured numpy dtype object.

    Return list of string representations of numpy formats from a structured 
    numpy dtype object.

    Used by :func:`tabular.io.saveSV` to write out format information in the 
    header.

    **Parameters**

            **dtype** :  numpy dtype object

                    Structured numpy dtype object to parse.

    **Returns**

            **out** :  list of strings

                    List of strings corresponding to numpy formats::

                            [dtype[i].descr[0][1] for i in range(len(dtype))]

    """
    return [dtype[i].descr[0][1] for i in range(len(dtype))]

def parsetypes(dtype):
    """
    Parse the types from a structured numpy dtype object.

    Return list of string representations of types from a structured numpy 
    dtype object, e.g. ['int', 'float', 'str'].

    Used by :func:`tabular.io.saveSV` to write out type information in the header.

    **Parameters**

            **dtype** :  numpy dtype object

                    Structured numpy dtype object to parse.

    **Returns**

            **out** :  list of strings

                    List of strings corresponding to numpy types::

                            [dtype[i].name.strip('1234567890').rstrip('ing') \ 
                             for i in range(len(dtype))]

    """
    return [dtype[i].name.strip('1234567890').rstrip('ing') 
            for i in range(len(dtype))]

def thresholdcoloring(coloring, names):
    """
    Threshold a coloring dictionary for a given list of column names.

    Threshold `coloring` based on `names`, a list of strings in::

            coloring.values()

    **Parameters**

            **coloring** :  dictionary

                    Hierarchical structure on the columns given in the header 
                    of the file; an attribute of tabarrays.

                    See :func:`tabular.tab.tabarray.__new__` for more
                    information about coloring.

            **names** :  list of strings

                    List of strings giving column names.

    **Returns**

            **newcoloring** :  dictionary

                    The thresholded coloring dictionary.

    """
    for key in coloring.keys():
        if len([k for k in coloring[key] if k in names]) == 0:
            coloring.pop(key)
        elif set(coloring[key]) == set(names):
            coloring.pop(key)
        else:
            coloring[key] = utils.uniqify([k for k in coloring[key] if k in 
                                           names])
    return coloring

def backslash(dir):
    '''
    Add '/' to the end of a path if not already the last character.

    Adds '/' to end of a path (meant to make formatting of directory path `dir` 
    consistently have the slash).

    **Parameters**

            **dir** :  string

                    Path to a directory.

    **Returns**

            **out** :  string

                    Same as `dir`, with '/' appended to the end if not already 
                    there.

    '''
    if dir[-1] != '/':
        return dir + '/'
    else:
        return dir

def delete(ToDelete):
    '''
    Unified "strong" version of delete (remove) for files and directories.

    Unified "strong" version of delete that uses `os.remove` for a file and 
    `shutil.rmtree` for a directory tree.

    **Parameters**

            **ToDelete** :  string

                    Path to a file or directory.

    **See Also:**

            `os <http://docs.python.org/library/os.html>`_, 
            `shutil <http://docs.python.org/library/shutil.html>`_

    '''
    if os.path.isfile(ToDelete):
        os.remove(ToDelete)
    elif os.path.isdir(ToDelete):
        shutil.rmtree(ToDelete)

def makedir(DirName):
    '''
     "Strong" directory maker.

    "Strong" version of `os.mkdir`.  If `DirName` already exists, this deletes 
    it first.

    **Parameters**

            **DirName** :  string

                    Path to a file directory that may or may not already exist.

    **See Also:**

            :func:`tabular.io.delete`, 
            `os <http://docs.python.org/library/os.html>`_

    '''
    if os.path.exists(DirName):
        delete(DirName)
    os.mkdir(DirName)
