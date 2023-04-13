import supabase


class DataBase:
    def __init__(self, url, key):
        self.database = supabase.create_client(url, key)

    """
    DATABASE 
    GETTERS
    """

    def get_employees(self) -> list:
        data = self.database.table("employees").select("*").execute().data
        return data

    def get_employee_by_id(self, employee_id) -> dict:
        data = self.database.table("employees").select("*").eq("id", employee_id).execute().data[0]
        return data

    def get_employee_by_telegram_id(self, telegram_id) -> dict:
        employee = self.database.table("employees").select("*").eq("telegram_id", telegram_id).execute().data[0]
        return employee

    def get_admin_id_list(self) -> list:
        admin_list: list = self.database.table("employees").select("*").eq("role_id", 1).execute().data
        admin_id_list = []

        for admin_user in admin_list:
            admin_id = admin_user["telegram_id"]

            if admin_id is not None:
                admin_id_list.append(admin_id)

        return admin_id_list

    def get_registration_requests(self):
        registration_requests = self.database.table("registration_requests").select("*").eq("is_cancelled",
                                                                                            False).execute().data
        return registration_requests

    def get_all_registration_requests(self):
        all_registration_requests = self.database.table("registration_requests").select("*").execute().data
        return all_registration_requests

    def get_registration_request_by_id(self, id):
        registration_request = self.database.table("registration_requests").select("*").eq("id", id).execute().data[0]
        return registration_request

    def get_employees_without_telegram_id(self):
        data = self.database.table("employees").select("*").execute()
        filtered_data = []

        for result in data.data:
            if result["telegram_id"] is None:
                filtered_data.append(result)

        return filtered_data

    def get_registered_employees(self):
        all_employees = self.database.table("employees").select("*").execute().data
        registered_employees = []

        for employee in all_employees:
            if employee["telegram_id"] is not None:
                registered_employees.append(employee)

        return registered_employees

    """
    DATABASE
    UPDATES
    """

    def set_telegram_id_into_employee(self, telegram_id, employee_id):
        self.database.table("employees").update({"telegram_id": telegram_id}).eq("id", employee_id).execute()

    def set_registration_request_is_cancelled(self, request_id):
        self.database.table("registration_requests").update({"is_cancelled": True}).eq("id", request_id).execute()

    """
    DATABASE
    INSERTS
    """

    def insert_into_registration_request(self, request):
        self.database.table("registration_requests").insert({
            "telegram_id": request["telegram_id"],
            "title": request["title"],
            "phone": request["phone"],
            "name": request["name"]}).execute()

    def insert_into_feedbacks(self, feedback):
        self.database.table("feedbacks").insert({
            "telegram_id": feedback["telegram_id"],
            "title": feedback["title"]
        }).execute()

    """
    DATABASE
    CONDITIONALS
    """

    def telegram_id_in_employees(self, telegram_id):
        data = self.database.table("employees").select("id").eq("telegram_id", telegram_id).execute()

        if len(data.data) > 0:
            return True

        return False

    def telegram_id_is_admin(self, telegram_id):
        data = self.database.table("employees").select("role_id").eq("telegram_id", telegram_id).execute().data[0]

        if data["role_id"] == 1:
            return True

        return False