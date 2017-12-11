"""
This example demonstrates usage of an interface centered on a single
Assignment class. This object is exactly parallel with the Assignment concept
in mturk.

An Assignment can include multiple pages/templates/tasks presented in a
structured and conditional way. These tasks are represented in the
database only implicitly, embedded in the Assignment table.

Server-side logic within an assignment is possible using this design.
We would need to implement a more general interface between app.py and
judicious.js than the current "post data upon task completion" model.

In this example, the class is just a data-holder. However, we could move
some (or all) of the experiment logic into a method. Is one option preferrable?
"""

class MouselabAssignment(Assignment):
    name = 'mouselab'
    title = "Pretend you're a mouse"
    reward = 0.15


def run_one_participant():
    # You could equivalently use:
    #   with Assignment(name='mouselab', title="Pretend you're a mouse", reward=0.15) as assn:
    with MouselabAssignment() as assn:
        scores = []
        result = assn.do('templates/consent.html')
        if not result.get('consent', False):
            return
        for trial in range(12):
            result = assn.do('templates/mouselab.html', {'trial': trial})
            scores.append(result['score'])
            if len(scores) > 3 and np.mean(scores) < 0:
                # An especially bad participant, terminate early.
                return

# 10 assignments running at a time
pool = Pool(n_jobs=10, backend='threading')
pool(delayed(run_one_participant)() for _ in range(50))




