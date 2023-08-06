import class_7zip_arch


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
for x in range(3):
    print("\ncycle", x, "\n")
    archer = class_7zip_arch.Class7zArch(data_in)
    files_num = archer.files_in_arch()
    print("arch have %s files" % files_num)

    for num, (path, data) in enumerate(generator_wrapper(archer)):
        print("%s\t%s\t%s" % (num, path, data[:10]))
        open('cts/' + path, 'wb').write(data)

    print("end arch")


print("end")