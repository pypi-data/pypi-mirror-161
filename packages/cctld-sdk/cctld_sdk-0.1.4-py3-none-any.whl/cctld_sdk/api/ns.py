from cctld_sdk.common.types import CCTLDActions


class NsApiMixin:
    def ns_add(self, ip: str, name: str):
        data = {"name": name, "ip": ip}
        return self.send_command(action=CCTLDActions.NS_ADD, data=data, root="nslist")

    def ns_list(self, start_at: int = 0, count: int = 100):
        data = {"id": start_at, "count": count}
        return self.send_command(action=CCTLDActions.NS_LIST, data=data)

    def ns_detail_by_id(self, ns_id: int):
        data = {"id": ns_id}
        return self.send_command(
            action=CCTLDActions.NS_DETAIL,
            data=data,
        )

    def ns_detail_by_name(self, name: str):
        data = {"name": name}
        return self.send_command(action=CCTLDActions.NS_LIST_NAMES, data=data)

    def ns_list_connected_to_given_ip(self, ip: str):
        data = {"ip": ip}
        return self.send_command(action=CCTLDActions.NS_LIST_IPS, data=data)

    def ns_list_start_by_given_id(self, start_id: int = 0, count=100):
        data = {"id": start_id, "count": count}
        return self.send_command(action=CCTLDActions.NS_LIST_IDS, data=data)
