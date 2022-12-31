import os
from flask import *
from flask_sqlalchemy import *
from sqlalchemy import select
from flask_login import *
import bcrypt
from datetime import datetime



#for picture
from werkzeug.utils import secure_filename
import uuid as uuid

from PIL import Image #module name = pillow

curr_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"

app.secret_key = b'755a270f1d4e4d5a8cb49442a338ac012cf185be11c17b2b4e2e2ea67a0856e2'

upload_folder = "static/images/"
app.config["UPLOAD_FOLDER"] = upload_folder

db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)

# salt = b'$2b$12$TuFQCkjOA/JLl1/HTpY5Uu'
salt = bcrypt.gensalt()


class App_user(db.Model, UserMixin):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    first_name = db.Column(db.String, nullable = False)
    profile_pic = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    # comments = db.relationship('Comment', backref = 'app_user', lazy = True)
    # posts = db.relationship('Post', backref = 'app_user', lazy = True)
    # followers = db.relationship('Follower', backref = 'app_user', lazy = True)

class Post(db.Model):
    __tablename__ = 'post'
    post_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    ID = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable = False)
    username = db.Column(db.String, db.ForeignKey('app_user.username'), nullable = False)
    image_path = db.Column(db.String(500), nullable = False)
    description = db.Column(db.String(200), nullable = False)
    time_stamp = db.Column(db.DateTime, default = datetime.utcnow)
    number_of_likes = db.Column(db.Integer, default = 0)
    # comments = db.relationship('Comment', backref = 'post', lazy = True)

class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    ID = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable = False)
    comment = db.Column(db.String, nullable = False)

class Follower(db.Model):
    __tablename__ = 'follower'
    serial_number = db.Column(db.Integer,autoincrement = True, primary_key = True)
    ID = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable = False)
    following_ID = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable = False)

class Likes(db.Model):
    __tablename__ = 'likes'
    serial_number = db.Column(db.Integer,autoincrement = True, primary_key = True)
    post_ID = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable = False)
    liked_by_userID = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable = False)

@login_manager.user_loader
def load_user(user):
    return App_user.query.get(int(user))

@app.route("/")
def redirect_to_login():
    return redirect("/login")

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        pwd = bytes(request.form["pwd"], 'utf-8')

        find_user = App_user.query.filter_by(username = uname).first()

        if find_user:
            user_pass = find_user.password
            # user_pass = bytes(user_pass, 'utf-8')
            if bcrypt.checkpw(pwd, user_pass):
                login_user(find_user)
                return redirect("/feed")
            else:
                return render_template("login.html", condition = 'invalid')
        else:
            return render_template("login.html", condition = 'invalid')


    status = request.args.get('status')
    print(status)
    return render_template("login.html", condition = status)

@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        fname = request.form['fname']
        lname = request.form['lname']
        uname = request.form['user_name']
        pwd = request.form['pwd']
        pic = request.files['pfp']
        isEmpty = App_user.query.filter_by(username = uname).first()

        if isEmpty:
            return redirect("/login?status=fail")

        pic_filename = secure_filename(pic.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_filename

        pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        pwd = bytes(pwd, 'utf-8')
        pwd = bcrypt.hashpw(pwd, salt)
        q = App_user(username = uname, first_name = fname, last_name = lname, password = pwd, profile_pic = pic_name)
        db.session.add(q)
        db.session.commit()

        return redirect("./login?status=success")

    return render_template("signup.html")

@app.route("/feed", methods=["get", "post"])
@login_required
def feed():
    uname = current_user.username
    other_users = App_user.query.filter(App_user.username != uname).all()

    if request.args.get("post_id")!=None and request.args.get("like")!=None:
        post_id = request.args.get("post_id")
        q = Likes(post_ID=post_id, liked_by_userID = current_user.id)
        db.session.add(q)
        db.session.commit()
        q = Post.query.filter_by(post_id=post_id).first()
        q.number_of_likes = q.number_of_likes + 1
        db.session.add(q)
        db.session.commit()
        return redirect("/feed")

    if request.args.get("post_id")!=None and request.args.get("unlike")!=None:
        post_id = request.args.get("post_id")
        q = Likes.query.filter(Likes.post_ID==post_id, Likes.liked_by_userID==current_user.id).first()
        db.session.delete(q)
        db.session.commit()
        q = Post.query.filter_by(post_id=post_id).first()
        q.number_of_likes = q.number_of_likes - 1
        db.session.add(q)
        db.session.commit()
        return redirect("/feed")

    posts_liked_by_user = Likes.query.filter_by(liked_by_userID = current_user.id).all()
    # posts_of_following_users = Post.query.join(Follower, Post.ID == Follower.following_ID).filter(Follower.ID == current_user.id)
    posts_of_following_users = db.session.query(Post).join(Follower, Post.ID == Follower.following_ID).filter(Follower.ID == current_user.id).order_by(Post.time_stamp)

    return render_template("feed.html", users = other_users, posts=posts_of_following_users, posts_liked_by_user = posts_liked_by_user)

@app.route("/feed/<user>")
@login_required
def profile_others(user):  
    q = App_user.query.filter_by(username = user).first_or_404()

    if request.args.get("follow")!=None:
        follow_query = Follower(ID = current_user.id, following_ID = q.id)
        db.session.add(follow_query)
        db.session.commit()
        return redirect("/feed/"+user)
    if request.args.get("unfollow")!=None:
        query = Follower.query.filter(Follower.ID == current_user.id, Follower.following_ID == q.id).first()
        db.session.delete(query)
        db.session.commit()
        return redirect("/feed/"+user)

    isfollow = db.session.query(Follower).filter(Follower.ID == current_user.id, Follower.following_ID == q.id).count()
    following = Follower.query.filter_by(ID = q.id).count()
    followers = Follower.query.filter_by(following_ID = q.id).count()
    posts = Post.query.filter(Post.ID == q.id).all()
    other_users = App_user.query.filter(App_user.username != current_user.username).all()

    return render_template("others_profile.html",users = other_users, user = q, isfollow = isfollow, followers = followers, following = following, posts = posts)

@app.route("/feed/search", methods = ["GET", "POST"])
@login_required
def search():
    return render_template("search.html")


@app.route("/profile", methods = ["GET", "POST"])
@login_required
def profile():
    if request.args.get("search")!=None:
        user = request.form['uname_req']
        s = "/feed/" + user
        return redirect(s)

    if request.args.get("deleted")!=None:
        id = request.args.get("deleted")
        q = Post.query.filter(Post.post_id == id).first()
        os.remove("static/"+q.image_path)
        db.session.delete(q)
        db.session.commit()
        return redirect("/profile")

    other_users = App_user.query.filter(App_user.username != current_user.username).all()
    following = Follower.query.filter_by(ID = current_user.id).count()
    followers = Follower.query.filter_by(following_ID = current_user.id).count()
    posts = Post.query.filter(Post.ID == current_user.id).all()

    return render_template("profile.html", users = other_users, follower = followers, following = following, post = posts)


@app.route("/profile/add_post", methods = ["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        pic = request.files["file"]
        desc = request.form["desc"]

        pic_filename = secure_filename(pic.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        pic.save(os.path.join("static/", pic_name))

        thumbnail = Image.open("static/"+ pic_name)
        size = (406, 406)
        # generating the thumbnail from given size
        thumbnail.thumbnail(size, Image.ANTIALIAS)

        offset_x = int(max((size[0] - thumbnail.size[0]) / 2, 0))
        offset_y = int(max((size[1] - thumbnail.size[1]) / 2, 0))
        offset_tuple = (offset_x, offset_y) #pack x and y into a tuple

        # create the image object to be the final product
        final_thumb = Image.new(mode='RGBA',size=size,color=(255,255,255,0))
        # paste the thumbnail into the full sized image
        final_thumb.paste(thumbnail, offset_tuple)
        # save (the PNG format will retain the alpha band unlike JPEG)
        final_thumb.save("static/"+ pic_name,'PNG')

        q = Post(ID = current_user.id, username = current_user.username, image_path = pic_name, description = desc)
        db.session.add(q)
        db.session.commit()
        return redirect("/profile")

    return render_template("add_post.html")

@app.route("/profile/edit", methods = ["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        user_pass = current_user.password
        x = request.form["old_pwd"]
        x = bytes(x, 'utf-8')

        if bcrypt.checkpw(x, user_pass) == False:
            return redirect("/profile/edit?invalid")

        pwd_new = False
        image = False
        fname = request.form["fname"]
        lname = request.form["lname"]
        pfp = request.files['pfp']
        # pwd = request.form["new_pwd"]
        pwd = request.form.get('new_pwd', None)
        q = App_user.query.filter(App_user.id == current_user.id).first()
        
        if(pwd != None):
            new_pass = request.form['new_pwd']
            pwd = bytes(new_pass, 'utf-8')
            pwd = bcrypt.hashpw(pwd, salt)
            pwd_new = True
        if(pfp.filename!=""):
            print("hi")
            image = True
            # pfp = request.files['pfp']
            image_filename = secure_filename(pfp.filename)
            pic_name = str(uuid.uuid1()) + "_" + image_filename

            pfp.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            
            os.remove("static/images/"+q.profile_pic)

            if(pwd_new):
                q.first_name = fname
                q.last_name = lname
                q.password = pwd
                q.profile_pic = pic_name
                db.session.commit()
            else:
                q.first_name = fname
                q.last_name = lname
                q.profile_pic = pic_name
                db.session.commit()
        else:
            if(pwd_new):
                q.first_name = fname
                q.last_name = lname
                q.password = pwd
                db.session.commit()
            else:
                q.first_name = fname
                q.last_name = lname
                db.session.commit()
        return redirect("/profile")

    if request.args.get("invalid")!=None:
        return render_template("edit_profile.html", condition = "fail")
    return render_template("edit_profile.html")

@app.route("/profile/followers")
@login_required
def display_followers():
    other_users = App_user.query.filter(App_user.username != current_user.username).all()
    followers = db.session.query(App_user).join(Follower, App_user.id == Follower.ID).filter(Follower.following_ID == current_user.id).all()
    return render_template("followers.html", followers = followers, users = other_users)

@app.route("/profile/following")
@login_required
def display_following():
    other_users = App_user.query.filter(App_user.username != current_user.username).all()
    following = db.session.query(App_user).join(Follower, App_user.id == Follower.following_ID).filter(Follower.ID == current_user.id).all()
    return render_template("following.html", following = following, users = other_users)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")    

if __name__ == '__main__':
    db.create_all()
    app.run(host="192.168.29.203", debug= True)
    # app.run(debug = True)