[![doc](https://img.shields.io/badge/-Documentation-blue)](https://advestis.github.io/addetect)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

#### Status
[![pytests](https://github.com/Advestis/addetect/actions/workflows/pull-request.yml/badge.svg)](https://github.com/Advestis/addetect/actions/workflows/pull-request.yml)
[![push-pypi](https://github.com/Advestis/addetect/actions/workflows/push-pypi.yml/badge.svg)](https://github.com/Advestis/addetect/actions/workflows/push-pypi.yml)
[![push-doc](https://github.com/Advestis/addetect/actions/workflows/push-doc.yml/badge.svg)](https://github.com/Advestis/addetect/actions/workflows/push-doc.yml)

![maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
[![issues](https://img.shields.io/github/issues/Advestis/addetect.svg)](https://github.com/Advestis/addetect/issues)
[![pr](https://img.shields.io/github/issues-pr/Advestis/addetect.svg)](https://github.com/Advestis/addetect/pulls)


#### Compatibilities
![ubuntu](https://img.shields.io/badge/Ubuntu-supported--tested-success)
![unix](https://img.shields.io/badge/Other%20Unix-supported--untested-yellow)

![python](https://img.shields.io/pypi/pyversions/addetect)


##### Contact
[![linkedin](https://img.shields.io/badge/LinkedIn-Advestis-blue)](https://www.linkedin.com/company/advestis/)
[![website](https://img.shields.io/badge/website-Advestis.com-blue)](https://www.advestis.com/)
[![mail](https://img.shields.io/badge/mail-maintainers-blue)](mailto:pythondev@advestis.com)

# addetect


## Installation

```

```

## Usage


Ce package permet de trouver les outliers d'une série, à partir de différentes méthodes.  
De plus, il permet aussi d'avoir de nombreux information sur la série

```python
import pandas as pd
from addetect.detector import Detector

serie = pd.Series([1,2, 3], index = pd.date_range(start='2022-01-01', end="2022-01-03"))
detector = Detector(serie)
outliers = Detector._standard_deviation()
```