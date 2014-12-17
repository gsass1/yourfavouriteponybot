from derpibooru import Search, sort
from random import choice

def get_rand_dbimage_for_key(key, count=200):
    images = [image for image in Search().query(key, "score.gte:50").sort_by(sort.RANDOM).limit(count)]
    if len(images) == 0:
        return None
    else:
        return choice(images)