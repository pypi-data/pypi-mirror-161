# coppertop-bones-demo

Examples written in Jupyter. 

Use this - https://nbviewer.jupyter.org - if github doesn't render properly. 

E.g. https://nbviewer.jupyter.org/github/DangerMouseB/examples/blob/main/think%20bayes/Ch%201%2C2%2C3%20-%20models.ipynb

<br>

#### Notebook dependencies and coppertop

I usually have matplotlib, plotnine, numpy, pandas, scipy, pymc3, etc, installed.

Install coppertop-xxx via `python -m pip install coppertop-xxx`. This also installs coppertop-xxx.

Clone https://github.com/DangerMouseB/coppertop-xxx to get the lastest verson of all three.

At the top of each notebook you'll find a cell that includes the following:

```
from dm.std import ensurePath
'/Users/david/repos/github/DangerMouseB/coppertop/src/dm' >> ensurePath       # <= set this to your path
```

The notebook should be good to go.

