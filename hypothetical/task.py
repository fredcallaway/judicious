"""
In this example, we specify an experimental design without instantiating an
explicit Assignment object. We fall back on a default Assignment with a
generic title and fixed reward. This is similar to the behavior of the
functions in judicious.tasks
"""

class MouselabTask(Task):
    name = 'mouselab'
    version = '0.0.0'
    template = 'templates/mouselab.html'
    parameters = {
        'cheese_level': 100  # a default parameter
    }


def run_one_participant():
    for trial in range(12):
        # Because there is no Assignment (passed as an argument or on the context
        # stack), the task below attaches to a default Assignment with a generic
        # title and fixed reward (as with the current implementation).
        task = MouselabTask(**params, trial=trial)
        result = task.run()
        scores.append(result['score'])
        if len(scores) > 3 and np.mean(scores) < 0:
            # An especially bad participant, terminate early.
            return

# 10 tasks running at a time
pool = Pool(n_jobs=10, backend='threading')
pool(delayed(run_one_participant)() for _ in range(50))




