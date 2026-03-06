from csv_reader import *
from apyori import apriori
import time

min_sup = 0.001   # Item must appear in x % of transactions
min_conf = 0.1    # Rule must be true x % of the time
min_lift = 1.0    # Rule must be x times more likely than random chance

rule_item_count = 2  # Custom filter to remove any rules that have less than x items

def get_product_name_dict():
    """
    Creates a mapping between product IDs and there corresponding name.
        Format: {1: "Banana", 2: "Apple", ...}
    :return: the product name mapping dictionary
    """
    products_df = pd.read_csv("data/products.csv", usecols=["product_id", "product_name"])
    name_map = dict(zip(products_df["product_id"], products_df["product_name"]))
    return name_map


def inspect(results, name_map):
    """
    Parses Apriori results and maps product IDs to their names.
    
    :param results: The list of RelationRecords returned by the apriori function.
    :param name_map: A dictionary mapping product IDs to product names.
    :return: A list of tuples containing formatted rules and their metrics.
    """
    lhs = [tuple(name_map.get(i, i) for i in result[2][0][0]) for result in results]
    rhs = [tuple(name_map.get(i, i) for i in result[2][0][1]) for result in results]
    supports = [result[1] for result in results]
    confidences = [result[2][0][2] for result in results]
    lifts = [result[2][0][3] for result in results]
    
    rule_length = [len(result[0]) for result in results]
    return list(zip(lhs, rhs, supports, confidences, lifts, rule_length))

def run_apriori():
    """
    Run the apriori function from the apyori library and create a csv file with the results.
    """
    
    # Get transactions
    print("Creating transactions...")
    transactions = create_transactions(True, False, False)
    
    # Run apriori and measure the time it takes
    print("Running apriori...")
    start_time = time.perf_counter()
    
    results = apriori(transactions,
                      min_support=min_sup,
                      min_confidence=min_conf,
                      min_lift=min_lift,
                      )
    
    # Convert generator to list to see how many rules we got
    rules = list(results)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    print(f"Apriori took {duration:.4f} seconds to run.")
    
    print(f"Number of rules generated: {len(rules)}")
    
    name_map = get_product_name_dict()
    # Create a DataFrame to easily sort and visualize
    result_df = pd.DataFrame(
        inspect(rules, name_map),
        columns = ['Left Hand Side', 'Right Hand Side', 'Support', 'Confidence', 'Lift', 'Total_Items']
    )
    
    # Filter out rules with too few items
    complex_rules = result_df[result_df['Total_Items'] >= rule_item_count].copy()
    
    complex_rules['Left Hand Side'] = complex_rules['Left Hand Side'].apply(lambda x: ' && '.join(x))
    complex_rules['Right Hand Side'] = complex_rules['Right Hand Side'].apply(lambda x: ' && '.join(x))
    complex_rules['Support_Confidence_Score'] = (complex_rules['Support'] ** 2) * complex_rules['Confidence']
    
    # Put results in output csv file
    output_path = "data_created/non-weekend-generated-rules.csv"
    top_rules = complex_rules.nlargest(n=100000, columns='Lift')
    top_rules.to_csv(output_path, index=False)
    
    print("Created csv file: ", output_path)