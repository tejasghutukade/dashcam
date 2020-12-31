
import os
import math
print("before import")

print("before functionA")


def functionA():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    print("Root Directory " + ROOT_DIR)


print("before functionB")


def functionB():
    print("Function B {}".format(math.sqrt(100)))


print("before __name__ guard")
if __name__ == '__main__':
    functionA()
    functionB()
print("after __name__ guard")
