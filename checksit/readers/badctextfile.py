#
# This module is for reading and writing the simple BADC text file format.
# This file format is based on the common separated value (CSV) format that
# is commonly produced by spreadsheet applications. It also checks to see if 
# certain metadata are available.
#
# SJP 2008-09-22

import sys, csv, string

import time
from io import StringIO

import collections



#-----
# value check functions.
# each function takes a values tuple and checks it 

def checkString(values):
    pass

def checkInt(values):
    for v in values:
        int(v) 

def checkFloat(values):
    for v in values:
        float(v) 

def checkLocation(values):
    if len(values) == 4 or len(values) == 2:
        for v in values: float(v)
    else:
        pass
    
def checkDate(values):
    # carries out a check against ISO standard date-time string
    # that conforms to one of:
    # Y-m-d
    # Y-m-d h
    # Y-m-d h:m
    # Y-m-d h:m:s
    # Y-m-d h:m:s.decimal

    for v in values:
        dateSplit = v.split(' ')
        dateString = "%Y-%m-%d"
        #print(v, v.split(' ')
        if len(dateSplit) == 2:
            timeSplit = dateSplit[1].split(':')
            if len(timeSplit) == 1:
                dateString = dateString + ' %H'
            if len(timeSplit) == 2:
                dateString = dateString + ' %H:%M'
            if len(timeSplit) == 3:
                dateString = dateString + ' %H:%M:%S'
                if '.' in v:
                    dateString = dateString + '.%f'

        time.strptime(v, dateString) 

def checkStandardName(values):
    pass

def checkHeight(values):
    float(values[0])

def checkFeatureType(values):
    pass

def checkCoordinateVariables(values):
    pass

def checkConventions(values):
    if values[0] != "BADC-CSV":
        raise BADCTextFileMetadataInvalid("Conventions must be BADC-CSV, not %s" % values[0])
    if values[1] != "1":
        raise BADCTextFileMetadataInvalid("Conventions must be 'BADC-CSV, 1', not %s" % values[1])
        
    

def checkType(values):
    v = values[0]
    if v not in ('int', 'float', 'char'):
        raise BADCTextFileMetadataNonstandard("Type not right must be int, float or char. not %s" % v)

def checkCellMethod(values):
    pass


    

# The BADCTextFile class is the main class for manipulating data.
class BADCTextFile:
    """ 
    MDinfo defines the valid use for the metadata items in the data
    files. The dictionary is keyed on the metadata label and has values
    that correspond to:
       A flag to say if the label can apply globally,
       A flag to say if the label can apply to a column,
       The minimum number of values associated with the label
       The maximum number of values associated with the label - -1 is used where any number are permitted
       A flag to say if the label is mandatory for 'basic' files
           (0=not mandatory, 1=mandatory existence for at least one column, 2=must exist for all columns)
       A flag to say if the label is mandatory for 'complete' files
           (0=not mandatory, 1=mandatory existence for at least one column, 2=must exist for all columns)
    """
#     MDinfo = {"title":                  (1,0,1,1,0,0,checkString, "A title for the data file"),
#               "comments":               (1,1,1,1,0,0,checkString, "Any text comment associated with data"),
#               "location":               (1,1,1,4,0,1,checkLocation, "Location for the data. Can be a name, bounding box, or lat and long values"),
#               "height":                 (1,1,2,2,0,0,checkHeight, "Height valid for data"),
#               "creator":                (1,1,1,2,0,1,checkString, "The name of the person and/or institute that created the data"),
#               "contributor":            (1,1,1,2,0,0,checkString, "The name of the person and/or institute that contributed to the data"),
#               "date_valid":             (1,1,1,2,0,1,checkDate, "The date the data is valid for. Needs to be YYYY-MM-DD form"),
#               "last_revised_date":      (1,1,1,1,0,1,checkDate, "The date the data was revised or worked up. Needs to be YYYY-MM-DD form"),
#               "history":                (1,1,1,1,0,1,checkString, "Text description of the file history"),
#               "reference":              (1,1,1,1,0,0,checkString, "Bibliographic reference"),
#               "source":                 (1,1,1,1,0,1,checkString, "The name of the tool used to produce the data. e.g. model name or instrument type"),
#               "observation_station":    (1,1,1,1,0,1,checkString, "The name of the observation station or instrument platform used"),
#               "rights":                 (1,1,1,1,0,0,checkString, "Conditions of use for the data"),
#               "activity":               (1,1,1,1,0,1,checkString, "The name of the activity sponsoring the collection of the data "),
#               "add_offset":             (0,1,1,1,0,0,checkFloat, "An offset value to add to the values recorded in the data"),
#               "scale_factor":           (0,1,1,1,0,0,checkFloat, "A scale factor to multiply the data values by"),
#               "valid_min":              (1,1,1,1,0,0,checkFloat, "Values below this value should be interpreted as missing"),
#               "valid_max":              (1,1,1,1,0,0,checkFloat, "Values above this value should be interpreted as missing"),
#               "valid_range":            (1,1,2,2,0,0,checkFloat, "Values outside this range should be interpreted as missing"),
#               "long_name":              (0,1,2,2,2,2,checkString, "Description of variable and its unit"),
#               "standard_name":          (0,1,3,3,0,0,checkStandardName, "Name of variable from a standard list, with unit and the name of the list"),
#               "feature_type":           (1,0,1,1,0,1,checkFeatureType, "type of feature: point series, trajectory or point collection"),
#               "coordinate_variable":    (0,1,0,2,1,1,checkCoordinateVariables, "Flag to show which column(s) are regarded as coordinate variables"),
#               "Conventions":            (1,0,2,2,1,1,checkConventions, "Metadata conventions used. Must be BADC-CSV, 1"),
#               "type":                   (0,1,1,1,0,2,checkType, "The type of the variables in a column. Should be char, int or float"),
#               "cell_method":            (1,1,1,4,0,0,checkCellMethod, "The cell method used in preparing the data")}
   
    
    #                                   [G,C,min,max,basic,complete]
    MDinfo = [("Conventions",           (1,0,2,2,1,1,checkConventions, "Metadata conventions used. Must be BADC-CSV, 1"))
             ,("long_name",             (0,1,2,2,2,2,checkString, "Description of variable and its unit"))
             ,("coordinate_variable",   (0,1,0,2,1,1,checkCoordinateVariables, "Flag to show which column(s) are regarded as coordinate variables"))
             ,("creator",               (1,1,1,2,0,1,checkString, "The name of the person and/or institute that created the data"))
             ,("source",                (1,1,1,1,0,1,checkString, "The name of the tool used to produce the data. e.g. model name or instrument type"))
             ,("observation_station",   (1,1,1,1,0,1,checkString, "The name of the observation station or instrument platform used"))
             ,("activity",              (1,1,1,1,0,1,checkString, "The name of the activity sponsoring the collection of the data "))
             ,("feature_type",          (1,0,1,1,0,1,checkFeatureType, "type of feature,point series, trajectory or point collection"))
             ,("location",              (1,1,1,4,0,1,checkLocation, "Location for the data. Can be a name, bounding box, or lat and long values"))
             ,("date_valid",            (1,1,1,2,0,1,checkDate, "The date the data is valid for. Needs to be YYYY-MM-DD form"))
             ,("last_revised_date",     (1,1,1,1,0,1,checkDate, "The date the data was revised or worked up. Needs to be YYYY-MM-DD form"))
             ,("history",               (1,1,1,1,0,1,checkString, "Text description of the file history"))
             ,("standard_name",         (0,1,3,3,0,0,checkStandardName, "Name of variable from a standard list, with unit and the name of the list"))
             ,("title",                 (1,0,1,1,0,0,checkString, "A title for the data file"))
             ,("comments",              (1,1,1,1,0,0,checkString, "Any text comment associated with data"))
             ,("contributor",           (1,1,1,2,0,0,checkString, "The name of the person and/or institute that contributed to the data"))
             ,("height",                (1,1,2,2,0,0,checkHeight, "Height valid for data"))
             ,("reference",             (1,1,1,1,0,0,checkString, "Bibliographic reference"))
             ,("rights",                (1,1,1,1,0,0,checkString, "Conditions of use for the data"))
             ,("valid_min",             (1,1,1,1,0,0,checkFloat, "Values below this value should be interpreted as missing"))
             ,("valid_max",             (1,1,1,1,0,0,checkFloat, "Values above this value should be interpreted as missing"))
             ,("valid_range",           (1,1,2,2,0,0,checkFloat, "Values outside this range should be interpreted as missing"))
             ,("type",                  (0,1,1,1,0,2,checkType, "The type of the variables in a column. Should be char, int or float"))
             ,("cell_method",           (1,1,1,4,0,0,checkCellMethod, "The cell method used in preparing the data"))              
             ,("add_offset",            (0,1,1,1,0,0,checkFloat, "An offset value to add to the values recorded in the data"))
             ,("scale_factor",          (0,1,1,1,0,0,checkFloat, "A scale factor to multiply the data values by"))
             ,("flag_values",           (0,1,1,-1,0,0,checkString, "Values used for flag table in data"))
             ,("flag_meanings",         (0,1,1,-1,0,0,checkString, "Meanings for each flag_value"))
             ]
                
                
                
    MDinfo = collections.OrderedDict(MDinfo)
    
    def __init__(self, fh):
        self.fh = fh
        self.version = 1
        self._data = BADCTextFileData()
        self._metadata = BADCTextFileMetadata()
        if self.fh.mode == 'r':
            self.parse()
        else:
            self.add_metadata('Conventions',('BADC-CSV', '1'),'G')


    def parse(self):

        reader = csv.reader(self.fh)
        section = 1
        for row in reader:
            try:

            # section 1 is the metadata section 
                if section == 1:
                    while row[-1] == '': 
                        row=row[:-1] # remove blank cells
                    
                    if len(row) == 0:
                        continue        # ignore blank lines
                    
                    elif len(row) == 1:
                        if row[0].lower() == 'data':
                            section = 2
                            continue
                    else:
                        label, ref, values = row[0], row[1], row[2:]
                        values = tuple(values)
                        self.add_metadata(label,values,ref) 
    
                # section 2 the column names
                elif section == 2:
                    while row[-1] == '':
                        row=row[:-1] # remove blank cells
                    for colname in row:
                        self.add_variable(colname)
                    section = 3
    
                # section 3 is the data section 
                elif section == 3:
                    while row[-1] == '':
                        row=row[:-1] # remove blank cells
                    
                    if len(row) == 0:
                        continue        # ignore blank lines
                    
                    elif len(row) == 1: 
                        if row[0].lower() == 'end data':
                            return
                    else:
                        # data row
                        self.add_datarecord(row) 

            except BADCTextFileError:
                print(row)
                raise 


    def check_valid(self):
    
        self.valid_check_error = []
    
        for label in BADCTextFile.MDinfo:
            applyg, applyc, mino, maxo, mandb, mandc, check, meaning = BADCTextFile.MDinfo[label]
           
            #if label == 'long_name':
           
            
            # if label can't apply globally but is defined raise error 
            if not applyg and self[label] != []:
                self.valid_check_error.append("Not allowed as global metadata parameter: %s, %s\n" %(label, self[label]))
                #raise BADCTextFileMetadataInvalid("Not allowed as global metadata parameter: %s, %s" %(label, self[label]))
            
            # if label can't apply to column but is defined raise error 
            if not applyc and self[label] == []:
                for colname in self.colnames():
                    if self[label,colname] != []: 
                        self.valid_check_error.append("Given metadata not allowed for a column: %s, %s, %s\n" %(label, colname, self[label,colname]))
                        #raise BADCTextFileMetadataInvalid("Given metadata not allowed for a column: %s, %s, %s" %(label, colname, self[label,colname]))
            
            # values have wrong number of fields
            
            
                  
            if applyg:
                for values in self[label]:
                    if maxo != -1 and len(values) > maxo:

                        self.valid_check_error.append("Max number of metadata fields (%s) exceeded for %s: %s\n" % (maxo, label, values))
                        #raise BADCTextFileMetadataInvalid("Max number of metadata fields (%s) exceeded for %s: %s" % (maxo, label, values))
                    if len(values) < mino:

                        self.valid_check_error.append("Min number of metadata fields (%s) not given for %s: %s\n" % (mino, label, values,))
                        #raise BADCTextFileMetadataInvalid("Min number of metadata fields (%s) not given for %s: %s" % (mino, label, values,))
            
            if applyc:            
                for colname in self.colnames():
                    if label in self._metadata.varRecords[colname]:
                        values = self._metadata.varRecords[colname][label]
                        if maxo != -1 and len(values) > maxo:

                            self.valid_check_error.append("Max number of metadata fields (%s) exceeded for %s: %s\n" % (maxo, label, values,))
                            #raise BADCTextFileMetadataInvalid("Max number of metadata fields (%s) exceeded for %s: %s" % (maxo, label, values,))
                        if len(values) < mino:
                            self.valid_check_error.append("Min number of metadata fields (%s) not given for %s: %s\n" % (mino, label, values,))
                            #raise BADCTextFileMetadataInvalid("Min number of metadata fields (%s) not given for %s: %s" % (mino, label, values,))

            #see if values are OK
        if self.valid_check_error != []:
            raise BADCTextFileMetadataInvalid(self.valid_check_error)
        
        else:        
            for values in self[label]:
                try:
                    check(values)
                except:
                    
                    raise BADCTextFileMetadataInvalid("Metadata field values invalid %s: %s  [%s]\n" % (label, values,sys.exc_value))    
            for colname in self.colnames():
                for values in self[label,colname]:
                    check(values)
                
                
            
    def check_colrefs(self):
        long_namesCnt = []
        
        for long_names in self._metadata:
            ref = long_names[2]
            long_namesCnt.append(ref)
        
        if len(long_namesCnt) == len(self.colnames()):
            try:
                for colName in long_namesCnt:
                    if not colName in self.colnames():
                        raise
            except:
                raise BADCTextFileMetadataInvalid('Column names %s not in column header list %s'% (colName,','.join(self.colnames())))
        else:
            raise BADCTextFileMetadataInvalid('Not all column headings given %s'% ','.join(self.colnames()))

    def check_complete(self, level='basic'):
        #self.check_colrefs()
        self.check_valid()
        self.basicCheckErrors = []
        
        for label in BADCTextFile.MDinfo:
            applyg, applyc, mino, maxo, mandb, mandc, check, meaning = BADCTextFile.MDinfo[label]
            #[G,C,min,max,basic,complete]
            
            # find level for check
            if level=='basic': 
                mand = mandb
            else: 
                mand = mandc
                      
            
            #if its not mandatory skip
            if not mand:
                continue
            print(level, label)

            print('doing this')
            # if applies globally then there should be a global record or
            # one at least one variable
            if applyg:
            
            
                if self[label] != []:
                    #found global value. next label
                    continue
                for colname in self.colnames():
                    if self[label,colname] != []:
                        break
                else:
                    self.basicCheckErrors.append("Basic global metadata not there: %s\n" % label)
                    #raise BADCTextFileMetadataIncomplete("Basic global metadata not there: %s" % label)
                  
            # if applies to column only then there should be a record for
            # each variable
            elif applyc and mand==2:
                               
                for colname in self.colnames():
                    try:
                        if self._metadata.varRecords[colname][label] == []:
                            raise
                    except:
                        self.basicCheckErrors.append('Basic column metadata not there: "%s" not there for %s\n' % (label, colname))
                        #raise BADCTextFileMetadataIncomplete('Basic column metadata not there: "%s" not there for %s' % (label, colname))

        if self.basicCheckErrors != []:
            raise BADCTextFileMetadataIncomplete(self.basicCheckErrors)
        
    def colnames(self):
        return tuple(self._data.colnames)

    def nvar(self):
        return self._data.nvar()

    def __len__(self):
        return len(self._data)

    def __getitem__(self, i):
        # -- ref change
        if type(i) == int:
            return self._data[i]
        else:
            return self._metadata[i]
        
    def add_variable(self,colname,data=()):
        # -- ref change
        self._data.add_variable(colname, data)

    def add_datarecord(self, datavalues):
        self._data.add_data_row(datavalues)


    def add_metadata(self, label, values, ref='G'):
        self._metadata.add_record(label, values, ref)
        

    def __repr__(self):
        return self.cvs()


        
    def cdl(self):
        # create a CDL file (to make NetCDF)
        s = "// This CDL file was generated from a BADC text file file\n"
        s = s + "netcdf foo { \n"
     
        s = s + "dimensions:\n   point = %s;\n\n" % len(self) 
     
        s = s + "variables: \n"
        for colname in self.colnames():
            print(colname)
            try:
                varname = "var%s" % int(colname.strip())
            except:
                varname = colname
            
            print(varname)
            
            vartype = self['type', colname][0][0]
            s = s + "    %s %s(point);\n" % (vartype, varname)
        s = s + "\n"
            
        s = s + self._metadata.cdl()
        s = s + "\n"
        
        s = s + "data:\n"
        for i in range(self.nvar()):
            varname = "var%s" % self._data.colnames[i]
            values = string.join(self[i], ', ')
            s =s + "%s = %s;\n" % (varname, values)
        s = s + "}\n"

        return s


    def NASA_Ames(self):
        # create a NASA-Ames file 1001 FFI
        header = []

        # find creator and institute
        c = ''
        inst = ''
        for creator in self['creator']:
            c = c + creator[0] +  '; '
            if len(creator) == 2: 
                inst = inst +  creator[1] +  '; '
        if inst == '': inst = 'Unknown'
        header.append(c[:-2])
        header.append(inst[:-2])

        # find source (DPT)
        s = ''
        for source in self['source']:
            s = s + source[0] +  '; '
        header.append(s[:-2])
    
        # find activiey
        a = ''
        for activity in self['activity']:
            a = a + activity[0] +  '; '
        header.append(a[:-2])
    
        # disk 1 of 1
        header.append("1 1")
    
        # dates 
        date_valid = self['date_valid']
        date_valid = min(date_valid)
        date_valid = date_valid[0]
        date_valid = date_valid.replace('-', ' ')
        last_revised_date = self['last_revised_date']
        last_revised_date = min(last_revised_date)
        last_revised_date = last_revised_date[0]
        last_revised_date = last_revised_date.replace('-', ' ')
        header.append("%s    %s" % (date_valid, last_revised_date))
    
        # ??
        header.append('0.0')
    
        # coord variable
        coord = self['coordinate_variables'][0][0]
        coord = self['long_name',int(coord)][0]
        coord = "%s (%s)" % (coord[0], coord[1])
        header.append(coord)
    
        # number of variables not coord variable
        header.append("%s" % (self.nvar()-1)) 
    
        #scale factors
        sf_line = ''
        for i in range(1,self.nvar()):
            sf = self['scale_factor',i]
            if len(sf)==0: sf = "1.0"
            else: sf = sf[0][0]
            sf_line = sf_line + "%s " % sf
        header.append(sf_line)
    
        #scale factors
        max_line = ''
        for i in range(1,self.nvar()):
            vm = self['valid_max',i]
            if len(vm)==0: vm = "1.0e99"
            else: vm = vm[0][0]
            vr = self['valid_range',i]
            if len(vr)==0: vr = "1.0e99"
            else: vr = vr[0][1]
            vm = min(float(vm), float(vr))
            max_line = max_line + "%s " % vm
        header.append(max_line)
    
        # variable names
        for i in range(1,self.nvar()):
            long_name = self['long_name',i][0]
            long_name = "%s (%s)" % (long_name[0], long_name[1])
            header.append(long_name)

        # normal comments
        header.append('1')
        header.append('File created from BADC text file')
    
        # special comments - all metadata to go in 
        s = StringIO()
        cvswriter = csv.writer(s)
        self._metadata.csv(cvswriter)
        metadata = s.getvalue()
        nlines = metadata.count('\n')
        header.append("%s" % (nlines+2))
        header.append("BADC-CSV style metadata:")
        header.append(s.getvalue()) 
    
        # make header
        header="%s 1001\n%s" % (len(header)+nlines, string.join(header,'\n'))

        # data space seperated
        data = ''
        for i in range(len(self)):
            data = data + string.join(self._data.getrow(i)) + '\n'

        
    
        return header+data
    


    def cvs(self):
        s = StringIO()
        cvswriter = csv.writer(s, lineterminator='\n' )
        self._metadata.csv(cvswriter)
        self._data.csv(cvswriter)
        return s.getvalue() 
        
    
class BADCTextFileData:

    # class to hold data in the files
    # BADCTextFileData is an aggregation of variables
    def __init__(self): 
        self.variables = []
        self.colnames = []
        
    def add_variable(self, name, values):
        if len(self.variables) == 0 or len(values) == len(self.variables[0]):
            self.variables.append(BADCTextFileVariable(values))
            self.colnames.append(name)
        else:
            raise BADCTextFileError("Wrong length of data")

    def add_data_row(self, values):
        if self.nvar() == 0 and len(values) != 0:
            for v in values:
                self.variables.append(BADCTextFileVariable((v,)))
        elif self.nvar() == len(values):
            for i in range(len(values)):
                self.variables[i].append(values[i])
        else:
            raise BADCTextFileError("Wrong length of data")

    def __len__(self):
        # number of data rows
        if len(self.variables) == 0:
            return 0
        else:
            return len(self.variables[0])

    def nvar(self):
        # number of variables
        return len(self.variables)

    def __getitem__(self, i):
        if type(i) == int:
            return self.variables[i].values
        else:
            col, row = i
            return self.variables[col][row]

    def getrow(self,i):
        row = []
        for j in range(self.nvar()):
            row.append(self.variables[j][i])
        return row
        
    def csv(self, csvwriter):
        csvwriter.writerow(('Data',))
        csvwriter.writerow(self.colnames)
        for i in range(len(self)):
            csvwriter.writerow(self.getrow(i))
        csvwriter.writerow(('End Data',))


class BADCTextFileVariable:

    # class to hold 1D data.    
    def __init__(self, values=[]):
        self.set_values(values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, i):
        return self.values[i]

    def append(self,v):
        self.values.append(v)

    def set_values(self, values):
        self.values = list(values)

        
class BADCTextFileMetadata:

    def __init__(self):
        # records in label, value form. Where label is the metadata label e.g. title and value is a tuple
        # e.g. ("my file",)
        self.globalRecords = []
        self.varRecords = {}

    def __getitem__(self, requested_item):
        # if the item is selected with a label and a column name then
        # use get the metadata record for the column. otherwise use expect the
        # metadata label for global
        val = []
        if type(requested_item) == tuple:
            # unpack the tuple...
            lab, col = requested_item
            
            # work through the list of global attritutes:
            for label, value in self.globalRecords:
                # no use of column here...
                if label == lab:
                    val.append(value)

            if lab in self.varRecords:
                if column in self.varRecords[lab]:
                    val.append(self.varRecords[lab][col]) 
        else:
            
            for label, value in self.globalRecords:
                if label == requested_item:
                    val.append(value)
        return val


    def add_record(self, label, values, ref='G'):
        if type(values) != tuple: values = (values,)
        if type(ref)== str and ref=='G':
            self.globalRecords.append((label,values))
        elif type(ref) ==str:
            
            if not ref in self.varRecords:
                self.varRecords[ref] = collections.OrderedDict()
            
            if not label in self.varRecords[ref]:
                self.varRecords[ref][label] = []
            self.varRecords[ref][label].extend(values)
            
            print(self.varRecords, ref, label, values)
           
            
    def cdl(self):
        # return cdl representation of metadata
        s = "// variable attributes\n"
        # make sure labels are unique for netCDF. e.g. creator, creator1, creator2
        used_labels = {}
        for label, column, values in self.varRecords:
            if used_labels.has_key((label,column)):
                use_label = "%s%s" % (label, used_labels[label,column])
                used_labels[label, column] = used_labels[label, column]+1
            else:
                use_label = label
                used_labels[label, column] = 1
            value = string.join(values, ', ')
            s =s+'        var%s:%s = "%s";\n' % (column, use_label, value)

        s=s+"// global attributes\n"
        used_labels = {}
        
        
        for label, values in self.globalRecords:
            if used_labels.has_key(label):
                use_label = "%s%s" % (label, used_labels[label])
                used_labels[label] = used_labels[label]+1
            else:
                use_label = label
                used_labels[label] = 1        
            value = string.join(values, ', ')
            s=s+'        :%s = "%s";\n' % (use_label, value)
        return s

    def csv(self, csvwriter):
        for label, values in self.globalRecords:
            csvwriter.writerow((label,'G') + values)
        for ref, values in self.varRecords.items():
            for label, value in values.items():
                csvwriter.writerow((label,ref) + value)
        
    def nc(self, ncfile_obj):
        
        ncfile_obj.Conventions = 'CF 1.6'
        
        for label, values in self.globalRecords:
            print(label, values)
            
            if label == 'Conventions':
                pass
            
            elif label in ncfile_obj.ncattrs():
                print(values)
                values = ncfile_obj.getncattr(label) + '\n ' + ', '.join(values)
                ncfile_obj.setncattr(label,values)    
            else:
                values = ', '.join(values)
                ncfile_obj.setncattr(label, values)        
        
        if ncfile_obj.history:
                     
            ncfile_obj.history = ncfile_obj.history + '\n File created from original BADC-CSV formatted file'
        
        print(self.globalRecords)
        




        # set up dimensions
        # there's just the one dimension here - as all BADC, CSV data are just one-dimensional anyway...
        # so make use of a generic "dim"

        ncfile_obj.createDimension('dim', None)
        
        # set variable attributes
        
        variables_dict = {}
                
        # first look for specific variable attributes and set these
        # then cope with anything else that remains
        # first set up all the variables based on the keys of the variable dictionary:
            
        for col_ref in self.varRecords.keys():
            
            try:
                col_name = 'var%s'% int(col_ref)
            except:
                col_name = col_ref
            
            var_type = self.varRecords[col_ref]['type'][0].strip()
            variable_to_add = ncfile_obj.createVariable(col_name,var_type,('dim',))
    
            # now to set variable attributes:
        
            for label, values in self.varRecords[col_ref].items():
                # in some cases we'll need to handle things in a special way...
                if label == 'long_name':
                    variable_to_add.setncattr(label, values[0])
                    variable_to_add.setncattr('units', values[1])
                
                elif label == 'standard_name':
                    variable_to_add.setncattr(label, ', '.join(values[0:1]))
                    
                elif label == 'type':
                    continue
                
                elif label == 'comment':
                
                    value_string = string.join(values, '\n ')
                    variable_to_add.setncattr(label, value_string)
            
                # just need to add in other translations from badc-csv to cf names in here...
                
                                
                else:

                    value_string = string.join(values, ', ')
                    variable_to_add.setncattr(label, value_string)
            
                
                
                
        print(ncfile_obj)
                      

class BADCTextFileError(Exception): pass
class BADCTextFileParseError(BADCTextFileError): pass #basic conform to format
class BADCTextFileDataError(BADCTextFileError): pass #wrong shape data
class BADCTextFileMetadataInvalid(BADCTextFileError): pass #wrong args for md
class BADCTextFileMetadataIncomplete(BADCTextFileError): pass #mandatory fields not included
class BADCTextFileMetadataNonstandard(BADCTextFileError): pass #values not in std lists


if __name__ == "__main__":
    fh = open('xxx.csv', 'w')
    t = BADCTextFile(fh)
    d1 = (1.2, 3.4, 5.6, 5.2)
    d2 = (2.2, 4.4, 5.7, 15.2)
    
    t.add_variable("temp",d1)
    t.add_variable("hieght",d2)
    t.add_metadata('units', 'K', 1)
    t.add_metadata('Creator', 'Sam Pepler')
    t.add_metadata('Creator', ('Prof Bigshot', 'Reading uni'))
    print(t)

    fh = open('test1.csv', 'r')
    t = BADCTextFile(fh)
    print(t)
    t.check_complete(1)
    #fh = open(r'Z:\scratch\test_ncgen\test1.cdl','wb')
    fh = open(r'test1.cdl','wb')
    fh.write(t.cdl())
    fh.close()

    print()
    print(t.cvs())
    fh = open(r'test1.na','wb')
    fh.write(t.NASA_Ames())
    fh.close()

