import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 配置
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RECIPE_IMAGES_PATH'], exist_ok=True)
    os.makedirs(app.config['USER_AVATARS_PATH'], exist_ok=True)
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.recipes import recipes_bp
    from app.routes.meal_plans import meal_plans_bp
    from app.routes.ingredients import ingredients_bp
    from app.routes.shopping_lists import shopping_lists_bp
    from app.routes.nutrition import nutrition_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    app.register_blueprint(meal_plans_bp, url_prefix='/api/meal-plans')
    app.register_blueprint(ingredients_bp, url_prefix='/api/ingredients')
    app.register_blueprint(shopping_lists_bp, url_prefix='/api/shopping-lists')
    app.register_blueprint(nutrition_bp, url_prefix='/api/nutrition')
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'The requested resource was not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error', 'message': 'An internal error occurred'}, 500
    
    # 根路由
    @app.route('/')
    def index():
        return {
            'message': '家庭食谱与膳食规划应用 API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'recipes': '/api/recipes',
                'meal_plans': '/api/meal-plans',
                'ingredients': '/api/ingredients',
                'shopping_lists': '/api/shopping-lists',
                'nutrition': '/api/nutrition'
            }
        }
    
    # 健康检查
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'timestamp': db.session.execute(db.text('SELECT CURRENT_TIMESTAMP')).scalar()}
    
    return app

# 导入模型
from app import models