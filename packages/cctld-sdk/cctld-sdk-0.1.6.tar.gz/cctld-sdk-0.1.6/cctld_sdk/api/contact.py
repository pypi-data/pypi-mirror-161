from cctld_sdk.models import *
from cctld_sdk.common.types import CCTLDActions


class ContactApiMixin:
    def __contact_add(self, contact_obj: PhysicalContact):
        data = contact_obj.__dict__
        return self.send_command(action=CCTLDActions.CONTACT_ADD, data=data)

    def contact_physical_add(self, contact_obj: PhysicalContact):
        return self.__contact_add(contact_obj=contact_obj)

    def contact_legal_add(self, contact_obj: LegalContact):
        return self.__contact_add(contact_obj=contact_obj)

    def contact_list(self, start_at: int = 0, count: int = 100):
        data = {"id": start_at, "count": count}
        return self.send_command(action=CCTLDActions.CONTACT_LIST, data=data)

    def contact_detail(self, contact_id: int):
        data = {"id": contact_id}
        return self.send_command(action=CCTLDActions.CONTACT_DETAIL, data=data)

    def contact_edit(self, contact_id: int, contact_obj: LegalContact):
        data = {"id": contact_id}
        data.update(contact_obj.__dict__)
        return self.send_command(action=CCTLDActions.CONTACT_EDIT, data=data)

    def contact_delete(self, contact_id: int):
        data = {
            "id": contact_id
        }  # fix deleted it (not appear in list) but can get detail
        return self.send_command(action=CCTLDActions.CONTACT_DELETE, data=data)

    def contact_id_list(self, start_at: int = 0, count: int = 100):
        data = {"id": start_at, "count": count}
        return self.send_command(action=CCTLDActions.CONTACT_LIST_IDS, data=data)
