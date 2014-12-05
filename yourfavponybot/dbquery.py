from derpibooru import Search, sort

def get_rand_dbimage_for_key(key):
    for image in Search().query(key, "score.gte:50").sort_by(sort.RANDOM).limit(1):
        return image