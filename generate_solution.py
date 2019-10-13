from planpath import *
from pathlib import Path
import math
import numpy as np
from generate_testcase import config
input_dir = Path('./INPUT')
output_dir = Path('./OUTPUT')


# input_dir = Path(config['output_dir'])
# output_dir = Path('generated_output')
output_dir.mkdir(exist_ok=True)
maps = [Map(i) for i in input_dir.glob('*')]

solutionD = []
solutionA= []
for m in maps:
    solutionD.append(graphsearch(m, 0, 'D'))
    solutionA.append(graphsearch(m, 0, 'A'))
result = list(zip(maps, solutionD, solutionA))
for i in range(len(result)):
    print("For test case\n{i}\nMap: {0}\nSolution for DLS: {1}\nSolution for A: {2}".format(
        *result[i], i=i+1))
