
import pandas as pd
from datetime import datetime, timedelta
from dotmap import DotMap
import json, copy
from collections import defaultdict

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from hankHDE import HankHDE
from include.defs import specials_bidict
from include.utils import bidict, cutOrPad

#############################
# move these mappings of provider and facility mappings to customer's ids 
# into a loadable csv or something similar

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

class NeptuneInterface():
    def __init__(self):
        self.data = None
        self.hde = HankHDE()
        self.fspecdf = pd.DataFrame() #fields spec
        self.hspecdf = pd.DataFrame() #headers spec
        self.aspecdf = pd.DataFrame() #appendix spec

    #jstring is a json formatted string, clearing any existing values in self from a prior loaded spec
    def loadHankJSON(self, jstring):
        f,h,a = self.fspecdf, self.hspecdf, self.aspecdf
        self.__init__()
        if jstring != '': 
            self.hde.loadFromJSON(jstring)
        self.fspecdf = f
        self.hspecdf = h
        self.aspecdf = a

        #need to map provider names to interface provider Ids and facility name to interface facility Ids
        for x, claim in enumerate(self.hde.jobdm.claim):
            p = claim.entitiesGrouped.providerFirst[0]+claim.entitiesGrouped.providerLast[0]+claim.entitiesGrouped.providerCredentials[0]
            pid = providerMap.get(p.lower(), p)
            #print(p, pid)
            self.hde.jobdm.claim[x].entitiesGrouped.interfaceProviderId=[pid]
        self.hde.jobdm.facility.interfaceFacilityId = facilityMap.get(self.hde.jobdm.facility.code, self.hde.jobdm.facility.code)
   
    #loads 3 tables from xlsfilepath representing the field definitions, header definitions, and appendix definitions
    def loadSpec(self, xlsfilepath, sheets={'fields': 'FIELDS','headers':'HEADERS', 'appendix':'APPENDIX'}):
        self.fspecdf = pd.read_excel(xlsfilepath, sheet_name=sheets.get('fields'))
        self.fspecdf['length'] = self.fspecdf['length'].fillna(0).astype(int) #in case you have blank rows that load nan and thus force this col to float
        self.fspecdf['fieldMandatory'] = self.fspecdf['fieldMandatory'].fillna('').astype(str) #in case you have blank rows that load nan
        self.fspecdf['appendixMap'] = self.fspecdf['appendixMap'].fillna('').astype(str) #in case you have blank rows that load nan 
        self.hspecdf = pd.read_excel(xlsfilepath, sheet_name=sheets.get('headers'))
        self.aspecdf = pd.read_excel(xlsfilepath, sheet_name=sheets.get('appendix'))
    
    #convert currently loaded hank.ai job to a single painted import
    def convertFromHank(self):
        return ''
    
    #convert multiple hank.ai jobs into a single painted import file
    def convertFromHankBatch(self, jsonstringlist):
        return {}


    

if 0:
    ########################################
    ########### USAGE EXAMPLES #############
    ########################################
    neptunespecfp = ''

    #instantiate the object
    iface = NeptuneInterface()
    #load the spec with mappings to your (i.e. hank's) fields
    iface.loadSpec(xlsfilepath=neptunespecfp)


    #############################
    ## PROCESS A SINGLE RECORD ##
    #############################
    #process a SINGLE hank job json and get the ascii contents of a file to import
    sji = iface.hde.sampleJSON() #get an example json from the hankHDE class
    iface.loadHankJSON(sji)
    iface.convertFromHank()


    #######################################
    ## PROCESS MULTIPLE RECORDS AS BATCH ##
    #######################################
    #process MULTIPLE (i.e. batch) hank job jsons at once and return a dict, grouped with keys representing unique facility codes, 
    #  of ascii strings to be written to file 
    exjsonfiles = [
        '../_hankSpecExamples/example.json', 
        '../_hankSpecExamples/example2.json',
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

    outdict = iface.convertFromHankBatch(jsonstringlist=jsonstrings)

    print("Writing painted import file outputs ...")
    for fac, content in outdict.items():
        outfilename='neptuneimport_{}.txt'.format(fac)
        with open(outfilename, 'w') as f:
            print(" -> writing {}".format(outfilename))
            f.write(content)
    print("DONE.")