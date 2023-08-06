import class_7zip_arch
import os

def generator_wrapper(iterable):
    gen = iter(iterable)
    while True:
        try:
            xx = next(gen)
            yield xx
        except StopIteration:
            break
        except Exception as e:
            print('!!!!!!!!!!!!!!!!!!!!1234', e) # or whatever kind of logging you want


data_in = open(r"cats.lzh", "rb").read()
for x in range(200000):
    if (x % 10) == 0:
        print("cycle", x, os.getpid(), "\n")

    archer = class_7zip_arch.Class7zArch(data_in)
    files_num = archer.files_in_arch()
    #print("arch have %s files" % files_num)

    is_ok, report, files_list = archer.extract_all()


print("end")