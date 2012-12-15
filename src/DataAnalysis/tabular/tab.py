'''
Class and functions pertaining to the tabular.tabarray class.

The :class:`tabarray` class is a column-oriented hierarchical data object and 
subclass of `numpy.ndarray <http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html?highlight=ndarray#numpy.ndarray>`_.

The basic structure of this module is that it contains:

*	The tabarray class.

*	Some helper functions for tabarray.  The helper functions are precisely 
	those necessary to wrap functions from the :mod:`tabular.spreadsheet` 
	module that operate on lists of arrays, to handle tabular's additional 
	structure.  These functions are named with the convention "tab_FNAME", e.g. 
	"tab_rowstack", "tab_join" &c.  The functions in :mod:`tabular.spreadsheet` 
	that only take a single array are all wrapped JUST as methods of tabarray, 
	and not as separate functions.

'''

import os
import csv

import numpy as np

import tabular.io as io
import tabular.spreadsheet as spreadsheet
import tabular.utils as utils

__all__ = ['tabarray', 'tab_colstack', 'tab_rowstack','tab_join']

DEFAULT_VERBOSITY=io.DEFAULT_VERBOSITY

def modifydocs(a, b, desc=''):
    """
    Convenience function for writing documentation.

    For a class method `a` that is essentially a wrapper for an outside 
    function `b`, rope in the docstring from `b` and append to that of `a`.  
    Also modify the docstring of `a` to get the indentation right.
    
    Will probably deprecate this soon.

    **Parameters**

            **a** :  class method

                    Class method wrapping `b`.

            **b** :  function

                    Function wrapped by `a`.

            **desc** :  string, optional

                    Description of `b`, e.g. restructured text providing a link
                    to the documentation for `b`.  Default is an empty string.

    **Returns**

            **newdoc** :  string

                    New docstring for `a`.

    """
    newdoc = a.func_doc.replace('\t\t', '\t')
    newdoc += "Documentation from " + desc + ":\n" + b.func_doc
    return newdoc

def tab_colstack(ListOfTabArrays, mode='abort'):
    '''
    "Horizontal stacking" of tabarrays, e.g. adding columns.

    Wrapper for :func:`tabular.spreadsheet.colstack` that deals with the 
    coloring and returns the result as a tabarray.

    Method calls::

            data = tabular.spreadsheet.colstack(ListOfTabArrays, mode=mode)

    '''

    data = spreadsheet.colstack(ListOfTabArrays, mode=mode)

    coloring = {}
    for a in ListOfTabArrays:
        for k in a.coloring:
            if k in coloring.keys():
                coloring[k] = utils.uniqify(coloring[k] + a.coloring[k])
            else:
                coloring[k] = a.coloring[k]

    for k in coloring.keys():
        s = [x for x in coloring[k] if x in data.dtype.names]
        if len(s) > 0:
            coloring[k] = s
        else:
            coloring.pop(k)

    data = data.view(tabarray)
    data.coloring = coloring
    return data
tab_colstack.func_doc = modifydocs(tab_colstack, spreadsheet.colstack, 
                                   ":func:`tabular.spreadsheet.colstack`")

def tab_rowstack(ListOfTabArrays, mode='nulls'):
    '''
    "Vertical stacking" of tabarrays, e.g. adding rows.

    Wrapper for :func:`tabular.spreadsheet.rowstack` that deals with the 
    coloring and returns the result as a tabarray.

    Method calls::

            data = tabular.spreadsheet.rowstack(ListOfTabArrays, mode=mode)

    '''

    data = spreadsheet.rowstack(ListOfTabArrays, mode=mode)

    coloring = {}
    for a in ListOfTabArrays:
        for k in a.coloring:
            if k in coloring.keys():
                coloring[k] = utils.uniqify(coloring[k] + a.coloring[k])
            else:
                coloring[k] = a.coloring[k]
    for k in coloring.keys():
        s = [x for x in coloring[k] if x in data.dtype.names]
        if len(s) > 0:
            coloring[k] = s
        else:
            coloring.pop(k)

    data = data.view(tabarray)
    data.coloring = coloring
    return data
tab_rowstack.func_doc = modifydocs(tab_rowstack, spreadsheet.rowstack, 
                                   ":func:`tabular.spreadsheet.rowstack`")

def tab_join(ToMerge, keycols=None, nullvals=None, renamer=None, 
             returnrenaming=False, Names=None):
    '''
    Database-join for tabular arrays.

    Wrapper for :func:`tabular.spreadsheet.join` that deals with the coloring 
    and returns the result as a tabarray.

    Method calls::

            data = tabular.spreadsheet.join

    '''

    [Result,Renaming] = spreadsheet.join(ToMerge, keycols=keycols, 
          nullvals=nullvals, renamer=renamer, returnrenaming=True, Names=Names)

    if isinstance(ToMerge,dict):
        Names = ToMerge.keys()
    else:
        Names = range(len(ToMerge))

    Colorings = dict([(k,ToMerge[k].coloring) if 'coloring' in dir(ToMerge[k])  
                                              else {} for k in Names])
    for k in Names:
        if k in Renaming.keys():
            l = ToMerge[k]
            Colorings[k] = \
                dict([(g, [n if not n in Renaming[k].keys() else Renaming[k][n] 
                       for n in l.coloring[g]]) for g in Colorings[k].keys()])
    Coloring = {}
    for k in Colorings.keys():
        for j in Colorings[k].keys():
            if j in Coloring.keys():
                Coloring[j] = utils.uniqify(Coloring[j] + Colorings[k][j])
            else:
                Coloring[j] = utils.uniqify(Colorings[k][j])

    Result = Result.view(tabarray)
    Result.coloring = Coloring

    if returnrenaming:
        return [Result,Renaming]
    else:
        return Result


class tabarray(np.ndarray):
    """
    Subclass of the numpy ndarray with extra structure and functionality.

    tabarray is a column-oriented data object based on the numpy ndarray with
    structured dtype, with added functionality and ability to define named 
    groups of columns.

    tabarray supports several i/o methods to/from a number of file formats, 
    including (separated variable) text (e.g. ``.txt``, ``.tsv``, ``.csv``), 
    numpy binary (``.npz``) and hierarchical separated variable (``.hsv``).

    Added functionality includes spreadsheet style operations such as "pivot", 
    "aggregate" and "replace".

    **Invariants**

            The names of all columns are distinct (unique) within one
            :mod:`tabarray`.

    """

    def __new__(subtype, array=None, records=None, columns=None, SVfile=None, 
                binary=None, HSVfile=None, HSVlist=None, shape=None, 
                dtype=None, formats=None, names=None, titles=None, 
                aligned=False, byteorder=None, buf=None, offset = 0,
                strides = None, comments=None, delimiter=None, 
                lineterminator='\n', escapechar=None, quoting=csv.QUOTE_MINIMAL, 
                quotechar='"', doublequote=True, skipinitialspace=False,
                skiprows=0, usecols=None, toload=None, metametadata=None, 
                namesinheader=True, headerlines=None, valuefixer=None, 
                linefixer=None, coloring=None, wrap=None, 
                verbosity=DEFAULT_VERBOSITY):
        """
        Unified constructor for tabarrays.

        **Specifying the data**

                Data can be passed to the constructor, or loaded from several 
                different file formats. The constructor first creates a numpy 
                ndarray with structured dtype. If provided, the constructor 
                adds the **coloring** attribute, which is a dictionary that 
                represents hierarchical structure on the columns, (e.g. groups
                of column names).

                **array** :  two-dimensional arrays (:class:`numpy.ndarray`)


                        >>> import numpy
                        >>> x = numpy.array([[1, 2], [3, 4]])
                        >>> tabarray(array=x)
                        tabarray([(1, 2), (3, 4)], 
                              dtype=[('f0', '<i4'), ('f1', '<i4')])
                        
                        **See also:**  `numpy.rec.fromrecords <http://docs.scipy.org/doc/numpy/reference/generated/numpy.core.records.fromrecords.html#numpy.core.records.fromrecords>`_

                **records** :  python list of records (tuples or lists)
 
                        >>> tabarray(records=[('bork', 1, 3.5), ('stork', 2, -4.0)], names=['x','y','z'])
                        tabarray([('bork', 1, 3.5), ('stork', 2, -4.0)], 
                              dtype=[('x', '|S5'), ('y', '<i4'), ('z', '<f8')])

                        **See also:**  `numpy.rec.fromrecords <http://docs.scipy.org/doc/numpy/reference/generated/numpy.core.records.fromrecords.html#numpy.core.records.fromrecords>`_

                **columns** :  list of python lists or
                1-D numpy arrays 
                
                        Fastest when passed a list of numpy arrays, rather than
                        a list of lists.

                        >>> tabarray(columns=[['bork', 'stork'], [1, 2], [3.5, -4.0]], names=['x','y','z']) 
                        tabarray([('bork', 1, 3.5), ('stork', 2, -4.0)], 
                              dtype=[('x', '|S5'), ('y', '<i4'), ('z', '<f8')])

                **See also:**  `numpy.rec.fromarrays <http://docs.scipy.org/doc/numpy/reference/generated/numpy.core.records.fromrecords.html#numpy.core.records.fromarrays>`_

                **SVfile** :  string

                        File path to a separated variable (CSV) text file.  
                        Load data from a CSV by calling::

                                tabular.io.loadSV(SVfile, comments, delimiter, 
                                lineterminator, skiprows, usecols, metametadata, 
                                namesinheader, valuefixer, linefixer)

                        **See also:**  :func:`saveSV`, 
                        :func:`tabular.io.loadSV`


                **binary** :  string

                        File path to a binary file. Load a ``.npz`` binary file 
                        created by the :func:`savebinary` by calling::

                                tabular.io.loadbinary(binary)

                        which uses :func:`numpy.load`.

                        **See also:** :func:`savebinary`, 
                        :func:`tabular.io.loadbinary`

                **HSVfile** :  string

                        File path to a hierarchical separated variable 
                        (``.hsv``) directory, or a comma separated variable 
                        (``.csv``) text file inside of a HSV directory 
                        corresponding to a single column of data.  Load a 
                        structured directory or single file defined by the 
                        :func:`saveHSV` method by calling::

                                tabular.io.loadHSV(HSVfile, toload)

                        **See also:** :func:`saveHSV`, 
                        :func:`tabular.io.loadHSV`, 
                        :func:`tabular.io.loadHSVlist`

                **HSVlist** :  list of strings

                        List of file paths to hierarchical separated variable
                        (``.hsv``) files and/or individual comma separated
                        variable (``.csv``) text files inside of HSV 
                        directories, all with the same number of records.  Load 
                        a list of file paths created by the :func:`saveHSV` 
                        method by calling::

                                tabular.io.loadHSVlist(HSVlist)

                        **See also:**  :func:`saveHSV`,  
                        :func:`tabular.io.loadHSV`, 
                        :func:`tabular.io.loadHSVlist`

        **Additional parameters**

                **coloring**:  dictionary

                        Hierarchical column-oriented structure.

                *	Colorings can be passed as argument:

                        *	In the *coloring* argument, pass a dictionary. Each 
                        	key is a string naming a color whose corresponding
                        	value is a list of column names (strings) in that 
                        	color.

                        *	If colorings are passed as argument, they override
                        	any colorings inferred from the input data.

                *	Colorings can be inferred from the input data:

                        *	If constructing from a ``.hsv`` directory, 
                        	colorings will be automatically inferred from the 
                        	directory tree.

                        *	If constructing from a CSV file (e.g. ``.tsv``, 
                        	``.csv``) created by :func:`saveSV`, colorings are 
                        	automatically parsed from the header when present.

                        *	If constructing from a numpy binary file (e.g. 
                        	``.npz``) created by :func:`savebinary`, colorings 
                        	are automatically loaded from a binary file 
                        	(``coloring.npy``) in the ``.npz`` directory.

                **wrap**:  string

                        Adds a color with name  *wrap* listing all column 
                        names. (When this  :class:`tabarray` is saved to a
                        ``.hsv`` directory, all columns will be nested in an
                        additional directory, ``wrap.hsv``.)

                **subtype**:  class

                        The class object for the actual type of the newly
                        created type(:class:`tabarray`) object; this will be
                        either type(:class:`tabarray`) or the type of a 
                        subclass).
                 
                                
                **usecols** :  sequence of non-negative integers, optional

                    If `usecols` is not `None`, only the columns it lists are
                    loaded, with 0 being the first column.  column names, 
                    coloring keys, and column numbers can be mixed
                
                **metametadata** :  dictionary of integers or pairs of integers
                    
                    Specifies supplementary metametadata information for use 
                    with SVfile loading.
                    
                **namesinheader** : Boolean, optional

                    If `namesinheader == True` and `metadatadict == None`, then 
                    assume metadatadict = {'names': headerlines-1}, e.g. the 
                    column names are in the last header line.
                    
                **headerlines** : integer, optional

                    The number of lines at the top of the file (after the first 
                    `skiprows` lines) corresponding to the header of the file, 
                    where metadata can be found (e.g. column names).

                **valuefixer**  :  lambda function, optional

                    Lambda function to apply to every value in the SV.
                    
                **linefixer** : lambda function, optional

                    Lambda function to apply to every line in the SV.
                    
                **verbosity** :  integer, optional

                   Sets how much detail from messages will be printed.
                   
                **skiprows** :  non-negative integer, optional

                    The first `skiprows` lines are ignored.
                               
             
                The following parameters duplicate things in the NumPy record 
                array creation inferface:
                
                **names** : list of strings
                	
                	Sets the names of the columns.
                	
                **formats** :  anything that can used in numpy.rec.array 
                construct as formats argument
                
                    Sets the datatypes of the columns. 
                
                **dtype** : numpy.dtype object
                
                    Sets the numpy dtype of the resulting tabarray, combining 
                    column format and column name information.  (If you set 
                    dtype, setting names or formats is unnecessary.)
                
                **byteorder**
                
                **aligned**
                

                The following parameters duplicate things in the Python CSV
                module interface:
                
                **delimiter** : single-character string
                
                    Delimiter to use to reading in using SVfile
               
                **lineterminator** : single-character string
                
                    Line terminator to use when reading in using SVfile
                    
                **quotechar**

                **escapechar**

                **quoting**

                **doublequote**

                **skipinitialspace**

                **dialect**
                
                
        **Special column names**

                        Column names that begin and end with double
                        underscores, e.g. '__column_name__' may be used
                        to hold row-by-row metadata.

                        One use of these special columns is for formatting
                        and communicating "side" information to other
                        :class:`tabarray` methods. For instance, various
                        specially designated columns can be used to tell
                        other applications that use :class:`tabarray` objects
                        how to interpret the rows in a way that would be
                        tedious for the user to have to remember to supply.

                        Two instances of this are used by the `aggregate_in`
                        function, :func:`tabular.spreadsheet.aggregate_in`:

                        *	A '__color__' column can be interpreted by a 
                        	browser's tabular-to-html representation. It is
                        	expected in each row to contain a web-safe hex
                        	triplet color specification, e.g. a string of the 
                        	form '#XXXXXX' (see
                        	http://en.wikipedia.org/wiki/Web_colors).

                        *	The '__aggregates__' column is used to disambiguate
                        	rows that are aggregates of data in other sets of
                        	rows for the ``.aggregate_in`` method (see comments 
                        	on that below).

                        This row-by-row information can also be used to specify
                        arbitrary higher-level groups of rows, in analogy to 
                        how the `coloring` attribute specifies groupings of 
                        columns.  This would work either by:

                        *	storing in a special column whose name specifies
                        	group name, a boolean in each row as to whether the
                        	row belongs to that group, or

                        *	for a "type" of grouping consisting of several  
                        	nonintersecting row groups, a single column 
                        	specifying by some string or integer code which
                        	group the row belongs to.  (An example of this is 
                        	the "__aggregates__" column used by the 
                        	``.aggregate_in`` method, see below for info about 
                        	this.)

        """

        if not array is None:
            if len(array) > 0:
                DataObj = utils.fromrecords(array, type=np.ndarray, dtype=dtype, 
                          shape=shape, formats=formats, names=names, 
                          titles=titles, aligned=aligned, byteorder=byteorder)
            else:
                DataObj = utils.fromarrays([[]]*len(array.dtype), type=np.ndarray,
                          dtype=dtype, shape=shape, formats=formats, 
                          names=names, titles=titles, aligned=aligned, 
                          byteorder=byteorder)
        elif not records is None:
            DataObj = utils.fromrecords(records, type=np.ndarray, dtype=dtype, shape=shape, 
                      formats=formats, names=names, titles=titles, 
                      aligned=aligned, byteorder=byteorder)
        elif not columns is None:
            DataObj = utils.fromarrays(columns,type=np.ndarray, dtype=dtype, shape=shape, 
                      formats=formats, names=names, titles=titles, 
                      aligned=aligned, byteorder=byteorder)
        elif not SVfile is None:
            chkExists(SVfile)
            # The returned DataObj is a list of numpy arrays.
            [DataObj, metadata] = \
                io.loadSV(fname=SVfile, names=names, dtype=dtype, shape=shape, 
                formats=formats, titles=titles, aligned=aligned, 
                byteorder=byteorder, buf=buf,offset=offset,strides=strides,
                comments=comments, delimiter=delimiter, 
                lineterminator=lineterminator, escapechar=escapechar,
                quoting=quoting,quotechar=quotechar,doublequote=doublequote,
                skipinitialspace=skipinitialspace, skiprows=skiprows, 
                usecols=usecols, metametadata=metametadata, 
                namesinheader=namesinheader, headerlines=headerlines, 
                valuefixer=valuefixer, linefixer=linefixer,verbosity=verbosity)
            if (names is None) and 'names' in metadata.keys() and metadata['names']:
                names = metadata['names']
            if (coloring is None) and 'coloring' in metadata.keys() and metadata['coloring']:
                coloring = metadata['coloring']

        elif not binary is None:
            chkExists(binary)
            # Returned DataObj is a numpy ndarray with structured dtype
            [DataObj, givendtype, givencoloring] = io.loadbinary(fname=binary)
            if (dtype is None) and (not givendtype is None):
                dtype = givendtype
            if (coloring is None) and (not givencoloring is None):
                coloring = givencoloring
            DataObj = utils.fromrecords(DataObj, type=np.ndarray, dtype=dtype, shape=shape,   
                      formats=formats, names=names, titles=titles, 
                      aligned=aligned, byteorder=byteorder)
        elif not HSVfile is None:
            chkExists(HSVfile)
            # The returned DataObj is a list of numpy arrays.
            [DataObj, givennames, givencoloring] = \
                                        io.loadHSV(path=HSVfile, toload=toload)
            if (names is None) and (not givennames is None):
                names = givennames
            if (coloring is None) and (not givencoloring is None):
                coloring = givencoloring
            DataObj = utils.fromarrays(DataObj, type=np.ndarray, dtype=dtype, shape=shape, 
                      formats=formats, names=names, titles=titles, 
                      aligned=aligned, byteorder=byteorder)
        elif not HSVlist is None:
            [chkExists(x) for x in HSVlist]
            return io.loadHSVlist(flist=HSVlist)
        else:
            DataObj = np.core.records.recarray.__new__(
                      subtype, shape, dtype=dtype, 
                      formats=formats, names=names, titles=titles, 
                      aligned=aligned, byteorder=byteorder, buf=buf, 
                      offset=offset, strides=strides)
                      
        DataObj = DataObj.view(subtype)              

        if not coloring is None:
            coloringsInNames = \
                 list(set(coloring.keys()).intersection(set(DataObj.dtype.names)))
            if len(coloringsInNames) == 0:
                DataObj.coloring = coloring
            else:
                print ("Warning:  the following coloring keys,", 
                       coloringsInNames, ", are also attribute (column) names " 
                       "in the tabarray.  This is not allowed, and so these " 
                       "coloring keys will be deleted.  The corresponding "
                       "columns of data will not be lost and will retain the "
                       "same names.")
                for c in coloringsInNames:
                    coloring.pop(c)
                DataObj.coloring = coloring
        else:
            DataObj.coloring = {}

        if not wrap is None:
            DataObj.coloring[wrap] = DataObj.dtype.names

        return DataObj
        

    def __array_finalize__(self, obj):
        """
        Set default attributes (e.g. `coloring`) if `obj` does not have them.

        Note:  this is called when you view a numpy ndarray as a tabarray.

        """
        self.coloring = getattr(obj, 'coloring', {})

    def extract(self):
        """
        Creates a copy of this tabarray in the form of a numpy ndarray.

        Useful if you want to do math on array elements, e.g. if you have a 
        subset of the columns that are all numerical, you can construct a 
        numerical matrix and do matrix operations.

        """
        return np.vstack([self[r] for r in self.dtype.names]).T.squeeze()

    def __getitem__(self, ind):
        """
        Returns a subrectangle of the table.

        The representation of the subrectangle depends on `type(ind)`. Also, 
        whether the returned object represents a new independent copy of the 
        subrectangle, or a "view" into this self object, depends on 
        `type(ind)`.

        *	If you pass the name of an existing coloring, you get a tabarray 
        	consisting of copies of columns in that coloring.

        *	If you pass a list of existing coloring names and/or column names, 
        	you get a tabarray consisting of copies of columns in the list 
        	(name of coloring is equivalent to list of names of columns in that 
        	coloring; duplicate columns are deleted).

        *	If you pass a :class:`numpy.ndarray`, you get a tabarray consisting 
        	a subrectangle of the tabarray, as handled by  
        	:func:`numpy.ndarray.__getitem__`:

                *	if you pass a 1D NumPy ndarray of booleans of `len(self)`,    
                	the rectangle contains copies of the rows for which the 
                	corresponding entry is `True`.

                *	if you pass a list of row numbers, you get a tabarray
                	containing copies of these rows.

        """
        if ind in self.coloring.keys():
            return self[self.coloring[ind]]
        elif isinstance(ind,list) and \
             all([a in self.dtype.names or a in self.coloring.keys() 
                                                           for a in ind]) and \
             set(self.coloring.keys()).intersection(ind):
            ns = utils.uniqify(utils.listunion([[a] if a in self.dtype.names 
                                          else self.coloring[a] for a in ind]))
            return self[ns]
        else:
            D = np.ndarray.__getitem__(self,ind)
            if isinstance(D,np.ndarray) and not D.dtype.names is None:
                D = D.view(tabarray)
                D.coloring = dict([(k, 
                list(set(self.coloring[k]).intersection(set(D.dtype.names)))) 
                for k in self.coloring.keys() if 
                len(set(self.coloring[k]).intersection(set(D.dtype.names))) > 0 
                and len(set(D.dtype.names).difference(self.coloring[k])) > 0])
            return D

    def addrecords(self, new):
        """
        Append one or more records to the end of the array.

        Method wraps::

                tabular.spreadsheet.addrecords(self, new)

        """
        data = spreadsheet.addrecords(self,new)
        data = data.view(tabarray)
        data.coloring = self.coloring
        return data
    addrecords.func_doc = modifydocs(addrecords, spreadsheet.addrecords, 
                                     ":func:`tabular.spreadsheet.addrecords`")

    def addcols(self, cols, names=None):
        """
        Add one or more new columns.

        Method wraps::

                tabular.spreadsheet.addcols(self, cols, names)

        """
        data = spreadsheet.addcols(self, cols, names)
        data = data.view(tabarray)
        data.coloring = self.coloring
        return data
    addcols.func_doc = modifydocs(addcols, spreadsheet.addcols, 
                                  ":func:`tabular.spreadsheet.addcols`")

    def deletecols(self, cols):
        """
        Delete columns and/or colors.

        Method wraps::

                tabular.spreadsheet.deletecols(self, cols)

        """
        deletenames = utils.uniqify(utils.listunion([[c] if c in 
        self.dtype.names else self.coloring[c] for c in cols]))
        return spreadsheet.deletecols(self,deletenames)
    deletecols.func_doc = modifydocs(deletecols, spreadsheet.deletecols, 
                                     ":func:`tabular.spreadsheet.deletecols`")

    def renamecol(self, old, new):
        """
        Rename column or color in-place.

        Method wraps::

                tabular.spreadsheet.renamecol(self, old, new)

        """
        spreadsheet.renamecol(self,old,new)
        for x in self.coloring.keys():
            if old in self.coloring[x]:
                ind = self.coloring[x].index(old)
                self.coloring[x][ind] = new
    renamecol.func_doc = modifydocs(renamecol, spreadsheet.renamecol, 
                                    ":func:`tabular.spreadsheet.renamecol`")

    def saveSV(self, fname, comments=None, metadata=None, printmetadict=None,
                       dialect = None, delimiter=None, doublequote=True, 
                       lineterminator='\n', escapechar = None, quoting=csv.QUOTE_MINIMAL, 
                       quotechar='"', skipinitialspace=False,verbosity=DEFAULT_VERBOSITY):
        """
        Save the tabarray to a single flat separated variable (CSV) text file.  

        Method wraps::

                tabular.io.saveSV(fname, self, comments, delimiter, linebreak, metadatakeys, printmetadatadict)

        """
        io.saveSV(fname,self, comments, metadata, printmetadict, 
                        dialect, delimiter, doublequote, lineterminator, escapechar, quoting, quotechar,skipinitialspace,verbosity=verbosity)
                        
    saveSV.func_doc = modifydocs(saveSV, io.saveSV, 
                                 ":func:`tabular.io.saveSV`")

    def savebinary(self, fname, savecoloring=True):
        """
        Save the tabarray to a numpy binary archive (``.npz``).
        
        Save the tabarray to a ``.npz`` zipped file containing ``.npy`` binary 
        files for data, plus optionally coloring and/or rowdata or simply to a 
        ``.npy`` binary file containing the data but no coloring or rowdata.

        Method wraps::

                tabular.io.savebinary(fname, self, savecoloring, saverowdata)

        """
        io.savebinary(fname=fname, X=self, savecoloring=savecoloring)
    savebinary.func_doc = modifydocs(savebinary, io.savebinary, 
                                     ":func:`tabular.io.savebinary`")

    def saveHSV(self, fname, printheaderfile=True):
        """
        Save the tabarray to a hierarchical separated variable (HSV) directory.
        
        Save the tabarray to a ``.hsv`` directory.  Each column is saved as a 
        separate comma-separated variable file (``.csv``), whose name includes 
        the column name and data type of the column (e.g. ``name.int.csv``, 
        ``name.float.csv``, ``name.str.csv``).

        Hierarchical structure on the columns, i.e. :attr:`coloring`, is
        preserved by the file directory structure, with subdirectories named 
        ``color.hsv`` and containing ``.csv`` files corrseponding to columns of 
        data grouped by that color.

        Finally, :attr:`rowdata` is stored as a dump of a pickled object in the 
        top level directory `fname`.

        The ``.hsv`` can later be loaded back by passing the file path `fname` 
        to the `HSV` argument of the :class:`tabarray` constructor.

        Method wraps::

                tabular.io.saveHSV(fname, self, printheaderfile)

        """
        io.saveHSV(fname=fname, X=self, printheaderfile=printheaderfile)
    saveHSV.func_doc = modifydocs(saveHSV, io.saveHSV, 
                                  ":func:`tabular.io.saveHSV`")

    def savecolumns(self, fname):
        """
        Save the tabarray to a set of flat ``.csv`` files, one per column. 
        
        Save the tabarray to a set of flat ``.csv`` files in ``.hsv`` format 
        (e.g. ``.int.csv``, ``.float.csv``, ``.str.csv``).  Note that data in 
        the *coloring* attribute is lost.

        Method wraps::

                tabular.io.savecolumns(fname, self)

        """
        io.savecolumns(fname=fname, X=self)
    savecolumns.func_doc = modifydocs(savecolumns, io.savecolumns, 
                                      ":func:`tabular.io.savecolumns`")

    def appendHSV(self, fname, order=None):
        """
        Append the tabarray to an existing on-disk HSV representation.
        
        Like :func:`saveHSV` but for appending instead of writing from scratch.

        Method wraps::

                tabular.io.appendHSV(fname, self, order)

        """
        io.appendHSV(fname=fname, RecObj=self, order=order)
    appendHSV.func_doc = modifydocs(appendHSV, io.appendHSV, 
                                    ":func:`tabular.io.appendHSV`")

    def appendcolumns(self, fname, order=None):
        """
        Append the tabarray to an existing on-disk flat HSV representation.
        
        Like :func:`savecolumns` but for appending instead of writing from 
        scratch.

        Method wraps::

                tabular.io.appendcolumns(fname, self, order)

        """
        io.appendcolumns(fname=fname, RecObj=self, order=order)
    appendcolumns.func_doc = modifydocs(appendcolumns, io.appendcolumns, 
                                        ":func:`tabular.io.appendcolumns`")

    def colstack(self, new, mode='abort'):
        """
        Horizontal stacking for tabarrays.

        Stack tabarray(s) in `new` to the right of `self`.

        **See also**

                :func:`tabular.tabarray.tab_colstack`, 
                :func:`tabular.spreadsheet.colstack`

        """
        if isinstance(new,list):
            return tab_colstack([self] + new,mode)
        else:
            return tab_colstack([self, new], mode)

    colstack.func_doc = modifydocs(colstack, spreadsheet.colstack,  
                                   ":func:`tabular.spreadsheet.colstack`")

    def rowstack(self, new, mode='nulls'):
        """
        Vertical stacking for tabarrays.

        Stack tabarray(s) in `new` below `self`.

        **See also**

                :func:`tabular.tabarray.tab_rowstack`, 
                :func:`tabular.spreadsheet.rowstack`

        """
        if isinstance(new,list):
            return tab_rowstack([self] + new, mode)
        else:
            return tab_rowstack([self, new], mode)

    rowstack.func_doc = modifydocs(rowstack, spreadsheet.rowstack, 
                                   ":func:`tabular.spreadsheet.rowstack`")

    def aggregate(self, On=None, AggFuncDict=None, AggFunc=None, 
                  returnsort=False):
        """
        Aggregate a tabarray on columns for given functions.

        Method wraps::

                tabular.spreadsheet.aggregate(self, On, AggFuncDict, AggFunc, returnsort)

        """
        if returnsort:
            [data, s] = spreadsheet.aggregate(X=self, On=On, 
                        AggFuncDict=AggFuncDict, AggFunc=AggFunc, 
                        returnsort=returnsort)
        else:
            data = spreadsheet.aggregate(X=self, On=On, 
                   AggFuncDict=AggFuncDict, AggFunc=AggFunc, 
                   returnsort=returnsort)
        data = data.view(tabarray)
        data.coloring = self.coloring
        if returnsort:
            return [data, s]
        else:
            return data
    aggregate.func_doc = modifydocs(aggregate, spreadsheet.aggregate, 
                                    ":func:`tabular.spreadsheet.aggregate`")

    def aggregate_in(self, On=None, AggFuncDict=None, AggFunc=None, 
                     interspersed=True):
        """
        Aggregate a tabarray and include original data in the result.

        See the :func:`aggregate` method.

        Method wraps::

                tabular.summarize.aggregate_in(self, On, AggFuncDict, AggFunc, interspersed)

        """
        data = spreadsheet.aggregate_in(Data=self, On=On, 
               AggFuncDict=AggFuncDict, AggFunc=AggFunc, 
               interspersed=interspersed)
        data = data.view(tabarray)
        data.view = self.coloring
        return data

    aggregate_in.func_doc = modifydocs(aggregate_in, spreadsheet.aggregate_in,  
                                    ":func:`tabular.spreadsheet.aggregate_in`")

    def pivot(self, a, b, Keep=None, NullVals=None, prefix='_'):
        """
        Pivot with `a` as the row axis and `b` values as the column axis.

        Method wraps::

                tabular.spreadsheet.pivot(X, a, b, Keep)

        """
        [data,coloring] = spreadsheet.pivot(X=self, a=a, b=b, Keep=Keep, 
                          NullVals=NullVals, prefix=prefix)
        data = data.view(tabarray)
        data.coloring = coloring
        return data

    pivot.func_doc = modifydocs(pivot, spreadsheet.pivot, 
                                ":func:`tabular.spreadsheet.pivot`")

    def replace(self, old, new, strict=True, cols=None, rows=None):
    	"""
    	Replace `old` with `new` in the rows `rows` of columns `cols`.
    	
    	Method wraps::
    	
    	        tabular.spreadsheet.replace(self, old, new, strict, cols, rows)
    	
    	"""
        spreadsheet.replace(self, old, new, strict, cols, rows)

    replace.func_doc = modifydocs(replace, spreadsheet.replace,
                                  ":func:`tabular.spreadsheet.replace`")

    def join(self, ToMerge, keycols=None, nullvals=None, 
             renamer=None, returnrenaming=False, selfname=None, Names=None):
        """
        Wrapper for spreadsheet.join, but handles coloring attributes.

        The `selfname` argument allows naming of `self` to be used if `ToMerge` 
        is a dictionary.

        **See also:** :func:`tabular.spreadsheet.join`, :func:`tab_join`
        """

        if isinstance(ToMerge,np.ndarray):
            ToMerge = [ToMerge]

        if isinstance(ToMerge,dict):
            assert selfname not in ToMerge.keys(), \
             ('Can\'t use "', selfname + '" for name of one of the things to '  
              'merge, since it is the same name as the self object.')
            if selfname == None:
                try:
                    selfname = self.name
                except AttributeError:
                    selfname = 'self'
            ToMerge.update({selfname:self})
        else:
            ToMerge = [self] + ToMerge

        return tab_join(ToMerge, keycols=keycols, nullvals=nullvals, 
                   renamer=renamer, returnrenaming=returnrenaming, Names=Names)

    def argsort(self, axis=-1, kind='quicksort', order=None):
        """
        Returns the indices that would sort an array.

        .. note::

                This method wraps `numpy.argsort`.  This documentation is 
                modified from that of `numpy.argsort`.

        Perform an indirect sort along the given axis using the algorithm 
        specified by the `kind` keyword.  It returns an array of indices of the 
        same shape as the original array that index data along the given axis 
        in sorted order.

        **Parameters**

                **axis** : int or None, optional

                        Axis along which to sort.  The default is -1 (the last 
                        axis). If `None`, the flattened array is used.

                **kind** : {'quicksort', 'mergesort', 'heapsort'}, optional

                        Sorting algorithm.

                **order** : list, optional

                        This argument specifies which fields to compare first, 
                        second, etc.  Not all fields need be specified.

        **Returns**

                **index_array** : ndarray, int

                        Array of indices that sort the tabarray along the 
                        specified axis.  In other words, ``a[index_array]`` 
                        yields a sorted `a`.

                **See Also**

                        sort : Describes sorting algorithms used.
                        lexsort : Indirect stable sort with multiple keys.
                        ndarray.sort : Inplace sort.

                **Notes**

                        See `numpy.sort` for notes on the different sorting 
                        algorithms.

                **Examples**

                        Sorting with keys:

                        >>> x = tabarray([(1, 0), (0, 1)], dtype=[('x', '<i4'), ('y', '<i4')])
                        >>> x
                        tabarray([(1, 0), (0, 1)], 
                              dtype=[('x', '<i4'), ('y', '<i4')])

                        >>> x.argsort(order=('x','y'))
                        array([1, 0])

                        >>> x.argsort(order=('y','x'))
                        array([0, 1])

        """
        index_array = np.core.fromnumeric._wrapit(self, 'argsort', axis, 
                                                     kind, order)
        index_array = index_array.view(np.ndarray)
        return index_array

def chkExists( path ):
    """If the given file or directory does not exist, raise an exception"""
    if not os.path.exists(path): 
        raise IOError("Directory or file %s does not exist" % path)