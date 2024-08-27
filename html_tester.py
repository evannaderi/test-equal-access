import os
import shutil
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def test_endpoint(endpoint, html_file, output_dir):
    filename = os.path.basename(html_file)
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    try:
        response = requests.post(endpoint, data=html_content, headers={'Content-Type': 'text/html'})
        response.raise_for_status()
        result = response.json()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{filename}_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"Tested {filename} against {endpoint}. Output written to {output_file}")
        return True
    except requests.RequestException as e:
        print(f"Error testing {filename} against {endpoint}: {str(e)}")
        return False

def main():
    # Configuration
    endpoints = [
        "http://localhost:3000/check",
    ]
    html_dir = "html_files"  # Directory containing HTML files
    output_dir = "test_results"  # Directory to store output JSON files

    # Delete and recreate the output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Get all HTML files
    html_files = [os.path.join(html_dir, f) for f in os.listdir(html_dir) if f.endswith('.html')]

    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for endpoint in endpoints:
            for html_file in html_files:
                futures.append(executor.submit(test_endpoint, endpoint, html_file, output_dir))

        # Wait for all tasks to complete
        for future in as_completed(futures):
            future.result()

    print("All tests completed.")

if __name__ == "__main__":
    main()

