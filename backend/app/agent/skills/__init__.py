from .types import Skill

SKILLS: list[Skill] = [
    {
        "name": "sales_analytics",
        "description": "适用场景：SQL编写；描述：关于销售业务的数据库表信息和业务逻辑，包括用户表、订单表、订单商品关联表等",
        "content": """
# 销售的数据库表信息
## databases info
- 数据库类型：MySQL

## Tables

### t_customers 用户表
- customer_id (PRIMARY KEY)
- name
- email
- signup_date
- status (active/inactive)
- customer_tier (bronze/silver/gold/platinum)

### t_orders 订单表
- order_id (PRIMARY KEY)
- customer_id (用户ID)
- order_date (订单日期)
- status (pending/completed/cancelled/refunded)
- total_amount (订单金额)
- sales_region (north/south/east/west)

### t_order_items 订单商品关联表
- item_id (PRIMARY KEY)
- order_id (订单ID)
- product_id (商品ID)
- quantity (数量)
- unit_price (单价)
- discount_percent (折扣百分比)

## 业务逻辑

**活跃用户**: status = 'active' AND signup_date <= CURRENT_DATE - INTERVAL '90 days'

**订单金额计算**: 只计算已完成订单的金额，已包含折扣。

**客户生命周期价值 (CLV)**: 计算客户所有已完成订单的金额总和。

**高价值订单**: 订单金额大于1000的订单。

## 示例查询

-- 获取最近3个月内订单金额最高的前10个用户
SELECT
    c.customer_id,
    c.name,
    c.customer_tier,
    SUM(o.total_amount) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
  AND o.order_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY c.customer_id, c.name, c.customer_tier
ORDER BY total_revenue DESC
LIMIT 10;
"""
    }
]