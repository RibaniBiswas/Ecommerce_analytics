
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

-- QUERY 04: Average Delivery Time by State

SELECT
    c.customer_state AS state,

    COUNT(o.order_id) AS total_orders,

    ROUND(
        AVG(
            julianday(o.order_delivered_customer_date) -
            julianday(o.order_purchase_timestamp)
        ),
        2
    ) AS avg_delivery_days

FROM orders AS o

JOIN customers AS c
    ON o.customer_id = c.customer_id

WHERE
    o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    AND o.order_purchase_timestamp IS NOT NULL

GROUP BY c.customer_state

ORDER BY avg_delivery_days DESC;

-- QUERY 05: Payment Method Analysis

SELECT

    payment_type,

    COUNT(*) AS total_transactions,

    ROUND(SUM(payment_value), 2) AS total_payment_value,

    ROUND(AVG(payment_value), 2) AS avg_payment_value,

    ROUND(AVG(payment_installments), 2) AS avg_installments

FROM payments

GROUP BY payment_type

ORDER BY total_payment_value DESC;

-- QUERY 06: Top 10 Performing Sellers

SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS total_items_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS avg_item_price

FROM order_items AS oi

JOIN orders AS o
    ON oi.order_id = o.order_id

WHERE o.order_status = 'delivered'

GROUP BY oi.seller_id

ORDER BY total_revenue DESC

LIMIT 10;

-- QUERY 07: Late vs On-Time Delivery Analysis

SELECT
    CASE
        WHEN order_delivered_customer_date >
             order_estimated_delivery_date
        THEN 'Late'
        ELSE 'On-Time'
    END AS delivery_status,

    COUNT(*) AS total_orders,

    ROUND(
        AVG(
            julianday(order_delivered_customer_date) -
            julianday(order_estimated_delivery_date)
        ), 2
    ) AS avg_days_difference

FROM orders

WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL

GROUP BY delivery_status

ORDER BY total_orders DESC;

-- QUERY 08: Review Score by Product Category

SELECT
    COALESCE(
        ct.product_category_name_english,
        p.product_category_name,
        'Unknown'
    ) AS product_category,

    COUNT(DISTINCT r.review_id) AS total_reviews,

    ROUND(AVG(r.review_score), 2) AS avg_review_score

FROM reviews AS r

JOIN order_items AS oi
    ON r.order_id = oi.order_id

JOIN products AS p
    ON oi.product_id = p.product_id

LEFT JOIN category_translation AS ct
    ON p.product_category_name = ct.product_category_name

GROUP BY product_category

HAVING COUNT(DISTINCT r.review_id) >= 50

ORDER BY avg_review_score DESC;







