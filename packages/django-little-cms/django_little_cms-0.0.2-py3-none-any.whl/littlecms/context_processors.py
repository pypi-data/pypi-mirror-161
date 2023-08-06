from littlecms.models import MenuOption


def menuOptions(request):
    menu_options = MenuOption.objects.filter(parent__isnull=True,
                                             is_active=True)
    return {'menu_options': menu_options}