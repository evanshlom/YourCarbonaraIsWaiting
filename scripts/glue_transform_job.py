import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BUCKET_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

bucket = args.get('BUCKET_NAME', 'aiawsattack-bucket')

# Read customer contacts from S3
customers_df = spark.read.json(f"s3://{bucket}/square_data/raw/customer_contacts.json")

# Read customer orders from S3
orders_df = spark.read.json(f"s3://{bucket}/square_data/raw/customer_orders.json")

# Explode line items to get individual products
orders_exploded = orders_df.select(
    col("id").alias("order_id"),
    col("customer_id"),
    col("created_at").alias("order_date"),
    col("total_money.amount").alias("order_total_cents"),
    explode("line_items").alias("item")
).select(
    col("order_id"),
    col("customer_id"),
    col("order_date"),
    col("order_total_cents"),
    col("item.name").alias("product_name"),
    col("item.quantity").alias("quantity"),
    col("item.total_money.amount").alias("item_total_cents")
)

# Aggregate order data by customer
customer_orders_agg = orders_exploded.groupBy("customer_id").agg(
    count("order_id").alias("total_orders"),
    sum("order_total_cents").alias("lifetime_value_cents"),
    collect_list(struct(
        col("order_date"),
        col("product_name"),
        col("quantity")
    )).alias("order_history"),
    max("order_date").alias("last_order_date"),
    min("order_date").alias("first_order_date")
)

# Calculate favorite items
favorite_items = orders_exploded.groupBy("customer_id", "product_name").agg(
    count("product_name").alias("times_ordered")
).groupBy("customer_id").agg(
    first(struct(
        col("product_name"),
        col("times_ordered")
    ), ignorenulls=True).alias("favorite_item")
)

# Join all data together
final_df = customers_df.join(customer_orders_agg, customers_df.id == customer_orders_agg.customer_id, "left") \
    .join(favorite_items, customers_df.id == favorite_items.customer_id, "left") \
    .select(
        customers_df.id.alias("customer_id"),
        customers_df.given_name,
        customers_df.family_name,
        customers_df.email_address,
        customers_df.phone_number,
        customers_df.created_at.alias("customer_since"),
        col("total_orders"),
        col("lifetime_value_cents"),
        col("last_order_date"),
        col("first_order_date"),
        col("favorite_item.product_name").alias("favorite_product"),
        col("favorite_item.times_ordered").alias("favorite_product_order_count"),
        col("order_history")
    )

# Calculate insights for email campaigns
final_with_insights = final_df.withColumn(
    "days_since_last_order",
    datediff(current_date(), to_date(col("last_order_date")))
).withColumn(
    "customer_segment",
    when(col("total_orders") >= 3, "loyal")
    .when(col("total_orders") == 1, "new")
    .otherwise("occasional")
).withColumn(
    "engagement_priority",
    when(col("days_since_last_order") > 60, "high")
    .when(col("days_since_last_order") > 30, "medium")
    .otherwise("low")
)

# Write the transformed data back to S3 as both JSON and Parquet
final_with_insights.write.mode("overwrite").json(f"s3://{bucket}/square_data/processed/customer_insights_json/")
final_with_insights.write.mode("overwrite").parquet(f"s3://{bucket}/square_data/processed/customer_insights_parquet/")

# Also create a simplified view for the agents
agent_view = final_with_insights.select(
    "customer_id",
    "given_name",
    "family_name", 
    "email_address",
    "customer_segment",
    "favorite_product",
    "favorite_product_order_count",
    "days_since_last_order",
    "total_orders",
    "engagement_priority"
)

agent_view.write.mode("overwrite").json(f"s3://{bucket}/square_data/processed/agent_view/")

job.commit()