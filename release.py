import re
import shutil
import subprocess
import pathlib
import glob
import sys


f = pathlib.Path('pyproject.toml')
f.write_text(re.sub(
    r"version\s*=\s*'(\d+)\.(\d+)\.(\d+)'",
    lambda m: f"version = '{m[1]}.{m[2]}.{int(m[3]) + 1}'",
    f.read_text(encoding='utf-8'),
    count=1
), encoding='utf-8')

shutil.rmtree('docs', ignore_errors=True)
shutil.rmtree('dist', ignore_errors=True)

subprocess.run(['pdoc', 'src/rae/__init__.py', '-o', 'docs'], check=True)
subprocess.run([sys.executable, '-m', 'build'], check=True)
subprocess.run([sys.executable, '-m', 'twine', 'upload', *glob.glob('dist/*')], check=True)
