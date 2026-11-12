from django.db import migrations

def setup_groups_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Product = apps.get_model('marketplace', 'Product')  # Adjust app name if necessary

    vendor_group, _ = Group.objects.get_or_create(name='Vendors')
    Group.objects.get_or_create(name='Buyers')

    # Assign product management permissions to the Vendors group
    product_ct = ContentType.objects.get_for_model(Product)
    vendor_permissions = Permission.objects.filter(
        content_type=product_ct,
        codename__in=['add_product', 'change_product', 'delete_product']
    )
    vendor_group.permissions.set(vendor_permissions)

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0005_productreview_is_verified'),  # Replace with your actual latest migration dependency
    ]

    operations = [
        migrations.RunPython(setup_groups_and_permissions),
    ]
