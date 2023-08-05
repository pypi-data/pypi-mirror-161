from robertcommonbasic.basic.os.env import get_env, set_env


def test():
    print(get_env('MQ_FILE_PATH'))
    set_env('ROBERT_ENV_TEST', 'v1')
    if 'v1' == get_env('ROBERT_ENV_TEST'):
        print(True)
    else:
        print(False)

test()