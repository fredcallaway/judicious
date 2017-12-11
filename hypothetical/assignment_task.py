"""
Building on assignment.py, we add a Task class to represent atomic 
(or at least somewhat modularized) elements of a larger experimental procedure.

     
             ┌────────────┐        ┌────────────┐  
             │            │        │            │  
             │ Assignment │        │ Assignment │  
             │            │        │            │  
             └────────────┘        └────────────┘  
                    │                     │        
               ┌────┴────┐           ┌────┴────┐   
               │         │           │         │   
               ▼         ▼           ▼         ▼   
           ┌──────┐  ┌──────┐    ┌──────┐  ┌──────┐
           │ Task │  │ Task │    │ Task │  │ Task │
           └──────┘  └──────┘    └──────┘  └──────┘



Benefits over Assignment-only design:
  - we can packages server-side logic with a template in a clear way
  - there is no need (at least less need) to implement additional server-frontend
    communication. Tasks should be small enough that they
  - we have more control in data wrangling, for post-hoc data analysis as well
    as active experimental design (see `average_score` below)
  - we can implement more of the experiment logic into a sane programming language

Beneftis over Task-only design:
  - we can construct within-participant designs and learning paradigms
    by composing small Tasks into longer procedures...
  - ...without
    - the time cost (to participants) of repeatedly submitting and accepting HITs
    - allowing participants to leave the experiment early with partial payment
        (Fred: now that I think of it, does the IRB require that we allow 
         early termination?)

However, as is often the case, the abstraction comes at the cost of
increased complexity and program length. That being said, if we didn't add
custom methods, the code would be of similar length (in characters).

NOTE: The Assignment and Task classes will ultimately be implemented in
      models.py, inheriting from db.Model. The sketches below are for
      illustration.
"""

      


class Assignment(object):
    """A contiguous sequence of Tasks performed by a single Person.

    The Assignment class parallels an Assignment in mturk. Its functions include:

        - composing Tasks into multi-stage HITs (platform neutral term?)
        - storing/computing parameters that are constant within participants but differing
          across participants (i.e. within-subject conditions)
        - storing/computing participant-level data aggregations, potentially as
          part of an adaptiveexperimental design
        - somehow contributing to compensating participants. Anotated with confidence:
          storing assignment_id (9/10), computing bonuses (7/10), granting bonuses (6/10)             
    """

    @classmethod
    def get_assignment(self):
        """Returns an Assignment on the context stack or the default Assignment."""
        return self._context() or Assignment()


class Task(object):
    """An atomic unit of behavioral research."""
    def __init__(self, assignment=None):
        if assignment is None:
            # A Task must be associated with an Assignment. 
            assignment = Assignment.get_assignment()
        self.assignment = assignment


class MouselabAssignment(Assignment):
    name = 'mouselab'
    version = '0.0.0'
    title = "Pretend you're a mouse"
    reward = 0.15


class MouselabTask(Task):
    name = 'mouselab'
    version = '0.0.0'
    template = 'templates/mouselab.html'
    parameters = {
        'cheese_level': 100  # a default parameter
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assn_score = self.assignment.total_score
        avg_score = self.assignment.siblings.score.mean()  # not real code
        difficulty = assn_score / avg_score  # go easy on the weak
        self.parameters['layout'] = self._generate_layout(difficulty)

    def _generate_layout(self, difficulty):
        return 'some clever programming'
    
    # A cached/lazy property that can be used for within-experiment processing.
    # Because store=True, it will be eagerly evaluated and added to self.result
    @Task.post_process(store=True)
    def total_score(self, data):
        return np.sum(t['score'] for t in data)


class ConsentTask(Task):
    """A consent form."""
    name = 'consent'
    version = '0.0.0'
    template = 'templates/consent.html'


def run_one_participant():
    with MouselabAssignment() as assn:
        scores = []
        # Any Task initialized in the with block (and without an explicit `assignment` argument)
        # will automatically attach to `assn`. See Task.__init__ for details.
        result = ConsentTask().run()
        if not result.get('consent', False):
            return
        
        for trial in range(12):
            # The `Task` base class handles keyword arguments appopriately.
            #   - The strict option is to require that key words be columns.
            #   - The leniant option is to pull out columns first, then assume
            #     that the remaining kwargs should update `params`. The
            #     code below assumes the leniant behavior.
            result = MouselabTask(**params, trial=trial).run()
            scores.append(result['score'])
            if len(scores) > 3 and np.mean(scores) < 0:
                # An especially bad participant, terminate early.
                return

# 10 assignments running at a time
pool = Pool(n_jobs=10, backend='threading')
pool(delayed(run_one_participant)() for _ in range(50))




