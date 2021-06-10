import uuid, random

num = 2 ** 48 - 1
my_uuid = str(uuid.uuid1(random.randint(0, 281474976710655))).replace("-", "")

print(my_uuid)
print(len(my_uuid))

