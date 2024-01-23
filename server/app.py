#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class isUserLogIn:
    def isThereALoggedInUserAndRetFunc(self, msess, rfunctrue, rfuncfalse, errmsg):
        skeys = msess.keys();
        print(skeys);
        print(msess.values());
        if (len(skeys) < 1 or "user_id" not in skeys): return rfuncfalse(msess, errmsg);
        elif (msess["user_id"] == None): return rfuncfalse(msess, errmsg);
        elif (type(msess["user_id"]) == int): return rfunctrue(msess);
        else: return rfuncfalse(msess, errmsg);
    
    def isThereALoggedInUser(self, msess, errmsg):
        return self.isThereALoggedInUserAndRetFunc(msess, self.retTrue, self.retFalse, errmsg);

    def retTrue(self, val = None, oval = None): return True;
    def retFalse(self, val = None, oval = None): return False;
    def retErrorWithMsg(self, msess, msg):
        print(msg);
        return {"Error": msg}, 401;
    def retErrorNotLoggedIn(self):
        print("401 Error NOT LOGGED IN!");
        return self.retErrorWithMsg(None, "401 Error NOT LOGGED IN!");
    def retErrorNotNeverLoggedIn(self):
        print("401 Error NOT AND NEVER LOGGED IN!");
        return self.retErrorWithMsg(None, "401 Error NOT AND NEVER LOGGED IN!");

    def retNone(self, vala = None, valb = None): return None;
    def genMyDataObj(self, mstrs, mdataobj):
        retobj = dict();
        for mstr in mstrs:
            retobj[mstr] = mdataobj[mstr];
        return retobj;

    def getValidDataObjectWithRFuncCall(self, mstrs, mdataobj, rfunc):
        if (mdataobj == None): raise ValueError("None type not allowed here!");
        if (mstrs == None or len(mstrs) < 1): return None;
        rjkys = mdataobj.keys();
        for mstr in mstrs:
            if (mstr in rjkys): pass;
            else:
                errmsg = f"422 Error you must include a {mstr}!";
                print(errmsg);
                return {"Error": errmsg}, 422;
        return rfunc(mstrs, mdataobj);

    def getValidDataObject(self, mstrs, mdataobj):
        return self.getValidDataObjectWithRFuncCall(mstrs, mdataobj, self.genMyDataObj);

    def keysMustBePresentInObject(self, mstrs, mdataobj):
        return self.getValidDataObjectWithRFuncCall(mstrs, mdataobj, self.retNone);

iuli = isUserLogIn();

class Signup(Resource):
    def genUser(self, mdataobj):
        print("INSIDE OF GENUSER():");
        rjkys = mdataobj.keys();
        kres = iuli.keysMustBePresentInObject(["username", "password"], mdataobj);
        if (kres == None): pass;
        else: return kres;
        try:
            usr = User(username=mdataobj["username"], image_url="", bio="");
        except Exception as exc:
            errmsg = "422 Error ATTEMPTED TO CREATE AN INVALID USER, INVALID USERNAME!";
            print(errmsg);
            return {"Error": errmsg}, 422;
        if ("image_url" in rjkys): usr.image_url = mdataobj["image_url"];
        if ("bio" in rjkys): usr.bio = mdataobj["bio"];
        usr.password_hash = mdataobj["password"];
        print(usr);
        return usr;

    def post(self):
        print("INSIDE OF SIGNUP():");
        rjsn = request.get_json();
        #rdta = request.get_data();
        print(request.form);
        print(rjsn);
        #print(rdta);
        #create a new user and save them to the db
        #create a new user here
        usr = None;
        res = None;
        if (len(request.form) < 1): res = self.genUser(rjsn);
        else: res = self.genUser(request.form);
        if (isinstance(res, User)): usr = res;
        else: return res;
        #save it to the db here
        try:
            db.session.add(usr);
            db.session.commit();
        except Exception as exc:
            errmsg = "422 Error ATTEMPTED TO CREATE AN INVALID USER, PROBABLY USERNAME ";
            errmsg += "ALREADY USED OR INVALID PASSWORD!";
            print(errmsg);
            return {"Error": errmsg}, 422;
        #save it to the session effectively loggin them in
        session["user_id"] = usr.id;
        #return and respond to the client
        return usr.to_dict(), 201;
        #print("404 Error NOT DONE YET WITH SIGN UP!");
        #return {"Error": "404 Error NOT DONE YET WITH SIGN UP!"}, 404;

class CheckSession(Resource):
    def retUser(self, msess):
        print("INSIDE OF RET-USER():");
        usr = User.query.filter_by(id=msess["user_id"]).first();
        if (usr == None):
            errmsg = f"422 Error NO VALID USER FOUND WITH THAT ID ({msess['user_id']})!";
            print(errmsg);
            return {"Error": errmsg}, 422;
        else:
            print("Successfully obtained and returned the user!");
            return usr.to_dict(), 200;

    def get(self):
        print("INSIDE OF CHECK-SESSION():");
        #skeys = session.keys();
        #if (len(skeys) < 1 or "user_id" not in skeys):
        #    return {"Error": "401 Error NOT LOGGED IN!"}, 401;
        #else: return User.query.filter_by(id=session["user_id"]).first().to_dict(), 200;
        return iuli.isThereALoggedInUserAndRetFunc(session, self.retUser, iuli.retErrorWithMsg,
                                                   "401 Error NOT LOGGED IN!");

class Login(Resource):
    def getUsernameAndPasswordFromData(self, mdataobj):
        return iuli.getValidDataObject(["username", "password"], mdataobj);

    def post(self):
        print("INSIDE OF LOGIN():");
        rjsn = request.get_json();
        #rdta = request.get_data();
        print(request.form);
        print(rjsn);
        #print(rdta);
        if (len(request.form) < 1):
            res = self.getUsernameAndPasswordFromData(rjsn);
        else: res = self.getUsernameAndPasswordFromData(request.form);
        if ("Error" in res.keys()): return res;
        usnm = res["username"];
        pswd = res["password"];
        usr = User.query.filter_by(username=usnm).first();
        if (usr == None): return {"Error": "401 Error NOT LOGGED IN! INVALID USERNAME!"}, 401;
        if (usr.authenticate(pswd)):
            session["user_id"] = usr.id;
            return usr.to_dict(), 200;
        else: return {"Error": "401 Error NOT LOGGED IN! INVALID PASSWORD!"}, 401;
        #print("404 Error NOT DONE YET WITH LOGGING IN!");
        #return {"Error": "404 Error NOT DONE YET WITH LOGGING IN!"}, 404;

class Logout(Resource):
    def remUser(self, msess):
        print("INSIDE OF REMUSER():");
        if (type(msess["user_id"]) == int):
            msess["user_id"] = None;
            return {}, 204;
        else:
            print("401 Error not logged in!");
            return {"Error": "401 Error not logged in!"}, 401;

    def delete(self):
        print("INSIDE OF LOGOUT-DELETE():");
        #skeys = session.keys();
        #if (len(skeys) < 1 or "user_id" not in skeys):
        #    return {"Error": "401 Error not and never logged in!"}, 401;
        #else: return self.remUsr(session);
        return iuli.isThereALoggedInUserAndRetFunc(session, self.remUser, iuli.retErrorWithMsg,
                                                   "401 Error not and never logged in!");
            

class RecipeIndex(Resource):
    def listRecipes(self, msess):
        print("INSIDE RECIPIE-INDEX-LIST():");
        usr = User.query.filter_by(id=msess["user_id"]).first();
        print(usr);
        print("all recipes:");
        rps = Recipe.query.all();
        #print(rps);
        print(len(rps));
        for rp in rps:
            print(rp);
            print(rp.user);
            print(rp.user_id);
        print("user recipes:");
        print(usr.recipes);
        rpsdicts = [rp.to_dict() for rp in usr.recipes];
        print(rpsdicts);
        return rpsdicts, 200;

    def get(self):
        print("INSIDE RECIPIE-INDEX-GET():");
        #skeys = session.keys();
        #if (len(skeys) < 1 or "user_id" not in skeys):
        #    return {"Error": "401 Error not and never logged in!"}, 401;
        #else: return self.remUsr(session);
        return iuli.isThereALoggedInUserAndRetFunc(session, self.listRecipes,
                                                   iuli.retErrorWithMsg,
                                                   "401 Error not and never logged in!");
        #return {"Error": "404 Error NOT DONE YET WITH LISTING THE RECIPES!"}, 404;

    def getNewRecipeDataFromDataObj(self, mdataobj):
        return iuli.getValidDataObject(["title", "instructions", "minutes_to_complete"],
                                       mdataobj);

    def createRecipe(self, msess):
        print("INSIDE RECIPIE-INDEX-CREATE():");
        usr = User.query.filter_by(id=msess["user_id"]).first();
        rp = None;
        try:
            rjsn = request.get_json();
            #rdta = request.get_data();
            print(request.form);
            print(rjsn);
            #print(rdta);
            if (len(request.form) < 1):
                res = self.getNewRecipeDataFromDataObj(rjsn);
            else: res = self.getNewRecipeDataFromDataObj(request.form);
            if ("Error" in res.keys()): return res;
            mt = res["title"];
            ins = res["instructions"];
            mins = res["minutes_to_complete"];
            rp = Recipe(title=mt, instructions=ins, minutes_to_complete=mins, user_id=usr.id);
            db.session.add(rp);
            db.session.commit();
        except Exception as exc:
            print("422 Error ATTEMPTED TO CREATE AN INVALID RECIPE!");
            return {"Error": "422 Error ATTEMPTED TO CREATE AN INVALID RECIPE!"}, 422;
        print("Successfully created the new recipe!");
        return rp.to_dict(), 201;
    
    def post(self):
        print("INSIDE RECIPIE-INDEX-POST():");
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