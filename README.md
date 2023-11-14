# Ceasium

A hassle free JSON based C build system.

**_Only tested with gcc_**

**_I have developed this on 2023-10-15 by myself. I have only minimally used it myself. It most likely still does not support some critical features for serious C development_**

## Introduction

I like programming in C, but I hate Makefiles and CMake. It takes an effort to learn and they do not have an intuitive syntax so I keep having to look up how to use them. In addition to this, they are quite time consuming to setup. I do admit, they are extremely configurable and portable. However, rarely do I need anything complicated. So I created Ceasium, which is very simple C build system.

It works by creating compiler commands and running them in console.

## Features

- It uses pkg-config to add the correct flags for libraries you list in the build file.
- Parallel compilation of into .o files
- Caching based on how .h/.c/.o modify times are.
  - When built .o modification time is set to latest .c file time or its include time. When it is built again it is checked if the new maximum modification time of .c or its include modification time is greater than the .o file modification time. If it is not - it means no recompilation is needed.
- Installation of missing packages.
  - This is achieved through defining package manager specific install commands. In the future this can be done automatically based on libraries list.

## Installation

```
pip install ceasium
```

## Prerequisites

- Python
- C compiler
- pkg-config (usually installed by default on all Linux distros, in case of Windows MSYS2 should have it for MACs `brew install pkg-config`).

## Usage

Ceasium provides these commands:

```c
ceasium init // Creates an empty c project
ceasium install // installs libraries defined in build.json
ceasium build // Builds .exe (default), .a or .dll based on configuration
ceasium clean // Removes entire build directory
```

- `init`
  - [Optional] `--path=<value>` defaults to current path
- `install`
  - [Optional] `--path=<value>` defaults to current path
  - [Required] Package manager name.
- `build`
  - [Optional] `--path=<value>` defaults to current path
- `clean`
  - [Optional] `--path=<value>` defaults to current path

## Configuration

Example config:

```json
{
  "name": "myapp",
  "type": "exe",
  "compiler": "gcc",
  "libraries": ["glew", "SDL2"],
  "flags": {
    "compiler": ["-g"],
    "linker": ["-lopengl"]
  },
  "packages": {
    "pacman": [
      "pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-glew",
      "pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-SDL2"
    ],
    "apt": [
      "sudo apt-get install -y libglew-dev",
      "sudo apt-get install -y libglfw3"
    ]
  }
}
```

- `name`: Name of the exe or library that will be built.
- `type`: ["so", "dll", "exe"] what will be built.
- `compiler`: ["gcc", "clang" ...other].
- `libraries`: A list of library names as they would be in pkg-config.
- `flags:compiler`: extra flags to be added right after compiler command.
- `flags:linker`: extra flags to be added at the end of compiler command.
- `package-manager`: package manager commands to use for `ceasium install`. The section of this name should be defined under packages.
- `packages`: list of commands for package installation based of different package managers.

## Support

If you would like to support here's a link for that.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/EvaldasZmitra)
