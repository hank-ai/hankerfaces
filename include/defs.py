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
