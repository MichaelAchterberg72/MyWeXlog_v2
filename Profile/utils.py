import random
import string

def code_generator(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_code7(instance, size=7):
    new_code=code_generator(size=size)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(alias=new_code).exists()
    if qs_exists:
        return create_code(size=7)
    return new_code
