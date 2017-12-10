"""Example judicio experiment."""

import asyncio
import numpy as np
import judicio

np.random.seed(2)

class DummyTask(judicio.Task):
    """Dummy task for debugging."""
    
    async def run(self, **params):
        await asyncio.sleep(0.5)
        return np.random.randint(2)

    async def run_many(self, params_seq):
        results = (self.run(**prm) for prm in params_seq)
        x = await asyncio.gather(*results)
        return x
      

def params():
    """A batch of parameters for one iteration of the experiment."""
    for guilty in (True, False):
        for i in range(3):
            yield {'guilty': guilty, 'i': i}


@judicio.run
async def main():
    task = DummyTask()
    consensus = False
    while not consensus:
        # Run a batch of HITs concurrently.
        results = await task.run_many(params())
        # If the results are undesirable, iterate!
        jurry = np.mean(results)
        print('Vote:', jurry)
        consensus = jurry in (0, 1)
    print('Final verdict:', 'Guilty' if jurry else 'Innocent')
