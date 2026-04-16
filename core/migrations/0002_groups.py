from django.db import migrations

GROUPS_PERMISSIONS = {
    'Administradores': 'ALL',
    'Professores': [
        ('core', 'aluno', ['view']),
        ('core', 'professor', ['view']),
        ('core', 'disciplina', ['add', 'change', 'view']),
        ('core', 'sala', ['view']),
        ('core', 'aula', ['add', 'change', 'delete', 'view']),
        ('core', 'presenca', ['change', 'view']),
    ],
    'Alunos': [
        ('core', 'disciplina', ['view']),
        ('core', 'aula', ['view']),
        ('core', 'presenca', ['add', 'view']),
    ],
}


def create_groups(apps, schema_editor):
    from django.apps import apps as global_apps
    from django.contrib.auth.management import create_permissions

    for app_config in global_apps.get_app_configs():
        create_permissions(app_config, apps=apps, verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    for group_name, perms in GROUPS_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)

        if perms == 'ALL':
            group.permissions.set(Permission.objects.all())
            continue

        permissions = []
        for app_label, model, actions in perms:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
            except ContentType.DoesNotExist:
                continue
            for action in actions:
                codename = f'{action}_{model}'
                perm = Permission.objects.filter(
                    content_type=ct, codename=codename
                ).first()
                if perm:
                    permissions.append(perm)
        group.permissions.set(permissions)


def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=GROUPS_PERMISSIONS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
