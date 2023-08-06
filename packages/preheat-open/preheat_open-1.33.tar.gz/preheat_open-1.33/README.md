# PreHEAT Open Python Package

This is the open Python package to consume Neogrids REST API.

For a quick introduction to how to use it on real-world data, see the [**quick start guide**](https://gitlab.com/neogrid-technologies-public/preheat-open-python/-/blob/master/docs/source/tutorials/demo.ipynb).

## Installation and configuration

### Simple installation:
Install the package directly from [PyPi](https://pypi.org/project/preheat-open/) using:

    pip install preheat_open



### Configuring the toolbox
First, make sure that you have created an API key for your user. This can be done on your [user profile page](https://app.neogrid.dk/icebear/#!/app/user/profile) in the PreHEAT App.

Now, you can store the API key in a configuration file. This user configuration file should be created in the following places:

| OS      | User level (recommended)                  | Machine level                  |  
|---------|-------------------------------------------|--------------------------------|
| Windows | C:/Users/[your user]/.preheat/config.json | (unsupported)                  |
| Linux   | ~/.preheat/config.json                    | /etc[/opt]/preheat/config.json |

The configuration files are read in the following priority order (using the first available):

1- User level

2- Machine level (Linux only): */etc/opt/preheat/config.json*

3- Machine level (Linux only): */etc/preheat/config.json*

And then add the following content in this file (adjusting with your API key):


```
{
  "PREHEAT_API_KEY": "YOUR_API_KEY_HERE"
}
```

Alternatively, you can also just import it explicitly in your code using the following command in your code 
(this is however not recommended, as you risk compromising your API key when sharing your code with others) :

```
from preheat_open import set_api_key

set_api_key("YOUR_API_KEY_HERE")
```

## Additional Information
You can find additional information about the [PreHeat API here](https://neogrid-technologies.gitlab.io/neogrid-api/).

## Contributions

We encourage pull requests if you have developed new interesting features.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
