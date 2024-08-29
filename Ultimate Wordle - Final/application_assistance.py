
class quick_tools():
    def convert_lowercase(phrase):
        return phrase.lower() if phrase != None and type(phrase) == str else phrase

    def check_list(variable):
        return True if variable != None and type(variable) == list else False

class debug_manager:
    @classmethod
    def module_redirect(self, _attr1=None, _attr2=None, _attr3=None, costom=None, content_code=None, event_priority=None):
        if "global_shutOff" != event_priority or "global_shutOff" not in event_priority:
            self._attr1 = _attr1
            self._attr2 = _attr2
            self._attr3 = _attr3
            self.costom = costom
            self.content_code = quick_tools.convert_lowercase(content_code)

            priority_amount = len(event_priority) if isinstance(event_priority, list) else 1
            for event in range(0, priority_amount):
                if event_priority[event] == self.content_code:
                    if costom != None and type(costom) == str:
                        print(costom)
                    elif event_priority[event] == 'window_resize':
                        debug_manager.window_status(self)
                    elif event_priority[event] == 'PLACEHOLDER1':
                        pass
                    elif event_priority[event] == 'PLACEHOLDER2':
                        pass
                    break

    def window_status(self):
        print(f"{self._attr1} size: {self._attr2} x {self._attr3}")


#debug_manager.module_redirect('swas', _attr3='threeee', content_code="window_resize", event_priority=['swasw', 'SWS', 'window_resize'])


