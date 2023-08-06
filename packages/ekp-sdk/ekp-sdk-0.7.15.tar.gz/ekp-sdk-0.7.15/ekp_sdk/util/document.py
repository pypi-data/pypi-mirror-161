from ekp_sdk.util.collection import collection


def documents(collectionName):
    return f'$["{collection(collectionName)}"].*'
