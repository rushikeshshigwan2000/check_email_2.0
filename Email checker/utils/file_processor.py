import pandas as pd
def process_uploaded_file(filepath):
    """Process uploaded file and return validation results."""
    try:
        if filepath.endswith('.csv'):
            # Try multiple encodings for CSV files
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(filepath, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Failed to decode CSV file with common encodings")
        elif filepath.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            raise ValueError("Unsupported file format")
        
        if 'Email' not in df.columns:
            raise ValueError("File must contain an 'Email' column")
        
        from utils.email_validator import validate_emails
        results = validate_emails(df)
        
        return pd.DataFrame(results, columns=['Email', 'Domain', 'Domain Valid', 'Email Valid'])
    
    except Exception as e:
        raise ValueError(f"Error processing file: {str(e)}")