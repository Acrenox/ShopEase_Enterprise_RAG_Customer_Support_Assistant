def rerank(results):
    return sorted(results, key=lambda item: float(item['score']))
