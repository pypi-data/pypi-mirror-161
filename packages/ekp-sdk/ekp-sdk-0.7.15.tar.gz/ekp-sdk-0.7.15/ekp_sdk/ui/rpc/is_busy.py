def is_busy(collection):
    return f'$.busy[?(@.id=="{collection}")]'