import smtplib
import dns.resolver

def extract_domain(email):
    """Extracts domain from an email."""
    try:
        return email.split("@")[1]
    except IndexError:
        return None

def is_domain_valid(domain):
    """Checks if the domain has MX records."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return True if mx_records else False
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout):
        return False

def is_email_valid(email, domain):
    """Validates email using SMTP by checking the recipient."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(mx_records[0].exchange)

        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo()
        server.mail('noreply@datagateway.in')
        code, message = server.rcpt(email)
        server.quit()

        return code == 250
    except Exception:
        return False

def validate_single_email(email):
    """Validates a single email and returns detailed results."""
    domain = extract_domain(email)
    if not domain:
        return {
            'email': email,
            'domain': None,
            'domain_valid': False,
            'email_valid': False,
            'error': 'Invalid email format'
        }
    
    domain_status = is_domain_valid(domain)
    email_status = is_email_valid(email, domain) if domain_status else False
    
    return {
        'email': email,
        'domain': domain,
        'domain_valid': domain_status,
        'email_valid': email_status,
        'error': None
    }

def validate_emails(df):
    """Validates emails in a DataFrame and returns results."""
    results = []
    for email in df['Email']:
        result = validate_single_email(email)
        results.append([
            result['email'],
            result['domain'],
            result['domain_valid'],
            result['email_valid']
        ])
    return results