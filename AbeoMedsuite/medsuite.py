#%%

import pandas as pd
from datetime import datetime, timedelta
from dotmap import DotMap
import json, copy
from collections import defaultdict

#############################
# move these mappings of provider and facility mappings to customer's medsuite ids 
# into a loadable csv or something like that before go live

#the provider mapping is based upon first name, last name, and credentials concatenated together and lowercase
providerMap = {
    'florencenightingalecrna': 'msfncrna',
    'williamoslermd': 'mswomd'
}
#the facility mapping is based upon the facility.code
facilityMap = {
    'bsc01': 'msbsc01',
    'bsc02': 'msbsc02'
}
##############################

class MedsuiteInterface():
    def __init__(self):
        self.data = None
        self.hde = HankHDE()
        self.rH = ''
        self.r01 = ''
        self.r02 = []
        self.r03 = ''
        self.r04 = []
        self.r05 = []
        self.r06 = []
        self.r07 = []
        self.rT = ''
        self.rowCount = 0
        self.fspecdf = pd.DataFrame() #fields spec
        self.hspecdf = pd.DataFrame() #headers spec
        self.aspecdf = pd.DataFrame() #appendix spec

    #copies self to a new object but DOES NOT copy the calculated .r* items
    def duplicate(self):
        newmsi = MedsuiteInterface()
        newmsi.fspecdf = self.fspecdf.copy()
        newmsi.hspecdf = self.hspecdf.copy()
        newmsi.aspecdf = self.aspecdf.copy()
        newmsi.hde = copy.copy(self.hde)
        return newmsi
    
    #jstring is a json formatted string, clearing any existing values in self from a prior loaded spec
    def loadHankJSON(self, jstring):
        f,h,a = self.fspecdf, self.hspecdf, self.aspecdf
        self.__init__()
        if jstring != '': 
            self.hde.loadFromJSON(jstring)
        self.fspecdf = f
        self.hspecdf = h
        self.aspecdf = a

        #need to map provider names to medsuite provider Ids and facility name to medsuite facility Ids
        for x, claim in enumerate(self.hde.jobdm.claim):
            p = claim.entitiesGrouped.providerFirst[0]+claim.entitiesGrouped.providerLast[0]+claim.entitiesGrouped.providerCredentials[0]
            pid = providerMap.get(p.lower())
            #print(p, pid)
            self.hde.jobdm.claim[x].entitiesGrouped.medsuiteProviderId=[pid]
        self.hde.jobdm.facility.medsuiteFacilityId = facilityMap.get(self.hde.jobdm.facility.code, 'NOMAPPING')

   
    #loads 3 tables from xlsfilepath representing the field definitions, header definitions, and appendix definitions
    def loadMedsuiteSpec(self, xlsfilepath, sheets={'fields': 'FIELDS','headers':'HEADERS', 'appendix':'APPENDIX'}):
        self.fspecdf = pd.read_excel(xlsfilepath, sheet_name=sheets.get('fields'))
        self.fspecdf['length'] = self.fspecdf['length'].fillna(0).astype(int) #in case you have blank rows that load nan and thus force this col to float
        self.fspecdf['fieldMandatory'] = self.fspecdf['fieldMandatory'].fillna('').astype(str) #in case you have blank rows that load nan
        self.fspecdf['appendixMap'] = self.fspecdf['appendixMap'].fillna('').astype(str) #in case you have blank rows that load nan 
        self.hspecdf = pd.read_excel(xlsfilepath, sheet_name=sheets.get('headers'))
        self.aspecdf = pd.read_excel(xlsfilepath, sheet_name=sheets.get('appendix'))
    
    #el is an element dictionary, representing a row in the medsuite spec table
    #returns a tuple containing element length, fieldName, mandatory flag, hankspecmap, dtformatstring, appendixmap
    def _getFields(self, el): 
        elen = el.get('length')
        fn = el.get('fieldName')
        man = 1 if el.get('fieldMandatory').upper()=='M' else 0
        hsm = el.get('hankSpecMap')
        if pd.isnull(hsm): hsm = ''
        dtformat = el.get('medsuiteDtFormatStr')
        appxmap = el.get('appendixMap').upper()
        return elen, fn, man, hsm, dtformat, appxmap
    
    #will cut val (a string) to length or pad it with padchars to output a fixed length string of length length
    #cutfrom: 'right' or 'left'. will remove characters from the side stated here if string is longer than length
    #padfrom: 'right' or 'left'. will pad string with padchar from the side stated here to output a string of defined length length
    def _cutOrPad(self, val, length, cutfrom='right', padfrom='right', padchar=' '):
        if len(val)>length: 
            if cutfrom=='right': return val[:length]
            else: return val[-length:]
        elif len(val)<length:
            if padfrom=='left': return val.rjust(length, padchar)
            else: return val.ljust(length, padchar)
        return val
    
    #job is the hankspec job dotmap. optional. 
    #recordIdentifier is the section in the medsuite spec you're generating (i.e. H, 01, 02, ..., T)
    #x, y, and z can be integers referencing array values from the medsuite spec mapping
    #note: you can pass a kwargs dict value that will be filled in for any field where spec has #kwargkey
    def _evalAndClean(self, recordIdentifier, job=None, x=0, y=0, z=0, **kwargs):
        totlen = 0
        outstr = ''
        if job==None: job=self.hde.jobdm
        fields = self.fspecdf[self.fspecdf['recordIdentifier']==recordIdentifier]
        for el in fields.to_dict('records'):
            try:
                elen, fn, man, hsm, dtformat, appxmap = self._getFields(el)
                totlen += elen #used at the end to double check return length is accurate
                newstr = ''
                if hsm.find('.')==-1: 
                    if not pd.isnull(hsm) and len(hsm)>0 and hsm[0]=='#': #special situation. fill in a passed kwargs
                        newstr = str(kwargs.get(hsm[1:]))
                    else: newstr = hsm #if there are no 'dots' in the spec map then this is a hardcoded value
                else:
                    # print(hsm)
                    try:
                        tout = eval(hsm)
                        otout = tout
                    except IndexError: #if an array simply had an out of index error then continue, using empty string as value
                        tout = ''
                    if type(tout)==DotMap: tout = '' #no specific value found
                    if not pd.isnull(dtformat) and dtformat!='' and tout != '': #if a datetime format string is set in the spec, format this object using it
                        tout = datetime.strptime(tout, self.hde.dtformat).strftime(dtformat)
                    elif not pd.isnull(appxmap) and appxmap!='' and tout!='':
                        tout = self._appendixMap(tout, appxmap)
                    newstr = tout
                newstr = newstr.replace('\n', '')

            except Exception as e:
                print("Exception caught. {}".format(e))
                newstr = ''
            if newstr=='' and man: raise Exception("Field '{}' in section '{}' is mandatory but no value found via json mapping ({}={}={})".format(fn, recordIdentifier, hsm, tout, otout))
            outstr += self._cutOrPad(newstr, elen)
        
        if totlen!=len(outstr): raise Exception('{} length is not equal. Expected {} chars, got {}.'.format(recordIdentifier, totlen, len(outstr)))
        return outstr


    def _generateH(self): #header record
        outstr = self._evalAndClean('H')
        self.rH = outstr
        return outstr

    def _generate01(self): #patient info record
        outstr = self._evalAndClean('01')
        self.r01 = outstr
        return outstr

    def _generate02(self): #related person records
        outlist = []
        for x, guar in enumerate(self.hde.jobdm.patientInfo.guarantor):
            outstr = self._evalAndClean('02', x=x)
            outlist.append(outstr)
        self.r02 = outlist
        return outlist

    def _generate03(self): #case information records
        outstr = self._evalAndClean('03')
        self.r03 = outstr
        return outstr


    def _generate04(self): #guarantor records
        outlist = []
        for x, guar in enumerate(self.hde.jobdm.patientInfo.guarantor):
            outstr= self._evalAndClean('04', x=x)
            outlist.append(outstr)
        self.r04 = outlist
        return outlist

    def _generate05(self): #insurance records
        outlist = []
        self.hde.jobdm.patientInfo.insurance = sorted(self.hde.jobdm.patientInfo.insurance, key=(lambda x: x.get('priority')))
        for x, ins in enumerate(self.hde.jobdm.patientInfo.insurance):
            outstr = self._evalAndClean('05', x=x)
            outlist.append(outstr)
        self.r05 = outlist
        return outlist

    def _generate06(self): #charge records
        outlist = []
        self.hde.jobdm.claim = sorted(self.hde.jobdm.claim, key=(lambda x: x.get('order')))
        for x, claim in enumerate(self.hde.jobdm.claim):
            outstr = self._evalAndClean('06', x=x)
            outlist.append(outstr)
        self.r06 = outlist
        return outlist       


    def _generate07(self, limit=1): #anesthesia time records
        outlist = []
        self.hde.jobdm.claim = sorted(self.hde.jobdm.claim, key=(lambda x: x.get('order')))
        for x, claim in enumerate(self.hde.jobdm.claim):
            if len(outlist)>=limit: continue #sometimes the number of 07 records should be limited to a set limit
            if 'anesCPT' not in claim.entitiesGrouped.keys() or type(claim.entitiesGrouped.anesCPT)==DotMap: 
                continue #looking for anesthesia time records ONLY
            outstr = self._evalAndClean('07', x=x)
            outlist.append(outstr)
        self.r07 = outlist
        return outlist    

    def _generateT(self, rowcount=0): #trailer record
        if rowcount==0:
            if self.r01 != '': rowcount += 1
            rowcount += len(self.r02)
            if self.r03 != '': rowcount += 1
            rowcount += len(self.r04)
            rowcount += len(self.r05)
            rowcount += len(self.r06)
            rowcount += len(self.r07)
        
        outstr = self._evalAndClean('T', sumrows=rowcount)
        self.rowcount = rowcount
        self.rT = outstr
        return outstr
    
    #generate all sections of the medsuite spec
    #has no return value. stores all results in self.r*
    def _generateALL(self):
        self._generateH()
        self._generate01()
        self._generate02()
        self._generate03()
        self._generate04()
        self._generate05()
        self._generate06()
        self._generate07()
        self._generateT()

    #helper function that processes any value that had an appendix set in the spec
    def _appendixMap(self, value, appendix):
        rval = value
        if appendix=='J': rval=self._appendixMap_GetServiceType(value)
        else:
            rval = self._appendixMap_Generic(value, appendix)

        #print("appendix map {} called on {}. rval={}".format(appendix, value, rval))
        return rval

    #looksup the value in the hankMapping column of the APPENDIX spec sheet, choosing from items based upon appendixCode (A, B, C...)
    #default is the string you'd like returned if no matching value is found in the hankMapping column
    def _appendixMap_Generic(self, value, appendixCode, default=''):
        stdf = self.aspecdf[self.aspecdf['appendix']==appendixCode]
        mask = stdf['hankMapping'].apply(lambda x: any(1 for y in x.split(',') if y.strip().lower()==value.lower()) if not pd.isnull(x) else False)
        res = stdf[mask]
        if len(res)==0: return default
        else: return res['code'].iloc[0]

    #lookup the ServiceType required by medsuite based upon a given cptcode
    def _appendixMap_GetServiceType(self, cptcode, default='07'):
        stdf = self.aspecdf[self.aspecdf['appendix']=='J']
        descs = specials_bidict.inverse.get(cptcode) #lookup the cpt code in the cptcode<->special type lookup dictionary
        if descs is None or len(descs)==0: return default

        mask = stdf['hankMapping'].apply(lambda x: any(1 for y in x.split(',') if y.strip() in descs) if not pd.isnull(x) else False)
        res = stdf[mask]['code']
        if len(res)==0: return default
        else: return res.iloc[0]
    
    #returns an ascii string of all the inner items of the medsuite spec, 01...07, NOT including the header H or trailer T
    def _writeRows(self):
        outstr = ""
        if self.r01 != "": outstr += self.r01 + '\n'
        if len(self.r02)>0: outstr += '\n'.join(self.r02) + '\n'
        if self.r03 != "": outstr += self.r03 + '\n'
        if len(self.r04)>0: outstr += '\n'.join(self.r04) + '\n'
        if len(self.r05)>0: outstr += '\n'.join(self.r05) + '\n'
        if len(self.r06)>0: outstr += '\n'.join(self.r06) + '\n'
        if len(self.r07)>0: outstr += '\n'.join(self.r07) + '\n'
        return outstr

    #generates the ascii string to write to a file for import into medsuites, for a SINGLE json case input
    #assumes you've already loaded self with the hank job spec using loadHankJSON(...)
    def generateMedsuiteImport(self, generateAll=True):
        if generateAll: self._generateALL()
        else: self._generateT() #always regenerate the trailer

        outstr = self.rH + '\n'
        outstr += self._writeRows()
        outstr += self.rT + '\n'
        return outstr
    
    #medsuite can import multiple different cases in one file but ALL rows in the file MUST be for the SAME facility
    #this will return a dict of facility:medsuiteimportfileasciicontents
    def generateMedsuiteImportBATCH(self, jsonstringlist):
        facilitydicts = defaultdict(list)
        facilityoutdict = {}
        for jsonstring in jsonstringlist:
            thismsi = self.duplicate()
            thismsi.loadHankJSON(jsonstring)
            facilitydicts[thismsi.hde.jobdm.facility.medsuiteFacilityId].append(thismsi)
        #print(facilitydicts)
        #now create the rows for each of these dicts and create seperate import files for each group
        for facility, msis in facilitydicts.items():
            f_msi = msis[0].duplicate()
            totalrows = 0
            outstr = ""
            for msi in msis:
                msi._generateALL()
                outstr += msi._writeRows()
                totalrows+= msi.rowcount
            outstr = f_msi._generateH() + '\n' + outstr + f_msi._generateT(rowcount=totalrows)
            facilityoutdict[facility] = outstr
            #f_msi.rH = msis[0].rH
        return facilityoutdict






########################################
########### USAGE EXAMPLES #############
########################################
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from hankHDE import HankHDE, specials_bidict

medsuitespecfp = 'Abeo Billing Export Layout V1.3_modHank.xlsx' #'G:/Shared drives/Hank.ai - ENGINEERING/Design, Specification and Architecture/Abeo Billing Export Layout V1.3_modHank.xlsx'

#instantiate the object
msi = MedsuiteInterface()
#load the medsuite spec with mappings to your (i.e. hank's) fields
msi.loadMedsuiteSpec(xlsfilepath=medsuitespecfp)


#############################
## PROCESS A SINGLE RECORD ##
#############################
#process a SINGLE hank job json and get the ascii contents of a file to import into medsuite
sji = msi.hde.sampleJSON() #get an example json from the hankHDE class
msi.loadHankJSON(sji)
msi.generateMedsuiteImport()


#######################################
## PROCESS MULTIPLE RECORDS AS BATCH ##
#######################################
#process MULTIPLE (i.e. batch) hank job jsons at once and return a dict, grouped with keys representing unique facility codes, 
#  of ascii strings to be written to file and imported into medsuites
exjsonfiles = [
    '../_hankSpecExamples/example.json', #'g:/Shared drives/Hank.ai - ACE - SHARED/Data Exchange/example.json'
    '../_hankSpecExamples/example2.json', #'g:/Shared drives/Hank.ai - ACE - SHARED/Data Exchange/example2.json'
    '../_hankSpecExamples/example3.json',
    '../_hankSpecExamples/example4.json'
]
jsonstrings = []
print("Loading hank.ai job jsons ...")
for ejf in exjsonfiles:
    print(" -> loading {}".format(ejf))
    try:
        with open(ejf, 'r') as f:
            jsonstrings.append(json.dumps(json.load(f)))
    except Exception as e:
        print("  -> error ({})".format(e))
        print("  -> continuing ...")
print("Done loading.")

outdict = msi.generateMedsuiteImportBATCH(jsonstringlist=jsonstrings)

print("Writing medsuite import file outputs ...")
for fac, content in outdict.items():
    outfilename='medsuiteimport_{}.txt'.format(fac)
    with open(outfilename, 'w') as f:
        print(" -> writing {}".format(outfilename))
        f.write(content)
print("DONE.")

# %%
