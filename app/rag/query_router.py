CATEGORY_KEYWORDS = {
    'shipping': ['shipping', 'delivery', 'delivered', 'shipment', 'ship', 'shipped', 'track', 'tracking', 'parcel', 'order status', 'arrive', 'arrival', 'dispatch', 'deliver'],
    'returns': ['return', 'replacement', 'damaged', 'wrong item', 'exchange'],
    'refunds': ['refund', 'money back', 'reimbursement', 'payment', 'reversal'],
    'cancellation': ['cancel', 'cancellation', 'cancelled', 'withdraw'],
    'warranty': ['warranty', 'guarantee', 'repair', 'defective', 'faulty', 'manufacturer warranty'],
    'product': ['product', 'price', 'availability', 'specification', 'stock'],
}


def detect_category(question: str) -> str:
    lowered = question.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return 'general'
