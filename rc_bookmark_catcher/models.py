from . import db

class Project(db.Model):
    
    # Primary Key
    project_id = db.Column(db.Integer, primary_key=True,nullable=False)

    # Other attributes
    project_title = db.Column(db.String(128))

class Instrument(db.Model):

    # Primary Keys (Composite)
    project_id = db.Column(db.Integer, primary_key=True,nullable=False)
    instrument_name = db.Column(db.String(128), primary_key=True,nullable=False)

    # Other attributes
    instrument_label = db.Column(db.String(256))

    # Constraints



class Field(db.Model):

    # Primary Keys (Composite)
    project_id = db.Column(db.Integer, primary_key=True,nullable=False)
    form_name = db.Column(db.String(128), primary_key=True,nullable=False)
    field_name = db.Column(db.String(128), primary_key=True,nullable=False)

    # Other attributes
    field_label = db.Column(db.String(256))

    # Relationship
    instrument = db.relationship( Instrument )

    # Constraints
    __table_args__ = ( 
        db.ForeignKeyConstraint(['project_id', 'form_name'], [Instrument.project_id,Instrument.instrument_name]),
    )


def create_all():
    db.create_all()

def drop_all():
    db.drop_all()