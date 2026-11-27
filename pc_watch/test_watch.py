"""Regression tests for conservative PC purchase filters; no network."""
import datetime as dt
import unittest
import watch

class TestCandidates(unittest.TestCase):
    def item(self, **updates):
        doc = {
          "id": "z123456789",
          "title": "MINISFORUM UM773 Ryzen 7 7735HS 32GB 1TB",
          "description": "CPU Ryzen 7 7735HS\nメモリ 32GB DDR5\nSSD 1TB\nWindows11 Pro 起動確認済み。ACアダプタ付属。",
          "status": "OPEN", "price": 44000,
          "createDate": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        doc.update(updates)
        return doc
    def test_full_system(self):
        result,why=watch.eligible(self.item())
        self.assertIsNotNone(result,why)
    def test_barebone_rejected(self):
        result,_=watch.eligible(self.item(description="メモリ SSD無し、ベアボーン"))
        self.assertIsNone(result)
    def test_sold_rejected(self):
        result,_=watch.eligible(self.item(status="SOLD"))
        self.assertIsNone(result)
    def test_overpriced_rejected(self):
        result,_=watch.eligible(self.item(price=75000))
        self.assertIsNone(result)
    def test_16gb_rejected(self):
        result,_=watch.eligible(self.item(title="MINISFORUM UM773 Ryzen 7 7735HS 16GB 1TB",description="CPU Ryzen 7 7735HS\nメモリ 16GB\nSSD 1TB\n正常に起動確認済み"))
        self.assertIsNone(result)
    def test_old_listing_rejected(self):
        old=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(hours=3)).isoformat()
        result,_=watch.eligible(self.item(createDate=old))
        self.assertIsNone(result)
    def test_no_os_rejected(self):
        result,_=watch.eligible(self.item(description="Ryzen 7 7735HS, メモリ32GB SSD1TB OS無し 動作確認"))
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
