from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
from utils.email_validator import validate_emails, validate_single_email
from utils.file_processor import process_uploaded_file
import pandas as pd
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'single_email' in request.form:
            email = request.form['single_email']
            return redirect(url_for('results', single_email=email))
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                try:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    return redirect(url_for('results', filename=filename))
                except Exception as e:
                    flash(f"Error uploading file: {str(e)}", 'error')
                    return redirect(url_for('index'))
    
    return render_template('index.html')

@app.route('/results')
def results():
    single_email = request.args.get('single_email')
    filename = request.args.get('filename')
    
    if single_email:
        result = validate_single_email(single_email)
        return render_template('results.html', single_result=result)
    elif filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        result_df = process_uploaded_file(filepath)
        
        # Save results to temp files
        temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        result_df.to_csv(temp_csv.name, index=False)
        
        temp_xlsx = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        with pd.ExcelWriter(temp_xlsx.name, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, index=False)
            
        return render_template('results.html', 
                            results=result_df.to_dict('records'),
                            csv_path=temp_csv.name,
                            xlsx_path=temp_xlsx.name)
    else:
        return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)