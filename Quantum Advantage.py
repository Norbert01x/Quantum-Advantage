import xcc
import strawberryfields as sf
import numpy as np

settings = xcc.Settings(REFRESH_TOKEN="Xanadu Cloud API key goes here")
settings.save()

connection = xcc.Connection.load()
assert connection.ping().ok


eng = sf.RemoteEngine("borealis")
device = eng.device


from strawberryfields.tdm import borealis_gbs, get_mode_indices

gate_args_list = borealis_gbs(device, modes=216, squeezing="high")
delays = [1, 6, 36]
n, N = get_mode_indices(delays)

from strawberryfields.ops import Sgate, Rgate, BSgate, MeasureFock

prog = sf.TDMProgram(N)

with prog.context(*gate_args_list) as (p, q):
    Sgate(p[0]) | q[n[0]]
    for i in range(len(delays)):
        Rgate(p[2 * i + 1]) | q[n[i]]
        BSgate(p[2 * i + 2], np.pi / 2) | (q[n[i + 1]], q[n[i]])
    MeasureFock() | q[0]

shots = 10_000
results = eng.run(prog, shots=shots, crop=True)
print(results.samples)