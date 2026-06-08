"""
Spending Breakdown Dialog - Model
Fetches per-category transaction detail for a given month
"""
import calendar


class SpendingBreakdownModel:
    """Model: Fetches categorised transactions for the breakdown dialog"""

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def get_breakdown(self, year, month):
        """
        Return spending grouped by category, each with individual transactions.

        Returns:
            {
                'month_label': 'April 2026',
                'total': 348.28,
                'categories': [
                    {
                        'name': 'Groceries',
                        'color': '#27AE60',
                        'total': 120.00,
                        'transactions': [
                            {'date': 'Apr 3', 'description': 'Walmart', 'amount': 75.00},
                            ...
                        ]
                    },
                    ...
                ]
            }
        """
        month_label = f"{calendar.month_name[month]} {year}"
        raw = self.data_manager.load_month_data(year, month)

        # Build category colour map
        colour_map = {
            cat['name']: cat.get('color', '#95A5A6')
            for cat in self.data_manager.categories
        }

        # Accumulate transactions per category
        categories: dict[str, dict] = {}

        for day_key, transactions in raw.items():
            day = int(day_key)
            date_label = f"{calendar.month_abbr[month]} {day}"

            for tx in transactions:
                if not isinstance(tx, dict):
                    continue
                if tx.get('status') == 'pending':
                    continue
                category = tx.get('category', 'Uncategorized')
                if category in ('Transfer', 'Debt Payment'):
                    continue
                amount = float(tx.get('amount', 0))
                if amount >= 0:       # only expenses
                    continue

                abs_amount = abs(amount)
                if category not in categories:
                    categories[category] = {
                        'name': category,
                        'color': colour_map.get(category, '#95A5A6'),
                        'total': 0.0,
                        'transactions': []
                    }
                categories[category]['total'] += abs_amount
                categories[category]['transactions'].append({
                    'date': date_label,
                    'day': day,          # for sorting
                    'description': tx.get('title', 'Untitled'),
                    'amount': abs_amount
                })

        # Sort transactions within each category by day
        cat_list = list(categories.values())
        for cat in cat_list:
            cat['transactions'].sort(key=lambda t: t['day'])

        # Sort categories by total descending
        cat_list.sort(key=lambda c: c['total'], reverse=True)

        grand_total = sum(c['total'] for c in cat_list)

        return {
            'month_label': month_label,
            'total': grand_total,
            'categories': cat_list
        }