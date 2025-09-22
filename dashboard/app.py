# Import necessary modules from Flask and Python standard library
from flask import Flask, jsonify, render_template, request  # Flask web framework tools
import json  # For reading JSON files
import os    # For working with file paths

# Create a Flask web application instance
app = Flask(__name__)

def load_jobs():
    """
    Loads job data from the jobs.json file.
    Returns a list of job dictionaries.
    """
    try:
        # Get the folder where this script (app.py) is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the path to the jobs.json file (one folder up, in 'data')
        jobs_path = os.path.join(base_dir, '..', 'data', 'jobs.json')
        # Open the jobs.json file and load its contents as Python data
        with open(jobs_path, 'r', encoding='utf-8') as file:
            jobs = json.load(file)
        return jobs  # Return the list of jobs
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file is missing or not valid JSON, return an empty list
        return []

@app.route('/')
def dashboard():
    """
    Handles the main dashboard page.
    Loads jobs, filters them if a search term is provided,
    calculates some statistics, and renders the dashboard HTML page.
    """
    jobs = load_jobs()  # Load all jobs from the JSON file
    
    # Get the 'search' parameter from the URL (e.g., ?search=python)
    search_term = request.args.get('search', '')
    
    # If a search term is provided, filter jobs by title or company
    if search_term:
        filtered_jobs = [
            job for job in jobs 
            if search_term.lower() in job.get('title', '').lower() or 
               search_term.lower() in job.get('company', '').lower()
        ]
    else:
        # If no search term, show all jobs
        filtered_jobs = jobs
    
    # Calculate statistics for the filtered jobs
    stats = {
        'total_jobs': len(filtered_jobs),  # Total number of jobs shown
        'with_salary': len([
            job for job in filtered_jobs 
            if job.get('salary', 'Not specified') != 'Not specified'
        ]),  # Number of jobs with a specified salary
        'companies': len(set([
            job.get('company', '') for job in filtered_jobs
        ]))  # Number of unique companies in the results
    }
    
    # Render the dashboard.html template, passing jobs, stats, and search term
    return render_template(
        'dashboard.html', 
        jobs=filtered_jobs, 
        stats=stats, 
        search_term=search_term
    )

@app.route('/api/jobs')
def api_jobs():
    """
    API endpoint that returns all jobs as JSON data.
    Useful for JavaScript or other programs to fetch job data.
    """
    jobs = load_jobs()  # Load all jobs
    return jsonify(jobs)  # Return jobs as JSON

# This block runs the app if you start this file directly (not imported)
if __name__ == '__main__':
    # Start the Flask development server  
    # debug=True: shows helpful error messages
    # host='0.0.0.0': makes the app accessible on your network
    # port=5000: runs the app on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)