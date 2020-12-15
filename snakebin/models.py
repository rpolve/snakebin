from snakebin import db


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, unique=False)
    complete = db.Column(db.Boolean)
    elapsed = db.Column(db.Integer)
    results = db.Column(db.Text)
    submitted = db.Column(db.Integer)

    def __repr__(self):
        return "<Job_id {}>".format(self.id)
