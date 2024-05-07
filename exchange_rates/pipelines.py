import csv
from datetime import datetime

class ExchangeRatesPipeline:
    def __init__(self):
        self.exchange_rates_file = 'exchange_rates.csv'
        self.fields = ['Base-Currency', 'Foreign-Currency', 'Exchange-Rate', 'Updated_at']

    def open_spider(self, spider):
        self.csvfile = open(self.exchange_rates_file, 'a', newline='')
        self.writer = csv.DictWriter(self.csvfile, fieldnames=self.fields)

        # Write headers only if the file is empty
        if self.csvfile.tell() == 0:
            self.writer.writeheader()

    def process_item(self, item, spider):
        updated = False
        rows = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.exchange_rates_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Base-Currency'] == item['base_currency'] and row['Foreign-Currency'] == item['foreign_currency']:
                    row['Exchange-Rate'] = item['exchange_rate']
                    row['Updated_at'] = now
                    updated = True
                rows.append(row)

        if not updated:
            new_row = {'Base-Currency': item['base_currency'], 'Foreign-Currency': item['foreign_currency'], 'Exchange-Rate': item['exchange_rate'], 'Updated_at': now}
            rows.append(new_row)

        with open(self.exchange_rates_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(rows)

        return item

    def close_spider(self, spider):
        self.csvfile.close()
