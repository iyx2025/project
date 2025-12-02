# 膳食营养健康系统概要设计文档

## 1. 概述

### 1.1 文档目的
本文档描述了膳食营养健康系统的概要设计，基于需求规格说明书，提供系统架构、模块划分、核心功能设计、数据库设计、接口设计等关键技术方案，为系统详细设计和开发提供指导依据。

### 1.2 术语定义
- **用户**：使用系统的个人，可以是普通用户或管理员
- **膳食记录**：用户记录的每日饮食信息，包括食物名称、份量、用餐时间等
- **营养素**：食物中含有的对人体有益的成分，如蛋白质、脂肪、碳水化合物、维生素、矿物质等
- **营养需求**：根据用户的年龄、性别、体重、活动水平等因素计算得出的每日所需营养素摄入量
- **膳食推荐**：系统根据用户的营养需求和偏好生成的饮食建议
- **营养分析**：对用户的膳食记录进行数据分析，评估其营养摄入是否均衡

## 2. 系统架构设计

### 2.1 整体架构
系统采用前后端分离的分层架构，主要包含以下层次：

```
前端展示层（Vue.js）→ 后端服务层（Django）→ 数据持久层（PostgreSQL）
```

### 2.2 详细架构说明

#### 2.2.1 前端架构
- **单页应用(SPA)**：基于Vue.js 3.x构建
- **状态管理**：使用Pinia管理全局状态
- **路由管理**：Vue Router处理前端路由
- **UI组件**：Element Plus提供UI组件
- **HTTP客户端**：Axios处理API请求
- **数据可视化**：ECharts实现营养数据图表展示

#### 2.2.2 后端架构
- **Web框架**：Django 4.x提供Web服务
- **API框架**：Django REST Framework构建RESTful API
- **认证授权**：JWT实现用户认证和授权
- **任务调度**：Celery处理异步任务（如营养分析）
- **缓存**：Redis缓存热点数据

#### 2.2.3 数据层
- **数据库**：PostgreSQL 14.x存储结构化数据
- **ORM**：Django ORM进行数据库操作
- **文件存储**：阿里云OSS存储用户头像、食谱图片等

### 2.3 系统交互流程图

```
用户 → 前端应用 → API网关 → 后端服务 → 数据库/第三方服务
```

## 3. 模块划分

### 3.1 核心模块

| 模块名称 | 主要职责 | 文件位置 |
| :--- | :--- | :--- |
| **用户管理模块** | 用户注册、登录、个人信息管理 | backend/apps/users/ |
| **膳食管理模块** | 食物管理、膳食记录、膳食计划、食谱管理 | backend/apps/meals/ |
| **营养分析模块** | 营养数据计算、报告生成、营养建议 | backend/apps/nutrition/ |
| **前端展示模块** | 用户界面渲染、交互处理 | frontend/src/views/ |

### 3.2 辅助模块

| 模块名称 | 主要职责 | 文件位置 |
| :--- | :--- | :--- |
| **认证授权模块** | 用户身份验证、权限控制 | backend/apps/authentication/ |
| **文件上传模块** | 处理头像、图片等文件上传 | backend/apps/upload/ |
| **数据缓存模块** | 缓存热点数据，提升性能 | backend/apps/cache/ |
| **定时任务模块** | 处理定期营养分析等异步任务 | backend/apps/tasks/ |

## 4. 核心功能设计

### 4.1 用户管理模块

#### 4.1.1 功能概述
- 用户注册（手机/邮箱）
- 用户登录（账号密码/验证码/第三方）
- 个人信息管理
- 健康档案管理
- 用户安全管理

#### 4.1.2 关键类设计

```python
# 用户模型
class User(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True, null=True)
    avatar = models.URLField(null=True)
    gender = models.CharField(max_length=10, null=True)
    birth_date = models.DateField(null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    bmi = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    role = models.CharField(max_length=20, default='user')
    status = models.CharField(max_length=20, default='active')

# 健康档案模型
class UserHealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile')
    activity_level = models.CharField(max_length=50, null=True)
    health_goal = models.CharField(max_length=100, null=True)
    dietary_preference = models.CharField(max_length=100, null=True)
    special_dietary_needs = ArrayField(models.TextField(), null=True)
    food_allergies = ArrayField(models.TextField(), null=True)
    daily_calorie_target = models.DecimalField(max_digits=7, decimal_places=2, null=True)
```

#### 4.1.3 业务流程
- **注册流程**：用户选择注册方式 → 填写信息 → 验证身份 → 设置密码 → 注册成功
- **登录流程**：用户输入凭证 → 验证身份 → 生成token → 登录成功
- **信息更新流程**：用户登录 → 修改信息 → 保存更改 → 更新成功

### 4.2 膳食管理模块

#### 4.2.1 功能概述
- 食物数据库管理
- 膳食记录添加与查询
- 膳食计划制定与推荐
- 食谱管理与分享
- 用餐提醒

#### 4.2.2 关键类设计

```python
# 食物模型
class Food(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    calories = models.DecimalField(max_digits=8, decimal_places=2)
    protein = models.DecimalField(max_digits=6, decimal_places=2)
    fat = models.DecimalField(max_digits=6, decimal_places=2)
    carbohydrate = models.DecimalField(max_digits=6, decimal_places=2)
    vitamins = models.JSONField(default=dict)
    minerals = models.JSONField(default=dict)
    image_url = models.URLField(null=True)

# 膳食记录模型
class MealLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_logs')
    date = models.DateField()
    meal_type = models.CharField(max_length=20)
    total_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_protein = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_fat = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_carbohydrate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    notes = models.TextField(null=True)

# 食物项目模型
class FoodItem(models.Model):
    meal_log = models.ForeignKey(MealLog, on_delete=models.CASCADE, related_name='food_items')
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True)
    custom_food_data = models.JSONField(null=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20)
    calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    protein = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fat = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    carbohydrate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
```

#### 4.2.3 业务流程
- **膳食记录流程**：选择用餐时间 → 搜索/选择食物 → 输入食用量 → 确认添加 → 保存记录
- **膳食计划生成流程**：用户设置健康目标 → 系统分析需求 → 生成计划 → 用户查看/调整 → 保存计划
- **食谱搜索流程**：输入搜索条件 → 展示匹配食谱 → 查看详情 → 收藏/添加到计划

### 4.3 营养分析管理模块

#### 4.3.1 功能概述
- 营养数据计算与统计
- 营养报告生成
- 营养摄入分析与可视化
- 个性化营养建议
- 健康监测与预警

#### 4.3.2 关键类设计

```python
# 营养分析模型
class NutritionAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_analyses')
    analysis_date = models.DateField()
    total_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    protein_intake = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fat_intake = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    carbohydrate_intake = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fiber_intake = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    vitamin_intake = models.JSONField(default=dict)
    mineral_intake = models.JSONField(default=dict)
    calorie_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

# 营养推荐标准模型
class NutritionRecommendation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nutrition_recommendation')
    daily_calorie_target = models.DecimalField(max_digits=7, decimal_places=2)
    daily_protein_target = models.DecimalField(max_digits=6, decimal_places=2)
    daily_fat_target = models.DecimalField(max_digits=6, decimal_places=2)
    daily_carbohydrate_target = models.DecimalField(max_digits=6, decimal_places=2)
    daily_fiber_target = models.DecimalField(max_digits=6, decimal_places=2)
    vitamin_targets = models.JSONField(default=dict)
    mineral_targets = models.JSONField(default=dict)
```

#### 4.3.3 业务流程
- **营养分析流程**：收集膳食数据 → 计算营养素摄入 → 对比推荐标准 → 生成分析结果 → 提供建议
- **报告生成流程**：用户选择报告类型和时间范围 → 系统生成报告 → 用户查看/导出
- **营养建议流程**：分析营养状况 → 识别问题 → 生成建议 → 用户查看 → 反馈

## 5. 数据库设计概述

### 5.1 数据库选择
- 主数据库：PostgreSQL 14.x
- 缓存：Redis

### 5.2 主要表结构

#### 5.2.1 用户相关表
- users：用户基本信息
- user_health_profiles：用户健康档案
- user_login_logs：用户登录记录

#### 5.2.2 食物与膳食相关表
- foods：食物信息
- meal_logs：膳食记录
- food_items：膳食项目
- meal_plans：膳食计划
- recipes：食谱信息
- recipe_collections：食谱收藏

#### 5.2.3 营养分析相关表
- nutrition_analyses：营养分析记录
- nutrition_recommendations：营养素推荐标准
- nutrition_reports：营养报告
- nutrition_advices：营养建议

### 5.3 关键索引设计
- users表：phone_number, email（唯一索引）
- foods表：name（全文搜索索引）, category
- meal_logs表：user_id, date, meal_type
- recipes表：title（全文搜索索引）
- nutrition_analyses表：user_id, analysis_date

### 5.4 数据安全设计
- 密码使用bcrypt哈希存储
- 敏感字段加密或脱敏
- 数据库连接使用SSL加密
- 实施严格的权限控制

## 6. 接口设计概述

### 6.1 API设计原则
- 遵循RESTful API规范
- 无状态设计
- 统一的请求/响应格式
- 版本控制
- 安全认证

### 6.2 主要API接口

#### 6.2.1 用户管理接口
- POST /api/v1/users/register：用户注册
- POST /api/v1/users/login：用户登录
- GET /api/v1/users/me：获取用户信息
- PATCH /api/v1/users/me：更新用户信息
- GET/POST/PUT /api/v1/users/health-profile：健康档案管理

#### 6.2.2 膳食管理接口
- GET/POST /api/v1/foods：食物管理
- GET/POST /api/v1/meal-logs：膳食记录管理
- GET/POST /api/v1/meal-plans：膳食计划管理
- POST /api/v1/meal-plans/generate：生成膳食计划
- GET/POST /api/v1/recipes：食谱管理

#### 6.2.3 营养分析接口
- GET /api/v1/nutrition/analyses：营养分析查询
- GET/POST /api/v1/nutrition/recommendations：营养推荐标准
- GET/POST /api/v1/nutrition/reports：营养报告管理
- GET /api/v1/nutrition/advices：营养建议查询

### 6.3 认证与授权
- JWT令牌认证
- 基于角色的访问控制(RBAC)
- 令牌有效期：24小时
- 刷新令牌有效期：7天

## 7. 安全设计

### 7.1 数据安全
- 敏感数据加密存储
- HTTPS传输加密
- 数据库安全配置
- 定期数据备份

### 7.2 应用安全
- 输入验证与过滤
- SQL注入防护
- XSS攻击防护
- CSRF攻击防护
- 接口限流

### 7.3 系统安全
- 服务器安全配置
- 日志记录与审计
- 安全漏洞扫描
- 定期安全更新

## 8. 性能优化设计

### 8.1 前端性能优化
- 组件懒加载
- 资源缓存
- 图片优化
- 路由预加载

### 8.2 后端性能优化
- 数据库索引优化
- 查询优化
- 缓存策略
- 数据库连接池
- 异步任务处理

### 8.3 系统性能指标
- API响应时间：< 200ms
- 页面加载时间：< 3s
- 并发用户数：支持10000+用户同时在线
- 数据库查询响应：< 50ms

## 9. 部署与集成方案

### 9.1 部署架构
- 容器化部署：Docker + Docker Compose
- CI/CD：GitHub Actions
- 负载均衡：Nginx
- 监控：Prometheus + Grafana

### 9.2 环境配置
- 开发环境：Docker Compose本地开发环境
- 测试环境：专用测试服务器
- 生产环境：云服务器集群

### 9.3 第三方服务集成
- 短信验证：阿里云短信服务
- 文件存储：阿里云OSS
- 缓存：Redis集群

## 10. 扩展性设计

### 10.1 功能扩展性
- 模块化设计，便于添加新功能
- 插件化架构，支持功能扩展
- API版本控制，兼容未来变更

### 10.2 系统扩展性
- 水平扩展支持
- 数据库读写分离
- 分布式缓存
- 微服务架构预留

## 11. 总结与建议

### 11.1 设计亮点
- 前后端分离架构，提高开发效率
- 模块化设计，便于维护和扩展
- 完善的安全机制，保障数据安全
- 高性能设计，提供良好用户体验

### 11.2 风险评估
- 食物数据库的完整性和准确性
- 营养分析算法的科学性和专业性
- 系统性能在大数据量下的表现
- 第三方服务依赖的稳定性

### 11.3 后续优化建议
- 引入机器学习算法优化营养推荐
- 开发移动应用客户端
- 增加社交功能，促进用户互动
- 扩展企业版功能，服务机构用户