# 测试Python环境和依赖包
import sys
print("Python版本:", sys.version)
print("Python路径:", sys.executable)

try:
    import flask
    print("✅ Flask已安装，版本:", flask.__version__)
except ImportError:
    print("❌ Flask未安装")

try:
    from flask_sqlalchemy import SQLAlchemy
    print("✅ Flask-SQLAlchemy已安装")
except ImportError:
    print("❌ Flask-SQLAlchemy未安装")

try:
    from flask_jwt_extended import JWTManager
    print("✅ Flask-JWT-Extended已安装")
except ImportError:
    print("❌ Flask-JWT-Extended未安装")

try:
    from flask_login import LoginManager
    print("✅ Flask-Login已安装")
except ImportError:
    print("❌ Flask-Login未安装")

try:
    from flask_cors import CORS
    print("✅ Flask-CORS已安装")
except ImportError:
    print("❌ Flask-CORS未安装")

try:
    from flask_migrate import Migrate
    print("✅ Flask-Migrate已安装")
except ImportError:
    print("❌ Flask-Migrate未安装")

print("\n环境检查完成！")