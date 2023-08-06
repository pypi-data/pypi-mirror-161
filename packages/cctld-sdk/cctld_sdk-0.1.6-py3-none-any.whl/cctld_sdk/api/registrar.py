from cctld_sdk.common.types import CCTLDActions


class RegistrarApiMixin:
    def password_change(self, new_password: str):
        data = {"pass": new_password}
        return self.send_command(action=CCTLDActions.USER_PASSWORD_CHANGE, data=data)

    def change_history(self, start_at: int = 0, count: int = 100):
        data = {"id": start_at, "count": count}
        return self.send_command(action=CCTLDActions.USER_ALL_EVENT_LOGS, data=data)

    def domains_change_history(self, start_at: int = 0, count: int = 100):
        data = {"id": start_at, "count": count}
        return self.send_command(action=CCTLDActions.USER_DOMAIN_EDIT_LOGS, data=data)

    def balance(self):
        data = {"get": ""}
        return self.send_command(action=CCTLDActions.USER_BALANCE, data=data)
