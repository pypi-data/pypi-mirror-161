<p align="center">
    <img src="https://demattos.io/img/cargparse.svg"><br/><br/>
    Parse configuration files with <code>argparse</code>.<br/><br/>
    <a href="https://pypi.org/project/cargparse/" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/cargparse?color=lightgrey" alt="Python version">
    </a>
    <a href="https://pypi.org/project/cargparse/" target="_blank">
        <img src="https://img.shields.io/pypi/v/cargparse?color=lightgrey" alt="PyPI version">
    </a>
    <a href="https://github.com/psf/black" target="_blank">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="code style: black">
    </a>
</p>

## Supported file types

<table align="center">
    <tr>
        <td align="center" width=75px></td>
        <td align="center" width=100px>type</td>
        <td align="center" width=200px>reader</td>
        <td align="center" width=200px>third-party</td>
        <td align="center" width=400px>note</td>
    </tr>
    <tr>
        <td align="center">✅</td>
        <td align="center"><code>cfg/ini</code></td>
        <td align="center"><code><a href="https://docs.python.org/3/library/configparser.html">configparser</a></code></td>
        <td align="center">no</td>
        <td align="center">Supports custom <code>ConfigParser</code> reader</td>
    </tr>
    <tr>
        <td align="center">✅</td>
        <td align="center"><code>json</code></td>
        <td align="center"><code><a href="https://docs.python.org/3/library/json.html">json</a></code></td>
        <td align="center">no</td>
        <td align="center"></td>
    </tr>
    <tr>
        <td align="center">✅</td>
        <td align="center"><code>toml</code></td>
        <td align="center"><code><a href="https://pypi.org/project/tomli/">tomli</a></code>/<code><a href="https://docs.python.org/3.11/library/tomllib.html">tomllib</a></code></td>
        <td align="center">yes/no</td>
        <td align="center"><code>tomllib</code> is built-in from Python 3.11 and was based on <code>tomli</code></td>
    </tr>
    <tr>
        <td align="center">✅</td>
        <td align="center"><code>yaml</code></td>
        <td align="center"><code><a href="https://pypi.org/project/PyYAML/">pyyaml</a></code></td>
        <td align="center">yes</td>
        <td align="center"></td>
    </tr>
</table>

## Installation

```
pip install cargparse
```

## Basic usage

Given  `config.yaml`:

```yaml
text: hello world
number: 42
```

Use `argparse` as you normally would for command line arguments!

```python
import argparse
import cargparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--text', type=str, required=True)
parser.add_argument('--number', type=int, required=True)
parser.add_argument('--decimal', type=float)
config = cargparse.Cargparse(parser).parse_file(sys.argv[1])
```

```
python test.py config.yaml
>> config
{'text': 'hello world', 'number': 42)
>> config.text
'hello world'
>> type(config.number)
<class 'int'>
```

⚠️ Read the [documentation]() for more information about type validation.

## Advanced usage

You are not restricted to a flat hierarchy.

```yaml
model:
  lstm:
    input_size: 100
    hidden_size:
      - 128
      - 64
  summary: True
```

Define a helper function to parse each nested section `args`, which is interpreted as a dictionary `str`.

```python
from __future__ import annotations

def parse_config(filename: Path | str) -> cargparse.Namespace:

    def model_namespace(args: str) -> cargparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument('--cnn', type=cnn_namespace)
        parser.add_argument('--lstm', type=lstm_namespace)
        parser.add_argument('--summary', type=cargparse.boolean)
        return cargparse.Cargparse(parser).parse_dict(args)

    def cnn_namespace(args: str) -> cargparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument('--in_channels', type=int, required=True)
        parser.add_argument('--out_channels', type=int, required=True)
        parser.add_argument('--kernel_width', type=int, required=True)
        return cargparse.Cargparse(parser).parse_dict(args)

    def lstm_namespace(args: str) -> cargparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument('--input_size', type=int, required=True)
        parser.add_argument('--hidden_size', type=cargparse.list_int, required=True)
        return cargparse.Cargparse(parser).parse_dict(args)

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=model_namespace, required=True)
    return cargparse.Cargparse(parser).parse_file(filename)

if __name__ == '__main__':
    config = parse_config(filename=sys.argv[1])
```

```
>> config.model.cnn
>> config.model.lstm.hidden_units
*** AttributeError: hidden_units not in namespace: ['hidden_size', 'input_size']
>> config.model.lstm.hidden_size
[128, 64]
```

⚠️ Read the [documentation]() for more information about type validation.
