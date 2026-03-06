import pandas as pd
import os
import json

"""
The sample size for reducing the transactions
"""
sample_size = 400_000


"""
pandas data type for 'aisles.csv'
"""
d_types_aisles = {
    "aisle_id": "uint16",
    "aisle": "string"
}

"""
pandas data type for order_products.csv
"""
d_type_order_products = {
    "order_id": "uint32",
    "product_id": "uint32",
    "add_to_cart_order": "uint8",
    "reordered": "bool"
}

"""
pandas data type for orders.csv
"""
d_type_orders = {
    "order_id": "uint32",
    "user_id": "uint32",
    "order_number": "uint8",
    "order_dow": "uint8",
    "order_hour_of_day": "uint8",
    "days_since_prior_order": "Int16"
}


def get_products_to_ignore():
    """
    Computes all the products that appear less than 'ignore_item_threshold' times in 'order_products.csv' or don't
    appear at all.
    :return: a set of product IDs to ignore.
    """
    ignore_item_threshold = 100
    
    order_products = pd.read_csv("data/order_products.csv", usecols=["product_id"], dtype={"product_id": "int32"})
    products = pd.read_csv("data/products.csv", usecols=["product_id"], dtype={"product_id": "int32"})
    
    all_ids = set(products["product_id"])
    present_ids = set(order_products["product_id"])
    missing_ids = all_ids - present_ids  # 3 missing IDs
    
    counts = order_products["product_id"].value_counts(ascending=True)
    rare_products = set(counts[counts <= ignore_item_threshold].index)
    
    products_to_ignore = missing_ids | rare_products
    
    print(f"Products that appear less than {ignore_item_threshold} times:", len(products_to_ignore))
    
    return products_to_ignore


def filter_and_sample(filter_orders: bool, orders):
    """
    Takes in an orders data frame and possibly filters out rows than don't satisfy certain conditions.
    :param filter_orders: boolean to filter or keep the orders as is.
    :param orders: the orders data frame (from orders.csv)
    :return: The filtered orders
    """
    if filter_orders:
        print("Filter applied to orders: True")
        # morning filter
        #orders_filtered = orders[(orders["order_hour_of_day"] >= 6) & (orders["order_hour_of_day"] <= 11)]
        # evening/midday filter
        #orders_filtered = orders[(orders["order_hour_of_day"] >= 12) & (orders["order_hour_of_day"] <= 20)]
        # night filter
        #orders_filtered = orders[(orders["order_hour_of_day"] > 20) | (orders["order_hour_of_day"] < 6)]
        
        # weekend filter
        #orders_filtered = orders[(orders["order_dow"] == 0) | (orders["order_dow"] == 6)]
        # non-weekend filter
        orders_filtered = orders[(orders["order_dow"] >= 1) & (orders["order_dow"] <= 5)]
        
    else:
        print("Filter applied to order: False")
        orders_filtered = orders
    
    if len(orders_filtered) > sample_size:
        orders_sample = orders_filtered.sample(n=sample_size, random_state=123, replace=False)
    else:
        orders_sample = orders_filtered
        
    return orders_sample


def create_transactions(filter_orders: bool, use_transactions_cache: bool, use_filtered_order_products_cache: bool):
    """
    Create the transactions list of lists to be used by the apriori algorithm.
    :param filter_orders: Whether the filter orders by, for example, time of day.
    :param use_transactions_cache: Whether or not to use the transactions cache if it exists.
    :param use_filtered_order_products_cache: Whether or not to use the filtered_order_products cache if it exists.
    :return:
    """
    
    # Possibly use transactions cache
    transactions_file_path = "data_created/transactions_cache.json"
    if os.path.exists(transactions_file_path) and use_transactions_cache:
        print(f"Loading transactions from cache: {transactions_file_path}")
        with open(transactions_file_path, "r") as f:
            return json.load(f)
    
    print("Cache not found. Generating transactions...")
    
    # Get orders + filter and sample
    orders = pd.read_csv("data/orders.csv", dtype=d_type_orders)
    print("Total amount of orders:", len(orders))
    orders_sample = filter_and_sample(filter_orders, orders)
    print("orders sample size:", len(orders_sample))
    
    # Load cache or create filtered_order_products.csv
    filtered_order_products_path = "data_filtered_products/filtered_order_products.csv"
    if os.path.exists(filtered_order_products_path) and use_filtered_order_products_cache:
        print("Retrieving filtered_order_products from cache.")
        filtered_order_products = pd.read_csv(filtered_order_products_path, dtype={"order_id": "uint32", "product_id": "uint32"})
    else:
        # Create reduced version of order_products.csv
        print("Creating filtered_order_products.csv and storing as cache")
        products_to_ignore = get_products_to_ignore()
        order_products = pd.read_csv("data/order_products.csv", dtype=d_type_order_products)
        filtered_order_products = order_products[~order_products["product_id"].isin(products_to_ignore)]
        filtered_order_products.to_csv(filtered_order_products_path, columns=["order_id", "product_id"], index=False)
    
    # Keep only products in sample
    sampled_order_ids = set(orders_sample["order_id"])
    filtered_order_products = filtered_order_products[
        (filtered_order_products["order_id"].isin(sampled_order_ids))
    ]
    
    # Create transactions (list of lists)
    transactions = (filtered_order_products.groupby("order_id")["product_id"]
                    .apply(list).values.tolist())
    print("final transactions count:", len(transactions))
    
    # Write to json to use as cache
    with open(transactions_file_path, "w") as f:
        json.dump(transactions, f)
    
    return transactions