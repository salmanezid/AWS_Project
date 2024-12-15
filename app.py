from flask import Flask,render_template,url_for,request,redirect,session,send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
import boto3
from io import BytesIO
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Initialize the S3 client
s3_client = boto3.client('s3')

# Bucket name
BUCKET_NAME = 'myimages52'
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'ljhgjhvhg87665544@zrfhbé54'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')
def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def format_bytes(size):

    if size < 0:
        raise ValueError("Size cannot be negative")

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}" if unit != "Bytes" else f"{size:.0f} {unit}"
        size /= 1024


def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension[1:].lower()  # Remove the dot and return in lowercase

class Account(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150),unique=True, nullable=False)
    password = db.Column(db.String(200),nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))
#@app.route('/register',methods=['POST','GET'])


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')
        user = Account.query.filter_by(username=username).first()
        if user and check_password(str(password),user.password):
            login_user(user)
            return redirect("/")
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')
@app.route('/download/<filename>')
@login_required
def download_file(filename):
    try:
        s3_object = s3_client.get_object(Bucket=BUCKET_NAME, Key=filename)
        file_content = s3_object['Body'].read()
        return send_file(
            BytesIO(file_content),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return f"Erreur lors du téléchargement du fichier : {e}", 500
@app.route('/Delete/<filename>')
@login_required
def delete_file(filename):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
        return redirect("/")
    except:
        return redirect("/")

@app.route('/upload',methods=['POST','GET'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400

        file = request.files['file']

        if file.filename == '':
            return 'No selected file', 400

        try:
            # Upload the file directly from memory to S3
            s3_client.upload_fileobj(
                file,  # File object from request.files
                BUCKET_NAME,  # S3 bucket name
                file.filename  # Destination key in S3
            )
            return redirect('/')
        except Exception as e:
            return f"An error occurred: {e}", 500
    else:
        return render_template('upload.html')

@app.route('/',methods=['POST','GET'])
@login_required
def dashboard():
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    for i in range(len(response["Contents"])):
        response["Contents"][i]["Size"]=format_bytes(response["Contents"][i]["Size"])
        response["Contents"][i]["extention"]=get_file_extension(response["Contents"][i]["Key"])
    return render_template('dashboard.html',data=response["Contents"])
@app.route('/accounts',methods=['POST','GET'])
@login_required
def accounts():
    if request.method =='POST':
        new_account=Account(username=request.form['username'],password=hash_password(request.form['pwd']))
        try:
            db.session.add(new_account)
            db.session.commit()
            return redirect("/accounts")
        except:

            return "account errer"

    else:
        accounts = Account.query.order_by(Account.date_creation).all()
        return render_template('account.html', accounts=accounts)
@app.route('/delete-acc/<int:id>')
@login_required
def delete_account(id):
    acc_to_delete=Account.query.get_or_404(id)
    try:
        db.session.delete(acc_to_delete)
        db.session.commit()

        return redirect('/accounts')
    except:
        redirect('/')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0')