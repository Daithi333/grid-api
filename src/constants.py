DATE_FORMAT = '%d/%m/%Y'
DATE_STYLE = 'DD/MM/YYYY'

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

JWT_EXCLUDED_ENDPOINTS = {'read_root', 'users.login', 'users.signup'}
