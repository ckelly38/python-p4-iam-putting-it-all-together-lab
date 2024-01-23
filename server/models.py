from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

from config import db, bcrypt

class MyValidator:
    def __init__(self):
        self.disablevalidator = True;
    
    def strHasAtMinOrMaximumXChars(self, numcs, mystr, usemax):
        #print(f"usemax = {usemax}");
        #print(f"numcs = {numcs}");
        #print(f"mystr = {mystr}");
        if (numcs == None or type(numcs) != int): raise ValueError("numcs must be an integer!");
        if (usemax == True or usemax == False): pass;
        else: raise ValueError("usemax must be a boolean variable and have a boolean value!");
        if (mystr == None): pass;
        else:
            if (type(mystr) == str): pass;
            else: raise ValueError("mystr must be a string!");
        if (not usemax and numcs < 0): raise ValueError("the absolute minimum allowed is zero!");
        if (self.disablevalidator): return True;
        if (usemax):
            if (mystr == None): return True;
            if (numcs < len(mystr)): return False;
            else: return True;
        else:
            if (numcs == 0): return True;
            elif (0 < numcs):
                if (mystr == None): return False;
                else: return not (len(mystr) < numcs);
            else: raise ValueError("the absolute minimum allowed is zero!");

    def strHasAtMaximumXChars(self, maxcs, mystr):
        retval = self.strHasAtMinOrMaximumXChars(maxcs, mystr, True);
        #print(retval);
        return retval;

    def strHasAtMinimumXChars(self, mincs, mystr):
        retval = self.strHasAtMinOrMaximumXChars(mincs, mystr, False);
        #print(retval);
        return retval;

    def strHasAtMinXAndAtMostY(self, mincs, maxcs, mystr):
        return (self.strHasAtMinimumXChars(mincs, mystr) and
                self.strHasAtMaximumXChars(maxcs, mystr));

mv = MyValidator();

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True);
    username = db.Column(db.String, unique=True, nullable=False);
    _password_hash = db.Column(db.String);
    image_url = db.Column(db.String);
    bio = db.Column(db.String);
    
    #varname = db.relationship("ClassName", back_populates="correspondingattribute");
    recipes = db.relationship("Recipe");

    #want to exclude the recipies from the serializer
    #serialize_rules = ('-recipes',);

    @validates("username")
    def isvalidusername(self, key, val):
        exists = mv.strHasAtMinimumXChars(1, val);
        if (exists): pass;
        else: raise ValueError("the username must have at least one character in it!");
        if (mv.disablevalidator): return val;
        unms = [usr.username for usr in User.query.all()];
        if (val in unms): raise ValueError("usernames must be unique!");
        else: return val;

    @hybrid_property
    def password_hash(self):
        raise AttributeError("not allowed to view the password hash outside of this class!");

    @password_hash.setter
    def password_hash(self, val):
        phsh = bcrypt.generate_password_hash(val.encode("utf-8"));
        self._password_hash = phsh.decode("utf-8");
    
    def authenticate(self, val):
        return bcrypt.check_password_hash(self._password_hash, val.encode("utf-8"));

    def __repr__(self):
        return f"<User: id: {self.id}, name: {self.username}, image_url: {self.image_url}, bio: {self.bio}, recipes: {self.recipes}>";

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )

    id = db.Column(db.Integer, primary_key=True);
    title = db.Column(db.String, nullable=False);
    instructions = db.Column(db.String,
    #                         db.CheckConstraint("length(instructions) >= 50"),
                             nullable=False);
    #instructions = db.Column(db.String,
    #                         db.CheckConstraint("instructions >= 50)"),
    #                         nullable=False);
    #instructions = db.Column(db.String,
    #                         db.CheckConstraint("NOT(LENGTH(instructions) < 50)"),
    #                         nullable=False);
    #instructions = db.Column(db.String,
    #                         db.CheckConstraint("LENGTH(instructions) >= 50"),
    #                         nullable=False);
    #instructions = db.Column(db.String,
    #                         db.CheckConstraint(db.func.length("instructions") >= 50),
    #                         nullable=False);
    #instructions = db.Column(db.String,
    #                         db.CheckConstraint(db.func.length("Recipe.instructions") >= 50),
    #                         nullable=False);
    minutes_to_complete = db.Column(db.Integer);
    
    #varname = db.relationship("ClassName", back_populates="correspondingattribute");
    #varname = db.Column(DataType, db.ForeignKey('dbtablename.colname'))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"));
    user = db.relationship("User", back_populates="recipes");

    #want to exclude the recipies from the serializer
    serialize_rules = ('-user',);

    #@validates("title")
    #def isvalidtitle(self, key, val):
    #    exists = mv.strHasAtMinimumXChars(1, val);
    #    if (exists): return val;
    #    else: raise ValueError("title must exist!");

    #@validates("instructions")
    #def isvalidinstructions(self, key, val):
    #    mincharmet = mv.strHasAtMinimumXChars(50, val);
    #    if (mincharmet): return val;
    #    else: raise ValueError("instructions must have at minimum 50 characters!");
    
    def __repr__(self):
        return f"<Recipe: title: {self.title}, instructions: {self.instructions}, minutes_to_complete: {self.minutes_to_complete}, user_id: {self.user_id}>";
