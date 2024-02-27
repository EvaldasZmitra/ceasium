# Ceasium

A hassle free JSON based GCC build system.

## Introduction

C is a great language, but tooling around it like CMake or Make are a bit
complicated. While CMake is great when it comes to being able to specify a
complicated build, its syntax has a steep learning curve and is quite cumbersome
and non-intuitive. Thus I created Ceasium.

## Features

Ceasium features most of the things that are regularly needed.

- pkg-config to resolve C_FLAGS and LD_FLAGS
- Ability to specify your own C_FLAGS and LD_FLAGS
- Build executables, static and dynamic libraries
- .c file discovery within a given directory
- Caching based on modification date including dependency discovery
- Exclusion of certain .o files when linking

## Installation

```
pip install ceasium
```

## Prerequisites

- Python
- GCC compiler
- pkg-config

## Usage

Ceasium provides these commands:

- `cs init`
- `cs build`
  - [Optional] `<src.json/test.json/whatever.json>` specify which json file to build
- `cs clean`

## Configuration

Example config:

```json
{
  "name": "game-engine",
  "type": "exe",
  "cflags": [
    "-I./include",
    "-g",
    "-W",
    "-Wall",
    "-O3",
    "-fopenmp",
    "-fdiagnostics-color=always"
  ],
  "ldflags": ["-lopengl32", "-fopenmp"],
  "libs": ["glew", "sdl2", "glib-2.0", "assimp"]
}
```
