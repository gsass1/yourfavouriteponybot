from derpibooru import Search, sort
from random import choice

def get_rand_dbimage_for_key(key):
    images = [image for image in Search().query(key, "score.gte:50").sort_by(sort.RANDOM).limit(100)]
    return choice(images)