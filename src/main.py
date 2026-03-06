from src.association_mining import run_apriori

"""
Make sure to set the working directory to the root of these project files (DM-Assignment-1)

Add the {aisles.csv, departments.csv, order_products.csv, orders.csv, products.csv} files to
the 'data' directory.
"""

def main():
    # File will be created in the 'data_created' directory
    results_file_name = "generated-rules.csv"
    run_apriori(results_file_name)
    
if __name__ == "__main__":
    main()