# Graphql

[![Tests](https://github.com/sanjarbek-ashurboyev/Graphql/actions/workflows/tests.yml/badge.svg)](https://github.com/sanjarbek-ashurboyev/Graphql/actions/workflows/tests.yml)

A GraphQL API built with Django and Graphene-Django: queries and full create, update and
delete mutations for products and their categories, with the GraphiQL explorer built in.

## Tech stack

Python · Django · Graphene-Django · django-cors-headers · SQLite

## Schema

| Type | Fields |
|---|---|
| `Category` | `id`, `title`, `products` |
| `Product` | `id`, `title`, `price`, `stock`, `category` |

**Queries:** `allCategories`, `allProducts`
**Mutations:** `createCategory`, `updateCategory`, `deleteCategory`,
`createProduct`, `updateProduct`, `deleteProduct`

## Example

```graphql
mutation {
  createProduct(title: "Keyboard", price: 250000, stock: 12, category: 1) {
    status
    message
  }
}

query {
  allProducts {
    id
    title
    price
    stock
    category { title }
  }
}
```

## Running locally

```bash
git clone https://github.com/sanjarbek-ashurboyev/Graphql.git
cd Graphql
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000/graphql/ to use the GraphiQL explorer.

## License

[MIT](LICENSE)
