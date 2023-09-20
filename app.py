from flask import Flask, render_template, request, Response
import csv
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script', methods=['POST'])
def run_script():
    from subprocess import run, PIPE, CalledProcessError, STDOUT

    source = request.form.get('source')  # Get the "source" value from the form

    # Define the command as a list of strings, including the user's input
    command = [
        "yolo",
        "task=detect",
        "mode=predict",
        "model=./best.pt",
        f"source={source}",  # Include the user's input
        "conf=0.5"
    ]

    try:
        result = run(command, stdout=PIPE, stderr=STDOUT, text=True, check=True)
        output = result.stdout  # Capture the output

        # Create a temporary CSV file with a specific path
        temp_dir = tempfile.gettempdir()  # Get the system's temporary directory
        temp_csv_file_path = os.path.join(temp_dir, 'output.csv')
        rows_to_write = []

        # Split the output into lines
        lines = output.strip().split('\n')

        for line in lines:
            columns = line.split(',')
            if len(columns) >= 11:
                # Keep the 1st, 10th, and 11th columns
                selected_columns = [columns[0], columns[9], columns[10]]
                rows_to_write.append(selected_columns)

        # Write the output to the CSV file
        with open(temp_csv_file_path, 'w', newline='') as temp_csv_file:
            temp_csv_file.write(output)

        # Provide a download link for the CSV file
        download_link = f'/download/output.csv'

    except CalledProcessError as e:
        # Handle any errors that occurred during command execution
        output = f"Error: {e}"
        download_link = None

    return render_template('result.html', output=output, download_link=download_link)

@app.route('/download/<filename>')
def download(filename):
    # Serve the CSV file for download
    return Response(
        open(os.path.join(tempfile.gettempdir(), filename), 'rb').read(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

if __name__ == '__main__':
    app.run(debug=True)
