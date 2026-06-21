from datetime import datetime
from ..extensions import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    link_url = db.Column(db.String(2048))
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time)
    has_deadline = db.Column(db.Boolean, nullable=False, default=True)
    show_on_board = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.String(10), nullable=False, default='media')
    category = db.Column(db.String(30), nullable=False, default='pessoal')
    status = db.Column(db.String(20), nullable=False, default='pendente')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    recurrence_type = db.Column(db.String(15), nullable=False, default='none')
    recurrence_start_date = db.Column(db.Date)
    recurrence_end_date = db.Column(db.Date)
    recurrence_days = db.Column(db.Integer)
    series_id = db.Column(db.String(36))
    overrides = db.relationship('GoalOccurrenceOverride', backref='goal', lazy=True, cascade='all, delete-orphan')


class GoalOccurrenceOverride(db.Model):
    __table_args__ = (db.UniqueConstraint('goal_id', 'occurrence_date'),)
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    occurrence_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    completed_at = db.Column(db.DateTime)
