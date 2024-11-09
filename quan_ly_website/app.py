from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer  # Sửa ở đây
from werkzeug.security import generate_password_hash, check_password_hash
from flask_caching import Cache

from models import db, User  # Import từ models.py
import api  # Import API blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:huyng1234@localhost:5432/quan_ly_website'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Khởi tạo các thành phần
db.init_app(app)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
mail = Mail(app)

# Đăng ký blueprint API
app.register_blueprint(api.api, url_prefix='/api')

# Route cho trang chủ
@app.route('/')
def home():
    users = User.query.all()  # Lấy danh sách người dùng từ cơ sở dữ liệu
    return render_template('index.html', users=users)  # Truyền danh sách người dùng vào template


# Route cho đăng ký (có thể sửa đổi để admin có thể chỉ định vai trò)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form.get('role', 'user')  # Vai trò mặc định là 'user'
        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Route cho đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('manage'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')
    return render_template('login.html')

# Route cho quản lý người dùng
@app.route('/manage')
def manage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Kiểm tra quyền truy cập
    if user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này.', 'danger')
        return redirect(url_for('home'))  # Hoặc redirect tới một trang khác

    users = User.query.all()  # Lấy danh sách người dùng
    return render_template('manage.html', users=users)


# Route cho đăng xuất
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Route cho đặt lại mật khẩu
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()
            msg = Message('Đặt lại mật khẩu', sender='your_email@gmail.com', recipients=[email])
            msg.body = f'''
                Để đặt lại mật khẩu của bạn, vui lòng nhấp vào liên kết sau:
                {url_for('reset_token', token=token, _external=True)}
            '''
            mail.send(msg)
        return redirect(url_for('login'))
    return render_template('reset_password.html')

# Route cho xác nhận token đặt lại mật khẩu
@app.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        return redirect(url_for('login'))
    if request.method == 'POST':
        password = request.form['password']
        user.password = generate_password_hash(password)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('reset_token.html')

# Route cho trang người dùng
@app.route('/user_profile')
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Người dùng thông thường có thể truy cập
    return render_template('user_profile.html', user=user)

# Route cho trang quản trị viên
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Chỉ admin mới có quyền truy cập
    if user.role != 'admin':
        flash('Bạn không có quyền truy cập trang này.', 'danger')
        return redirect(url_for('home'))

    return render_template('admin_dashboard.html')

# Route cho trang xem thông tin người dùng
@app.route('/view_profile')
def view_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Kiểm tra xem người dùng có tồn tại không
    if user is None:
        flash('Người dùng không tồn tại.', 'danger')
        return redirect(url_for('home'))

    return render_template('view_profile.html', user=user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tạo lại bảng
    app.run(debug=True)