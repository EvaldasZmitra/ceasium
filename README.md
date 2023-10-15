# Ceasium

A hassle free JSON based C (gcc) build system.

## Introduction

I like programming in C, but I hate Makefiles and CMake. It takes an effort to learn and they do not have an intuitive syntax so I keep having to look up how to use them. In addition to this, they are quite time consuming to setup. I do admit, they are extremely configurable and portable. However, rarely do I need anything complicated. So I created Ceasium, which is very simple C gcc build system.

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
