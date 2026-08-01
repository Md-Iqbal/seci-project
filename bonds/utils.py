from datetime import datetime


def generate_WEB_application_no(last_id):
    year = datetime.now().year
    return f"WEB-{year}-{last_id:06d}"

def generate_USDB_application_no(last_id):
    year = datetime.now().year
    return f"USDB-{year}-{last_id:06d}"