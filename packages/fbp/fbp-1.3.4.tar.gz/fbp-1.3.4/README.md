# BuildPy: A Build System for only C, C++
written in Python

# Usage
install pip module:
```
pip install fbp
```

then create file with named <project-name>.buildpy in your C/C++ project <br>
run command `fbp <project-name>` when build

# Example
```
folders {
  include = include
  source  = src
}

build {
  .fast = true
  .use_glob = true
  .no_overwrite = copy_folder

  compiler {
    c   = clang
    cpp = clang++
  }

  extensions {
    c   = c
    cpp = cc cxx cpp
  }

  flags {
    opti  = -O2
    c     = $opti -Wno-switch -Wimplicit-fallthrough
    cpp   = $c -std=c++20
    link  = -Wl,--gc-sections
  }

  objects_folder = build
  linker = $compiler.cpp
}
```

# Contribute
welcome!
