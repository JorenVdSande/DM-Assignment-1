from src.association_mining import run_apriori

"""
Make sure to set the working directory to the root of these project files (DM-Assignment-1)
"""

def main():
    results_file_name = "generated-rules.csv"
    run_apriori(results_file_name)
    
if __name__ == "__main__":
    main()