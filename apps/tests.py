from django.test import TestCase

from apps.models import Category, Product
from apps.schema import schema


class SchemaTests(TestCase):
    def run_query(self, query):
        result = schema.execute(query)
        self.assertIsNone(result.errors, result.errors)
        return result.data

    def setUp(self):
        self.phones = Category.objects.create(title='Phones')
        self.laptops = Category.objects.create(title='Laptops')
        self.product = Product.objects.create(title='Pixel', price=500, stock=3, category=self.phones)

    def test_all_categories(self):
        data = self.run_query('{ allCategories { title } }')
        self.assertEqual({c['title'] for c in data['allCategories']}, {'Phones', 'Laptops'})

    def test_all_products_returns_products(self):
        data = self.run_query('{ allProducts { title stock category { title } } }')
        self.assertEqual(data['allProducts'], [{'title': 'Pixel', 'stock': 3, 'category': {'title': 'Phones'}}])

    def test_create_category(self):
        data = self.run_query('mutation { createCategory(title: "Tablets") { status } }')
        self.assertEqual(data['createCategory']['status'], 201)
        self.assertTrue(Category.objects.filter(title='Tablets').exists())

    def test_create_product(self):
        data = self.run_query(
            f'mutation {{ createProduct(title: "ThinkPad", price: 900, stock: 2, category: {self.laptops.pk}) {{ status }} }}'
        )
        self.assertEqual(data['createProduct']['status'], 201)
        self.assertEqual(Product.objects.get(title='ThinkPad').category, self.laptops)

    def test_create_product_with_unknown_category(self):
        data = self.run_query('mutation { createProduct(title: "X", price: 1, stock: 1, category: 999) { status } }')
        self.assertEqual(data['createProduct']['status'], 404)
        self.assertFalse(Product.objects.filter(title='X').exists())

    def test_update_category(self):
        self.run_query(f'mutation {{ updateCategory(id: {self.phones.pk}, title: "Smartphones") {{ status }} }}')
        self.phones.refresh_from_db()
        self.assertEqual(self.phones.title, 'Smartphones')

    def test_update_product_category(self):
        data = self.run_query(
            f'mutation {{ updateProduct(id: {self.product.pk}, category: {self.laptops.pk}) {{ status }} }}'
        )
        self.assertEqual(data['updateProduct']['status'], 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.category, self.laptops)

    def test_update_product_stock_to_zero(self):
        self.run_query(f'mutation {{ updateProduct(id: {self.product.pk}, stock: 0) {{ status }} }}')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)

    def test_update_missing_product(self):
        data = self.run_query('mutation { updateProduct(id: 999, stock: 1) { status } }')
        self.assertEqual(data['updateProduct']['status'], 404)

    def test_delete_product(self):
        data = self.run_query(f'mutation {{ deleteProduct(id: {self.product.pk}) {{ status message }} }}')
        self.assertEqual(data['deleteProduct']['status'], 200)
        self.assertFalse(Product.objects.exists())

    def test_delete_category_cascades_to_products(self):
        data = self.run_query(f'mutation {{ deleteCategory(id: {self.phones.pk}) {{ status }} }}')
        self.assertEqual(data['deleteCategory']['status'], 200)
        self.assertFalse(Product.objects.exists())

    def test_delete_missing_returns_404(self):
        data = self.run_query('mutation { deleteProduct(id: 999) { status } deleteCategory(id: 999) { status } }')
        self.assertEqual(data['deleteProduct']['status'], 404)
        self.assertEqual(data['deleteCategory']['status'], 404)
