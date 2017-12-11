from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

db = SQLAlchemy(None)


class Experiment(db.Model):
    """A group of Assignments with a common scientific telos."""
    __tablename__ = "experiment"

    id = db.Column(UUID, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    version = db.Column(db.String(16))
    parameters = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    assignments = db.relationship('Assignment', backref='experiment')


class Assignment(db.Model):
    """A single continuous interaction with a Person.

    This maps exactly onto the assignment concept in mturk.
    """
    __tablename__ = "assignment"

    id = db.Column(UUID, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    version = db.Column(db.String(64))
    parameters = db.Column(db.JSON)

    platform_id = db.Column(db.String(64), nullable=False)  # e.g. mturk AssignmentId
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    context_id = db.Column(UUID, db.ForeignKey('context.id'), nullable=False)
    experiment_id = db.Column(UUID, db.ForeignKey('experiment.id'))  # nullable?
    tasks = db.relationship('Task', backref='assignment')


class Task(db.Model):
    """A task to be completed by a judicious participant."""
    __tablename__ = "task"

    id = db.Column(UUID, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    version = db.Column(db.String(64))
    parameters = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_queued_at = db.Column(db.DateTime)
    last_started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    result = db.Column(db.JSON)

    person_id = db.Column(UUID, db.ForeignKey('person.id'))
    context_id = db.Column(UUID, db.ForeignKey('context.id'), nullable=False)
    assignment_id = db.Column(UUID, db.ForeignKey('assignment.id'))

    def __init__(self, id, context_id, name, parameters=None):
        self.id = id
        self.context_id = context_id
        self.name = name
        self.parameters = parameters

    def __repr__(self):
        return '<Task %r>' % self.name

    def timeout(self):
        """Placed timed-out tasks back on the queue."""
        app.logger.info("Timeout on task {}, requeuing.".format(self.id))
        self.last_started_at = None
        self.last_queued_at = datetime.now()
        db.session.add(self)
        db.session.commit()
        self.requeue()

    def requeue(self):
        if self.person_id:
            pq[str(self.person_id)].put({"id": self.id})
        else:
            pq["open"].put({"id": self.id})


class Person(db.Model):
    """An identity to be claimed by a judicious participant."""
    __tablename__ = "person"

    id = db.Column(UUID, primary_key=True, nullable=False)
    platform_id = db.Column(db.String(64))  # e.g. mturk WorkerId
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    claimed_at = db.Column(db.DateTime)
    
    tasks = db.relationship("Task", backref='person')
    context_id = db.Column(UUID, db.ForeignKey('context.id'))

    def __init__(self, id, context_id):
        self.id = id
        self.context_id = context_id

    def __repr__(self):
        return '<Person %r>' % self.id

# Fred: The purpose of this class is not clear to me.
class Context(db.Model):
    """A particular run of a script."""

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<Context %r>' % self.id

    id = db.Column(UUID, primary_key=True, nullable=False)
    tasks = db.relationship("Task", backref='context')
    persons = db.relationship("Person", backref='context')