import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from delivery import calculate_delivery_cost


class TestInputValidation(unittest.TestCase):
    """Проверка отклонения некорректных входных данных."""

    def test_weight_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual((cost, date), (-1, "0000-00-00"))

    def test_weight_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(50.1, 100, "обычный")
        self.assertEqual((cost, date), (-1, "0000-00-00"))

    def test_distance_below_minimum_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 0, "обычный")
        self.assertEqual((cost, date), (-1, "0000-00-00"))

    def test_distance_above_maximum_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 5001, "обычный")
        self.assertEqual((cost, date), (-1, "0000-00-00"))

    def test_invalid_package_type_returns_error(self):
        cost, date = calculate_delivery_cost(1.0, 100, "летающий")
        self.assertEqual((cost, date), (-1, "0000-00-00"))


class TestBoundaryValues(unittest.TestCase):
    """Проверка граничных значений — они должны считаться валидными."""

    def test_minimum_boundary_values_are_valid(self):
        # ровно нижняя граница: weight=0.1, distance=1
        cost, date = calculate_delivery_cost(0.1, 1, "обычный")
        self.assertNotEqual(cost, -1)

    def test_maximum_boundary_values_are_valid(self):
        # ровно верхняя граница: weight=50.0, distance=5000
        cost, date = calculate_delivery_cost(50.0, 5000, "обычный")
        self.assertNotEqual(cost, -1)


class TestBaseCostCalculation(unittest.TestCase):
    """Проверка расчёта базовой стоимости без надбавок."""

    def test_base_cost_for_light_package_short_distance(self):
        # base_cost(200) + distance(100)*5 = 700, вес не даёт надбавки
        cost, date = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_distance_cost_increases_with_distance(self):
        cost_short, _ = calculate_delivery_cost(1.0, 100, "обычный")
        cost_long, _ = calculate_delivery_cost(1.0, 1000, "обычный")
        self.assertGreater(cost_long, cost_short)

    def test_weight_exactly_five_kg_gets_no_multiplier(self):
        # ГРАНИЧНЫЙ СЛУЧАЙ: условие в коде "weight > 5.0", поэтому
        # вес РОВНО 5.0 не получает коэффициент 1.2 (хотя 5.01 уже получает).
        # Тест документирует текущее поведение — стоит уточнить у автора
        # кода, задумана ли эта асимметрия границы.
        cost, date = calculate_delivery_cost(5.0, 100, "обычный")
        self.assertEqual(cost, 700)


class TestWeightMultiplier(unittest.TestCase):
    """Проверка весовых коэффициентов."""

    def test_medium_weight_applies_1_2_multiplier(self):
        # (200 + 100*5) * 1.2 = 840
        cost, date = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(cost, 840)

    def test_heavy_weight_applies_1_5_multiplier(self):
        # (200 + 100*5) * 1.5 = 1050
        cost, date = calculate_delivery_cost(25.0, 100, "обычный")
        self.assertEqual(cost, 1050)


class TestPackageTypeSurcharge(unittest.TestCase):
    """Проверка надбавок за тип посылки."""

    def test_fragile_package_adds_300_rubles(self):
        cost, date = calculate_delivery_cost(1.0, 100, "хрупкий")
        self.assertEqual(cost, 1000)  # 700 + 300

    def test_dangerous_package_adds_1000_rubles(self):
        cost, date = calculate_delivery_cost(1.0, 100, "опасный")
        self.assertEqual(cost, 1700)  # 700 + 1000


class TestDeliveryDateCalculation(unittest.TestCase):
    """Проверка расчёта даты доставки (точка отправления зафиксирована: 2026-09-03)."""

    def test_short_distance_takes_one_day(self):
        cost, date = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_long_distance_takes_more_days(self):
        # distance // 500 = 1000 // 500 = 2 дня
        cost, date = calculate_delivery_cost(1.0, 1000, "обычный")
        self.assertEqual(date, "2026-09-05")

    def test_max_distance_takes_ten_days(self):
        # 5000 // 500 = 10 дней
        cost, date = calculate_delivery_cost(1.0, 5000, "обычный")
        self.assertEqual(date, "2026-09-13")


class TestExpressDeliveryBusinessLogic(unittest.TestCase):
    """
    ОЖИДАЕМАЯ бизнес-логика экспресс-доставки (по смыслу, а не по коду):
    экспресс должен быть быстрее ОБЫЧНОЙ доставки, но не может быть
    ДЕШЕВЛЕ и не может занимать 0 дней. Эти тесты специально написаны
    так, чтобы поймать баг, если реализация нарушает эту логику.
    """

    def test_express_delivery_should_not_be_cheaper_than_standard(self):
        standard_cost, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=False)
        express_cost, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        # Ожидание: экспресс-доставка стоит НЕ МЕНЬШЕ обычной (обычно — дороже).
        self.assertGreaterEqual(
            express_cost,
            standard_cost,
            "Экспресс-доставка не должна быть дешевле обычной — "
            "похоже, в коде коэффициент для is_express перепутан "
            "(умножение на 0.5 вместо надбавки).",
        )

    def test_express_delivery_date_should_be_at_least_one_day_later(self):
        cost, date = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        # Ожидание: доставка не может занять 0 дней — минимум 1 день,
        # даже при экспресс-доставке на короткое расстояние.
        self.assertNotEqual(
            date,
            "2026-09-03",
            "Дата доставки совпадает с датой заказа — похоже, деление "
            "days_needed // 2 для экспресс-доставки не защищено от "
            "обнуления при days_needed == 1.",
        )


if __name__ == "__main__":
    unittest.main()