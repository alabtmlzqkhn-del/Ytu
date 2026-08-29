import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "CHANGE-THIS-TO-A-LONG-RANDOM-SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///site.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
app.config["MAX_CONTENT_LENGTH"] = 300 * 1024 * 1024
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    mimetype = db.Column(db.String(100), nullable=False)

def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None

def login_required(admin=False):
    def deco(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user: return redirect(url_for("login"))
            if admin and not user.is_admin: abort(403)
            return fn(*args, **kwargs)
        return wrapped
    return deco

@app.route("/")
@login_required()
def index():
    return render_template("index.html", media=Media.query.order_by(Media.id.desc()).all(), user=current_user())

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user(): return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash,password):
            session.clear(); session["user_id"] = user.id
            return redirect(url_for("index"))
        flash("الإيميل أو كلمة المرور غير صحيحة")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("login"))

@app.route("/admin")
@login_required(admin=True)
def admin():
    return render_template("admin.html", users=User.query.all(), media=Media.query.order_by(Media.id.desc()).all(), user=current_user())

@app.route("/admin/users", methods=["POST"])
@login_required(admin=True)
def add_user():
    email=request.form.get("email","").strip().lower()
    password=request.form.get("password","")
    if not email or not password: flash("اكتب الإيميل والباسورد")
    elif User.query.filter_by(email=email).first(): flash("هذا الإيميل موجود")
    else:
        db.session.add(User(email=email,password_hash=generate_password_hash(password)))
        db.session.commit(); flash("تمت إضافة المستخدم")
    return redirect(url_for("admin"))

@app.route("/admin/upload", methods=["POST"])
@login_required(admin=True)
def upload():
    title=request.form.get("title","بدون عنوان").strip()
    f=request.files.get("file")
    if not f or not f.filename:
        flash("اختر ملفاً"); return redirect(url_for("admin"))
    filename=secure_filename(f.filename)
    root,ext=os.path.splitext(filename)
    unique=f"{root}_{os.urandom(6).hex()}{ext}"
    f.save(os.path.join(app.config["UPLOAD_FOLDER"],unique))
    db.session.add(Media(title=title,filename=unique,mimetype=f.mimetype or "application/octet-stream"))
    db.session.commit(); flash("تم رفع المحتوى")
    return redirect(url_for("admin"))

@app.route("/media/<int:media_id>")
@login_required()
def media_file(media_id):
    item=db.session.get(Media,media_id)
    if not item: abort(404)
    return send_from_directory(app.config["UPLOAD_FOLDER"],item.filename)

@app.route("/admin/media/<int:media_id>/delete",methods=["POST"])
@login_required(admin=True)
def delete_media(media_id):
    item=db.session.get(Media,media_id)
    if item:
        path=os.path.join(app.config["UPLOAD_FOLDER"],item.filename)
        if os.path.exists(path): os.remove(path)
        db.session.delete(item); db.session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/users/<int:user_id>/delete",methods=["POST"])
@login_required(admin=True)
def delete_user(user_id):
    user=db.session.get(User,user_id)
    if user and not user.is_admin:
        db.session.delete(user); db.session.commit()
    return redirect(url_for("admin"))

if __name__=="__main__":
    with app.app_context():
        db.create_all()
        email=os.environ.get("ADMIN_EMAIL","moamel").lower()
        password=os.environ.get("ADMIN_PASSWORD","moamel")
        if not User.query.filter_by(email=email).first():
            db.session.add(User(email=email,password_hash=generate_password_hash(password),is_admin=True))
            db.session.commit()
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
