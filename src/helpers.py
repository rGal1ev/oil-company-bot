def is_admin(database, telegram_id):
    admin_id_list = database.get_admin_id_list()


    if telegram_id in admin_id_list:
        return True

    return False


def get_id(call_data):
    return call_data.split(":")[1]
