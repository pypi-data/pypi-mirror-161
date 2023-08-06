[翻訳者募集中]

# BuildPy: 新しい簡単でシンプルなビルドスクリプト

# 使い方
あなたの c/cpp プロジェクトの中にサブモジュールとしてこのリポジトリをクローンします。<br>
そして、同じ場所に `<project-name>.buildpy` という名前で、ビルドスクリプトを用意します。<br>

# ビルド
ビルドするときに、以下のコマンドを実行します <br>
拡張子は自動で追加されるので、書く必要はありません。
```
python3 BuildPy/__main__.py <project-name>
```

# スクリプトのサンプル
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
どんなプルリクエストでも遠慮なく投稿してください！