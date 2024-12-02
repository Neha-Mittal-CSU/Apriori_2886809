from flask import Flask, request, render_template
import os
import csv
from itertools import combinations
from collections import defaultdict, Counter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def apriori_gen(itemsets, length):
    """Generate candidate itemsets of a given length."""
    candidates = set()
    for i in range(len(itemsets)):
        for j in range(i + 1, len(itemsets)):
            union_set = itemsets[i] | itemsets[j]
            if len(union_set) == length:
                candidates.add(union_set)
    return candidates

def has_infrequent_subset(candidate, itemsets):
    """Check if a candidate has any infrequent subsets."""
    for subset in combinations(candidate, len(candidate) - 1):
        if frozenset(subset) not in itemsets:
            return True
    return False

def find_frequent_1_itemsets(transactions, min_support):
    """Find frequent 1-itemsets."""
    item_counts = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    return {frozenset([item]) for item, count in item_counts.items() if count >= min_support}

def filter_candidates(transactions, candidates, min_support):
    """Filter candidates based on minimum support."""
    item_counts = defaultdict(int)
    for transaction in transactions:
        for candidate in candidates:
            if candidate.issubset(transaction):
                item_counts[candidate] += 1
    return {itemset for itemset, count in item_counts.items() if count >= min_support}

def apriori(transactions, min_support):
    """Apriori algorithm implementation."""
    transactions = [set(t) for t in transactions]
    current_itemsets = find_frequent_1_itemsets(transactions, min_support)
    all_frequent_itemsets = list(current_itemsets)
    
    k = 2
    while current_itemsets:
        candidates = apriori_gen(current_itemsets, k)
        current_itemsets = filter_candidates(transactions, candidates, min_support)
        all_frequent_itemsets.extend(current_itemsets)
        k += 1
    return all_frequent_itemsets

def load_transactions(file_path):
    """Load transactions from a CSV file."""
    transactions = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            transactions.append(set(map(int, row)))
    return transactions

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        min_support = request.form['min_support']

        # Validate file and input
        if not file or not min_support.isdigit() or int(min_support) <= 0:
            return "<pre>Error: Invalid file or minimum support value.</pre>"

        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        try:
            # Load transactions and run Apriori
            transactions = load_transactions(file_path)
            min_support = int(min_support)
            results = apriori(transactions, min_support)
            
            # Prepare output
            output = f"Input file: {file.filename}\n"
            output += f"Minimal support: {min_support}\n"
            output += "{ "
            unique_results = sorted(set(results), key=lambda x: (len(x), sorted(x)))
            for i, itemset in enumerate(unique_results):
                itemset_str = ', '.join(map(str, sorted(itemset)))
                output += f"{{ {itemset_str} }}"
                if i < len(unique_results) - 1:
                    output += " "
            output += " }\n"
            output += f"End - total items: {len(unique_results)}\n"
            return f"<pre>{output}</pre>"
        except Exception as e:
            return f"<pre>Error: {str(e)}</pre>"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
