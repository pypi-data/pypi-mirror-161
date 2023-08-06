# 开发者注意事项
由于使用了numba，在m1 mac上，需要使用homebrew安装llvm@11，然后指定'''export LLVM_CONFIG=/opt/homebew/opt/llvm@11/bin/llvm-config'''，否在会卡在llvmlite安装上报错。