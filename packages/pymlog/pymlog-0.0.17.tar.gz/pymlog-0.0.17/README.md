# MLog

A minimal logging utility for machine learning experiments.

## Installation

```
pip install mlog
```

## Logging

```python3
import mlog
import random

CONFIG = {'num_epochs': 100}

# Create a new run with an associated configuration
run = mlog.start(run='run_name', config=CONFIG, save='train.py')

# Log seamlessly
for epoch in range(CONFIG['num_epochs']):
    loss = random.random() * (1.05 ** (- epoch))
    run.log(epoch=epoch, loss=loss)
    metric = random.random()
    run.log(epoch=epoch, metric=metric)
```

## Quick preview

```sh
mlog plot epoch loss --group
mlog plot epoch loss --group --aggregate median
mlog plot epoch loss --group --aggregate median --intervals max
mlog plot loss metric --scatter
```

## Plotting

```python3
import matplotlib.pyplot as plt
import pandas as pd

# Retrieve data
df = mlog.get('epoch', 'loss')
df = df.groupby('epoch').aggregate(['mean', 'min', 'max'])

# Plot data
fig, ax = plt.subplots()
ax.plot(df.index, df.loss['mean'])
ax.fill_between(df.index, df.loss['min'], df.loss['max'], alpha=0.4)
plt.show()
```
