from .base import BaseEntity

class Call(BaseEntity):
    def __init__(self, id, **kwargs):
        account_sid = ""
        answered_by = None
        caller_name = None
        direction = ""
        duration = None
        forwarded_from = ""
        from_formatted = ""
        _from = ""
        group_sid = None
        parent_call_sid = None
        phone_number_sid = ""
        sid = ""
        start_time = ""
        status = ""
        to = ""
        to_formatted = ""
        trunk_sid = None
        queue_time = None
        
        self.set_params(kwargs)
        BaseEntity.__init__(self, id)
