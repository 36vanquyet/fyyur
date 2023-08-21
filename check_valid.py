import re
from wtforms.validators import ValidationError
    
def validate_phone(self, phone):
    us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
    match = re.search(us_phone_num, phone.data)
    if not match:
        raise ValidationError('Error, phone number must be in format xxx-xxx-xxxx')