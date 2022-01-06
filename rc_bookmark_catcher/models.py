from . import db



class Project(db.Model):
    # Primary Key
    pid = db.Column(db.Integer, primary_key=True,nullable=False, autoincrement=False)

    # Other attributes
    project_title = db.Column(db.String(256))
    stu = db.Column(db.String(128))
    api_token = db.Column(db.String(128))
    is_longitudinal = db.Column(db.Integer)
    has_repeating_instruments_or_events = db.Column(db.Integer)
    surveys_enabled = db.Column(db.Integer)

    # Relationships -- you have to use back_populates and not backref so you can have asymmetric cascades
    instruments = db.relationship('Instrument', back_populates='project', cascade = ['all', 'delete', 'delete-orphan'], order_by = 'Instrument.instrument_label')



class Instrument(db.Model):

    # Primary Keys (Composite)
    pid = db.Column(db.Integer, nullable=False )
    instrument_name = db.Column(db.String(128), nullable=False)

    # Other attributes
    order_num = db.Column(db.Integer)
    instrument_label = db.Column(db.String(256))

    # Constraints
    __table_args__ = (
        db.PrimaryKeyConstraint('pid','instrument_name'),
        db.ForeignKeyConstraint(['pid'], ['project.pid']),
    )

    # Relationships -- you have to use back_populates and not backref so you can have asymmetric cascades
    # not sure how I got the overlaps arguments to work, did trial and error
    project = db.relationship('Project', back_populates = 'instruments', overlaps = 'instruments')
    #variables = db.relationship('Field', back_populates = 'instrument', overlaps = 'variables', order_by='Field.order_num')

class Field(db.Model):

    # Primary Keys (Composite)
    project_id = db.Column(db.Integer, nullable=False )
    field_name = db.Column(db.String(128), nullable=False)

    # Other attributes
    order_num = db.Column(db.Integer)
    form_name = db.Column(db.String(128), nullable=False)
    field_label = db.Column(db.Text)

    # Constraints
    __table_args__ = (
        db.PrimaryKeyConstraint('project_id', 'field_name'),
        db.ForeignKeyConstraint(['project_id'], ['project.pid']),
        db.ForeignKeyConstraint(['project_id', 'form_name'], ['instrument.pid','instrument.instrument_name']),
    )

    # Relations -- you have to use back_populates and not backref so you can have asymmetric cascades
    # not sure how I got the overlaps arguments to work, did trial and error
    #instrument = db.relationship('Instrument', back_populates = 'variables', overlaps = 'variables' )
    #project = db.relationship('Project', back_populates = 'variables', overlaps = 'instrument,variables')

class Template(db.Model):
    # Primary Key
    template_name = db.Column(db.String(128), nullable = False, primary_key = True)

    # Other attributes
    template_label = db.Column(db.Text)

    # Relations
    #hovs = db.relationship('Hov', back_populates = 'template', cascade = ['all', 'delete', 'delete-orphan'], order_by = 'Hov.order_num')
    #projects = db.relationship('Project', back_populates = 'template', order_by = 'Project.project_id' )

class Hov(db.Model):
    # Primary Keys (Composite)
    template_name = db.Column(db.String(128), nullable = False)
    hov_name = db.Column(db.String(128), nullable = False)

    # Other attributes
    hov_variable = db.Column(db.String(128))
    hov_observer = db.Column(db.String(128))
    hov_date = db.Column(db.String(128))
    hov_label = db.Column(db.Text)
    order_num = db.Column(db.Integer)

    # Constraints
    __table_args__ = (
        db.PrimaryKeyConstraint('template_name', 'hov_name'),
        db.ForeignKeyConstraint(['template_name'], ['template.template_name']),
    )

    # Relations
    #template = db.relationship('Template', back_populates = 'hovs')