import random
import string
from secrets import randbelow

def code_generator(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_code7(instance, size=7):
    new_code=code_generator(size=size)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(alias=new_code).exists()
    if qs_exists:
        return create_code(size=7)
    return new_code

def create_code9(instance, size=7):
    a = randbelow(size)+2
    new_code=code_generator(size=a)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=new_code).exists()
    if qs_exists:
        return create_code(size=7)
    return new_code

def create_code8(instance, size=7):
    a = randbelow(size)+2
    new_code=code_generator(size=a)
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(ref_no=new_code).exists()
    if qs_exists:
        return create_code(size=7)
    return new_code
