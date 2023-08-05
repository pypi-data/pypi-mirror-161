from robertcommonbasic.basic.encrypt.md5 import md5_encryption


def test_md5(name, psw):
    md5_psw = md5_encryption(name)
    if md5_psw == psw:
        print(True)
    else:
        print(False)

test_md5('Gc@13579#ZyH', '7b7d3900c3b86cd79a9fb0a904b35cf5')