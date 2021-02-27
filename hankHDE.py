#%%
import pandas as pd
import numpy as np
import os, sys, random, datetime, json
from collections import OrderedDict, Counter
from dotmap import DotMap #to allow specs to have a column that references keys in the hank spec via something like job.patient.addres

from include.defs import *

class HankHDE():
    def __init__(self):
        self.job = None
        self.jobdm = DotMap()
        self.claimdf = pd.DataFrame()
        self.icd10s = []
        self.dtformat = "%Y-%m-%d %H:%M:%S" #the datetime string format used throughout the hank spec
    
    #jstring is a json formatted string
    def loadFromJSON(self, jstring, addAnesthesiaFields=True):
        try:
            self.job = json.loads(jstring).get('job')
            self.claimdf = pd.DataFrame()

            #create a simple df that contains the entities in the claim entities list, maintaining passed order as order and inferred order as lineitemidx
            for lix, li in enumerate(self.job.get('claim', [])):
                entdf = pd.DataFrame(li.get('entities', []))
                entdf['lineitemidx'] = lix
                entdf['order'] = entdf['order'].fillna(1).astype(int) #set default order of entity to 1 if not set
                self.claimdf = pd.concat([self.claimdf, entdf]).reset_index(drop=True)
            self.claimdf = self.claimdf.sort_values(by=['lineitemidx','type','order'], ascending=[True, True, True])

            #now let's merge the entityValue fields, maintaining passed order, into a list in a column entityValues
            grouped_claimdf = self.claimdf.groupby(['lineitemidx', 'type'])['entityValue'].apply(np.array).reset_index().rename(columns={'entityValue':'entityValues'}) #agg({'entityValue':lambda x: [x]}))
            #now let's merge dump this back into the job dict creating a new key for each line item containing the dict, called 'entitiesGrouped'
            for grp, item in grouped_claimdf.groupby('lineitemidx'):
              self.job['claim'][grp]['entitiesGrouped'] = dict(zip(item['type'], item['entityValues'])) #making a dict with type the key, entityValues the value
            self.jobdm = DotMap(self.job)
            if addAnesthesiaFields: self.addAnesthesiaFields()
        except Exception as e:
            print("Error loading json. ({})".format(e))    

    #add a few custom fields that make mapping from other systems easier for anesthesia case types and claims
    def addAnesthesiaFields(self):
        self.job['icd10s'] = self.claimdf[self.claimdf['type']=='icd10']['entityValue'].value_counts().keys().to_list() #makes sure the icds are ordered most frequest to least from the lineitems
        self.job['modifiers'] = self.claimdf[self.claimdf['type']=='modifier']['entityValue'].value_counts().keys().to_list() #makes sure the icds are ordered most frequest to least from the lineitems
        
        for tm in self.job.get('careTeam'):
            if tm.get('role').lower()=='surgeon':
                self.job['surgeonFirst']=tm.get('providerFirst')
                self.job['surgeonLast']=tm.get('providerLast')
                self.job['surgeonId']=tm.get('providerId')

        self.jobdm = DotMap(self.job)

    #get a sample json string representing a job in the hank.ai format
    def sampleJSON(self):
        return testjstr #json.dumps(testj, indent=2)



########################################
########### USAGE EXAMPLES #############
########################################

#instatiate the object
hde = HankHDE()
#hde.loadFromJSON(json.dumps(testj))
#load a json string (testjstr is hardcoded as an example in this file above)
hde.loadFromJSON(testjstr, addAnesthesiaFields=1)
#view the job dictionary
hde.job
#view the gruoped claim line items as a dict
hde.job['claim'][0]['entitiesGrouped']
#view the grouped claim line items as a dotmap
dict(hde.jobdm.claim[0].entitiesGrouped)


# %%
