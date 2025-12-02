# 膳食营养健康系统详细设计文档

## 1. 概述

### 1.1 文档目的
本文档基于系统需求规格说明书和概要设计文档，提供膳食营养健康系统的详细设计方案，包括系统架构、模块设计、数据结构、算法实现、文件目录结构等关键技术细节，为开发团队提供具体的实现指导。

### 1.2 术语定义
- **用户**：使用系统的个人，可以是普通用户或管理员
- **膳食记录**：用户记录的每日饮食信息，包括食物名称、份量、用餐时间等
- **营养素**：食物中含有的对人体有益的成分，如蛋白质、脂肪、碳水化合物、维生素、矿物质等
- **营养需求**：根据用户的年龄、性别、体重、活动水平等因素计算得出的每日所需营养素摄入量
- **膳食推荐**：系统根据用户的营养需求和偏好生成的饮食建议
- **营养分析**：对用户的膳食记录进行数据分析，评估其营养摄入是否均衡
- **JWT**：JSON Web Token，用于身份认证的安全令牌
- **ORM**：对象关系映射，用于数据库操作的编程技术

## 2. 系统架构详细设计

### 2.1 整体架构设计
系统采用前后端分离的分层架构设计，确保系统的可维护性、可扩展性和高性能。整体架构由以下几个主要层次组成：

```
用户交互层 → 前端应用层 → API网关层 → 后端服务层 → 数据持久层 → 第三方服务层
```

- **用户交互层**：包括PC浏览器、移动设备浏览器等用户交互界面
- **前端应用层**：基于Vue.js构建的单页应用(SPA)，负责UI渲染和用户交互
- **API网关层**：处理请求路由、负载均衡、认证授权、限流等功能
- **后端服务层**：Django应用，实现业务逻辑和数据处理
- **数据持久层**：PostgreSQL数据库和Redis缓存，负责数据存储和高速访问
- **第三方服务层**：提供短信验证、文件存储等辅助功能

### 2.2 前端架构详细设计

#### 2.2.1 技术栈
- **框架**：Vue.js 3.x
- **状态管理**：Pinia
- **路由管理**：Vue Router 4.x
- **UI组件库**：Element Plus
- **HTTP客户端**：Axios
- **图表库**：ECharts 5.x
- **构建工具**：Vite
- **CSS预处理器**：SCSS
- **类型检查**：TypeScript（可选）

#### 2.2.2 前端架构组件
- **App.vue**：应用入口组件，负责全局布局和主题配置
- **路由配置**：管理应用页面路由和权限控制
- **状态管理**：使用Pinia管理全局状态，包括用户信息、应用设置等
- **API服务**：封装Axios请求，统一处理API调用
- **公共组件**：可复用的UI组件，如表单、对话框、表格等
- **业务组件**：特定业务功能的组件，如膳食记录表单、营养分析图表等
- **工具函数**：通用的辅助函数库

#### 2.2.3 前端目录结构（详细结构见第6章）
```
frontend/
├── src/
│   ├── assets/        # 静态资源
│   ├── components/    # 公共组件
│   ├── views/         # 页面组件
│   ├── store/         # Pinia状态管理
│   ├── router/        # Vue Router配置
│   ├── services/      # API服务
│   ├── utils/         # 工具函数
│   ├── hooks/         # 自定义钩子
│   ├── styles/        # 全局样式
│   ├── plugins/       # 插件配置
│   ├── App.vue        # 根组件
│   └── main.js        # 入口文件
```

### 2.3 后端架构详细设计

#### 2.3.1 技术栈
- **Web框架**：Django 4.x
- **REST API**：Django REST Framework 3.14+
- **认证授权**：JWT (JSON Web Token)
- **任务调度**：Celery 5.x
- **消息队列**：Redis（用于Celery）
- **缓存**：Redis
- **ORM**：Django ORM
- **验证工具**：Django Validators
- **API文档**：Swagger/OpenAPI 3.0

#### 2.3.2 后端架构组件
- **URL路由**：管理API端点和视图函数映射
- **视图层**：处理HTTP请求，返回HTTP响应
- **序列化器**：处理数据序列化和反序列化
- **模型层**：定义数据库模型和业务逻辑
- **权限系统**：实现基于角色的访问控制(RBAC)
- **中间件**：处理请求前置和后置逻辑，如认证、日志等
- **服务层**：封装复杂业务逻辑
- **工具模块**：提供通用功能支持

#### 2.3.3 后端目录结构（详细结构见第6章）
```
backend/
├── config/            # Django配置
├── apps/              # 应用模块
│   ├── users/         # 用户管理模块
│   ├── meals/         # 膳食管理模块
│   ├── nutrition/     # 营养分析模块
│   ├── authentication/ # 认证授权模块
│   └── upload/        # 文件上传模块
├── core/              # 核心功能模块
├── utils/             # 工具函数
├── middleware/        # 自定义中间件
├── tasks/             # Celery任务
├── api/               # API定义
├── requirements.txt   # 依赖列表
└── manage.py          # 管理脚本
```

### 2.4 数据层详细设计

#### 2.4.1 数据库设计
- **主数据库**：PostgreSQL 14.x
- **数据库连接池**：使用Django内置连接池或pgBouncer
- **数据库索引策略**：基于查询频率和性能需求设计索引
- **数据分区**：对大表进行分区处理，提高查询性能

#### 2.4.2 缓存设计
- **缓存技术**：Redis 6.x+
- **缓存策略**：
  - 食物数据库缓存（TTL: 24小时）
  - 用户会话缓存（TTL: 会话有效期）
  - 热门食谱缓存（TTL: 1小时）
  - 营养推荐缓存（TTL: 用户下次登录）
- **缓存失效策略**：使用发布订阅机制实现缓存一致性

#### 2.4.3 文件存储设计
- **存储服务**：阿里云OSS
- **存储结构**：
  - 用户头像：`avatars/{user_id}/{filename}`
  - 食谱图片：`recipes/{recipe_id}/{filename}`
  - 营养报告：`reports/{user_id}/{date}/{filename}`
- **访问控制**：通过预签名URL提供安全访问

### 2.5 系统交互流程详细设计

#### 2.5.1 用户认证流程
```
用户 → 前端登录页面 → 提交登录凭证 → API网关 → 认证服务 → 验证凭证 → 生成JWT → 返回JWT → 前端存储JWT → 后续请求携带JWT
```

#### 2.5.2 膳食记录创建流程
```
用户 → 前端膳食记录页面 → 选择食物 → 输入份量 → 提交记录 → API网关 → 膳食管理服务 → 验证数据 → 保存记录 → 触发营养分析 → 返回创建结果 → 前端更新界面
```

#### 2.5.3 营养分析流程
```
用户请求分析 → 前端发起请求 → API网关 → 营养分析服务 → 查询膳食数据 → 计算营养摄入 → 对比推荐标准 → 生成分析报告 → 缓存结果 → 返回分析数据 → 前端展示结果
```

#### 2.5.4 异步任务处理流程
```
触发异步任务 → 任务入队(Celery) → 工作节点处理 → 执行业务逻辑 → 更新数据库/发送通知 → 任务完成
```

## 3. 核心模块详细设计

### 3.1 用户管理模块详细设计

#### 3.1.1 模块概述
用户管理模块负责用户注册、登录、个人信息管理、健康档案管理等核心功能，是系统的基础模块。

#### 3.1.2 类图设计

```
+----------------+       +-------------------+
|     User       |<------| UserHealthProfile |
+----------------+       +-------------------+
| id             |       | id                |
| username       |       | user_id           |
| phone_number   |       | activity_level    |
| email          |       | health_goal       |
| password_hash  |       | dietary_preference|
| avatar         |       | special_needs     |
| gender         |       | food_allergies    |
| birth_date     |       | calorie_target    |
| height         |       +-------------------+
| weight         |
| bmi            |
| role           |
| status         |
| created_at     |
| updated_at     |
| last_login     |
+----------------+
         ^
         |
+----------------+
| UserService    |
+----------------+
| create_user()  |
| authenticate() |
| update_profile()|
| get_user()     |
| update_health_data()|
+----------------+
```

#### 3.1.3 数据结构设计

```python
# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField

class User(AbstractUser):
    # 基本信息扩展
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=[('male', '男'), ('female', '女'), ('other', '其他')])
    birth_date = models.DateField(null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="身高(cm)")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="体重(kg)")
    bmi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="BMI指数")
    
    # 系统相关
    role = models.CharField(max_length=20, default='user', choices=[('user', '普通用户'), ('nutritionist', '营养师'), ('admin', '管理员')])
    status = models.CharField(max_length=20, default='active', choices=[('active', '正常'), ('frozen', '冻结'), ('deleted', '已删除')])
    
    # 覆盖Django默认字段
    email = models.EmailField(unique=True, null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['status']),
        ]

class UserHealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile')
    activity_level = models.CharField(max_length=50, null=True, blank=True, 
                                     choices=[('sedentary', '久坐'), ('lightly_active', '轻度活动'), 
                                              ('moderately_active', '中度活动'), ('very_active', '高度活动'), 
                                              ('extra_active', '极高活动')])
    health_goal = models.CharField(max_length=100, null=True, blank=True,
                                 choices=[('maintain', '维持体重'), ('lose', '减重'), ('gain', '增肌'), ('improve', '改善健康')])
    dietary_preference = models.CharField(max_length=100, null=True, blank=True)
    special_dietary_needs = ArrayField(models.TextField(), null=True, blank=True)
    food_allergies = ArrayField(models.TextField(), null=True, blank=True)
    daily_calorie_target = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_health_profiles'

class UserLoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    login_ip = models.GenericIPAddressField(null=True, blank=True)
    login_device = models.CharField(max_length=255, null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='success', choices=[('success', '成功'), ('failed', '失败')])
    
    class Meta:
        db_table = 'user_login_logs'
        indexes = [
            models.Index(fields=['user', 'login_time']),
        ]
```

#### 3.1.4 核心算法实现

##### 3.1.4.1 BMI计算算法
```python
def calculate_bmi(height, weight):
    """计算BMI指数
    
    Args:
        height: 身高(cm)
        weight: 体重(kg)
    
    Returns:
        float: BMI指数
    """
    if not height or not weight or height <= 0 or weight <= 0:
        return None
    
    # BMI = 体重(kg) / 身高(m)^2
    height_m = height / 100
    bmi = weight / (height_m * height_m)
    return round(bmi, 2)
```

##### 3.1.4.2 基础代谢率(BMR)计算算法
```python
def calculate_bmr(gender, weight, height, age):
    """使用Mifflin-St Jeor公式计算基础代谢率
    
    Args:
        gender: 性别
        weight: 体重(kg)
        height: 身高(cm)
        age: 年龄
    
    Returns:
        float: 基础代谢率(kcal/天)
    """
    if not all([gender, weight, height, age]) or weight <= 0 or height <= 0 or age <= 0:
        return None
    
    if gender == 'male':
        # 男性: BMR = 10 × 体重(kg) + 6.25 × 身高(cm) - 5 × 年龄 + 5
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        # 女性: BMR = 10 × 体重(kg) + 6.25 × 身高(cm) - 5 × 年龄 - 161
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    return round(bmr, 2)
```

##### 3.1.4.3 每日热量需求计算算法
```python
def calculate_daily_calories(bmr, activity_level, health_goal):
    """根据基础代谢率、活动水平和健康目标计算每日热量需求
    
    Args:
        bmr: 基础代谢率
        activity_level: 活动水平
        health_goal: 健康目标
    
    Returns:
        float: 每日热量目标
    """
    if not bmr:
        return None
    
    # 活动水平系数
    activity_factors = {
        'sedentary': 1.2,           # 久坐
        'lightly_active': 1.375,    # 轻度活动
        'moderately_active': 1.55,  # 中度活动
        'very_active': 1.725,       # 高度活动
        'extra_active': 1.9         # 极高活动
    }
    
    # 健康目标调整系数
    goal_adjustments = {
        'lose': 0.85,      # 减重：减少15%
        'maintain': 1.0,   # 维持：不变
        'gain': 1.15,      # 增肌：增加15%
        'improve': 1.0     # 改善健康：不变
    }
    
    activity_factor = activity_factors.get(activity_level, 1.2)
    goal_adjustment = goal_adjustments.get(health_goal, 1.0)
    
    # 计算总热量需求
    total_calories = bmr * activity_factor * goal_adjustment
    return round(total_calories, 2)
```

#### 3.1.5 服务层设计
```python
# services.py
from datetime import datetime
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserHealthProfile, UserLoginLog
from .utils import calculate_bmi, calculate_bmr, calculate_daily_calories

class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_user(username, password, email=None, phone_number=None, **kwargs):
        """创建新用户"""
        # 验证密码强度
        try:
            validate_password(password)
        except ValidationError as e:
            raise Exception(f"密码不符合要求: {', '.join(e.messages)}")
        
        # 检查手机号和邮箱是否已存在
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise Exception("该手机号已被注册")
        if email and User.objects.filter(email=email).exists():
            raise Exception("该邮箱已被注册")
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            phone_number=phone_number,
            **kwargs
        )
        
        # 创建健康档案
        UserHealthProfile.objects.create(user=user)
        
        return user
    
    @staticmethod
    def authenticate_user(login_id, password):
        """用户认证"""
        # 尝试用手机号认证
        user = authenticate(username=login_id, password=password)
        if not user and '@' in login_id:
            # 尝试用邮箱认证
            try:
                user_obj = User.objects.get(email=login_id)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user:
            # 记录登录日志
            UserLoginLog.objects.create(
                user=user,
                status='success'
            )
            # 更新最后登录时间
            user.last_login = datetime.now()
            user.save(update_fields=['last_login'])
            return user
        return None
    
    @staticmethod
    def generate_tokens(user):
        """生成JWT令牌"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    @staticmethod
    def update_user_profile(user, **kwargs):
        """更新用户资料"""
        # 计算BMI（如果提供了身高体重）
        if 'height' in kwargs and 'weight' in kwargs:
            height = kwargs['height']
            weight = kwargs['weight']
            kwargs['bmi'] = calculate_bmi(height, weight)
        
        # 更新用户资料
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.save()
        return user
    
    @staticmethod
    def update_health_profile(user, **kwargs):
        """更新健康档案"""
        profile, created = UserHealthProfile.objects.get_or_create(user=user)
        
        # 计算每日热量目标（如果提供了足够信息）
        if 'activity_level' in kwargs or 'health_goal' in kwargs:
            activity_level = kwargs.get('activity_level', profile.activity_level)
            health_goal = kwargs.get('health_goal', profile.health_goal)
            
            if activity_level and health_goal and user.height and user.weight:
                # 计算年龄
                age = None
                if user.birth_date:
                    today = datetime.now().date()
                    age = today.year - user.birth_date.year - \
                          ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
                
                if age:
                    # 计算BMR和每日热量目标
                    bmr = calculate_bmr(user.gender, user.weight, user.height, age)
                    daily_calories = calculate_daily_calories(bmr, activity_level, health_goal)
                    kwargs['daily_calorie_target'] = daily_calories
        
        # 更新健康档案
        for field, value in kwargs.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        profile.save()
        return profile
```

### 3.2 膳食管理模块详细设计

#### 3.2.1 模块概述
膳食管理模块是系统的核心功能模块，负责食物数据管理、膳食记录、膳食计划制定和食谱管理等功能。

#### 3.2.2 类图设计

```
+----------------+       +----------------+       +----------------+
|      Food      |<------|    FoodItem    |------>|    MealLog     |
+----------------+       +----------------+       +----------------+
| id             |       | id             |       | id             |
| name           |       | meal_log_id    |       | user_id        |
| category       |       | food_id        |       | date           |
| calories       |       | quantity       |       | meal_type      |
| protein        |       | unit           |       | notes          |
| fat            |       | calories       |       +----------------+
| carbohydrate   |       | protein        |              ^
| vitamins       |       | fat            |              |
| minerals       |       | carbohydrate   |              |
+----------------+       +----------------+              |
        ^                                                |
        |                                                |
+----------------+                       +----------------+
|     Recipe     |                       |    MealPlan    |
+----------------+                       +----------------+
| id             |                       | id             |
| title          |                       | user_id        |
| description    |                       | name           |
| ingredients    |                       | start_date     |
| instructions   |                       | end_date       |
| prep_time      |                       | plan_data      |
| cook_time      |                       +----------------+
| servings       |
| calories_per_serving |
+----------------+
```

#### 3.2.3 数据结构设计

```python
# models.py
from django.db import models
from django.contrib.postgres.fields import JSONField

from apps.users.models import User

class Food(models.Model):
    """食物信息"""
    name = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=100, db_index=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2, help_text="热量(kcal/100g)")
    protein = models.DecimalField(max_digits=6, decimal_places=2, help_text="蛋白质含量(g/100g)")
    fat = models.DecimalField(max_digits=6, decimal_places=2, help_text="脂肪含量(g/100g)")
    carbohydrate = models.DecimalField(max_digits=6, decimal_places=2, help_text="碳水化合物含量(g/100g)")
    fiber = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="膳食纤维含量(g/100g)")
    sodium = models.DecimalField(max_digits=7, decimal_places=2, default=0, help_text="钠含量(mg/100g)")
    vitamins = JSONField(default=dict, help_text="维生素含量")
    minerals = JSONField(default=dict, help_text="矿物质含量")
    unit = models.CharField(max_length=20, default="g", help_text="计量单位")
    image_url = models.URLField(null=True, blank=True)
    source = models.CharField(max_length=100, default="system", help_text="数据来源")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'foods'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['name', 'category'], name='unique_food_name_category'),
        ]

class MealLog(models.Model):
    """用户膳食记录"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '加餐'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_logs')
    date = models.DateField(db_index=True)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, db_index=True)
    notes = models.TextField(null=True, blank=True)
    total_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_protein = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_fat = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_carbohydrate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meal_logs'
        indexes = [
            models.Index(fields=['user', 'date', 'meal_type']),
            models.Index(fields=['date']),
        ]

class FoodItem(models.Model):
    """膳食项目"""
    meal_log = models.ForeignKey(MealLog, on_delete=models.CASCADE, related_name='food_items')
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True, blank=True)
    custom_food_data = JSONField(null=True, blank=True, help_text="自定义食物数据")
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20)
    calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    protein = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fat = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    carbohydrate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'food_items'

class MealPlan(models.Model):
    """膳食计划"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    plan_data = JSONField(default=dict, help_text="计划数据，按天和餐次存储")
    is_system_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meal_plans'
        indexes = [
            models.Index(fields=['user', 'start_date', 'end_date']),
        ]

class Recipe(models.Model):
    """食谱信息"""
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)
    ingredients = JSONField(default=list, help_text="食材清单")
    instructions = models.TextField(help_text="烹饪步骤")
    prep_time = models.IntegerField(default=0, help_text="准备时间(分钟)")
    cook_time = models.IntegerField(default=0, help_text="烹饪时间(分钟)")
    servings = models.IntegerField(default=1, help_text="份量")
    calories_per_serving = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    image_url = models.URLField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'recipes'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['created_by']),
            models.Index(fields=['likes_count']),
        ]

class RecipeCollection(models.Model):
    """食谱收藏"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipe_collections')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='collected_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recipe_collections'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_user_recipe_collection'),
        ]
```

#### 3.2.4 核心算法实现

##### 3.2.4.1 食物营养计算算法
```python
def calculate_food_nutrition(food, quantity, unit):
    """根据食物和食用量计算营养成分
    
    Args:
        food: Food对象或自定义食物数据
        quantity: 食用量
        unit: 计量单位
    
    Returns:
        dict: 计算后的营养成分
    """
    # 标准化单位转换（这里简化处理，实际可能需要更复杂的单位转换系统）
    if unit != 'g':
        # 假设其他单位已转换为克
        pass
    
    # 计算比例因子（相对于100g的比例）
    factor = quantity / 100
    
    # 计算营养成分
    if isinstance(food, dict):
        # 自定义食物
        return {
            'calories': round(food.get('calories', 0) * factor, 2),
            'protein': round(food.get('protein', 0) * factor, 2),
            'fat': round(food.get('fat', 0) * factor, 2),
            'carbohydrate': round(food.get('carbohydrate', 0) * factor, 2),
        }
    else:
        # 数据库食物
        return {
            'calories': round(food.calories * factor, 2),
            'protein': round(food.protein * factor, 2),
            'fat': round(food.fat * factor, 2),
            'carbohydrate': round(food.carbohydrate * factor, 2),
        }
```

##### 3.2.4.2 膳食记录汇总计算算法
```python
def calculate_meal_log_totals(meal_log):
    """计算膳食记录的营养总和
    
    Args:
        meal_log: MealLog对象
    
    Returns:
        dict: 营养总和
    """
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbohydrate = 0
    
    # 遍历所有食物项目
    for food_item in meal_log.food_items.all():
        total_calories += food_item.calories
        total_protein += food_item.protein
        total_fat += food_item.fat
        total_carbohydrate += food_item.carbohydrate
    
    return {
        'total_calories': round(total_calories, 2),
        'total_protein': round(total_protein, 2),
        'total_fat': round(total_fat, 2),
        'total_carbohydrate': round(total_carbohydrate, 2),
    }
```

##### 3.2.4.3 膳食计划生成算法
```python
def generate_meal_plan(user, start_date, end_date, preferences=None):
    """生成个性化膳食计划
    
    Args:
        user: 用户对象
        start_date: 开始日期
        end_date: 结束日期
        preferences: 饮食偏好设置
    
    Returns:
        dict: 生成的膳食计划数据
    """
    import random
    from datetime import timedelta
    
    # 获取用户健康档案
    try:
        health_profile = user.health_profile
    except User.health_profile.RelatedObjectDoesNotExist:
        health_profile = None
    
    # 计算每日热量需求
    daily_calories = health_profile.daily_calorie_target if health_profile else 2000
    
    # 餐次热量分配比例（根据健康目标调整）
    if health_profile and health_profile.health_goal == 'lose':
        # 减重目标：早餐占比增加
        meal_ratios = {'breakfast': 0.35, 'lunch': 0.40, 'dinner': 0.20, 'snack': 0.05}
    elif health_profile and health_profile.health_goal == 'gain':
        # 增肌目标：午餐和晚餐占比增加
        meal_ratios = {'breakfast': 0.25, 'lunch': 0.35, 'dinner': 0.30, 'snack': 0.10}
    else:
        # 维持体重：均衡分配
        meal_ratios = {'breakfast': 0.30, 'lunch': 0.40, 'dinner': 0.25, 'snack': 0.05}
    
    # 根据饮食偏好过滤食物
    category_filters = []
    if preferences and preferences.get('dietary_preference') == 'vegetarian':
        category_filters.append('vegetarian')
    
    # 生成计划数据
    plan_data = {}
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        plan_data[date_str] = {}
        
        # 为每个餐次生成食物
        for meal_type, ratio in meal_ratios.items():
            meal_calories = daily_calories * ratio
            
            # 查询适合的食物（这里简化处理，实际需要更复杂的食物选择算法）
            foods = Food.objects.filter(category__in=category_filters) if category_filters else Food.objects.all()
            
            # 随机选择食物并计算合适的份量
            selected_foods = []
            remaining_calories = meal_calories
            
            while remaining_calories > 0 and foods.exists():
                # 随机选择食物
                food = random.choice(foods[:100])  # 限制选择范围提高性能
                
                # 计算合适的份量（基于热量）
                if food.calories > 0:
                    # 控制每份食物不超过剩余热量的40%
                    quantity_needed = min(remaining_calories / food.calories * 100, remaining_calories * 0.4 / food.calories * 100)
                    quantity_needed = max(50, quantity_needed)  # 至少50克
                    
                    selected_foods.append({
                        'food_id': food.id,
                        'food_name': food.name,
                        'quantity': round(quantity_needed, 1),
                        'unit': 'g',
                        'calories': round(food.calories * quantity_needed / 100, 2)
                    })
                    
                    remaining_calories -= food.calories * quantity_needed / 100
                
                # 如果剩余热量较少，退出循环
                if remaining_calories < 50:
                    break
            
            plan_data[date_str][meal_type] = selected_foods
        
        current_date += timedelta(days=1)
    
    return plan_data
```

#### 3.2.5 服务层设计
```python
# services.py
from django.db import transaction
from django.db.models import Q
from datetime import date, datetime

from .models import Food, MealLog, FoodItem, MealPlan, Recipe, RecipeCollection
from .utils import calculate_food_nutrition, calculate_meal_log_totals, generate_meal_plan

class FoodService:
    """食物服务类"""
    
    @staticmethod
    def search_foods(keyword=None, category=None, page=1, page_size=20):
        """搜索食物"""
        queryset = Food.objects.all()
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) | Q(category__icontains=keyword))
        
        # 分类过滤
        if category:
            queryset = queryset.filter(category=category)
        
        # 分页
        total = queryset.count()
        foods = queryset[(page-1)*page_size:page*page_size]
        
        return {
            'foods': list(foods),
            'total': total,
            'page': page,
            'page_size': page_size
        }
    
    @staticmethod
    def create_custom_food(user, **kwargs):
        """创建自定义食物"""
        kwargs['source'] = 'user'
        kwargs['created_by'] = user
        
        return Food.objects.create(**kwargs)

class MealService:
    """膳食服务类"""
    
    @staticmethod
    @transaction.atomic
    def create_meal_log(user, meal_date, meal_type, food_items_data, notes=None):
        """创建膳食记录"""
        # 创建膳食记录
        meal_log = MealLog.objects.create(
            user=user,
            date=meal_date,
            meal_type=meal_type,
            notes=notes
        )
        
        # 添加食物项目
        for item_data in food_items_data:
            # 计算营养成分
            if 'food_id' in item_data:
                food = Food.objects.get(id=item_data['food_id'])
                nutrition = calculate_food_nutrition(food, item_data['quantity'], item_data['unit'])
                food_item = FoodItem.objects.create(
                    meal_log=meal_log,
                    food=food,
                    quantity=item_data['quantity'],
                    unit=item_data['unit'],
                    **nutrition
                )
            else:
                # 自定义食物
                custom_food_data = item_data['custom_food_data']
                nutrition = calculate_food_nutrition(custom_food_data, item_data['quantity'], item_data['unit'])
                food_item = FoodItem.objects.create(
                    meal_log=meal_log,
                    custom_food_data=custom_food_data,
                    quantity=item_data['quantity'],
                    unit=item_data['unit'],
                    **nutrition
                )
        
        # 更新总营养成分
        totals = calculate_meal_log_totals(meal_log)
        for field, value in totals.items():
            setattr(meal_log, field, value)
        meal_log.save()
        
        # 触发营养分析任务（异步）
        from apps.tasks import tasks
        tasks.generate_daily_nutrition_analysis.delay(user.id, meal_date)
        
        return meal_log
    
    @staticmethod
    def get_meal_logs(user, date_from=None, date_to=None, meal_type=None):
        """查询膳食记录"""
        queryset = MealLog.objects.filter(user=user)
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if meal_type:
            queryset = queryset.filter(meal_type=meal_type)
        
        return queryset.order_by('-date', 'meal_type')
    
    @staticmethod
    @transaction.atomic
    def generate_user_meal_plan(user, start_date, end_date, preferences=None):
        """为用户生成膳食计划"""
        # 生成计划数据
        plan_data = generate_meal_plan(user, start_date, end_date, preferences)
        
        # 保存膳食计划
        meal_plan = MealPlan.objects.create(
            user=user,
            name=f'膳食计划-{start_date.strftime("%Y%m%d")}-{end_date.strftime("%Y%m%d")}',
            start_date=start_date,
            end_date=end_date,
            plan_data=plan_data,
            is_system_generated=True
        )
        
        return meal_plan

class RecipeService:
    """食谱服务类"""
    
    @staticmethod
    def search_recipes(keyword=None, ingredients=None, page=1, page_size=20):
        """搜索食谱"""
        queryset = Recipe.objects.all()
        
        # 关键词搜索
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)
        
        # 分页
        total = queryset.count()
        recipes = queryset[(page-1)*page_size:page*page_size]
        
        return {
            'recipes': list(recipes),
            'total': total,
            'page': page,
            'page_size': page_size
        }
    
    @staticmethod
    def create_recipe(user, **kwargs):
        """创建食谱"""
        kwargs['created_by'] = user
        return Recipe.objects.create(**kwargs)
    
    @staticmethod
    def toggle_recipe_collection(user, recipe_id):
        """收藏/取消收藏食谱"""
        recipe = Recipe.objects.get(id=recipe_id)
        
        # 查找是否已收藏
        collection, created = RecipeCollection.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        
        # 如果已收藏，则取消收藏
        if not created:
            collection.delete()
            return False  # 返回False表示取消收藏
        
        return True  # 返回True表示收藏
    
    @staticmethod
    def increment_recipe_views(recipe_id):
        """增加食谱浏览次数"""
        recipe = Recipe.objects.get(id=recipe_id)
        recipe.views_count += 1
        recipe.save(update_fields=['views_count'])
        return recipe
```

### 3.3 营养分析管理模块详细设计

#### 3.3.1 模块概述
营养分析管理模块负责对用户的膳食记录进行营养分析，生成各类营养报告，并提供个性化的营养建议。

#### 3.3.2 类图设计

```
+-------------------+       +---------------------+
|  NutritionAnalysis|<------| NutritionRecommendation|
+-------------------+       +---------------------+
| id                |       | id                  |
| user_id           |       | user_id             |
| analysis_date     |       | calorie_target      |
| total_calories    |       | protein_target      |
| protein_intake    |       | fat_target          |
| fat_intake        |       | carbohydrate_target |
| carbohydrate_intake|      | fiber_target        |
| fiber_intake      |       +---------------------+
| vitamin_intake    |                ^
| mineral_intake    |                |
| calorie_percentage|                |
+-------------------+                |
        ^                            |
        |                            |
+-------------------+       +---------------------+
|  NutritionReport  |       |   NutritionAdvice   |
+-------------------+       +---------------------+
| id                |       | id                  |
| user_id           |       | user_id             |
| report_type       |       | analysis_id         |
| report_date       |       | advice_type         |
| start_date        |       | content             |
| end_date          |       | priority            |
| report_data       |       | is_read             |
+-------------------+       +---------------------+
```

#### 3.3.3 数据结构设计

```python
# models.py
from django.db import models
from django.contrib.postgres.fields import JSONField

from apps.users.models import User

class NutritionAnalysis(models.Model):
    """营养分析记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_analyses')
    analysis_date = models.DateField(db_index=True)
    total_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    protein_intake = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fat_intake = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    carbohydrate_intake = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fiber_intake = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    vitamin_intake = JSONField(default=dict, help_text="维生素摄入")
    mineral_intake = JSONField(default=dict, help_text="矿物质摄入")
    calorie_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="热量达成率")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nutrition_analyses'
        indexes = [
            models.Index(fields=['user', 'analysis_date']),
            models.Index(fields=['analysis_date']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'analysis_date'], name='unique_user_daily_analysis'),
        ]

class NutritionRecommendation(models.Model):
    """营养素推荐标准"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nutrition_recommendation')
    daily_calorie_target = models.DecimalField(max_digits=7, decimal_places=2, default=2000)
    daily_protein_target = models.DecimalField(max_digits=6, decimal_places=2, default=60)
    daily_fat_target = models.DecimalField(max_digits=6, decimal_places=2, default=65)
    daily_carbohydrate_target = models.DecimalField(max_digits=6, decimal_places=2, default=300)
    daily_fiber_target = models.DecimalField(max_digits=6, decimal_places=2, default=25)
    vitamin_targets = JSONField(default=dict, help_text="维生素推荐摄入量")
    mineral_targets = JSONField(default=dict, help_text="矿物质推荐摄入量")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nutrition_recommendations'

class NutritionReport(models.Model):
    """营养报告"""
    REPORT_TYPE_CHOICES = [
        ('daily', '日报'),
        ('weekly', '周报'),
        ('monthly', '月报'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    report_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    report_data = JSONField(default=dict, help_text="报告数据")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'nutrition_reports'
        indexes = [
            models.Index(fields=['user', 'report_type', 'report_date']),
        ]

class NutritionAdvice(models.Model):
    """营养建议"""
    ADVICE_TYPE_CHOICES = [
        ('deficiency', '营养素不足'),
        ('excess', '营养素过量'),
        ('balance', '营养平衡建议'),
        ('goal', '健康目标建议'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_advices')
    analysis = models.ForeignKey(NutritionAnalysis, on_delete=models.CASCADE, related_name='advices', null=True)
    advice_type = models.CharField(max_length=20, choices=ADVICE_TYPE_CHOICES)
    content = models.TextField()
    priority = models.CharField(max_length=20, default='normal', choices=[('high', '高'), ('normal', '中'), ('low', '低')])
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'nutrition_advices'
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'priority']),
        ]
```

#### 3.3.4 核心算法实现

##### 3.3.4.1 营养分析算法
```python
def analyze_daily_nutrition(user, target_date):
    """分析用户指定日期的营养摄入
    
    Args:
        user: 用户对象
        target_date: 目标日期
    
    Returns:
        dict: 营养分析结果
    """
    from apps.meals.models import MealLog
    
    # 获取指定日期的所有膳食记录
    meal_logs = MealLog.objects.filter(user=user, date=target_date)
    
    # 计算总摄入量
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbohydrate = 0
    total_fiber = 0
    vitamin_intake = {}
    mineral_intake = {}
    
    for meal_log in meal_logs:
        total_calories += meal_log.total_calories
        total_protein += meal_log.total_protein
        total_fat += meal_log.total_fat
        total_carbohydrate += meal_log.total_carbohydrate
        
        # 计算纤维和微量营养素（从食物项目中获取）
        for food_item in meal_log.food_items.all():
            # 纤维
            if food_item.food:
                factor = food_item.quantity / 100
                total_fiber += food_item.food.fiber * factor
                
                # 维生素
                for vitamin, amount in food_item.food.vitamins.items():
                    vitamin_intake[vitamin] = vitamin_intake.get(vitamin, 0) + amount * factor
                
                # 矿物质
                for mineral, amount in food_item.food.minerals.items():
                    mineral_intake[mineral] = mineral_intake.get(mineral, 0) + amount * factor
    
    # 获取用户的营养推荐标准
    try:
        recommendation = user.nutrition_recommendation
        calorie_percentage = (total_calories / recommendation.daily_calorie_target * 100) if recommendation.daily_calorie_target > 0 else 0
    except User.nutrition_recommendation.RelatedObjectDoesNotExist:
        calorie_percentage = 0
    
    # 返回分析结果
    return {
        'total_calories': round(total_calories, 2),
        'protein_intake': round(total_protein, 2),
        'fat_intake': round(total_fat, 2),
        'carbohydrate_intake': round(total_carbohydrate, 2),
        'fiber_intake': round(total_fiber, 2),
        'vitamin_intake': {k: round(v, 2) for k, v in vitamin_intake.items()},
        'mineral_intake': {k: round(v, 2) for k, v in mineral_intake.items()},
        'calorie_percentage': round(calorie_percentage, 2),
    }
```

##### 3.3.4.2 营养建议生成算法
```python
def generate_nutrition_advices(user, analysis):
    """基于营养分析生成建议
    
    Args:
        user: 用户对象
        analysis: 营养分析对象
    
    Returns:
        list: 营养建议列表
    """
    advices = []
    
    # 获取用户的营养推荐标准
    try:
        recommendation = user.nutrition_recommendation
    except User.nutrition_recommendation.RelatedObjectDoesNotExist:
        return advices
    
    # 热量摄入建议
    if analysis.calorie_percentage < 80:
        advices.append({
            'advice_type': 'deficiency',
            'content': f'您今日的热量摄入仅达到目标的{analysis.calorie_percentage:.1f}%，建议适当增加食物摄入，特别是富含优质蛋白质的食物。',
            'priority': 'high' if analysis.calorie_percentage < 60 else 'normal'
        })
    elif analysis.calorie_percentage > 120:
        advices.append({
            'advice_type': 'excess',
            'content': f'您今日的热量摄入超过目标的{analysis.calorie_percentage:.1f}%，建议控制食物摄入量，减少高脂肪、高糖分食物的摄入。',
            'priority': 'high' if analysis.calorie_percentage > 140 else 'normal'
        })
    
    # 蛋白质摄入建议
    protein_percentage = (analysis.protein_intake / recommendation.daily_protein_target * 100) if recommendation.daily_protein_target > 0 else 0
    if protein_percentage < 70:
        advices.append({
            'advice_type': 'deficiency',
            'content': '您的蛋白质摄入不足，建议增加鱼、肉、蛋、奶、豆制品等富含优质蛋白质的食物。',
            'priority': 'normal'
        })
    
    # 脂肪摄入建议
    fat_percentage = (analysis.fat_intake / recommendation.daily_fat_target * 100) if recommendation.daily_fat_target > 0 else 0
    if fat_percentage > 120:
        advices.append({
            'advice_type': 'excess',
            'content': '您的脂肪摄入偏高，建议减少油炸食品、肥肉等高脂肪食物，选择橄榄油、坚果等健康脂肪来源。',
            'priority': 'normal'
        })
    
    # 碳水化合物摄入建议
    carb_percentage = (analysis.carbohydrate_intake / recommendation.daily_carbohydrate_target * 100) if recommendation.daily_carbohydrate_target > 0 else 0
    if carb_percentage > 130:
        advices.append({
            'advice_type': 'excess',
            'content': '您的碳水化合物摄入偏高，建议减少精制谷物和添加糖的摄入，增加全谷物、蔬菜等富含膳食纤维的食物。',
            'priority': 'normal'
        })
    
    # 膳食纤维建议
    fiber_percentage = (analysis.fiber_intake / recommendation.daily_fiber_target * 100) if recommendation.daily_fiber_target > 0 else 0
    if fiber_percentage < 50:
        advices.append({
            'advice_type': 'deficiency',
            'content': '您的膳食纤维摄入严重不足，建议多吃全谷物、蔬菜、水果和豆类食物。',
            'priority': 'high'
        })
    elif fiber_percentage < 80:
        advices.append({
            'advice_type': 'deficiency',
            'content': '您的膳食纤维摄入偏低，建议增加蔬菜和水果的摄入。',
            'priority': 'normal'
        })
    
    # 检查微量营养素
    # 这里简化处理，实际应检查各种维生素和矿物质
    
    # 根据健康目标提供建议
    try:
        health_profile = user.health_profile
        if health_profile.health_goal == 'lose' and analysis.calorie_percentage > 110:
            advices.append({
                'advice_type': 'goal',
                'content': '为了达到减重目标，建议适当控制热量摄入，增加运动量。',
                'priority': 'normal'
            })
        elif health_profile.health_goal == 'gain' and analysis.calorie_percentage < 100:
            advices.append({
                'advice_type': 'goal',
                'content': '为了达到增重目标，建议增加热量摄入，特别是优质蛋白质和健康脂肪。',
                'priority': 'normal'
            })
    except:
        pass
    
    return advices
```

##### 3.3.4.3 营养报告生成算法
```python
def generate_nutrition_report(user, report_type, start_date, end_date):
    """生成营养报告
    
    Args:
        user: 用户对象
        report_type: 报告类型 (daily/weekly/monthly)
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        dict: 报告数据
    """
    from datetime import datetime
    from django.db.models import Avg, Sum
    
    # 查询时间范围内的营养分析数据
    analyses = NutritionAnalysis.objects.filter(
        user=user,
        analysis_date__gte=start_date,
        analysis_date__lte=end_date
    ).order_by('analysis_date')
    
    # 获取用户的营养推荐标准
    try:
        recommendation = user.nutrition_recommendation
    except User.nutrition_recommendation.RelatedObjectDoesNotExist:
        recommendation = None
    
    # 计算平均值和总和
    if analyses.exists():
        # 计算平均摄入量
        avg_calories = analyses.aggregate(Avg('total_calories'))['total_calories__avg'] or 0
        avg_protein = analyses.aggregate(Avg('protein_intake'))['protein_intake__avg'] or 0
        avg_fat = analyses.aggregate(Avg('fat_intake'))['fat_intake__avg'] or 0
        avg_carbohydrate = analyses.aggregate(Avg('carbohydrate_intake'))['carbohydrate_intake__avg'] or 0
        avg_fiber = analyses.aggregate(Avg('fiber_intake'))['fiber_intake__avg'] or 0
        
        # 计算总摄入量
        total_calories = analyses.aggregate(Sum('total_calories'))['total_calories__sum'] or 0
        total_protein = analyses.aggregate(Sum('protein_intake'))['protein_intake__sum'] or 0
        total_fat = analyses.aggregate(Sum('fat_intake'))['fat_intake__sum'] or 0
        total_carbohydrate = analyses.aggregate(Sum('carbohydrate_intake'))['carbohydrate_intake__sum'] or 0
    else:
        avg_calories = avg_protein = avg_fat = avg_carbohydrate = avg_fiber = 0
        total_calories = total_protein = total_fat = total_carbohydrate = 0
    
    # 计算营养素摄入达成率
    if recommendation:
        avg_calorie_percentage = (avg_calories / recommendation.daily_calorie_target * 100) if recommendation.daily_calorie_target > 0 else 0
        avg_protein_percentage = (avg_protein / recommendation.daily_protein_target * 100) if recommendation.daily_protein_target > 0 else 0
        avg_fiber_percentage = (avg_fiber / recommendation.daily_fiber_target * 100) if recommendation.daily_fiber_target > 0 else 0
    else:
        avg_calorie_percentage = avg_protein_percentage = avg_fiber_percentage = 0
    
    # 准备趋势数据
    trend_data = []
    for analysis in analyses:
        trend_data.append({
            'date': analysis.analysis_date.strftime('%Y-%m-%d'),
            'calories': float(analysis.total_calories),
            'protein': float(analysis.protein_intake),
            'fat': float(analysis.fat_intake),
            'carbohydrate': float(analysis.carbohydrate_intake),
        })
    
    # 生成报告数据
    report_data = {
        'summary': {
            'report_type': report_type,
            'period': f'{start_date.strftime("%Y-%m-%d")} 至 {end_date.strftime("%Y-%m-%d")}',
            'days_counted': analyses.count(),
            'total_calories': round(total_calories, 2),
            'average_daily_calories': round(avg_calories, 2),
            'calorie_percentage': round(avg_calorie_percentage, 2),
        },
        'average_nutrition': {
            'calories': round(avg_calories, 2),
            'protein': round(avg_protein, 2),
            'fat': round(avg_fat, 2),
            'carbohydrate': round(avg_carbohydrate, 2),
            'fiber': round(avg_fiber, 2),
            'protein_percentage': round(avg_protein_percentage, 2),
            'fiber_percentage': round(avg_fiber_percentage, 2),
        },
        'macronutrient_ratio': {
            'protein': round(avg_protein * 4 / avg_calories * 100, 1) if avg_calories > 0 else 0,
            'fat': round(avg_fat * 9 / avg_calories * 100, 1) if avg_calories > 0 else 0,
            'carbohydrate': round(avg_carbohydrate * 4 / avg_calories * 100, 1) if avg_calories > 0 else 0,
        },
        'trend_data': trend_data,
        'recommendations': [],
    }
    
    # 添加改进建议
    if avg_calorie_percentage < 80:
        report_data['recommendations'].append('您的平均热量摄入不足，建议适当增加食物摄入。')
    elif avg_calorie_percentage > 120:
        report_data['recommendations'].append('您的平均热量摄入过高，建议控制食物摄入量。')
    
    if avg_protein_percentage < 70:
        report_data['recommendations'].append('您的蛋白质摄入不足，建议增加优质蛋白质的摄入。')
    
    if avg_fiber_percentage < 50:
        report_data['recommendations'].append('您的膳食纤维摄入严重不足，建议多吃蔬菜、水果和全谷物。')
    
    return report_data
```

#### 3.3.5 服务层设计
```python
# services.py
from django.db import transaction
from datetime import date, datetime, timedelta

from .models import NutritionAnalysis, NutritionRecommendation, NutritionReport, NutritionAdvice
from .utils import analyze_daily_nutrition, generate_nutrition_advices, generate_nutrition_report

class NutritionService:
    """营养分析服务类"""
    
    @staticmethod
    @transaction.atomic
    def create_or_update_daily_analysis(user, target_date=None):
        """创建或更新每日营养分析"""
        if target_date is None:
            target_date = date.today()
        
        # 分析营养摄入
        analysis_data = analyze_daily_nutrition(user, target_date)
        
        # 创建或更新分析记录
        analysis, created = NutritionAnalysis.objects.update_or_create(
            user=user,
            analysis_date=target_date,
            defaults=analysis_data
        )
        
        # 生成营养建议
        advices_data = generate_nutrition_advices(user, analysis)
        
        # 删除旧的建议
        NutritionAdvice.objects.filter(user=user, analysis=analysis).delete()
        
        # 创建新的建议
        for advice_data in advices_data:
            NutritionAdvice.objects.create(
                user=user,
                analysis=analysis,
                **advice_data
            )
        
        return analysis
    
    @staticmethod
    def get_user_analysis(user, date_from=None, date_to=None):
        """获取用户的营养分析记录"""
        queryset = NutritionAnalysis.objects.filter(user=user)
        
        if date_from:
            queryset = queryset.filter(analysis_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(analysis_date__lte=date_to)
        
        return queryset.order_by('-analysis_date')
    
    @staticmethod
    def create_or_update_recommendation(user, **kwargs):
        """创建或更新营养推荐标准"""
        recommendation, created = NutritionRecommendation.objects.update_or_create(
            user=user,
            defaults=kwargs
        )
        return recommendation
    
    @staticmethod
    def generate_user_report(user, report_type, start_date=None, end_date=None):
        """生成用户营养报告"""
        # 确定日期范围
        if report_type == 'daily':
            if not start_date:
                start_date = date.today() - timedelta(days=1)  # 默认昨天
            end_date = start_date
        elif report_type == 'weekly':
            if not start_date:
                # 默认为上周
                today = date.today()
                start_date = today - timedelta(days=today.weekday() + 7)
                end_date = start_date + timedelta(days=6)
            elif not end_date:
                end_date = start_date + timedelta(days=6)
        elif report_type == 'monthly':
            if not start_date:
                # 默认为上月
                today = date.today()
                if today.month == 1:
                    start_date = date(today.year - 1, 12, 1)
                else:
                    start_date = date(today.year, today.month - 1, 1)
                # 计算月末
                if start_date.month == 12:
                    end_date = date(start_date.year, 12, 31)
                else:
                    end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
            elif not end_date:
                # 计算月末
                if start_date.month == 12:
                    end_date = date(start_date.year, 12, 31)
                else:
                    end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
        
        # 确保日期范围内的每日分析都已生成
        current_date = start_date
        while current_date <= end_date:
            NutritionService.create_or_update_daily_analysis(user, current_date)
            current_date += timedelta(days=1)
        
        # 生成报告数据
        report_data = generate_nutrition_report(user, report_type, start_date, end_date)
        
        # 保存报告
        report = NutritionReport.objects.create(
            user=user,
            report_type=report_type,
            report_date=date.today(),
            start_date=start_date,
            end_date=end_date,
            report_data=report_data
        )
        
        return report
    
    @staticmethod
    def get_user_advices(user, is_read=None, limit=10):
        """获取用户的营养建议"""
        queryset = NutritionAdvice.objects.filter(user=user)
        
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        
        return queryset.order_by('-priority', '-created_at')[:limit]
    
    @staticmethod
    def mark_advice_as_read(advice_id):
        """标记建议为已读"""
        advice = NutritionAdvice.objects.get(id=advice_id)
        advice.is_read = True
        advice.save(update_fields=['is_read'])
        return advice

## 4. 数据库详细设计

### 4.1 数据库表结构设计

#### 4.1.1 用户相关表

**users表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 用户ID |
| username | CharField(150) | UNIQUE NOT NULL | 用户名 |
| first_name | CharField(150) | NULL | 名字 |
| last_name | CharField(150) | NULL | 姓氏 |
| email | EmailField | UNIQUE NULL | 邮箱 |
| phone_number | CharField(20) | UNIQUE NULL | 手机号 |
| password | CharField(128) | NOT NULL | 密码哈希值 |
| avatar | URLField | NULL | 头像URL |
| gender | CharField(10) | NULL | 性别 |
| birth_date | DateField | NULL | 出生日期 |
| height | DecimalField(5,2) | NULL | 身高(cm) |
| weight | DecimalField(5,2) | NULL | 体重(kg) |
| bmi | DecimalField(4,2) | NULL | BMI指数 |
| role | CharField(20) | DEFAULT 'user' | 角色 |
| status | CharField(20) | DEFAULT 'active' | 状态 |
| is_superuser | BooleanField | DEFAULT False | 是否超级用户 |
| is_staff | BooleanField | DEFAULT False | 是否员工 |
| is_active | BooleanField | DEFAULT True | 是否激活 |
| date_joined | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 注册时间 |
| last_login | DateTimeField | NULL | 最后登录时间 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**user_health_profiles表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 健康档案ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| activity_level | CharField(50) | NULL | 活动水平 |
| health_goal | CharField(100) | NULL | 健康目标 |
| dietary_preference | CharField(100) | NULL | 饮食偏好 |
| special_dietary_needs | JSONB | NULL | 特殊饮食需求 |
| food_allergies | JSONB | NULL | 食物过敏 |
| daily_calorie_target | DecimalField(7,2) | NULL | 每日热量目标 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**user_login_logs表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 日志ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| login_ip | GenericIPAddressField | NULL | 登录IP |
| login_device | CharField(255) | NULL | 登录设备 |
| login_time | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 登录时间 |
| logout_time | DateTimeField | NULL | 登出时间 |
| status | CharField(20) | DEFAULT 'success' | 状态 |

#### 4.1.2 食物与膳食相关表

**foods表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 食物ID |
| name | CharField(255) | NOT NULL | 食物名称 |
| category | CharField(100) | NOT NULL | 食物分类 |
| calories | DecimalField(8,2) | NOT NULL | 热量(kcal/100g) |
| protein | DecimalField(6,2) | NOT NULL | 蛋白质含量(g/100g) |
| fat | DecimalField(6,2) | NOT NULL | 脂肪含量(g/100g) |
| carbohydrate | DecimalField(6,2) | NOT NULL | 碳水化合物含量(g/100g) |
| fiber | DecimalField(6,2) | DEFAULT 0 | 膳食纤维含量(g/100g) |
| sodium | DecimalField(7,2) | DEFAULT 0 | 钠含量(mg/100g) |
| vitamins | JSONB | DEFAULT '{}' | 维生素含量 |
| minerals | JSONB | DEFAULT '{}' | 矿物质含量 |
| unit | CharField(20) | DEFAULT 'g' | 计量单位 |
| image_url | URLField | NULL | 图片URL |
| source | CharField(100) | DEFAULT 'system' | 数据来源 |
| created_by | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 创建者 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**meal_logs表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 膳食记录ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| date | DateField | NOT NULL | 记录日期 |
| meal_type | CharField(20) | NOT NULL | 餐次类型 |
| notes | TextField | NULL | 备注 |
| total_calories | DecimalField(8,2) | DEFAULT 0 | 总热量 |
| total_protein | DecimalField(6,2) | DEFAULT 0 | 总蛋白质 |
| total_fat | DecimalField(6,2) | DEFAULT 0 | 总脂肪 |
| total_carbohydrate | DecimalField(6,2) | DEFAULT 0 | 总碳水化合物 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**food_items表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 食物项目ID |
| meal_log_id | BigIntegerField | FOREIGN KEY REFERENCES meal_logs(id) | 膳食记录ID |
| food_id | BigIntegerField | FOREIGN KEY REFERENCES foods(id) | 食物ID |
| custom_food_data | JSONB | NULL | 自定义食物数据 |
| quantity | DecimalField(8,2) | NOT NULL | 数量 |
| unit | CharField(20) | NOT NULL | 单位 |
| calories | DecimalField(8,2) | DEFAULT 0 | 热量 |
| protein | DecimalField(6,2) | DEFAULT 0 | 蛋白质 |
| fat | DecimalField(6,2) | DEFAULT 0 | 脂肪 |
| carbohydrate | DecimalField(6,2) | DEFAULT 0 | 碳水化合物 |

**meal_plans表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 膳食计划ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| name | CharField(255) | NOT NULL | 计划名称 |
| start_date | DateField | NOT NULL | 开始日期 |
| end_date | DateField | NOT NULL | 结束日期 |
| plan_data | JSONB | DEFAULT '{}' | 计划数据 |
| is_system_generated | BooleanField | DEFAULT False | 是否系统生成 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**recipes表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 食谱ID |
| title | CharField(255) | NOT NULL | 食谱标题 |
| description | TextField | NULL | 食谱描述 |
| ingredients | JSONB | DEFAULT '[]' | 食材清单 |
| instructions | TextField | NOT NULL | 烹饪步骤 |
| prep_time | IntegerField | DEFAULT 0 | 准备时间(分钟) |
| cook_time | IntegerField | DEFAULT 0 | 烹饪时间(分钟) |
| servings | IntegerField | DEFAULT 1 | 份量 |
| calories_per_serving | DecimalField(8,2) | DEFAULT 0 | 每份热量 |
| image_url | URLField | NULL | 图片URL |
| created_by | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 创建者 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 更新时间 |
| likes_count | IntegerField | DEFAULT 0 | 点赞数 |
| views_count | IntegerField | DEFAULT 0 | 浏览次数 |

**recipe_collections表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 收藏ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| recipe_id | BigIntegerField | FOREIGN KEY REFERENCES recipes(id) | 食谱ID |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 4.1.3 营养分析相关表

**nutrition_analyses表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 分析ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| analysis_date | DateField | NOT NULL | 分析日期 |
| total_calories | DecimalField(8,2) | DEFAULT 0 | 总热量 |
| protein_intake | DecimalField(6,2) | DEFAULT 0 | 蛋白质摄入量 |
| fat_intake | DecimalField(6,2) | DEFAULT 0 | 脂肪摄入量 |
| carbohydrate_intake | DecimalField(6,2) | DEFAULT 0 | 碳水化合物摄入量 |
| fiber_intake | DecimalField(6,2) | DEFAULT 0 | 膳食纤维摄入量 |
| vitamin_intake | JSONB | DEFAULT '{}' | 维生素摄入 |
| mineral_intake | JSONB | DEFAULT '{}' | 矿物质摄入 |
| calorie_percentage | DecimalField(5,2) | DEFAULT 0 | 热量达成率 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**nutrition_recommendations表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 推荐ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| daily_calorie_target | DecimalField(7,2) | DEFAULT 2000 | 每日热量目标 |
| daily_protein_target | DecimalField(6,2) | DEFAULT 60 | 每日蛋白质目标 |
| daily_fat_target | DecimalField(6,2) | DEFAULT 65 | 每日脂肪目标 |
| daily_carbohydrate_target | DecimalField(6,2) | DEFAULT 300 | 每日碳水化合物目标 |
| daily_fiber_target | DecimalField(6,2) | DEFAULT 25 | 每日膳食纤维目标 |
| vitamin_targets | JSONB | DEFAULT '{}' | 维生素目标 |
| mineral_targets | JSONB | DEFAULT '{}' | 矿物质目标 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**nutrition_reports表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 报告ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| report_type | CharField(20) | NOT NULL | 报告类型 |
| report_date | DateField | NOT NULL | 报告日期 |
| start_date | DateField | NOT NULL | 开始日期 |
| end_date | DateField | NOT NULL | 结束日期 |
| report_data | JSONB | DEFAULT '{}' | 报告数据 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**nutrition_advices表**
| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| id | BigAutoField | PRIMARY KEY | 建议ID |
| user_id | BigIntegerField | FOREIGN KEY REFERENCES users(id) | 用户ID |
| analysis_id | BigIntegerField | FOREIGN KEY REFERENCES nutrition_analyses(id) | 分析ID |
| advice_type | CharField(20) | NOT NULL | 建议类型 |
| content | TextField | NOT NULL | 建议内容 |
| priority | CharField(20) | DEFAULT 'normal' | 优先级 |
| is_read | BooleanField | DEFAULT False | 是否已读 |
| created_at | DateTimeField | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 4.2 数据库关系图

```
+----------------+       +-------------------+
|     users      |<------| user_health_profiles|
+----------------+       +-------------------+
| id (PK)        |       | id (PK)           |
| username       |       | user_id (FK)      |
| email          |       | activity_level    |
| phone_number   |       | health_goal       |
+----------------+       +-------------------+
        |
        |       +----------------+
        |       | user_login_logs|
        |<------|                |
        |       | id (PK)        |
        |       | user_id (FK)   |
        |       +----------------+
        |
        |       +----------------+
        |       |     foods      |
        |<------|                |
        |       | id (PK)        |
        |       | name           |
        |       +----------------+
        |
        |       +----------------+
        |       |   meal_logs    |
        |<------|                |
        |       | id (PK)        |
        |       | user_id (FK)   |
        |       | date           |
        |       +----------------+      +----------------+
        |                |             |    recipes     |
        |                |             +----------------+
        |                |             | id (PK)        |
        |                |             | title          |
        |                |             | created_by (FK)|
        |                |             +----------------+
        |                |                      ^
        |                |                      |
        |                v                      |
        |       +----------------+       +----------------+
        |       |   food_items   |       | recipe_collections|
        |       +----------------+       +----------------+
        |       | id (PK)        |       | id (PK)        |
        |       | meal_log_id (FK)|      | user_id (FK)   |
        |       | food_id (FK)   |      | recipe_id (FK) |
        |       +----------------+       +----------------+
        |
        |       +----------------+
        |       |  meal_plans    |
        |<------|                |
        |       | id (PK)        |
        |       | user_id (FK)   |
        |       +----------------+
        |
        |       +-------------------+
        |       |nutrition_analyses |
        |<------|                   |
        |       | id (PK)           |
        |       | user_id (FK)      |
        |       | analysis_date     |
        |       +-------------------+      +---------------------+
        |                     |            |nutrition_recommendations|
        |                     |            +---------------------+
        |                     |            | id (PK)             |
        |                     |            | user_id (FK)        |
        |                     |            +---------------------+
        |                     |                      ^
        |                     |                      |
        |                     v                      |
        |       +-------------------+       +----------------+
        |       | nutrition_advices |       |nutrition_reports|
        |       +-------------------+       +----------------+
        |       | id (PK)           |       | id (PK)         |
        |       | user_id (FK)      |       | user_id (FK)    |
        |       | analysis_id (FK)  |       | report_type     |
        |       +-------------------+       +----------------+
```

### 4.3 数据迁移和初始化计划

#### 4.3.1 数据迁移策略
1. 使用Django的内置迁移系统管理数据库模式变更
2. 每次模型变更都生成对应的迁移文件
3. 迁移文件应包含详细注释说明变更内容
4. 大型迁移应先在测试环境验证

#### 4.3.2 初始数据导入
1. 食物基础数据：导入常见食物的营养成分数据
2. 营养推荐标准：根据年龄、性别等提供默认推荐值
3. 测试用户数据：创建不同角色的测试用户

```python
# 初始数据导入脚本示例 (data/initial_data.py)
import os
import json
from django.core.management.base import BaseCommand
from apps.foods.models import Food
from apps.nutrition.models import NutritionRecommendation

class Command(BaseCommand):
    help = '导入初始数据'
    
    def handle(self, *args, **options):
        # 导入食物数据
        self.import_foods()
        # 导入营养推荐标准
        self.import_recommendations()
    
    def import_foods(self):
        # 从JSON文件导入食物数据
        with open('data/foods.json', 'r', encoding='utf-8') as f:
            foods_data = json.load(f)
        
        for food_data in foods_data:
            Food.objects.get_or_create(
                name=food_data['name'],
                category=food_data['category'],
                defaults={
                    'calories': food_data['calories'],
                    'protein': food_data['protein'],
                    'fat': food_data['fat'],
                    'carbohydrate': food_data['carbohydrate'],
                    'fiber': food_data.get('fiber', 0),
                    'sodium': food_data.get('sodium', 0),
                    'vitamins': food_data.get('vitamins', {}),
                    'minerals': food_data.get('minerals', {}),
                }
            )
        
        self.stdout.write(self.style.SUCCESS('食物数据导入完成'))
    
    def import_recommendations(self):
        # 导入营养推荐标准
        recommendations = [
            {'age_group': 'adult_male', 'daily_calorie_target': 2500, 'daily_protein_target': 65, ...},
            {'age_group': 'adult_female', 'daily_calorie_target': 2000, 'daily_protein_target': 50, ...},
        ]
        
        for rec in recommendations:
            # 这里只是示例，实际应根据用户的年龄、性别等动态生成
            pass
        
        self.stdout.write(self.style.SUCCESS('营养推荐标准导入完成'))

### 4.1 数据库表结构详细设计

### 4.2 索引设计

### 4.3 数据约束

### 4.4 数据库迁移计划

## 5. API详细设计

### 5.1 API设计原则

### 5.2 用户管理API详细设计

### 5.3 膳食管理API详细设计

### 5.4 营养分析API详细设计

### 5.5 认证与授权API

## 6. 项目文件目录结构

### 6.1 前端项目结构

```
nutrition-frontend/            # 前端项目根目录
├── public/                    # 静态资源目录
│   ├── favicon.ico           # 网站图标
│   ├── index.html            # HTML入口文件
│   └── manifest.json         # Web App配置
├── src/                      # 源代码目录
│   ├── assets/               # 资源文件目录
│   │   ├── images/           # 图片资源
│   │   ├── icons/            # 图标资源
│   │   └── styles/           # 全局样式
│   ├── components/           # 通用组件
│   │   ├── common/           # 基础通用组件
│   │   │   ├── Button/       # 按钮组件
│   │   │   ├── Card/         # 卡片组件
│   │   │   └── Form/         # 表单组件
│   │   ├── layout/           # 布局组件
│   │   │   ├── Header/       # 页头组件
│   │   │   ├── Footer/       # 页脚组件
│   │   │   └── Sidebar/      # 侧边栏组件
│   │   └── business/         # 业务组件
│   │       ├── FoodItem/     # 食物项目组件
│   │       ├── MealLogCard/  # 膳食记录卡片组件
│   │       └── NutritionChart/ # 营养图表组件
│   ├── pages/                # 页面组件
│   │   ├── Login/            # 登录页面
│   │   ├── Register/         # 注册页面
│   │   ├── Dashboard/        # 仪表盘页面
│   │   ├── UserProfile/      # 用户资料页面
│   │   ├── HealthProfile/    # 健康档案页面
│   │   ├── FoodDatabase/     # 食物数据库页面
│   │   ├── MealRecords/      # 膳食记录页面
│   │   ├── MealPlanner/      # 膳食计划页面
│   │   ├── Recipes/          # 食谱页面
│   │   ├── NutritionAnalysis/ # 营养分析页面
│   │   └── Reports/          # 报告页面
│   ├── redux/                # Redux状态管理
│   │   ├── actions/          # Redux动作
│   │   ├── reducers/         # Redux减速器
│   │   ├── store.js          # Redux存储配置
│   │   └── types.js          # 动作类型定义
│   ├── services/             # API服务
│   │   ├── api.js            # API配置
│   │   ├── authService.js    # 认证服务
│   │   ├── userService.js    # 用户服务
│   │   ├── foodService.js    # 食物服务
│   │   ├── mealService.js    # 膳食服务
│   │   └── nutritionService.js # 营养分析服务
│   ├── utils/                # 工具函数
│   │   ├── formatters.js     # 格式化工具
│   │   ├── validators.js     # 验证工具
│   │   └── helpers.js        # 辅助函数
│   ├── hooks/                # 自定义钩子
│   │   ├── useAuth.js        # 认证钩子
│   │   └── useApi.js         # API请求钩子
│   ├── routes/               # 路由配置
│   │   ├── index.js          # 路由配置入口
│   │   └── PrivateRoute.js   # 私有路由组件
│   ├── App.js                # 应用根组件
│   ├── index.js              # 应用入口文件
│   └── setupTests.js         # 测试配置
├── .gitignore                # Git忽略文件
├── package.json              # 项目依赖
├── package-lock.json         # 依赖版本锁定
├── README.md                 # 项目说明
└── eslint.config.js          # ESLint配置
```

### 6.2 后端项目结构

```
nutrition-backend/            # 后端项目根目录
├── apps/                     # Django应用目录
│   ├── accounts/             # 账户管理应用
│   │   ├── migrations/       # 数据库迁移文件
│   │   ├── models/           # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py       # 用户模型
│   │   │   ├── health_profile.py # 健康档案模型
│   │   │   └── login_log.py  # 登录日志模型
│   │   ├── serializers/      # 序列化器
│   │   │   ├── __init__.py
│   │   │   ├── user_serializer.py
│   │   │   └── health_profile_serializer.py
│   │   ├── services/         # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py
│   │   │   └── auth_service.py
│   │   ├── views/            # API视图
│   │   │   ├── __init__.py
│   │   │   ├── auth_views.py
│   │   │   └── user_views.py
│   │   ├── urls.py           # 路由配置
│   │   ├── permissions.py    # 权限控制
│   │   ├── signals.py        # 信号处理
│   │   └── __init__.py
│   ├── foods/                # 食物管理应用
│   │   ├── migrations/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── food.py
│   │   ├── serializers/
│   │   │   ├── __init__.py
│   │   │   └── food_serializer.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── food_service.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   └── food_views.py
│   │   ├── urls.py
│   │   └── __init__.py
│   ├── meals/                # 膳食管理应用
│   │   ├── migrations/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── meal_log.py
│   │   │   ├── food_item.py
│   │   │   └── meal_plan.py
│   │   ├── serializers/
│   │   │   ├── __init__.py
│   │   │   ├── meal_log_serializer.py
│   │   │   ├── food_item_serializer.py
│   │   │   └── meal_plan_serializer.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── meal_service.py
│   │   │   └── plan_service.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── meal_log_views.py
│   │   │   └── meal_plan_views.py
│   │   ├── urls.py
│   │   └── __init__.py
│   ├── recipes/              # 食谱管理应用
│   │   ├── migrations/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── recipe.py
│   │   │   └── recipe_collection.py
│   │   ├── serializers/
│   │   │   ├── __init__.py
│   │   │   ├── recipe_serializer.py
│   │   │   └── collection_serializer.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── recipe_service.py
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── recipe_views.py
│   │   │   └── collection_views.py
│   │   ├── urls.py
│   │   └── __init__.py
│   ├── nutrition/            # 营养分析应用
│   │   ├── migrations/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py
│   │   │   ├── recommendation.py
│   │   │   ├── report.py
│   │   │   └── advice.py
│   │   ├── serializers/
│   │   │   ├── __init__.py
│   │   │   ├── analysis_serializer.py
│   │   │   ├── recommendation_serializer.py
│   │   │   ├── report_serializer.py
│   │   │   └── advice_serializer.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py
│   │   │   ├── report_service.py
│   │   │   └── calculator.py  # 营养计算器
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   ├── analysis_views.py
│   │   │   ├── report_views.py
│   │   │   └── advice_views.py
│   │   ├── urls.py
│   │   └── __init__.py
│   └── storage/              # 文件存储应用
│       ├── models/
│       ├── services/
│       ├── views/
│       ├── urls.py
│       └── __init__.py
├── core/                     # 核心配置目录
│   ├── settings/             # 配置文件
│   │   ├── __init__.py
│   │   ├── base.py           # 基础配置
│   │   ├── development.py    # 开发环境配置
│   │   ├── production.py     # 生产环境配置
│   │   └── testing.py        # 测试环境配置
│   ├── urls.py               # 根路由配置
│   ├── wsgi.py               # WSGI配置
│   ├── asgi.py               # ASGI配置
│   └── __init__.py
├── utils/                    # 工具目录
│   ├── decorators.py         # 自定义装饰器
│   ├── middleware.py         # 中间件
│   ├── validators.py         # 验证器
│   ├── jwt.py                # JWT工具
│   └── __init__.py
├── templates/                # 模板目录
├── static/                   # 静态文件目录
├── media/                    # 媒体文件目录
├── data/                     # 数据目录
│   ├── foods.json            # 初始食物数据
│   └── initial_data.py       # 初始数据导入脚本
├── tests/                    # 测试目录
│   ├── test_accounts.py
│   ├── test_foods.py
│   ├── test_meals.py
│   └── test_nutrition.py
├── manage.py                 # Django管理脚本
├── requirements.txt          # 项目依赖
├── requirements-dev.txt      # 开发依赖
├── Dockerfile                # Docker配置
├── docker-compose.yml        # Docker Compose配置
├── .env.example              # 环境变量示例
├── .gitignore                # Git忽略文件
└── README.md                 # 项目说明
```

### 6.3 配置文件结构

#### 6.3.1 前端配置文件

**package.json**
```json
{
  "name": "nutrition-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.14.0",
    "react-redux": "^8.0.7",
    "@reduxjs/toolkit": "^1.9.5",
    "antd": "^5.6.0",
    "axios": "^1.4.0",
    "chart.js": "^4.3.0",
    "react-chartjs-2": "^5.2.0",
    "dayjs": "^1.11.9",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "@babel/core": "^7.22.5",
    "@babel/preset-env": "^7.22.5",
    "@babel/preset-react": "^7.22.5",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^5.16.5",
    "eslint": "^8.43.0",
    "eslint-plugin-react": "^7.32.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "jest": "^29.5.0",
    "webpack": "^5.87.0",
    "webpack-cli": "^5.1.4",
    "webpack-dev-server": "^4.15.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

#### 6.3.2 后端配置文件

**requirements.txt**
```
Django==4.2.2
Django REST framework==3.14.0
psycopg2-binary==2.9.6
PyJWT==2.7.0
python-dotenv==1.0.0
pillow==9.5.0
celery==5.3.1
redis==4.5.5
django-cors-headers==4.0.0
pytest-django==4.6.0
python-dateutil==2.8.2
django-filter==23.2
```

**DATABASES 配置 (settings/base.py)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}
```

**REST_FRAMEWORK 配置 (settings/base.py)**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

#### 6.3.3 目录结构设计原则

##### 6.3.3.1 前端项目结构设计原则
1. **组件化设计**：将UI拆分为可重用的组件，按功能和类型进行分类
2. **状态管理**：使用Redux进行全局状态管理，分离状态逻辑和UI逻辑
3. **服务层抽象**：将API调用封装到独立的服务层，便于维护和测试
4. **路由与页面分离**：清晰区分路由配置和页面组件
5. **工具函数独立**：将通用功能抽离为工具函数
6. **响应式设计**：确保组件和布局在不同设备上都有良好的显示效果

##### 6.3.3.2 后端项目结构设计原则
1. **应用模块化**：按业务领域划分Django应用，每个应用职责单一
2. **MVC模式**：遵循模型-视图-控制器模式，分离数据、业务逻辑和表现层
3. **服务层模式**：在模型和视图之间增加服务层，封装复杂业务逻辑
4. **配置分离**：按环境分离配置，便于部署和维护
5. **RESTful API设计**：遵循RESTful API设计原则，提供标准化的接口
6. **测试驱动开发**：包含完整的测试框架，支持自动化测试

## 7. 部署与集成方案

### 7.1 开发环境配置

#### 7.1.1 前端开发环境

**技术栈要求：**
- Node.js v16.14+ 或 v18.12+
- npm v8.3+ 或 yarn v1.22+
- Git

**配置步骤：**
1. 克隆代码仓库
   ```bash
   git clone [repository-url]
   cd nutrition-frontend
   ```
2. 安装依赖
   ```bash
   npm install
   # 或
   yarn install
   ```
3. 创建环境配置文件 `.env.development`
   ```
   REACT_APP_API_URL=http://localhost:8000/api
   REACT_APP_ENV=development
   ```
4. 启动开发服务器
   ```bash
   npm start
   # 或
   yarn start
   ```

#### 7.1.2 后端开发环境

**技术栈要求：**
- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- Git

**配置步骤：**
1. 克隆代码仓库
   ```bash
   git clone [repository-url]
   cd nutrition-backend
   ```
2. 创建虚拟环境
   ```bash
   python -m venv venv
   # 激活虚拟环境
   # Windows
   venv\Scripts\activate
   # Linux/MacOS
   source venv/bin/activate
   ```
3. 安装依赖
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
4. 创建环境配置文件 `.env`
   ```
   # 数据库配置
   DB_NAME=nutrition_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   
   # Redis配置
   REDIS_URL=redis://localhost:6379/0
   
   # 用于JWT签名的密钥
   SECRET_KEY=your-secret-key-here
   
   # 环境设置
   DEBUG=True
   ```
5. 初始化数据库
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py loaddata data/initial_data.json
   ```
6. 启动开发服务器
   ```bash
   python manage.py runserver
   ```
7. 启动Celery工作器（在单独的终端中）
   ```bash
   celery -A core worker --loglevel=info
   ```

### 7.2 测试环境配置

#### 7.2.1 Docker Compose配置

**docker-compose.test.yml**
```yaml
version: '3.8'

services:
  frontend-test:
    build:
      context: ./nutrition-frontend
      dockerfile: Dockerfile.test
    environment:
      - REACT_APP_API_URL=http://backend-test:8000/api
      - REACT_APP_ENV=test
    command: npm test -- --watchAll=false
    depends_on:
      - backend-test

  backend-test:
    build:
      context: ./nutrition-backend
      dockerfile: Dockerfile
    environment:
      - DEBUG=True
      - DB_NAME=nutrition_test_db
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_HOST=db-test
      - DB_PORT=5432
      - REDIS_URL=redis://redis-test:6379/0
      - SECRET_KEY=test-secret-key
    command: >
      sh -c "python manage.py migrate && 
             python manage.py loaddata data/initial_data.json && 
             python manage.py runserver 0.0.0.0:8000"
    ports:
      - "8000:8000"
    depends_on:
      - db-test
      - redis-test

  db-test:
    image: postgres:14
    environment:
      - POSTGRES_DB=nutrition_test_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres-test-data:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  redis-test:
    image: redis:6
    ports:
      - "6380:6379"

volumes:
  postgres-test-data:
```

#### 7.2.2 测试环境部署流程

1. 构建并启动测试环境
   ```bash
   docker-compose -f docker-compose.test.yml up --build
   ```
2. 运行测试套件
   ```bash
   # 前端测试
   docker-compose -f docker-compose.test.yml run frontend-test npm test
   
   # 后端测试
   docker-compose -f docker-compose.test.yml run backend-test python -m pytest
   ```

### 7.3 生产环境配置

#### 7.3.1 前端生产环境

**构建配置：**
- 使用Docker多阶段构建优化镜像大小
- 采用Nginx作为静态资源服务器

**Dockerfile.frontend**
```dockerfile
# 构建阶段
FROM node:16-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf**
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
```

#### 7.3.2 后端生产环境

**Dockerfile.backend**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p static media

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBUG=False

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# 暴露端口
EXPOSE 8000

# 使用Gunicorn作为WSGI服务器
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "30"]
```

#### 7.3.3 生产环境Docker Compose配置

**docker-compose.prod.yml**
```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./nutrition-frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=https://api.nutrition-app.example.com
      - REACT_APP_ENV=production
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./nutrition-backend
      dockerfile: Dockerfile.backend
    environment:
      - DEBUG=False
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=api.nutrition-app.example.com,localhost
    volumes:
      - media-volume:/app/media
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-worker:
    build:
      context: ./nutrition-backend
      dockerfile: Dockerfile.backend
    command: celery -A core worker --loglevel=info
    environment:
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-beat:
    build:
      context: ./nutrition-backend
      dockerfile: Dockerfile.backend
    command: celery -A core beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./nutrition-backend/db-init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:6
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-data:
  redis-data:
  media-volume:
```

#### 7.3.4 生产环境部署步骤

1. 准备环境变量文件 `.env.production`
   ```
   DB_NAME=nutrition_prod_db
   DB_USER=postgres
   DB_PASSWORD=your-secure-password
   SECRET_KEY=your-secure-secret-key
   ```

2. 部署应用
   ```bash
   export $(cat .env.production | xargs)
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

3. 初始化数据库（首次部署）
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
   docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
   ```

### 7.4 CI/CD流程设计

#### 7.4.1 GitHub Actions配置

**前端CI/CD配置 (.github/workflows/frontend-cicd.yml)**
```yaml
name: Frontend CI/CD

on:
  push:
    branches: [ main, develop ]
    paths: [ 'nutrition-frontend/**' ]
  pull_request:
    branches: [ main, develop ]
    paths: [ 'nutrition-frontend/**' ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
          cache: 'npm'
          cache-dependency-path: nutrition-frontend/package-lock.json
      - name: Install dependencies
        working-directory: nutrition-frontend
        run: npm ci
      - name: Run linting
        working-directory: nutrition-frontend
        run: npm run lint
      - name: Run tests
        working-directory: nutrition-frontend
        run: npm test -- --watchAll=false
  
  build-and-deploy:
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: yourdockerhubusername/nutrition-frontend
          tags: |
            type=ref,event=branch
            type=sha,prefix={{sha}}-
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./nutrition-frontend
          file: ./nutrition-frontend/Dockerfile.frontend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
      - name: Deploy to production/development
        if: github.ref == 'refs/heads/main'
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_SERVER_HOST }}
          username: ${{ secrets.SERVER_USERNAME }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /path/to/app
            docker-compose pull frontend
            docker-compose up -d frontend
```

**后端CI/CD配置 (.github/workflows/backend-cicd.yml)**
```yaml
name: Backend CI/CD

on:
  push:
    branches: [ main, develop ]
    paths: [ 'nutrition-backend/**' ]
  pull_request:
    branches: [ main, develop ]
    paths: [ 'nutrition-backend/**' ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:6
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'
          cache-dependency-path: nutrition-backend/requirements*.txt
      - name: Install dependencies
        working-directory: nutrition-backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run linting
        working-directory: nutrition-backend
        run: |
          pip install flake8
          flake8 .
      - name: Run tests
        working-directory: nutrition-backend
        env:
          DB_NAME: test_db
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_HOST: localhost
          DB_PORT: 5432
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key
          DEBUG: True
        run: python -m pytest
  
  build-and-deploy:
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to DockerHub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: yourdockerhubusername/nutrition-backend
          tags: |
            type=ref,event=branch
            type=sha,prefix={{sha}}-
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./nutrition-backend
          file: ./nutrition-backend/Dockerfile.backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
      - name: Deploy to production/development
        if: github.ref == 'refs/heads/main'
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_SERVER_HOST }}
          username: ${{ secrets.SERVER_USERNAME }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /path/to/app
            docker-compose pull backend celery-worker celery-beat
            docker-compose up -d backend celery-worker celery-beat
```

#### 7.4.2 部署流程概述

1. **开发流程**
   - 开发人员在功能分支上工作
   - 提交代码并创建Pull Request
   - CI自动运行测试和代码质量检查
   - 代码审查通过后合并到develop分支
   - develop分支部署到测试环境

2. **发布流程**
   - 从develop分支创建发布分支
   - 进行最终测试和修复
   - 合并到main分支
   - main分支触发生产环境部署
   - 部署完成后进行冒烟测试

3. **回滚策略**
   - 保留之前稳定版本的Docker镜像
   - 维护数据库备份
   - 出现问题时，回滚到上一个稳定版本
   - 使用Docker Compose的rollback命令或重新部署特定版本

## 8. 测试策略

### 8.1 单元测试设计

#### 8.1.1 后端单元测试

**测试框架：**
- `pytest` 作为测试运行器
- `pytest-django` 作为Django集成
- `mock` 和 `unittest.mock` 用于模拟对象和行为

**测试范围：**
- 数据模型验证和方法
- 序列化器逻辑
- 业务服务层核心算法
- 工具函数和辅助方法

**测试覆盖率目标：** 80%以上的代码覆盖率

**测试组织结构：**
```
tests/
├── conftest.py              # 测试配置和fixtures
├── apps/
│   ├── test_accounts/
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   ├── test_services.py
│   │   └── test_views.py
│   ├── test_foods/
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── test_meals/
│   │   ├── test_models.py
│   │   └── test_services.py
│   └── test_nutrition/
│       ├── test_models.py
│       ├── test_services.py
│       └── test_calculator.py
└── utils/
    ├── test_jwt.py
    └── test_validators.py
```

**测试示例：**

```python
# tests/apps/test_nutrition/test_calculator.py
import pytest
from nutrition.services.calculator import Calculator

@pytest.mark.django_db
def test_calculate_bmi():
    calculator = Calculator()
    # 正常体重范围
    assert calculator.calculate_bmi(70, 1.75) == pytest.approx(22.86, rel=1e-2)
    # 偏瘦范围
    assert calculator.calculate_bmi(50, 1.75) == pytest.approx(16.33, rel=1e-2)
    # 偏胖范围
    assert calculator.calculate_bmi(90, 1.75) == pytest.approx(29.39, rel=1e-2)

@pytest.mark.django_db
def test_calculate_bmr():
    calculator = Calculator()
    # 男性BMR计算
    assert calculator.calculate_bmr(30, 70, 1.75, 'male') == pytest.approx(1694.3, rel=1e-2)
    # 女性BMR计算
    assert calculator.calculate_bmr(30, 60, 1.65, 'female') == pytest.approx(1392.6, rel=1e-2)
```

#### 8.1.2 前端单元测试

**测试框架：**
- `Jest` 作为测试运行器和断言库
- `React Testing Library` 用于组件测试
- `Redux Testing Library` 用于Redux状态测试

**测试范围：**
- 组件渲染和行为
- 钩子函数功能
- Redux actions和reducers
- 工具函数和格式化器

**测试覆盖率目标：** 75%以上的代码覆盖率

**测试组织结构：**
```
src/
├── components/
│   ├── common/
│   │   ├── Button/
│   │   │   └── Button.test.js
│   │   └── ...
│   └── business/
│       ├── FoodItem/
│       │   └── FoodItem.test.js
│       └── ...
├── hooks/
│   ├── useAuth.test.js
│   └── useApi.test.js
├── redux/
│   ├── actions/
│   │   └── authActions.test.js
│   └── reducers/
│       └── authReducer.test.js
└── utils/
    ├── formatters.test.js
    └── validators.test.js
```

**测试示例：**

```javascript
// src/components/business/FoodItem/FoodItem.test.js
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../../redux/store';
import FoodItem from './FoodItem';

describe('FoodItem Component', () => {
  const mockFood = {
    id: 1,
    name: 'Apple',
    calories: 52,
    protein: 0.3,
    carbs: 13.8,
    fat: 0.2,
    category: 'Fruits',
    imageUrl: '/images/apple.jpg'
  };

  test('renders food item with correct information', () => {
    render(
      <Provider store={store}>
        <FoodItem food={mockFood} />
      </Provider>
    );
    
    expect(screen.getByText('Apple')).toBeInTheDocument();
    expect(screen.getByText('52 kcal')).toBeInTheDocument();
    expect(screen.getByText('Protein: 0.3g')).toBeInTheDocument();
    expect(screen.getByText('Carbs: 13.8g')).toBeInTheDocument();
    expect(screen.getByText('Fat: 0.2g')).toBeInTheDocument();
  });

  test('calls onAddToMeal when Add to Meal button is clicked', () => {
    const onAddToMeal = jest.fn();
    
    render(
      <Provider store={store}>
        <FoodItem food={mockFood} onAddToMeal={onAddToMeal} />
      </Provider>
    );
    
    fireEvent.click(screen.getByText('Add to Meal'));
    expect(onAddToMeal).toHaveBeenCalledWith(mockFood);
  });
});
```

### 8.2 集成测试设计

#### 8.2.1 API集成测试

**测试工具：**
- `pytest` 与 `pytest-django`
- Django REST framework的测试客户端

**测试范围：**
- 完整的API端点流程
- 请求验证和响应格式
- 权限控制和身份验证
- 序列化和反序列化过程

**测试示例：**

```python
# tests/apps/test_meals/test_views.py
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestMealLogAPI:
    @pytest.fixture
    def authenticated_client(self):
        # 创建测试用户和认证客户端
        user = User.objects.create_user(username='testuser', password='testpass')
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_create_meal_log(self, authenticated_client):
        # 创建膳食记录的测试
        payload = {
            'meal_type': 'breakfast',
            'log_date': '2023-06-15',
            'food_items': [
                {'food': 1, 'quantity': 2, 'unit': 'serving'}
            ]
        }
        response = authenticated_client.post('/api/meals/logs/', payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['meal_type'] == 'breakfast'
        assert response.data['log_date'] == '2023-06-15'

    def test_get_user_meal_logs(self, authenticated_client):
        # 获取用户膳食记录的测试
        response = authenticated_client.get('/api/meals/logs/')
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)  # 因为使用了分页
        assert 'results' in response.data
```

#### 8.2.2 前后端集成测试

**测试工具：**
- `Cypress` 用于端到端测试

**测试范围：**
- 用户登录流程
- 数据展示和交互
- 表单提交和验证
- 跨页面导航

**测试组织结构：**
```
cypress/
├── fixtures/           # 测试数据
├── integration/        # 测试用例
│   ├── auth/          # 认证相关测试
│   │   ├── login.spec.js
│   │   └── register.spec.js
│   ├── meals/         # 膳食相关测试
│   │   ├── meal-log.spec.js
│   │   └── meal-plan.spec.js
│   └── nutrition/     # 营养分析相关测试
│       └── analysis.spec.js
├── plugins/           # Cypress插件
└── support/           # 测试辅助函数
```

**测试示例：**

```javascript
// cypress/integration/meals/meal-log.spec.js
describe('Meal Logging', () => {
  beforeEach(() => {
    // 登录用户
    cy.login('testuser', 'testpassword');
    // 访问膳食记录页面
    cy.visit('/meals/records');
  });

  it('should allow users to add a new meal log', () => {
    // 点击添加膳食按钮
    cy.get('[data-testid="add-meal-btn"]').click();
    
    // 选择早餐类型
    cy.get('[data-testid="meal-type-select"]').select('breakfast');
    
    // 选择日期
    cy.get('[data-testid="log-date-picker"]').type('2023-06-15');
    
    // 添加食物
    cy.get('[data-testid="food-search"]').type('apple{enter}');
    cy.get('[data-testid="add-food-btn-1"]').click();
    
    // 设置数量
    cy.get('[data-testid="food-quantity-1"]').clear().type('1');
    
    // 保存膳食记录
    cy.get('[data-testid="save-meal-btn"]').click();
    
    // 验证保存成功
    cy.contains('Meal log created successfully').should('be.visible');
    
    // 验证新记录出现在列表中
    cy.get('[data-testid="meal-log-item"]').should('contain', 'Breakfast');
    cy.get('[data-testid="meal-log-item"]').should('contain', '2023-06-15');
    cy.get('[data-testid="meal-log-item"]').should('contain', 'Apple');
  });
});
```

### 8.3 系统测试设计

#### 8.3.1 功能测试

**测试方法：**
- 基于用户故事的验收测试
- 测试场景覆盖所有关键业务流程
- 测试用例设计采用等价类划分和边界值分析

**关键测试场景：**

1. **用户账户管理流程**
   - 用户注册、登录和个人信息管理
   - 健康档案的创建和更新
   - 密码重置和账户设置

2. **膳食记录和管理流程**
   - 记录日常膳食摄入
   - 查看和编辑历史膳食记录
   - 快速添加常用食物

3. **营养分析和报告流程**
   - 查看每日营养摄入分析
   - 生成周期性营养报告
   - 接收个性化营养建议

4. **膳食计划流程**
   - 创建和编辑膳食计划
   - 基于目标自动生成膳食建议
   - 将计划转换为实际记录

#### 8.3.2 用户界面测试

**测试要点：**
- 响应式设计适配各种设备尺寸
- 交互元素的可用性和易用性
- 错误提示和边界情况的友好展示
- 国际化和本地化支持

**测试工具：**
- `Cypress` 进行UI交互测试
- 浏览器开发者工具进行响应式设计测试
- `jest-axe` 进行可访问性测试

#### 8.3.3 兼容性测试

**测试范围：**
- 主要浏览器兼容性（Chrome, Firefox, Safari, Edge最新版本）
- 不同操作系统兼容性（Windows, macOS, Linux）
- 移动设备兼容性（iOS, Android）

**测试方法：**
- 使用浏览器测试工具进行自动化兼容性测试
- 在实际设备上进行手动验证
- 使用云测试平台（如BrowserStack）进行大规模兼容性测试

### 8.4 性能测试设计

#### 8.4.1 后端性能测试

**测试工具：**
- `locust` 用于负载测试
- `k6` 用于性能基准测试

**测试指标：**
- API响应时间（P95, P99）
- 系统吞吐量（TPS）
- 并发用户数支持
- 资源使用情况（CPU, 内存）

**测试场景：**

1. **API端点性能测试**
   - 单一API端点的响应时间测试
   - 关键业务流程的性能测试
   - 数据库查询性能测试

2. **负载测试**
   - 模拟100/500/1000并发用户访问
   - 持续负载测试（30分钟）
   - 峰值负载测试（短时间内用户量突增）

3. **扩展性测试**
   - 水平扩展能力测试
   - 资源增加与性能提升的关系

**测试示例：**

```python
# locustfile.py
from locust import HttpUser, task, between

class NutritionAppUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # 用户登录
        self.client.post("/api/auth/login/", {
            "username": "testuser",
            "password": "testpassword"
        })
    
    @task(1)
    def get_meal_logs(self):
        self.client.get("/api/meals/logs/")
    
    @task(2)
    def get_foods(self):
        self.client.get("/api/foods/?search=apple")
    
    @task(1)
    def get_nutrition_analysis(self):
        self.client.get("/api/nutrition/analysis/?date=2023-06-15")
```

#### 8.4.2 前端性能测试

**测试工具：**
- `Lighthouse` 用于性能评分
- `WebPageTest` 用于深入性能分析
- Chrome DevTools Performance面板

**测试指标：**
- 首次内容绘制（FCP）
- 最大内容绘制（LCP）
- 首次输入延迟（FID）
- 累积布局偏移（CLS）
- JavaScript执行时间
- 资源加载时间

**优化目标：**
- Lighthouse性能评分85+分
- LCP < 2.5秒
- FID < 100ms
- CLS < 0.1

#### 8.4.3 数据库性能测试

**测试工具：**
- PostgreSQL性能分析工具
- Django Debug Toolbar

**测试场景：**
- 大数据量下的查询性能
- 复杂聚合查询的执行计划分析
- 索引使用情况验证
- 事务性能测试

**测试方法：**
- 使用真实数据量的测试环境
- 分析查询执行计划
- 监控慢查询日志
- 验证索引设计合理性

## 9. 安全与性能优化

### 9.1 安全设计详细方案

#### 9.1.1 身份验证与授权

**身份验证实现：**
- 使用JWT (JSON Web Token) 进行无状态身份验证
- 实现密码哈希存储（使用Django的PBKDF2算法）
- 支持邮箱/用户名登录方式
- 密码复杂度要求（长度、大小写、特殊字符）
- 实现账户锁定机制（防止暴力破解）

**授权实现：**
- 基于Django的Permission系统实现细粒度权限控制
- 使用Django REST Framework的权限类（`IsAuthenticated`, `IsOwnerOrReadOnly`等）
- 实现基于角色的访问控制（RBAC）
- API端点权限验证

**代码示例：**

```python
# accounts/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """只允许资源所有者修改数据"""
    
    def has_object_permission(self, request, view, obj):
        # 允许GET, HEAD, OPTIONS请求（只读操作）
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 检查是否为资源所有者
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False

class IsNutritionistOrReadOnly(permissions.BasePermission):
    """只允许营养师修改特定数据"""
    
    def has_permission(self, request, view):
        # 允许GET, HEAD, OPTIONS请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 检查用户是否为营养师角色
        return request.user.is_authenticated and request.user.profile.role == 'nutritionist'
```

```python
# accounts/middleware.py
import time
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseForbidden

class LoginAttemptLimiter:
    """限制登录尝试次数的中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path == '/api/auth/login/':
            # 检查是否需要限制登录尝试
            ip = request.META.get('REMOTE_ADDR')
            username = request.POST.get('username')
            
            if ip and username:
                # 这里应使用缓存或数据库实现登录尝试限制
                # 简化示例：
                attempts_key = f'login_attempts:{ip}:{username}'
                # 使用缓存系统跟踪尝试次数和时间
                # 实现逻辑：如果短时间内尝试次数过多，返回403
                
        response = self.get_response(request)
        return response
```

#### 9.1.2 数据安全

**数据加密：**
- 敏感数据传输使用TLS/SSL加密（HTTPS）
- 敏感字段存储加密（如身份证号、健康数据等）
- 使用AES-256加密算法保护核心敏感数据

**数据验证：**
- 使用Django的表单验证和模型验证
- 实现自定义验证器确保数据完整性
- 输入清洗防止XSS攻击

**数据隐私：**
- 遵循GDPR和相关隐私法规
- 实现用户数据访问和删除机制
- 健康数据匿名化处理

**代码示例：**

```python
# accounts/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_password_strength(value):
    """验证密码强度"""
    # 至少8个字符
    if len(value) < 8:
        raise ValidationError(_('密码长度至少为8个字符'))
    
    # 至少包含一个大写字母
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('密码必须包含至少一个大写字母'))
    
    # 至少包含一个小写字母
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('密码必须包含至少一个小写字母'))
    
    # 至少包含一个数字
    if not re.search(r'[0-9]', value):
        raise ValidationError(_('密码必须包含至少一个数字'))
    
    # 至少包含一个特殊字符
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(_('密码必须包含至少一个特殊字符'))

def validate_health_data(value):
    """验证健康数据的合理性"""
    # 身高验证（cm）
    if 'height' in value and not (50 <= value['height'] <= 250):
        raise ValidationError(_('身高数据不合理，请输入有效的身高值（50-250cm）'))
    
    # 体重验证（kg）
    if 'weight' in value and not (10 <= value['weight'] <= 300):
        raise ValidationError(_('体重数据不合理，请输入有效的体重值（10-300kg）'))
```

#### 9.1.3 API安全

**API保护措施：**
- 实现速率限制（Rate Limiting）
- API端点输入验证
- 跨站请求伪造（CSRF）防护
- 跨域资源共享（CORS）配置

**代码示例：**

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',         # 匿名用户限制
        'user': '1000/day',        # 认证用户限制
        'login': '5/minute',       # 登录接口限制
        'api': '100/minute',       # 常规API限制
    },
}

# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # 生产环境域名
]

CORS_ALLOW_CREDENTIALS = True
```

```python
# config/middleware.py
from django.middleware.csrf import CsrfViewMiddleware

class CustomCsrfMiddleware(CsrfViewMiddleware):
    """自定义CSRF中间件，增强CSRF保护"""
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # 针对API请求的额外CSRF保护逻辑
        # 例如：对某些敏感操作添加额外的验证
        return super().process_view(request, callback, callback_args, callback_kwargs)
```

#### 9.1.4 安全日志与监控

**日志记录：**
- 记录所有身份验证事件（登录成功/失败）
- 记录敏感操作（数据修改、删除等）
- 记录异常和错误情况

**监控与告警：**
- 实时监控异常访问模式
- 配置安全事件告警机制
- 定期安全审计

**代码示例：**

```python
# accounts/services.py
import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger(__name__)

def user_login(request, username, password):
    """用户登录服务，添加详细日志记录"""
    # 记录登录尝试
    logger.info(
        f'Login attempt for user: {username}, IP: {request.META.get("REMOTE_ADDR")}, '\
        f'User-Agent: {request.META.get("HTTP_USER_AGENT")}'
    )
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # 登录成功
        login(request, user)
        
        # 更新最后登录时间
        user.last_login = timezone.now()
        user.save()
        
        logger.info(f'Login successful for user: {username}, User ID: {user.id}')
        return user
    else:
        # 登录失败
        logger.warning(
            f'Login failed for user: {username}, IP: {request.META.get("REMOTE_ADDR")}'
        )
        return None
```

### 9.2 性能优化详细方案

#### 9.2.1 后端性能优化

**数据库优化：**
- 合理设计索引（基于查询模式）
- 使用查询优化器分析和优化SQL
- 实现数据库查询缓存
- 批量操作替代单次操作

**代码示例：**

```python
# meals/services.py
from django.db import connection, transaction
from django.db.models import Prefetch, Count, Sum
from meals.models import MealLog, FoodItem, MealFood

def get_user_meal_stats(user, start_date, end_date):
    """获取用户特定时间段内的膳食统计数据，使用优化的查询"""
    # 使用Prefetch减少查询次数
    meal_logs = MealLog.objects.filter(
        user=user,
        log_date__range=[start_date, end_date]
    ).prefetch_related(
        Prefetch('meal_foods', queryset=MealFood.objects.select_related('food'))
    )
    
    # 聚合计算总营养摄入
    nutrition_totals = (
        MealFood.objects
        .filter(meal_log__user=user, meal_log__log_date__range=[start_date, end_date])
        .annotate(total_calories=Sum('quantity', 'food__calories'))
        .values('total_calories')
    )
    
    return {
        'meal_logs_count': meal_logs.count(),
        'nutrition_totals': nutrition_totals
    }

def bulk_update_food_items(food_items):
    """批量更新食物项目，减少数据库交互"""
    with transaction.atomic():
        for food_item in food_items:
            # 仅更新需要更改的字段
            food_item.save(update_fields=['name', 'category', 'updated_at'])
    
    return len(food_items)
```

**缓存策略：**
- 使用Redis缓存热点数据
- 实现多级缓存架构（应用缓存、数据库缓存、CDN）
- 缓存失效策略（TTL、手动失效）
- 缓存预热机制

**代码示例：**

```python
# config/settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "nutrition_app",
        "TIMEOUT": 3600,  # 默认缓存1小时
    },
    "food_cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "food_cache",
        "TIMEOUT": 86400,  # 食物数据缓存24小时
    }
}
```

```python
# foods/services.py
from django.core.cache import cache
from foods.models import FoodItem, FoodCategory

def get_popular_foods(limit=20):
    """获取热门食物列表，使用缓存优化"""
    cache_key = f'popular_foods:{limit}'
    
    # 尝试从缓存获取
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # 缓存未命中，从数据库获取
    popular_foods = FoodItem.objects.filter(
        is_popular=True
    ).select_related('category').order_by('-usage_count')[:limit]
    
    # 转换为可序列化数据
    result = [{
        'id': food.id,
        'name': food.name,
        'category': food.category.name if food.category else None,
        'calories': food.calories,
        'protein': food.protein,
        'carbs': food.carbs,
        'fat': food.fat,
        'image_url': food.image_url,
    } for food in popular_foods]
    
    # 存入缓存，设置过期时间为1小时
    cache.set(cache_key, result, 3600)
    
    return result

def invalidate_food_cache():
    """使食物相关缓存失效"""
    # 清除热门食物缓存
    for limit in [10, 20, 50]:
        cache.delete(f'popular_foods:{limit}')
    
    # 清除分类缓存
    cache.delete('food_categories')
```

**异步处理：**
- 使用Celery处理耗时任务
- 实现异步邮件发送
- 异步数据处理和分析
- 任务队列和优先级管理

**代码示例：**

```python
# config/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('nutrition_app')

# 使用Django设置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现tasks.py文件
app.autodiscover_tasks()
```

```python
# nutrition/tasks.py
from celery import shared_task
from django.utils import timezone
from nutrition.models import NutritionAnalysis
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=3)
def generate_nutrition_report(user_id, date_from, date_to):
    """生成营养报告的异步任务"""
    try:
        user = User.objects.get(id=user_id)
        
        logger.info(f'开始生成用户 {user.username} 的营养报告: {date_from} 到 {date_to}')
        
        # 这里实现详细的营养分析逻辑
        # ...
        
        # 保存分析结果
        analysis = NutritionAnalysis.objects.create(
            user=user,
            date_from=date_from,
            date_to=date_to,
            # 分析结果数据
            # ...
        )
        
        logger.info(f'用户 {user.username} 的营养报告生成完成，ID: {analysis.id}')
        
        # 发送通知邮件
        send_report_notification.delay(user_id, analysis.id)
        
        return analysis.id
        
    except Exception as e:
        logger.error(f'生成营养报告失败: {str(e)}')
        raise

@shared_task
def send_report_notification(user_id, analysis_id):
    """发送报告通知邮件"""
    # 实现邮件发送逻辑
    # ...
```

#### 9.2.2 前端性能优化

**资源优化：**
- 代码分割（Code Splitting）和懒加载
- 静态资源压缩（JS, CSS, Images）
- 使用Webpack优化构建流程
- Tree Shaking移除未使用代码

**示例配置：**

```javascript
// webpack.config.js
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  entry: './src/index.js',
  output: {
    filename: '[name].[contenthash].js',
    path: path.resolve(__dirname, 'build'),
    publicPath: '/',
    clean: true,
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
    runtimeChunk: 'single',
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8,
    }),
    // 可选：仅在分析构建时启用
    // new BundleAnalyzerPlugin(),
  ],
  // ... 其他配置
};
```

**React性能优化：**
- 使用React.memo, useMemo, useCallback优化渲染性能
- 虚拟列表处理大量数据
- 图片懒加载
- 状态管理优化（Redux性能优化）

**代码示例：**

```javascript
// src/components/business/FoodList.jsx
import React, { useMemo, useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { VirtualTable } from 'react-virtualized';
import FoodItem from './FoodItem';

const FoodList = () => {
  const { foods, loading, error } = useSelector(state => state.food);
  const [searchQuery, setSearchQuery] = useState('');
  
  // 使用useMemo缓存过滤结果
  const filteredFoods = useMemo(() => {
    if (!searchQuery.trim()) return foods;
    
    return foods.filter(food => 
      food.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      food.category.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [foods, searchQuery]);
  
  // 使用React.memo优化组件渲染
  const Row = React.memo(({ index, key, style }) => {
    const food = filteredFoods[index];
    return (
      <div key={key} style={style}>
        <FoodItem food={food} />
      </div>
    );
  });
  
  // 使用虚拟列表优化大量数据渲染
  const rowRenderer = ({ index, key, style }) => {
    return <Row index={index} key={key} style={style} />;
  };
  
  return (
    <div className="food-list">
      <input
        type="text"
        placeholder="搜索食物..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="search-input"
      />
      
      {loading ? (
        <div className="loading">加载中...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : (
        <VirtualTable
          width={800}
          height={600}
          headerHeight={20}
          rowHeight={80}
          rowCount={filteredFoods.length}
          rowRenderer={rowRenderer}
        />
      )}
    </div>
  );
};

export default React.memo(FoodList);
```

**网络优化：**
- API请求优化（合并请求、分页加载）
- 实现请求缓存
- 使用HTTP/2
- CDN加速静态资源

**代码示例：**

```javascript
// src/services/apiService.js
import axios from 'axios';
import { getToken } from '../utils/auth';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 统一错误处理
    if (error.response?.status === 401) {
      // 处理未授权错误
      // 可以在此处重定向到登录页或刷新token
    }
    return Promise.reject(error);
  }
);

// 实现请求缓存
const requestCache = new Map();

const getCachedRequest = (url, params) => {
  const cacheKey = `${url}_${JSON.stringify(params || {})}`;
  const cachedData = requestCache.get(cacheKey);
  
  if (cachedData && (Date.now() - cachedData.timestamp < cachedData.ttl)) {
    return cachedData.data;
  }
  
  return null;
};

const setCachedRequest = (url, params, data, ttl = 300000) => {
  const cacheKey = `${url}_${JSON.stringify(params || {})}`;
  requestCache.set(cacheKey, {
    data,
    timestamp: Date.now(),
    ttl,
  });
};

export const getCachedData = async (url, params, forceRefresh = false) => {
  // 对于不会频繁变化的数据，使用缓存
  if (!forceRefresh) {
    const cachedData = getCachedRequest(url, params);
    if (cachedData) {
      return cachedData;
    }
  }
  
  try {
    const response = await api.get(url, { params });
    setCachedRequest(url, params, response.data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api;
```

#### 9.2.3 系统架构优化

**微服务设计考虑：**
- 服务拆分策略（按功能领域拆分）
- 服务间通信（REST, gRPC）
- 服务发现和负载均衡
- 分布式事务处理

**容器化与编排：**
- 使用Docker容器化应用
- Kubernetes编排管理
- 自动扩缩容策略
- 健康检查和自愈能力

**监控与性能分析：**
- 使用Prometheus监控系统指标
- Grafana可视化监控数据
- ELK栈进行日志收集和分析
- 性能分析工具使用（如Py-Spy, Chrome Profiler）

**示例配置：**

```yaml
# docker-compose.prod.yml 部分配置
version: '3.8'

services:
  web:
    image: nutrition_app_web
    build: .
    restart: always
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    expose:
      - 8000
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - SECRET_KEY=${SECRET_KEY}
      - DB_HOST=db
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8000/health/" || exit 1]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

#### 9.2.4 数据库性能优化

**索引优化：**
- 创建复合索引支持多字段查询
- 唯一索引确保数据完整性
- 部分索引减少索引大小
- 定期维护和重建索引

**查询优化：**
- N+1查询问题解决
- 使用select_related和prefetch_related
- 只查询需要的字段（values和values_list）
- 使用annotate和aggregate优化聚合查询

**数据库配置优化：**
- 连接池配置
- 查询缓存配置
- 参数调优（work_mem, maintenance_work_mem等）
- 分区表策略（针对历史数据）

**代码示例：**

```python
# 优化的模型索引设计
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MealLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_logs')
    meal_type = models.CharField(max_length=20, choices=[
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '加餐'),
    ])
    log_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # 复合索引优化日期范围查询
        indexes = [
            models.Index(fields=['user', 'log_date']),
            models.Index(fields=['log_date', 'meal_type']),
            # 部分索引只索引最近30天的数据
            models.Index(fields=['user', 'meal_type'], condition=models.Q(log_date__gte=models.functions.Now() - datetime.timedelta(days=30))),
        ]
        # 确保每个用户每天每个餐类型只有一条记录
        unique_together = ['user', 'log_date', 'meal_type']

# 优化的查询示例
def get_user_meal_history(user, start_date, end_date, meal_type=None):
    """获取用户膳食历史，使用优化的查询"""
    query = MealLog.objects.filter(
        user=user,
        log_date__range=[start_date, end_date]
    )
    
    # 可选的餐类型过滤
    if meal_type:
        query = query.filter(meal_type=meal_type)
    
    # 使用prefetch_related加载关联数据，避免N+1查询
    return query.prefetch_related(
        Prefetch('meal_foods', queryset=MealFood.objects.select_related('food'))
    ).order_by('-log_date', 'meal_type')
```

```sql
-- 数据库级优化查询示例（PostgreSQL）
-- 分析营养摄入趋势的优化查询
SELECT 
    DATE_TRUNC('week', log_date) AS week,
    meal_type,
    AVG(total_calories) AS avg_calories,
    AVG(total_protein) AS avg_protein,
    AVG(total_carbs) AS avg_carbs,
    AVG(total_fat) AS avg_fat
FROM (
    SELECT 
        ml.log_date,
        ml.meal_type,
        SUM(mf.quantity * f.calories) AS total_calories,
        SUM(mf.quantity * f.protein) AS total_protein,
        SUM(mf.quantity * f.carbs) AS total_carbs,
        SUM(mf.quantity * f.fat) AS total_fat
    FROM meals_meallog ml
    JOIN meals_mealfood mf ON ml.id = mf.meal_log_id
    JOIN foods_fooditem f ON mf.food_id = f.id
    WHERE ml.user_id = 1
      AND ml.log_date >= '2023-01-01'
      AND ml.log_date <= '2023-12-31'
    GROUP BY ml.log_date, ml.meal_type
) AS daily_totals
GROUP BY week, meal_type
ORDER BY week, meal_type;
```

#### 9.2.5 安全和性能平衡策略

**安全与性能权衡：**
- 选择性应用高强度加密（仅敏感数据）
- 缓存策略与数据一致性平衡
- 速率限制配置优化
- 日志详细程度与性能平衡

**最佳实践：**
- 定期安全和性能审计
- A/B测试新功能性能影响
- 持续监控和调优
- 建立性能基准和安全标准

## 10. 总结与建议

### 10.1 设计总结

本文档详细设计了一个基于React和Django的智能营养膳食分析系统，该系统旨在帮助用户记录日常膳食、分析营养摄入并获取个性化的营养建议。通过采用前后端分离的架构设计，系统实现了高度的模块化和可扩展性。

**核心功能设计总结：**
- **用户管理模块**：实现了完整的用户注册、登录、个人资料管理功能，支持普通用户和营养师两种角色
- **食物营养数据库**：设计了结构化的食物数据模型，包含详细的宏量和微量营养素信息
- **膳食记录与分析**：支持用户记录每日膳食，自动计算营养摄入并进行趋势分析
- **个性化推荐系统**：基于用户健康数据和营养目标提供膳食建议和食物推荐
- **营养师咨询平台**：连接用户和营养师，支持在线咨询和专业指导

**技术架构总结：**
- **前端技术栈**：React.js + Redux + Material-UI，实现了高性能、响应式的用户界面
- **后端技术栈**：Django + Django REST Framework，提供了安全、高效的API服务
- **数据库设计**：PostgreSQL关系型数据库，设计了规范化的表结构和合理的索引策略
- **缓存策略**：Redis缓存热点数据，提升系统性能
- **异步处理**：Celery任务队列处理耗时操作，保证系统响应速度

### 10.2 设计亮点

1. **完整的营养数据分析体系**
   - 实现了多维度的营养数据分析，包括宏量营养素、微量营养素、热量平衡等
   - 支持按日、周、月的时间维度进行趋势分析
   - 提供可视化图表直观展示营养摄入情况

2. **灵活的权限管理系统**
   - 基于角色的访问控制（RBAC），区分普通用户和营养师权限
   - 细粒度的资源级权限控制，确保数据安全
   - 实现了资源所有权验证，保护用户隐私数据

3. **高性能架构设计**
   - 多级缓存策略，优化系统响应速度
   - 数据库查询优化，通过索引设计和查询优化减少响应时间
   - 前后端性能优化措施，包括代码分割、懒加载、虚拟列表等

4. **完善的安全防护措施**
   - JWT无状态身份验证，保障API安全
   - 密码强度验证和哈希存储，保护用户账户安全
   - 请求速率限制和输入验证，防止恶意攻击
   - 敏感数据加密存储，保护用户健康数据隐私

5. **可扩展的系统架构**
   - 模块化设计，便于功能扩展和维护
   - 容器化部署方案，支持水平扩展
   - 清晰的API设计，便于第三方系统集成

### 10.3 潜在风险与应对策略

1. **数据量增长风险**
   - **风险**：随着用户数量和食物数据的增长，数据库性能可能下降
   - **应对策略**：
     - 实施数据库分区策略，按时间或用户ID分区
     - 定期数据归档，将历史数据迁移到冷存储
     - 优化查询和索引，确保复杂查询的性能

2. **系统安全风险**
   - **风险**：用户健康数据属于敏感信息，存在数据泄露风险
   - **应对策略**：
     - 定期进行安全审计和渗透测试
     - 实施数据脱敏和加密传输
     - 遵循GDPR等数据保护法规
     - 加强访问日志监控，及时发现异常访问

3. **系统扩展性风险**
   - **风险**：随着用户量增加，系统可能面临性能瓶颈
   - **应对策略**：
     - 采用微服务架构拆分核心功能
     - 实施自动扩缩容机制
     - 优化数据库和缓存策略
     - 考虑使用CDN加速静态资源分发

4. **第三方依赖风险**
   - **风险**：系统依赖多个第三方库和服务，存在版本更新和兼容性问题
   - **应对策略**：
     - 使用依赖锁定文件固定版本
     - 建立依赖更新测试流程
     - 关键服务考虑备份方案

5. **用户体验风险**
   - **风险**：复杂的营养分析可能导致用户理解困难，影响产品采用率
   - **应对策略**：
     - 持续进行用户测试和反馈收集
     - 优化界面设计，提供更直观的可视化展示
     - 增加交互式教程和帮助文档
     - 定期更新推荐算法，提高个性化准确度

### 10.4 未来优化方向

1. **功能增强**
   - 集成智能语音助手，支持语音记录膳食
   - 开发移动应用版本，提供离线功能
   - 添加社交功能，支持用户分享和社区互动
   - 引入AI图像识别，通过拍照自动识别食物和分量
   - 开发食谱推荐系统，基于用户偏好和库存食材

2. **性能优化**
   - 实施更细粒度的缓存策略
   - 引入GraphQL减少过度获取和多次请求
   - 优化数据库读写分离
   - 考虑使用时序数据库存储时间序列的营养数据
   - 前端性能优化，包括PWA支持和资源预加载

3. **智能化升级**
   - 引入机器学习算法优化营养推荐准确性
   - 开发预测模型，分析用户饮食习惯变化趋势
   - 实现异常饮食行为检测和提醒
   - 提供AI驱动的个性化营养计划制定

4. **业务扩展**
   - 支持多语言和多地区营养标准
   - 集成健身追踪功能，实现营养与运动的结合
   - 开发企业版，支持团队健康管理
   - 建立营养师入驻平台，提供付费咨询服务

5. **技术升级**
   - 升级到最新的前端框架和工具链
   - 考虑使用Docker和Kubernetes实现更完善的容器编排
   - 引入服务网格技术管理微服务通信
   - 实施更完善的监控和可观测性系统
   - 建立自动化测试和部署流程，提高开发效率

### 10.5 结论

本设计文档提供了智能营养膳食分析系统的全面技术规划，涵盖了从系统架构到具体实现的各个方面。通过采用现代化的技术栈和最佳实践，该系统能够满足用户对营养健康管理的需求，同时具备良好的可扩展性和可维护性。

在实施过程中，建议按照模块化的方式逐步开发，优先实现核心功能，同时注重用户体验和系统性能。通过持续的迭代优化和用户反馈收集，系统可以不断完善和发展，最终成为一个成熟、可靠的营养健康管理平台。

通过本系统的实施，用户将能够更加科学地管理自己的饮食，获取个性化的营养指导，从而改善健康状况和生活质量。同时，系统也为营养师提供了一个高效的工作平台，帮助他们更好地为用户提供专业服务。