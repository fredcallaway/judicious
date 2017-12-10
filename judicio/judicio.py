"""Asynchronous Judicious implementation.

Also: dative singular of judicium meaning decision, opinion or trial.
"""

import asyncio

class Task(object):
    """A task to be completed by a judicious participant."""
    version: str = '0.0'

    async def run(self, params):
        raise NotImplementedError()


class TemplateTask(object):
    """A task defined in a jinja template."""
    version: str = '0.0'
    def __init__(self, template):
        super().__init__()
        self.template = template

    async def run(self, params):
        raise NotImplementedError()
      

# Not sure whether to use a class here. It could potentially allow
# for more flexibility down the road (e.g. multiple event loops)
class Judicio(object):
    """One class to rule them all."""
    def __init__(self):
        self.loop = asyncio.get_event_loop()
    
    def run(self, func):
        self.loop.run_until_complete(func())

    async def gather(self, *results):
        return await asyncio.gather(*results)


def run(func):
    """Runs an asynchronous function until completion.

    Convenience wrapper around Judicio.run
    """
    return Judicio().run(func)