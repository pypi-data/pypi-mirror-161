![](https://fastly.jsdelivr.net/gh/gpchn/my-netdisk-on-github-pages@main/image/1659073774591colorout.png)

# Colorout
An easy tool to print with random colors. Made by Python.  
Available on pypi.

## Table of contents
- [Beginning](#colorout)
- [Install](#install)
- [Usage](#usage)
- [Maintainers](#maintainers)
- [License](#license)

## Install
This project uses Python3.10.5  
You can run it with any [python3](https://python.org/downloads/).
Use pip to install:
```
pip install colorout
```

## Usage
```python3
# Import the colorout module.
import colorout
# Use its function: colorout.
# Print the text with a random color.
colorout.colorout("Some text")

from colorama import Fore
# Use its function: colorget.
# Colorget: get a random color.
# Fore.RESET: reset using the color to print.
print(colorout.colorget() + "Some text" + Fore.RESET)

# Use its function: anycolorout.
# anycolorout: choose a color and print with it.
colorout.anycolorout("Some text", "green")

# Use its functions: infoout, warningout, errorout.
# infoout: for print info text. (print text with blue)
colorout.infoout("Some info")
# warningout: (yellow)
colorout.warningout("Some warnings")
# errorout: (red)
colorout.errorout("Some errors")
```

## Maintainers
[@Gpchn](https://github.com/gpchn)

## License
[Apache-2.0](https://github.com/gpchn/colorout/blob/main/LICENSE)©Gpchn