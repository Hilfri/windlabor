import numpy as np

x = np.linspace(0, 2*np.pi, 100000)
x = np.sin(x)
rms = np.sqrt(np.mean(np.square(x)))
print(rms)
print(1/np.sqrt(2))
