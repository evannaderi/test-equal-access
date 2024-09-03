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

    # Wrap HTML content in JSON
    payload = json.dumps({"html": html_content})

    start_time = time.time()
    try:
        response = requests.post(endpoint_path, data=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        
        try:
            result: any = response.json()
        except json.JSONDecodeError:
                print("Response is not valid JSON")
                print(f"Type of response: {type(response)}")
                print("Response content:")
                print(response.content)
                print("Response text (if available):")
                print(response.text)                  
                print("Available attributes and methods in the response object:")


                raise ValueError("Response is not valid JSON")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{endpoint_name}_{filename}_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        log_message = f"Tested {filename} against {endpoint_name} ({endpoint_path}). Output written to {output_file}. Time taken: {elapsed_time:.2f} seconds"
        
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(log_message + "\n")
        
        print(log_message)
        return True
    except (requests.RequestException, ValueError) as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        error_message = f"Error testing {filename} against {endpoint_name} ({endpoint_path}): {str(e)}. Time taken: {elapsed_time:.2f} seconds"
        
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(error_message + "\n")
        
        print(error_message)
        return False

def main():
    endpoints = {
        "bed_express_server": "http://localhost:3000/check",  # Bed's express server
        "lambda_function": "http://localhost:3001/check",  # Lambda function
        "ea2_express_server": "http://localhost:3002/check",  # EA2's express server
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

