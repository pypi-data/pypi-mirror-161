# DjangoLDP Community

## Create & assign your users to a default community

To automatically create a community and assign all your local users to it, use the following command:

```bash
./manage.py create_community --name="My community"
```

## Extend community with your own datas

See [DjangoLDP-ESA](https://git.startinblox.com/djangoldp-packages/djangoldp-esa) as an example.

### Nest a field

Add to your project `settings.py`:

```python
COMMUNITY_NESTED_FIELDS = ['my_model_with_a_one_to_one_to_community']
```

You can nest as many field as needed.

### Nest a inline admin

Add to your project `settings.py`:

```python
COMMUNITY_ADMIN_INLINES = [("djangoldp_mypackage.admin", "MyModelInline",)]
```

Where:

- `MyModelInline` is the name of your inline class, should be a `admin.StackedInline` or a `admin.TabularInline`.
- `djangoldp_mypackage` is your package name

You can nest as many inlines as needed.
