# Ceasium

A hassle free JSON based C build system.

**_I have developed this on 2023-10-15 by myself. I have only minimally used it myself. It most likely still does not support some critical features for serious C development_**

## Introduction

I like programming in C, but I hate Makefiles and CMake. It takes an effort to learn and they do not have an intuitive syntax so I keep having to look up how to use them. In addition to this, they are quite time consuming to setup. I do admit, they are extremely configurable and portable. However, rarely do I need anything complicated. So I created Ceasium, which is very simple C uild system.

It works by creating compiler commands and running them in console. It uses pkg-config to add the correct flags for libraries you list in the build file.

## Installation

```
pip install ceasium
```

## Prerequisites

- Python
- C compiler
- pkg-config (usually installed by default on all Linux distros, incase of Windows MSYS2 should have it for MACs `brew install pkg-config`).

## Usage

Ceasium provides these commands:

```c
ceasium init // Creates an empty c project
ceasium install // installs libraries defined in build.json
ceasium build // Builds .exe (default), .a or .dll based on configuration
ceasium run // Runs the built exe file
ceasium clean // Removes entire build directory
```

Arguments

All commands:

`--path=<project-root-path>`

Path to project root.

## Configuration

Example config:

```json
{
  "name": "myapp",
  "type": "exe",
  "compiler": "gcc",
  "libraries": ["opengl32", "glew32", "glfw3", "SDL2"],
  "package-manager": "pacman",
  "WarningsAsErrors": false,
  "OptimizationLevel": 3,
  "packages": {
    "pacman": [
      "pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-glew",
      "pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-SDL2",
      "pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-glfw"
    ],
    "apt": [
      "sudo apt-get install -y libglew-dev",
      "sudo apt-get install -y libglfw3",
      "sudo apt-get install -y libglfw3-dev",
      "sudo apt-get install -y libglfw3"
    ]
  }
}
```

## Future Improvements

Thinking about what could ceasium use to be better a few things come to mind:

- Do not rebuild unchanged files
- Package management. Adding pacman, apt lines might get tedious. Something like `ceasium install glew32` would be nice. For this an index would need to be maintained which maps the name `glew32` to a valid apt or pacman package.
- Time for usage. I will be frank here - I have developed this on 2023-10-15, this needs to get more usage before I can know what is bad what is good and what needs to change.

## Support

If you would like to support here's a link for that.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/EvaldasZmitra)
