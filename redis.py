import os
import shutil
import requests
import git
from collections import Counter

GITHUB_TOKEN = 'access_token=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'


def canonize(source):
    stop_symbols = '\'\'\"\"{}.,!?:;\n\r()'

    return [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x]


def compare(source1, source2):
    same = 0
    for i in range(len(source1)):
        if source1[i] in source2:
            same = same + 1
    return same * 2 / float(len(source1) + len(source2)) * 100


def list_is_direct(name_path, level=0):
    list_item = os.listdir(name_path)
    files = []
    for item in list_item:
        if os.path.isdir(name_path + '/' + item):
            files += list_is_direct(name_path + '/' + item, level + 1)
        else:
            try:
                text = open(name_path + '/' + item, 'r')
                tmp = text.read()
                tmp = canonize(tmp)
                files += tmp
                text.close()
            except Exception:
                pass
    return files


def genShingle(source):
    import binascii
    shingleLen = 2
    out = []
    for i in range(len(source) - (shingleLen - 1)):
        # print(str(int((i/(len(source) - (shingleLen - 1)))*100)) + '%')
        tmp = binascii.crc32(' '.join([x for x in source[i:i + shingleLen]]).encode('utf-8'))
        out.append(tmp)

    return out


if __name__ == '__main__':
    repoID = '28457823'
    url = f"https://api.github.com/repositories/{repoID}?&" + GITHUB_TOKEN
    json = requests.get(url).json()
    try:
        git.Repo.clone_from(json['clone_url'], '/home/main/PycharmProjects/GitParser/' + repoID)
    except:
        pass
    data = list_is_direct('/home/main/PycharmProjects/GitParser/' + repoID)
    data = genShingle(data)

    counter = Counter(data)
    data = counter.keys()
    print('50%')

    import redis
    redis = redis.Redis(
        host='localhost',
        port='6379')
    for a in data:
        redis.rpush(a, repoID)

    shutil.rmtree('/home/main/PycharmProjects/GitParser/' + repoID)
