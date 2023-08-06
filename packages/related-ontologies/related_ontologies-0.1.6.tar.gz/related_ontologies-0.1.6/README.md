<div id="top"></div>

[![Python](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://colab.research.google.com/)

[![DOI](https://zenodo.org/badge/515409655.svg)](https://zenodo.org/badge/latestdoi/515409655)



<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h3 align="center">Related Clinical Ontologies</h3>

  <p align="center">
A package to suggest related clinical ontologies    <br />
    (LOINC, SNOMED-CT, etc.)
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about">About</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#requirements">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
</ol>
</details>



<!-- ABOUT THE PROJECT -->
## About
...

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

...


<p align="right">(<a href="#top">back to top</a>)</p>


### Requirements

The package requires the following to run:

* [Pandas][pandas]~=1.4.2
* [NumPy][numpy]~=1.22.3
* [SciPy][scipy]~=1.7.3
* [Scikit-learn][sklearn]~=1.1.1
* [PyYAML][pyyaml] >= 6.0
* [Ftfy][ftfy] >= 6.1.1
* [Fuzzywuzzy][fuzzywuzzy] >= 0.18.0
* [Jaro-Winkler][jaro] >= 2.0.0

All packages are listed in ```requirements.txt```.


<p align="right">(<a href="#top">back to top</a>)</p>


### Installation
   ```sh
   pip install related_ontologies
   ```

<p align="right">(<a href="#top">back to top</a>)</p>




## Usage

```
import related_ontologies
```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the [MIT][mit] License.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* Alistair Johnson, DPhil | The Hospital for Sick Children

<p align="right">(<a href="#top">back to top</a>)</p>


[sklearn]: https://scikit-learn.org/stable/install.html

[pandas]: https://pandas.pydata.org/docs/getting_started/install.html

[numpy]: https://numpy.org/install/

[scipy]: https://scipy.org/install/

[ftfy]: https://pypi.org/project/ftfy/

[pyyaml]: https://pypi.org/project/PyYAML/

[fuzzywuzzy]: https://pypi.org/project/fuzzywuzzy/

[jaro]: https://pypi.org/project/jaro-winkler/

[mit]: https://opensource.org/licenses/MIT