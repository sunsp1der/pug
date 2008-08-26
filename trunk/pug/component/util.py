"""Component utility functions"""
    
def is_valid_component_class(object, comp):
    validClass = False
    if comp._class_list:
        if hasattr(object,'componentClassList'):
            objectClassList = object.componentClassList
        else:
            objectClassList = []
        for cls in comp._class_list:
            if isinstance(object,cls):
                validClass = True
                break
            for oCls in objectClassList:
                if issubclass( oCls,cls):
                    validClass = True
                    break
            if validClass:
                break
    else:
        return True
    return validClass