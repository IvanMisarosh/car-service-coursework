
def update_supplier(supplier, *, supplier_name=None, email=None, phone=None):
    # TODO: add validation/clean the data
    if supplier_name is not None:
        supplier.set_supplier_name(supplier_name)

    if email is not None:
        supplier.set_email(email)

    if phone is not None:
        supplier.set_phone_number(phone)

    return supplier