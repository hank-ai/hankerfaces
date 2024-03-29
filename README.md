<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo_name, twitter_handle, email, project_title, project_description
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/hank-ai/hankerfaces">
    <img src="https://hank.ai/images/logo-bordered.png" alt="Logo" width="141" height="54">
  </a>

  <h3 align="center">Hankerfaces</h3>

  <p align="center">
    Hank.ai Interfaces, Specs, and Conversion utilities
    <br />
    <a href="https://github.com/hank-ai/hankerfaces"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/hank-ai/hankerfaces">View Demo</a>
    ·
    <a href="https://github.com/hank-ai/hankerfaces/issues">Report Bug</a>
    ·
    <a href="https://github.com/hank-ai/hankerfaces/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#hankai-json-specification">Hank.ai Data Exchange Specification</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
    <a href="#usage">Usage</a>
     <ul>
      <li><a href="#abeo-medsuite-conversion">Abeo Medsuite</a></li>
      <li><a href="#painted-horse-international-phi-conversion">PHI (Painted Horse International)</a></li>
      <li><a href="#sierra-medlink-conversion">Sierra Medlink</a></li>
      <li><a href="#blue9-neptune-conversion">blue9 Neptune</a></li>
     </ul>
    </li>
      <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>


#
<!-- ABOUT THE PROJECT -->
## About The Project
This project includes the hank.ai data-exchange specification and examples, conversion classes (python), and resulting 3rd party import examples

### Hank.ai JSON Specification:
* [Hank-AI-BillingandHealthDataExchange-Version-02-022021.JSON](Hank-AI-BillingandHealthDataExchange-Version-02-022021.JSON) (note: best viewed as 'json with comments' in vscode)



### Built With

* [python3]()
* [hank.ai]()




<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these steps.

### Prerequisites

* python3 (recommmend using anaconda and a virtual env)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/hank-ai/hankerfaces.git
   cd hankerfaces
   ```
2. Install requirements
   ```sh
   pip install requirements.txt
   ```



<!-- USAGE EXAMPLES -->
# Usage

## Abeo Medsuite conversion

1. define file locations
```python3
medsuitespecfp = 'AbeoMedsuite/Abeo Billing Export Layout V1.3_modHank.xlsx'
```
2. import and instantiate an instance of the medsuite interface class
```python3
from AbeoMedsuite import medsuite
msi = medsuite.MedsuiteInterface()
```
3. load the medsuite spec with mappings to hank.ai fields
```python3
msi.loadSpec(xlsfilepath=medsuitespecfp)
```

#
### Process a single example record
Returns the contents of the Medsuite import file (ascii string with newlines)
```python3
sji = msi.hde.sampleJSON() #get an example json from the hankHDE class
msi.loadHankJSON(sji) #load the hank.ai job json
msi.convertFromHank() #convert it to medsuite format
```
#
### Process multiple records together (i.e. batch)
_Process MULTIPLE (i.e. batch) hank job jsons at once, grouping outputs by facility code_

Load the contents of some hank.ai json examples
```python3
import json
exjsonfiles = [
    '_hankSpecExamples/example.json',
    '_hankSpecExamples/example2.json',
    '_hankSpecExamples/example3.json',
    '_hankSpecExamples/example4.json'
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
```
Convert the list of loaded json contents into a dictionary of facilitycode:medsuitefilecontents
```python3
outdict = msi.convertFromHankBatch(jsonstringlist=jsonstrings)
```

Iterate over the dictionary and write out to files
```python3
print("Writing medsuite import file outputs ...")
for fac, content in outdict.items():
    outfilename='medsuiteimport_{}.txt'.format(fac)
    with open(outfilename, 'w') as f:
        print(" -> writing {}".format(outfilename))
        f.write(content)
print("DONE.")
```
#

## Painted Horse Incorporated (PHI) conversion:
1. define file locations
```python3
phispecfp = 'PHI/spec.csv'
```
2. import and instantiate an instance of the phi interface class
```python3
from PHI import paintedhorse
phi = paintedhorse.PaintedHorseInterface()
```
### Process a single example record (hank.ai -> phi)
```
under development
```
### Process a single example record (phi -> hank.ai)
```
under development
```


## Sierra Medlink conversion:
1. define file locations
```python3
medlinkspecfp = 'medlink/spec.csv'
```
2. import and instantiate an instance of the medlink interface class
```python3
from sierra import medlink
smli = medlink.MedlinkInterface()
```
### Process a single example record (hank.ai -> medlink)
```
under development
```
### Process a single example record (medlink -> hank.ai)
```
under development
```




#

## blue9 Neptune conversion:
1. define file locations
```python3
neptunespecfp = 'blue9/spec.csv'
```
2. import and instantiate an instance of the neptune interface class
```python3
from blue9 import neptune
bni = neptune.NeptuneInterface()
```
### Process a single example record (hank.ai -> neptune)
```
under development
```
### Process a single example record (neptune -> hank.ai)
```
under development
```

#

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/hank-ai/hankerfaces/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.



<!-- CONTACT -->
## Contact

Jack Neil - [@realjackneil](https://twitter.com/realjackneil) - jack.neil@hank.ai

Project Link: [https://github.com/hank-ai/hankerfaces](https://github.com/hank-ai/hankerfaces)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [abeo](https://abeo.com)
* [phi](https://phimedos.com)
* [sierra health/medlink](https://sierrahealth.net/the-sierra-healthcare-companies/)
* [blue9](https://blueninesystems.com)





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/hank-ai/hankerfaces.svg?style=for-the-badge
[contributors-url]: https://github.com/hank-ai/hankerfaces/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/hank-ai/hankerfaces.svg?style=for-the-badge
[forks-url]: https://github.com/hank-ai/hankerfaces/network/members
[stars-shield]: https://img.shields.io/github/stars/hank-ai/hankerfaces.svg?style=for-the-badge
[stars-url]: https://github.com/hank-ai/hankerfaces/stargazers
[issues-shield]: https://img.shields.io/github/issues/hank-ai/hankerfaces.svg?style=for-the-badge
[issues-url]: https://github.com/hank-ai/hankerfaces/issues
[license-shield]: https://img.shields.io/github/license/hank-ai/hankerfaces.svg?style=for-the-badge
[license-url]: https://github.com/hank-ai/hankerfaces/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/company/hankai