#%%
import pandas as pd
import numpy as np
import os, sys, random, datetime, json
from collections import OrderedDict, Counter
from dotmap import DotMap #to allow specs to have a column that references keys in the hank spec via something like job.patient.addres

#a bidirectional dictionary. call dictname.inverse to make the values the keys
class bidict(dict):
    def __init__(self, *args, **kwargs):
        super(bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            if hasattr(value, '__iter__'):
                for v in value:
                    self.inverse.setdefault(v,[]).append(key)        
            else: self.inverse.setdefault(value,[]).append(key) 

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key) 
        super(bidict, self).__setitem__(key, value)
        if hasattr(value, '__iter__'):
            for v in value:
                self.inverse.setdefault(v,[]).append(key)  
        self.inverse.setdefault(value,[]).append(key)        

    def __delitem__(self, key):
        self.inverse.setdefault(self[key],[]).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]: 
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)

specials_bidict = bidict({ #line item types based upon cpt codes, for billing data mapping
    'proc-line-arterial': ['36620', '36625'],
    'proc-line-central': ['36555', '36556', '36557', '36558'],
    'proc-line-swan': ['93503'],
    'proc-tee': ['93312','93313', '93314'],
    'proc-laborepidural': ['01967'],
    'proc-epidural': ['62318','62319'],
    'ob': ['01961','01962','01967','01968'],
    'ultrasoundguidance': ['76942'],
    'proc-intubation': ['31500'],
    'proc-nerveblock': [str(x).zfill(5) for x in range(64400, 64531)],
    'primary-extremeage': ['99100'],
    'primary-hypothermia': ['99116'],
    'primary-hypotension': ['99115'],
    'primary-emergent': ['99140'],
    'primary-anesthesia': [str(x).zfill(5) for x in range(100, 1999) if x not in [1953,1996]]
    })

testj = {
            'job':{
                'claim': [
                    {
                        'entities':[
                            {'type': 'surgCPT',
                                'entityValue': '44180'
                            },
                            {'type': 'anesCPT',
                                'entityValue': '00790'
                            },
                            {'type': 'icd10',
                                'order': 1,
                                'entityValue': 'k436'
                            },
                            {'type': 'icd10',
                                'order': 2,
                                'entityValue': 'k660'
                            },
                            {'type': 'icd10',
                                'order': 3,
                                'entityValue': 't8189xa'
                            },
                            {'type': 'icd10',
                                'order': 4,
                                'entityValue': 'g8918'
                            },
                            {'type': 'modifier',
                                'order': 1,
                                'entityValue': 'qz'
                            },
                            {'type': 'modifier',
                                'order': 2,
                                'entityValue': 'p3'
                            },
                            {'type': 'providerFirst',
                                'entityValue': 'florence'
                            },
                            {'type': 'providerLast',
                                'entityValue': 'nightingale'
                            },
                            {'type': 'providerCredentials',
                                'entityValue': 'crna'
                            }         
                        ],
                        'order': 1
                    },
                    {
                        'entities':[
                            {'type': 'surgCPT',
                                'entityValue': '64488'
                            },
                            {'type': 'icd10',
                                'order': 1,
                                'entityValue': 'k436'
                            },
                            {'type': 'icd10',
                                'order': 2,
                                'entityValue': 'k660'
                            },
                            {'type': 'icd10',
                                'order': 3,
                                'entityValue': 't8189xa'
                            },
                            {'type': 'icd10',
                                'order': 4,
                                'entityValue': 'g8918'
                            },
                            {'type': 'modifier',
                                'order': 1,
                                'entityValue': '59'
                            },
                            {'type': 'providerFirst',
                                'entityValue': 'william'
                            },
                            {'type': 'providerLast',
                                'entityValue': 'osler'
                            },
                            {'type': 'providerCredentials',
                                'entityValue': 'md'
                            }         
                        ],
                        'order': 2
                    },
                    {
                        'entities':[
                            {'type': 'surgCPT',
                                'entityValue': '99140'
                            },
                            {'type': 'icd10',
                                'order': 1,
                                'entityValue': 'k436'
                            },
                            {'type': 'icd10',
                                'order': 2,
                                'entityValue': 'k660'
                            },
                            {'type': 'icd10',
                                'order': 3,
                                'entityValue': 't8189xa'
                            },
                            {'type': 'icd10',
                                'order': 4,
                                'entityValue': 'g8918'
                            },
                            {'type': 'providerFirst',
                                'entityValue': 'florence'
                            },
                            {'type': 'providerLast',
                                'entityValue': 'nightingale'
                            },
                            {'type': 'providerCredentials',
                                'entityValue': 'crna'
                            }         
                        ],
                        'order': 3
                    }

                ],
                'input': {
                    'entities': [
                        {
                            'inputType': 'text',
                            'createdTime': '2021-01-01 10:20:00',
                            'inputSource': 'SurgeryProcedureDescription',
                            'content': 'left total knee arthroplasty',
                            'inputId': 'abcde-12345-fghij-67890'
                        },
                        {
                            'inputType': 'text',
                            'createdTime': '2021-01-01 10:20:00',
                            'inputSource': 'SurgeryDiagnosisDescription',
                            'content': 'left knee degenerative arthritis and pain',
                            'inputId': 'abcde-12345-fghij-67891'
                        },
                    ]
                },
                'patientInfo': {
                    'patient': {
                        'accn': 'accn12345',
                        'dob': '1950-01-01 00:00:00',
                        'sex': 'f',
                        'first': 'patient',
                        'last': 'zero',
                        'middle': 'number',
                        'mrn': 'mrn1000003',
                        'ssn': '111-22-3333',
                        'phone': [
                            {
                                'number': '904-438-4265',
                                'type': 'mobile'
                            },
                            {
                                'number': '888-888-8888',
                                'type': 'work'
                            }
                        ],
                        'address': [
                            {
                                'street1': '808 lady street',
                                'city': 'columbia',
                                'state': 'sc',
                                'zip': '29201'
                            }
                        ]

                    },
                    'insurance': [
                        {
                            'company': 'bcbs sc',
                            'groupId': 'aa11111111',
                            'priority': '1'
                        },
                        {
                            'company': 'medicare advantage',
                            'groupId': 'z22222222z',
                            'priority': '2'
                        }
                    ]

                },
                'careTeam': [
                    {
                        'providerFirst': 'william',
                        'providerLast': 'osler',
                        'providerId': '5551',
                        'role': 'AnesSupervisor',
                        'startTime': '2021-01-01 11:00:00',
                        'endTime': '2021-01-01 13:23:10'
                    },
                    {
                        'providerFirst': 'florence',
                        'providerLast': 'nightingale',
                        'providerId': '3331',
                        'role': 'CRNA',
                        'startTime': '2021-01-01 11:00:00',
                        'endTime': '2021-01-01 13:23:10'
                    }
                ],
                'facility': {
                    'name': 'best surgery center',
                    'type': 'outpatient',
                    'code': 'bsc01',
                    'timeZone': 'EST'
                },
                'jobInfo': {
                    'encounterNumber': 'encn1001',
                    'anesType': 'spinal',
                    'asaps': '3',
                    'emergent': '0',
                    'anesStartTime': '2021-01-01 11:00:00',
                    'anesEndTime': '2021-01-01 13:23:10',
                    'ORsuite': 'or 3',
                    'OrsuiteId': 'or3'
                }
            }
        }

testjstr = """
{
    "job": {
      "claim": [
        {
          "entities": [
            {
              "type": "surgCPT",
              "entityValue": "44180"
            },
            {
              "type": "anesCPT",
              "entityValue": "00790"
            },
            {
              "type": "icd10",
              "order": 2,
              "entityValue": "k436"
            },
            {
              "type": "icd10",
              "order": 1,
              "entityValue": "k660"
            },
            {
              "type": "icd10",
              "order": 3,
              "entityValue": "t8189xa"
            },
            {
              "type": "icd10",
              "order": 4,
              "entityValue": "g8918"
            },
            {
              "type": "modifier",
              "order": 1,
              "entityValue": "qz"
            },
            {
              "type": "modifier",
              "order": 2,
              "entityValue": "p3"
            },
            {
              "type": "providerFirst",
              "entityValue": "florence"
            },
            {
              "type": "providerLast",
              "entityValue": "nightingale"
            },
            {
              "type": "providerCredentials",
              "entityValue": "crna"
            }
          ],
          "order": 1
        },
        {
          "entities": [
            {
              "type": "surgCPT",
              "entityValue": "64488"
            },
            {
              "type": "icd10",
              "order": 1,
              "entityValue": "k436"
            },
            {
              "type": "icd10",
              "order": 2,
              "entityValue": "k660"
            },
            {
              "type": "icd10",
              "order": 3,
              "entityValue": "t8189xa"
            },
            {
              "type": "icd10",
              "order": 4,
              "entityValue": "g8918"
            },
            {
              "type": "modifier",
              "order": 1,
              "entityValue": "59"
            },
            {
              "type": "providerFirst",
              "entityValue": "william"
            },
            {
              "type": "providerLast",
              "entityValue": "osler"
            },
            {
              "type": "providerCredentials",
              "entityValue": "md"
            }
          ],
          "order": 2
        },
        {
          "entities": [
            {
              "type": "surgCPT",
              "entityValue": "99140"
            },
            {
              "type": "icd10",
              "order": 1,
              "entityValue": "k436"
            },
            {
              "type": "icd10",
              "order": 2,
              "entityValue": "k660"
            },
            {
              "type": "icd10",
              "order": 3,
              "entityValue": "t8189xa"
            },
            {
              "type": "icd10",
              "order": 4,
              "entityValue": "g8918"
            },
            {
              "type": "providerFirst",
              "entityValue": "florence"
            },
            {
              "type": "providerLast",
              "entityValue": "nightingale"
            },
            {
              "type": "providerCredentials",
              "entityValue": "crna"
            }
          ],
          "order": 3
        }
      ],
      "input": {
        "entities": [
          {
            "inputType": "text",
            "createdTime": "2021-01-01 10:20:00",
            "inputSource": "SurgeryProcedureDescription",
            "content": "left total knee arthroplasty",
            "inputId": "abcde-12345-fghij-67890"
          },
          {
            "inputType": "text",
            "createdTime": "2021-01-01 10:20:00",
            "inputSource": "SurgeryDiagnosisDescription",
            "content": "left knee degenerative arthritis and pain",
            "inputId": "abcde-12345-fghij-67891"
          }
        ]
      },
      "patientInfo": {
        "patient": {
          "accn": "accn12345",
          "dob": "1950-01-01 00:00:00",
          "sex": "f",
          "first": "patient",
          "last": "zero",
          "middle": "midname",
          "mrn": "mrn1000003",
          "ssn": "111-22-3333",
          "phone": [
            {
              "number": "9044384265",
              "type": "mobile"
            }
          ],
          "address": [
            {
              "street1": "808 lady street",
              "city": "columbia",
              "state": "sc",
              "zip": "29201"
            }
          ]
        },
        "guarantor": [
          {
            "first": "momma",
            "last": "bear",
            "phone": [
              {
                "number": "9044384265",
                "type": "mobile"
              }
            ],
            "address": [
              {
                "street1": "808 lady street",
                "city": "columbia",
                "state": "sc",
                "zip": "29201"
              }
            ]
          }
        ],
        "insurance": [
          {
            "company": "bcbs sc",
            "groupId": "aa11111111",
            "priority": "2"
          },
          {
            "company": "medicare advantage",
            "groupId": "z22222222z",
            "priority": "1"
          }
        ]
      },
      "careTeam": [
        {
          "providerFirst": "william",
          "providerLast": "osler",
          "providerId": "5551",
          "role": "AnesSupervisor",
          "startTime": "2021-01-01 11:00:00",
          "endTime": "2021-01-01 13:23:10"
        },
        {
          "providerFirst": "florence",
          "providerLast": "nightingale",
          "providerId": "3331",
          "role": "CRNA",
          "startTime": "2021-01-01 11:00:00",
          "endTime": "2021-01-01 13:23:10"
        },
        {
          "providerFirst": "ivanna",
          "providerLast": "cut",
          "providerCredentials": "DO",
          "role": "Surgeon"
        }
      ],
      "facility": {
        "name": "best surgery center",
        "type": "outpatient",
        "code": "bsc01",
        "timeZone": "EST"
      },
      "jobInfo": {
        "encounterNumber": "encn1001",
        "anesType": "spinal",
        "asaps": "3",
        "emergent": "0",
        "anesStartTime": "2021-01-01 11:00:00",
        "anesEndTime": "2021-01-01 13:23:10",
        "ORsuite": "or 3",
        "OrsuiteId": "or3"
      }
    }
  }
      """

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
        except IOError: #Exception as e:
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
hde.jobdm.claim[0].entitiesGrouped


