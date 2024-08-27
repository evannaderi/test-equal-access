import os
import shutil
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

def test_endpoint(endpoint_name, endpoint_path, html_file, output_dir, log_file):
    filename = os.path.basename(html_file)
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    start_time = time.time()
    try:
        response = requests.post(endpoint_path, data=html_content, headers={'Content-Type': 'text/html'})
        response.raise_for_status()
        result = response.json()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{endpoint_name}_{filename}_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Tested {filename} against {endpoint_name} ({endpoint_path}). Output written to {output_file}. Time taken: {elapsed_time:.2f} seconds\n")
        
        print(f"Tested {filename} against {endpoint_name} ({endpoint_path}). Output written to {output_file}. Time taken: {elapsed_time:.2f} seconds")
        return True
    except requests.RequestException as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Error testing {filename} against {endpoint_name} ({endpoint_path}): {str(e)}. Time taken: {elapsed_time:.2f} seconds\n")
        
        print(f"Error testing {filename} against {endpoint_name} ({endpoint_path}): {str(e)}. Time taken: {elapsed_time:.2f} seconds")
        return False

def main():
    endpoints = {
        "express_server": "http://localhost:3000/check",  # Bed's express server
        "lambda_function": "http://localhost:3001/check",  # Lambda function
    }
    html_dir = "html_files"  # Directory containing HTML files
    output_dir = "test_results"  # Directory to store output JSON files
    log_file = "test_log.txt"  # Log file to store timing information

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    if os.path.exists(log_file):
        os.remove(log_file)
        
    html_files = [os.path.join(html_dir, f) for f in os.listdir(html_dir) if f.endswith('.html')]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for endpoint_name, endpoint_path in endpoints.items():
            for html_file in html_files:
                futures.append(executor.submit(test_endpoint, endpoint_name, endpoint_path, html_file, output_dir, log_file))

        for future in as_completed(futures):
            future.result()

    print("All tests completed.")

if __name__ == "__main__":
    main()

