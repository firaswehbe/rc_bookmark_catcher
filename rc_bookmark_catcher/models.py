from . import db

class Project(db.Model):
    
    # Primary Key
    project_id = db.Column(db.Integer, primary_key=True,nullable=False)

    # Other attributes
    project_title = db.Column(db.String(128))
    api_token = db.Column(db.String(128))


class Instrument(db.Model):

    # Primary Keys (Composite)
    project_id = db.Column(db.Integer, primary_key=True,nullable=False)
    instrument_name = db.Column(db.String(128), primary_key=True,nullable=False)

    # Other attributes
    order_num = db.Column(db.Integer)
    instrument_label = db.Column(db.String(256))

    # Relationships
    project = db.relationship(Project, backref='instruments')

    # Constraints
    __table_args__ = (
        db.ForeignKeyConstraint(['project_id'], [Project.project_id]),
    )



class Field(db.Model):

    # Primary Keys (Composite)
    project_id = db.Column(db.Integer, primary_key=True,nullable=False)
    form_name = db.Column(db.String(128), primary_key=True,nullable=False)
    field_name = db.Column(db.String(128), primary_key=True,nullable=False)

    # Other attributes
    order_num = db.Column(db.Integer)
    field_label = db.Column(db.String(256))

    # Relationship
    instrument = db.relationship( Instrument )

    # Constraints
    __table_args__ = ( 
        db.ForeignKeyConstraint(['project_id', 'form_name'], [Instrument.project_id,Instrument.instrument_name]),
    )
