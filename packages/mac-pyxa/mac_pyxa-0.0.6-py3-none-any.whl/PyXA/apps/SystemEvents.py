"""Control the macOS System Events application using JXA-like syntax.
"""

from PyXA import XABase

class XASystemEventsApplication(XABase.XAApplication, XABase.XACanConstructElement, XABase.XAAcceptsPushedElements):
    def __init__(self, properties):
        super().__init__(properties)

    def processes(self):
        return super().elements("applicationProcesses", XABase.XAApplicationProcess)

    def processes_with_properties(self, properties):
        return super().elements_with_properties("applicationProcesses", properties, XABase.XAApplicationProcess)
    
    def process(self, index: int):
        return super().element_at_index("applicationProcesses", index, XABase.XAApplicationProcess)

    def first_process(self):
        return super().first_element("applicationProcesses", XABase.XAApplicationProces)

    def last_process(self):
        return super().last_element("applicationProcesses", XABase.XAApplicationProcess)

class XASystemEventsUIElement(XABase.XAHasElements):
    def __init__(self, properties):
        super().__init__(properties)
        self.xa_scut = {}

    def entire_contents(self) -> 'XASystemEventsUIElement':
        print(self.xa_elem.entireContents())
        return self

    # def all(self, specifier, in_class = "groups", force_update = False):
    #     if (specifier, in_class) in self.xa_scut and not force_update:
    #         return self.xa_scut[(specifier, in_class)]

    #     valid_specifiers = {
    #         "windows": XASystemEventsWindow,
    #         "groups": XASystemEventsGroup,
    #         "text_fields": XASystemEventsTextField,
    #         "text_areas": XASystemEventsTextArea,
    #         "buttons": XASystemEventsButton,
    #         "actions": XASystemEventsAction,
    #     }
    #     target_class = valid_specifiers[specifier]

    #     target_objects = []
    #     sub_objects = self.__getattribute__(in_class)()
    #     for item in sub_objects:
    #         target_objects.extend(item.all(specifier, in_class))

    #     if isinstance(self, target_class):
    #         target_objects.append(self)
    #     else:
    #         target_objects.extend(self.__getattribute__(specifier)())

    #     self.xa_scut[(specifier, in_class)] = target_objects
    #     return target_objects