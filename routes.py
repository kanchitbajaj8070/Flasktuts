from flask import render_template, url_for, flash,abort, redirect,request
from flaskblog import app, db,bcrypt,login_manager
from flaskblog.forms import RegistrationForm, LoginForm,UpdateAccountForm,PostForm
from flaskblog.models import User, Post
from PIL import Image
from flask_login import login_user, current_user, logout_user,login_required
import os,secrets
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer# used in reset password

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.route("/")
@app.route("/home")
def hello():
    page=request.args.get('page',default=1,type=int)# asking the web page on which page are we
    #http://127.0.0.1:5000/?page=2
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(per_page=2,page=page)
    return render_template('Homepage.html', posts=posts)

@app.route("/Contactus")
def contactus():
    return render_template('Contactus.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('hello'))
    for e in User.query.all():
        print(e)
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        db.session.add(User(username=form.username.data,password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),email=form.email.data,image_file='default.jpg'))
        db.session.commit()
        flash(f'your account has been created you can now log in','success')
        return redirect(url_for('login'))
    return render_template('Register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('hello'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and  bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # login back to aacount if it requires login
            next_page=request.args.get('next')
            if next_page:
                return redirect(next_page)# redirecting to a page if it requires a login
            else:
               return redirect(url_for('hello'))
            return redirect(url_for('hello'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('Login.html', title='Login', form=form)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('hello'))
def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    f_name,f_ext=os.path.split(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/profile_pics',picture_fn)
    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    #form_picture.save(picture_fn)
    return picture_fn


@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file=picture_file
        current_user.username=form.username.data
        current_user.email=form.email.data# direct updation on database
        db.session.commit()
        flash('Your account has been updated!!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':#setting intial values
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html',image_file=image_file,form=form)

@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.commit()
        flash('your past has been created !!!','success')
        return redirect(url_for('hello'))
    return render_template('create_post.html',form=form,legend=" New Post")

@app.route("/post/<int:post_id>")
def post(post_id):
    post=Post.query.get_or_404(post_id)# if doesnt exist then 404
    return render_template('post.html',post=post)

@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def post_update(post_id):
    form = PostForm()
    post=Post.query.get_or_404(post_id)# if doesnt exist then 404
    if post.author.username!=current_user.username:
        abort(403)# forbidden operation
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash('Your post has been updated','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method=='GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', form=form,legend="Update Post")
@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    form = PostForm()
    post=Post.query.get_or_404(post_id)# if doesnt exist then 404
    if post.author.username!=current_user.username:
        abort(403)# forbidden operation
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully', 'info')
    return redirect(url_for('hello'))
@app.route("/user/<username>")
def user_posts(username):
    page=request.args.get('page',default=1,type=int)# asking the web page on which page are we
    #http://127.0.0.1:5000/?page=2
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc()).paginate(per_page=2,page=page)
    return render_template('user_posts.html', posts=posts,user=user)
