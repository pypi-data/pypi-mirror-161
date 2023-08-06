import class_7zip_arch

data_in = open(r"cats.lzh", "rb").read()
for x in range(3):
    print("\ncycle", x, "\n")
    archer = class_7zip_arch.Class7zArch(data_in)
    files_num = archer.files_in_arch()
    print("arch have %s files" % files_num)

    for num, (path, data) in enumerate(archer):
        print("%s\t%s\t%s" % (num, path, data[:10]))
        open(path, 'wb').write(data)

    print("end arch")


print("end")