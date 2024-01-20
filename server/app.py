#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class isUserLogIn:
    def isThereALoggedInUserAndRetFunc(self, msess, rfunctrue, rfuncfalse, errmsg):
        skeys = msess.keys();
        if (len(skeys) < 1 or "user_id" not in skeys): return rfuncfalse(msess, errmsg);
        else: return rfunctrue(msess);
    
    def isThereALoggedInUser(self, msess, errmsg):
        return self.isThereALoggedInUserAndRetFunc(msess, self.retTrue, self.retFalse, errmsg);

    def retTrue(self, val = None, oval = None): return True;
    def retFalse(self, val = None, oval = None): return False;
    def retErrorWithMsg(self, msess, msg): return {"Error": msg}, 401;
    def retErrorNotLoggedIn(self):
        return self.retErrorWithMsg(None, "401 Error NOT LOGGED IN!");
    def retErrorNotNeverLoggedIn(self):
        return self.retErrorWithMsg(None, "401 Error NOT AND NEVER LOGGED IN!");

iuli = isUserLogIn();

class Signup(Resource):
    def post(self):
        #create a new user and save them to the db
        #create a new user here
        #usr = User(username=?, image_url=?, bio=?);
        #usr._password_hash = ?;
        #save it to the db here
        #db.session.add(usr);
        #db.session.commit();
        #save it to the session effectively loggin them in
        #session["user_id"] = usr.id;
        #return and respond to the client
        #return usr.to_dict(), 201;
        return {"Error": "404 Error NOT DONE YET WITH SIGN UP!"}, 404;

class CheckSession(Resource):
    def retUser(self, msess):
        return User.query.filter_by(id=msess["user_id"]).first().to_dict(), 200;

    def get(self):
        #skeys = session.keys();
        #if (len(skeys) < 1 or "user_id" not in skeys):
        #    return {"Error": "401 Error NOT LOGGED IN!"}, 401;
        #else: return User.query.filter_by(id=session["user_id"]).first().to_dict(), 200;
        return iuli.isThereALoggedInUserAndRetFunc(session, self.retUser, iuli.retErrorWithMsg,
                                                   "401 Error NOT LOGGED IN!");

class Login(Resource):
    def post(self):
        #usr = User.query.filter_by(username=?).first();
        #if (usr == None): return {"Error": "401 Error NOT LOGGED IN! INVALID USERNAME!"}, 401;
        #if (usr.authenticate(?)):
        #    session["user_id"] = usr.id;
        #    return usr.to_dict(), 200;
        #else: return {"Error": "401 Error NOT LOGGED IN! INVALID PASSWORD!"}, 401;
        return {"Error": "404 Error NOT DONE YET WITH LOGGING IN!"}, 404;

class Logout(Resource):
    def remUser(self, msess):
        if (type(msess["user_id"]) == int):
            msess["user_id"] = None;
            return {}, 204;
        else: return {"Error": "401 Error not logged in!"}, 401;

    def delete(self):
        #skeys = session.keys();
        #if (len(skeys) < 1 or "user_id" not in skeys):
        #    return {"Error": "401 Error not and never logged in!"}, 401;
        #else: return self.remUsr(session);
        return iuli.isThereALoggedInUserAndRetFunc(session, self.remUser, iuli.retErrorWithMsg,
                                                   "401 Error not and never logged in!");
            

class RecipeIndex(Resource):
    def listRecipes(self, msess):
        usr = User.query.filter_by(id=msess["user_id"]).first();
        return {[rp.to_dict() for rp in usr.recipies]}, 200;

    def get(self):
        #skeys = session.keys();
        #if (len(skeys) < 1 or "user_id" not in skeys):
        #    return {"Error": "401 Error not and never logged in!"}, 401;
        #else: return self.remUsr(session);
        return iuli.isThereALoggedInUserAndRetFunc(session, self.listRecipes,
                                                   iuli.retErrorWithMsg,
                                                   "401 Error not and never logged in!");
        #return {"Error": "404 Error NOT DONE YET WITH LISTING THE RECIPES!"}, 404;

    def createRecipe(self, msess):
        usr = User.query.filter_by(id=msess["user_id"]).first();
        rp = None;
        try:
            #rp = Recipe(title=?, instructions=?, minutes_to_complete=?, user_id=usr.id);
            #db.session.add(rp);
            #db.session.commit();
            pass;
        except Exception as exc:
            return {"Error": "422 Error ATTEMPTED TO CREATE AN INVALID RECIPE!"}, 422;
        return rp, 201;
    
    def post(self):
        return iuli.isThereALoggedInUserAndRetFunc(session, self.createRecipe,
                                                   iuli.retErrorWithMsg,
                                                   "401 Error not and never logged in!");
        #return {"Error": "404 Error NOT DONE YET WITH CREATING A RECIPE!"}, 404;

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)