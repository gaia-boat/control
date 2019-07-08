The Gaia Boat is an autonomous boat designed to collect trash from a lake’s shore. It uses image processing to detect obstacles and trash, an app for tracing routes and a series of other embedded software for controlling the hardware.

## Other Gaia Boat’s software links

- [gaia router](https://github.com/gaia-boat/router)
- [gaia control](https://github.com/gaia-boat/control)
- [gaia app](https://github.com/gaia-boat/app)
- [gaia communication](https://github.com/gaia-boat/communication)
- [gaia image processing](https://github.com/gaia-boat/image-processing)

## The control module

### Usage and installation

#### Usage

This module is used to represent the internal state-driven machine, modeled after **Petri’s Net**, that is the core of the Gaia Boat project’s operational logic, while doing the integration between sensors, electronic components and high level software.

#### Installation

To install the package you must install if through pip, using the following command:

```shell
pip install gaia-control
```

Or adding it into your requirements file. You can see the latest version [HERE](https://pypi.org/project/gaia-control/).

If you want to upgrade its version you must use:

```shell
pip install --upgrade gaia-control
```

**Note:** this module has every other Gaia software as dependency, the only exception is the mobile app.