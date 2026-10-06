import graphene
from graphene_django import DjangoObjectType

from apps.models import Category, Product


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = '__all__'


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'


class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    all_products = graphene.List(ProductType)

    def resolve_all_categories(self, info):
        return Category.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.select_related('category')


class CreateCategory(graphene.Mutation):
    message = graphene.String()
    status = graphene.Int()

    class Arguments:
        title = graphene.String(required=True)

    def mutate(self, info, title):
        Category.objects.create(title=title)
        return CreateCategory(message="Yaratildi", status=201)


class CreateProduct(graphene.Mutation):
    message = graphene.String()
    status = graphene.Int()

    class Arguments:
        title = graphene.String(required=True)
        price = graphene.Int(required=True)
        stock = graphene.Int(required=True)
        category = graphene.Int(required=True)

    def mutate(self, info, title, price, stock, category):
        if not Category.objects.filter(pk=category).exists():
            return CreateProduct(message="Category topilmadi", status=404)
        Product.objects.create(title=title, price=price, stock=stock, category_id=category)
        return CreateProduct(message="Yaratildi", status=201)


class UpdateCategory(graphene.Mutation):
    message = graphene.String()
    status = graphene.Int()

    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()

    def mutate(self, info, id, title=None):
        category = Category.objects.filter(pk=id).first()
        if category is None:
            return UpdateCategory(message="Category topilmadi", status=404)
        if title is not None:
            category.title = title
            category.save(update_fields=['title'])
        return UpdateCategory(message="Category o'zgartirildi", status=200)


class UpdateProduct(graphene.Mutation):
    message = graphene.String()
    status = graphene.Int()

    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        price = graphene.Int()
        stock = graphene.Int()
        category = graphene.Int()

    def mutate(self, info, id, title=None, price=None, category=None, stock=None):
        product = Product.objects.filter(pk=id).first()
        if product is None:
            return UpdateProduct(message="Product topilmadi", status=404)
        # `is not None`, not truthiness: stock=0 and price=0 are valid updates.
        if title is not None:
            product.title = title
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        if category is not None:
            if not Category.objects.filter(pk=category).exists():
                return UpdateProduct(message="Category topilmadi", status=404)
            product.category_id = category
        product.save()
        return UpdateProduct(message="Product o'zgartirildi", status=200)


class DeleteCategory(graphene.Mutation):
    message = graphene.String()
    status = graphene.Int()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        deleted, _ = Category.objects.filter(pk=id).delete()
        if not deleted:
            return DeleteCategory(message="Category topilmadi", status=404)
        return DeleteCategory(message="Category o'chirildi", status=200)


class DeleteProduct(graphene.Mutation):
    message = graphene.String()
    status = graphene.Int()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        deleted, _ = Product.objects.filter(pk=id).delete()
        if not deleted:
            return DeleteProduct(message="Product topilmadi", status=404)
        return DeleteProduct(message="Product o'chirildi", status=200)


class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()


schema = graphene.Schema(query=Query , mutation=Mutation)





