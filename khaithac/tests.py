import datetime as dt
from decimal import Decimal

from django.test import TestCase

from core.models import PostOffice
from khaithac.models import (
    KhaiThacImportBatch,
    KhaiThacPriceCard,
    KhaiThacRawProduction,
    KhaiThacServiceMapping,
)
from khaithac.services.pricing import compute_fund_breakdown, get_unit_price, load_price_cards


class FundBreakdownTests(TestCase):
    """Kiem tra cong thuc Quy tien luong = Sum(San luong x Don gia theo
    Nhom dich vu), bao gom truong hop don gia thay doi giua thang (VB1054
    -> VB1182) va truong hop Loai chua duoc anh xa (KT1)."""

    def setUp(self):
        self.po = PostOffice.objects.create(code="530100", name="KTC1 Hue 1")
        self.batch = KhaiThacImportBatch.objects.create(
            post_office=self.po, production_date=dt.date(2026, 3, 15)
        )
        KhaiThacServiceMapping.objects.create(loai_raw="E_TN", nhom_dich_vu=KhaiThacServiceMapping.NHOM_EMS)
        KhaiThacServiceMapping.objects.create(loai_raw="KT1", nhom_dich_vu=None)
        KhaiThacPriceCard.objects.create(
            nhom_dich_vu=KhaiThacServiceMapping.NHOM_EMS, unit_price=Decimal("300"),
            effective_from=dt.date(2026, 1, 1), effective_to=dt.date(2026, 2, 28),
        )
        KhaiThacPriceCard.objects.create(
            nhom_dich_vu=KhaiThacServiceMapping.NHOM_EMS, unit_price=Decimal("317"),
            effective_from=dt.date(2026, 3, 1), effective_to=None,
        )

    def test_get_unit_price_picks_correct_period(self):
        cards = load_price_cards()
        self.assertEqual(get_unit_price(cards, "EMS", dt.date(2026, 2, 15)), Decimal("300"))
        self.assertEqual(get_unit_price(cards, "EMS", dt.date(2026, 3, 15)), Decimal("317"))

    def test_fund_uses_mapped_price_and_excludes_unmapped(self):
        KhaiThacRawProduction.objects.create(
            import_batch=self.batch, post_office=self.po, production_date=dt.date(2026, 3, 15),
            ca="CA1", loai_raw="E_TN", weight_tier="<=2kg", so_luong=100,
        )
        KhaiThacRawProduction.objects.create(
            import_batch=self.batch, post_office=self.po, production_date=dt.date(2026, 3, 15),
            ca="CA2", loai_raw="KT1", weight_tier="<=2kg", so_luong=50,
        )
        result = compute_fund_breakdown(self.po, 2026, 3)
        self.assertEqual(result["tong_quy_tien_luong"], Decimal("31700"))  # 100 x 317
        self.assertEqual(result["tong_san_luong_tinh_tien"], 100)
        self.assertEqual(result["unmapped_loai"], {"KT1": 50})
        self.assertEqual(result["by_nhom_thang"]["EMS"]["so_luong"], 100)

    def test_fund_sums_multiple_weight_tiers_into_one_loai(self):
        KhaiThacRawProduction.objects.create(
            import_batch=self.batch, post_office=self.po, production_date=dt.date(2026, 3, 15),
            ca="CA1", loai_raw="E_TN", weight_tier="<=2kg", so_luong=100,
        )
        KhaiThacRawProduction.objects.create(
            import_batch=self.batch, post_office=self.po, production_date=dt.date(2026, 3, 15),
            ca="CA1", loai_raw="E_TN", weight_tier=">2kg", so_luong=20,
        )
        result = compute_fund_breakdown(self.po, 2026, 3)
        self.assertEqual(result["tong_san_luong_tinh_tien"], 120)
        self.assertEqual(result["tong_quy_tien_luong"], Decimal("38040"))  # 120 x 317
