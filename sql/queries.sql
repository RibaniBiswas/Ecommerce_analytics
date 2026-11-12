
-- QUERY 01: Monthly Revenue Analysis

SELECT
    strftime('%Y-%m', o.order_purchase_timestamp) AS order_month,
    ROUND(SUM(oi.price), 2) AS monthly_revenue

FROM orders AS o

JOIN order_items AS oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'delivered'

GROUP BY order_month

ORDER BY order_month;

-- QUERY 02: Top 10 Product Categories by Revenue

SELECT
    COALESCE(t.product_category_name_english,
             'Unknown') AS category,

    ROUND(SUM(oi.price), 2) AS total_revenue

FROM order_items AS oi

JOIN products AS p
    ON oi.product_id = p.product_id

LEFT JOIN category_translation AS t
    ON p.product_category_name = t.product_category_name

GROUP BY category

ORDER BY total_revenue DESC

LIMIT 10;

-- QUERY 03: Top 10 States by Revenue and Customers

SELECT
    c.customer_state AS state,

    COUNT(DISTINCT c.customer_unique_id) AS total_customers,

    ROUND(SUM(oi.price), 2) AS total_revenue

FROM orders AS o

JOIN customers AS c
    ON o.customer_id = c.customer_id

JOIN order_items AS oi
    ON o.order_id = oi.order_id

WHERE o.order_status = 'delivered'

GROUP BY c.customer_state

ORDER BY total_revenue DESC

LIMIT 10;


