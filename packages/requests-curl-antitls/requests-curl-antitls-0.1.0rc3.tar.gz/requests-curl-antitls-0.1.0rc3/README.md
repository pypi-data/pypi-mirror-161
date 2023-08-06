# requests which pass through tls

### 安装
- pip install requests-curl-antitls
- 执行以下脚本

```python
# 如果有多个虚拟环境，刚才哪个python安装的curl，就用哪个python执行这个
import sys
import os

base = os.path.join(sys.prefix, "lib", "libcurl-impersonate-chrome.so")

with open(base, "rb") as inp, open("/usr/lib/libcurl-impersonate-chrome.so.4","wb") as out:
    data = inp.read()
    out.write(data)
```