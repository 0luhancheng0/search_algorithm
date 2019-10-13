from planpath import *
from pathlib import Path
import math
import numpy as np
config = {
    'size' : (9, 10),
    'obstacles' : [0.3], 
    'output_dir' : 'generated_testcase'
}


def random_index(size, sample=1):
    outshape = (sample,2)
    idx = np.zeros(outshape)
    idx = np.random.choice(np.arange(size), size=outshape,replace=True)
    return idx


ALL_TILE_TYPES = ['R', 'X', 'S', 'G']
def generate_testcase(config):
    output_dir_path = Path(config['output_dir'])
    output_dir_path.mkdir(exist_ok=True)
    testcase_seq = 0
    for s in range(*config['size']):
        for obs_portion in config['obstacles']:
            normal_tile_num = math.floor(s*s*obs_portion)

            start_goal_idx = random_index(s, 2)
            while (start_goal_idx[0] == start_goal_idx[1]).all():
                start_goal_idx = random_index(s, 2)
            mountains_idx = random_index(s, normal_tile_num)
            M = np.chararray((s, s), unicode=True)
            M[mountains_idx.T[0], mountains_idx.T[1]] = 'X'
            M[start_goal_idx[0][0], start_goal_idx[0][1]] = 'S'
            M[start_goal_idx[1][0], start_goal_idx[1][1]] = 'G'
            M[M==''] = 'R'
            assert (M == 'S').any()
            assert (M == 'G').any()
        
            outfile = output_dir_path / str(testcase_seq)
            with outfile.open(mode='w') as f:
                tmp = [''.join(row) + '\n' for row in M]
                
                f.writelines([str(s)+'\n'])
                f.writelines(tmp)
                # f.write(i +'\n' for i  in tmp)
                testcase_seq += 1



        


    return

if __name__ == "__main__":
    generate_testcase(config)
