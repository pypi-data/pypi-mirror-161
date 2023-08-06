### 加密整个文件夹:
cd mkdocs && pyarmor obfuscate __init__.py

### 不同平台，需要分别执行，得到不同的_pytransform文件
Mac：_pytransform.dylib
Linux：_pytransform.so
Win：_pytransform.dll

### 拷贝分拣到docs/
cp mkdocs/dist/* ../docs
cp mkdocs/template ../docs
cp mkdocs/index.rst ../docs