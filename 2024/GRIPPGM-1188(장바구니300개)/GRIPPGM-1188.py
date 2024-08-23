# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('/opt/homebrew/lib/python3.11/site-packages')
from bs4 import BeautifulSoup

def read_html_file(file_path):
    """Read HTML file content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def parse_html(html_content):
    """Parse HTML content and extract data from shop-group-row and product-row."""
    soup = BeautifulSoup(html_content, 'html.parser')
    shop_groups = soup.find_all(class_='shop-group-row')

    data = {}
    for group in shop_groups:
        producer_id = group.get('data-producer-id')
        if producer_id:
            product_rows = group.find_all(class_='product-row')
            product_ids = [product.get('data-product-id') for product in product_rows if product.get('data-product-id')]
            data[producer_id] = product_ids

    return data

def get_neighbors(product_list, product_id):
    """Find the previous and next elements in the list relative to the given product_id."""
    index = product_list.index(product_id)
    prev_product = product_list[index - 1] if index > 0 else None
    next_product = product_list[index + 1] if index < len(product_list) - 1 else None
    return prev_product, next_product

def get_latest_files(directory):
    """Get the two most recently modified HTML files in the specified directory."""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.html')]
    
    if not files:
        print("No HTML files found in the directory.")
        return None, None

    files.sort(key=os.path.getmtime, reverse=True)
    
    if len(files) < 2:
        print("Not enough HTML files to compare.")
        return None, None

    return files[0], files[1]

def compare_html_files(file1_path, file2_path):
    """Compare two HTML files and report differences in data-producer-id and product-rows."""
    print(f"비교 원본 파일 : {file2_path}")
    print(f"비교 파일 : {file1_path}")

    # Read HTML files
    html_content1 = read_html_file(file1_path)
    html_content2 = read_html_file(file2_path)

    # Parse both HTML contents
    data1 = parse_html(html_content1)  # data1 corresponds to the newer file
    data2 = parse_html(html_content2)  # data2 corresponds to the older file
    
    # Calculate total product count for both files
    total_products_file1 = sum(len(product_ids) for product_ids in data1.values())
    total_products_file2 = sum(len(product_ids) for product_ids in data2.values())
    
    # Print total product counts
    print(f"\nTotal Product Count in HTML (newer) {file1_path}: {total_products_file1}")
    print(f"Total Product Count in HTML (older) {file2_path}: {total_products_file2}\n")

    # Print out the producer IDs and product counts
    print('\n##########')
    print(f'Shop-group-row and product counts in HTML (newer) {file1_path}:')
    i = 0
    for producer_id, product_ids in data1.items():
        i += 1  # Increment the counter in each iteration
        print(f'Producer ID: {producer_id}, \nProduct Count: {len(product_ids)}, Product IDs: {product_ids}\n')
    
    print(f'\nShop-group-row and product counts in HTML (older) {file2_path}:')
    i = 0
    for producer_id, product_ids in data2.items():
        i += 1  # Increment the counter in each iteration
        print(f'{i} Producer ID: {producer_id}, \nProduct Count: {len(product_ids)}, Product IDs: {product_ids}\n')

    # Compare product lists between the two files
    added_products = {}
    deleted_products = {}

    for producer_id, product_ids1 in data1.items():
        product_ids2 = data2.get(producer_id, [])
        added = set(product_ids1) - set(product_ids2)
        if added:
            added_products[producer_id] = sorted(added)

    for producer_id, product_ids2 in data2.items():
        product_ids1 = data1.get(producer_id, [])
        deleted = set(product_ids2) - set(product_ids1)
        if deleted:
            deleted_products[producer_id] = sorted(deleted)

    print('\n\n##########')
    print(f'"{file2_path}" >>> {file1_path}(최신 파일)에 추가된 product list:')
    if added_products:
        for producer_id, products in added_products.items():
            for product in products:
                prev_product, next_product = get_neighbors(data1[producer_id], product)
                print(f'\nProducer ID: {producer_id}, \nAdded Product ID: {product}, \nPrevious: {prev_product}, \nNext: {next_product}')
    else:
        print("None")       

    print('\n##########')
    print(f'"{file1_path}"(최신 파일)에서 삭제된 product list:')
    if deleted_products:
        for producer_id, products in deleted_products.items():
            for product in products:
                prev_product, next_product = get_neighbors(data2[producer_id], product)
                print(f'\nProducer ID: {producer_id}, \nDeleted Product ID: {product}, \nPrevious: {prev_product}, \nNext: {next_product}')
    else:
        print("None")

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Get the two most recent HTML files in the script's directory
latest_file, previous_file = get_latest_files(script_directory)

if latest_file and previous_file:
    # Compare the HTML files
    compare_html_files(latest_file, previous_file)
