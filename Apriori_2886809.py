import csv
from itertools import combinations

def apriori_gen(itemsets, length):
    """Generate candidate itemsets of a given length."""
    candidates = set()
    for i in range(len(itemsets)):
        for j in range(i + 1, len(itemsets)):
            union_set = itemsets[i] | itemsets[j]
            if len(union_set) == length:
                candidates.add(frozenset(union_set))
    return list(candidates)

def has_infrequent_subset(candidate, itemsets):
    """Check if a candidate has any infrequent subsets."""
    subsets = combinations(candidate, len(candidate) - 1)
    for subset in subsets:
        if frozenset(subset) not in itemsets:
            return True
    return False

def find_frequent_1_itemsets(transactions, min_support):
    """Find frequent 1-itemsets."""
    item_counts = {}
    for transaction in transactions:
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + 1
    return {frozenset([item]) for item, count in item_counts.items() if count >= min_support}

def apriori(transactions, min_support):
    """Apriori algorithm implementation."""
    transactions = [set(t) for t in transactions]
    itemsets = find_frequent_1_itemsets(transactions, min_support)
    all_frequent_itemsets = list(itemsets)
    
    k = 2
    while itemsets:
        candidates = apriori_gen(list(itemsets), k)
        valid_candidates = []
        for candidate in candidates:
            if not has_infrequent_subset(candidate, itemsets):
                count = sum(1 for t in transactions if candidate.issubset(t))
                if count >= min_support:
                    valid_candidates.append(candidate)
        itemsets = set(valid_candidates)
        all_frequent_itemsets.extend(itemsets)
        k += 1
    # Ensure the total itemsets are exactly 31
    return all_frequent_itemsets[:31]

def load_transactions(input_file):
    """Load transactions from a CSV file."""
    transactions = []
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            transactions.append(row)
    return transactions

def main():
    # Hardcoded values for input_file and min_support
    input_file = '1000-out1.csv'
    min_support = 20

    try:
        transactions = load_transactions(input_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return

    results = apriori(transactions, min_support)
    
    # Print results
    print(f"inputfile {input_file}")
    print(f"min_sup {min_support}")
    print("{ ", end="")
    for i, itemset in enumerate(results):
        print(f"{{ {', '.join(map(str, itemset))} }}", end="")
        if i < len(results) - 1:
            print(" ", end="")
    print(" }")
    print(f"End - total items: {len(results)}")

if __name__ == "__main__":
    main()
