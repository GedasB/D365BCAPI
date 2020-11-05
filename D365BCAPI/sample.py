from D365BCAPI.D365BCv1API import Connect

"""
This is sample usage of D365BCv1API. Used standard Dynamics 365 Business Central platform 16.xx(17.xx) objects 
API v1.0 pages.
Existing API pages can be get http://{server}:{port}/{tenant}/api/v1.0/
metadata can be get http://{server}:{port}/{tenant}/api/v1.0/$metadata
Sample flow is:
1. Looking for customer name starting by "Cronus". If do not exists - create. "Recordset read & record create" example
2. Looking for items '1996-S' '2000-S' and g/l account '6610'. Get it id - requires for sales order creation.
 "Get field value" example
3. Create sales order with 4 lines: 2 item lines, g/l account line, comment line. Get created sales order documentid.
  Few related "records creation" example 
4. Add 2 more lines to the existing order. "Add lines to existing order" example.
5. Modify description in comment line in existing order. "Modify existing line" example
6. Delete one line from existing order. "Record delete" example
7. Execute action Microsoft.NAV.shipAndInvoice on just created sales order. "Execute action" example
8. Check is invoice created and what are Total Amount and Remaining Amount in it.
"""

user = psw = "a"  # basic authentication

# customers
url_customers = "http://bs17:7048/BC/api/v1.0/customers"  # page 5471
custname = 'Cronus'  # begin of customer name

# create connection object: url, basic authentication, headers recommended by MS
customers = Connect(url_customers, (user, psw), {"Accept-Language": "en-us"})
# we can only find customer by begin of name
customers.filter_text = f"displayName ge '{custname}' and displayName le '{custname}Z'"
# filter is: where displayName is greater or equal to Cronus and less or equal CronusZ
response_list = customers.read()  # read filtered customers
if len(response_list) > 0:
    print("Read customers", response_list[0].get("displayName"))  # 1st customer name

if customers.except_error is not None:
    raise Exception(customers.except_error)

if len(response_list) > 0:  # customer exists
    custno = response_list[0].get("number")  # if customer exists then get it No.
else:  # create customer if not found
    custno = "91000"
    new_customer = {
        "number": custno,
        "displayName": "Cronusb Ski House",
        "type": "Company",
        "phoneNumber": "256 123456",
        "email": "calsberg@gmail.com",
        "website": "cronus.co.uk",
        "taxLiable": False,
        "currencyCode": "EUR",
        "blocked": " ",
        "address": {
            "street": "Paco str 2",
            "city": "Vilnius",
            "state": "",
            "countryLetterCode": "LT",
            "postalCode": "LT-25126"}
    }
    response_list = customers.insert(new_customer)  # new customer is created

print("Sales order Customer No", custno)

# find item and itemId - it requires for sales document lines creation
url_item = "http://bs17:7048/BC/api/v1.0/items"  # page 5470

item = Connect(url_item, (user, psw), {"Accept-Language": "en-us"})
item.filter_text = "number eq '1996-S'"
item_response = item.read()
item_1_id = None
if len(item_response) > 0:  # item exists
    item_1_id = item_response[0].get("id")  # get item1 id

item.filter_text = "number eq '2000-S'"  # change filter and call for another item
item_response = item.read()
item_2_id = None
if len(item_response) > 0:  # customer exists
    item_2_id = item_response[0].get("id")  # get item2 id

# find g/l account and itemId - it requires for sales document lines
url_account = "http://bs17:7048/BC/api/v1.0/accounts"  # page 5470

account = Connect(url_account, (user, psw), {"Accept-Language": "en-us"})
account.filter_text = "number eq '6610'"  # g/l account no is 6610
account_response = account.read()
account_id = None
if len(account_response) > 0:  # item exists
    account_id = account_response[0].get("id")  # get account id, will be used in order line

# create sales order

# new order dictionary NAV page 5495 and lines NAV page 5496
ext_doc_no = "FDA 17598"  # Only by external document no we can find sales order,
# as for document no is used No. Series
new_order = {
    "externalDocumentNumber": ext_doc_no,  # this is number we'll search created document and get it No.
    "orderDate": "2020-02-06",  # limited by CRONUS demo license date range
    "customerNumber": custno,  # customer number taken/created in previous step
    "currencyCode": "EUR",
    "pricesIncludeTax": False,
    "salesperson": "PS",
    "requestedDeliveryDate": "2020-02-15",
    "status": "Draft",
    "phoneNumber": "370 698 13123",
    "email": "liber.town@contoso.com",
    "shippingPostalAddress": {  # Changing shipping address just for fun
        "street": "Another Str. 77",
        "city": "Hamburg",
        "state": "",
        "countryLetterCode": "DE",
        "postalCode": "DE-20097"
    },
    "salesOrderLines": [  # Navigation property to "Collection(Microsoft.NAV.salesOrderLine)"
        {
            "sequence": "10000",  # mandatory line number
            "lineType": "Item",
            # line type (Comment, Accounts, Item, Resource, Fixed Asset, Charge) can be found at table 5476 >
            # field(9029; "API Type"; Enum "Invoice Line Agg. Line Type")
            "itemId": item_1_id,  # mandatory item_Id (or blank if account_id is used)
            "description": "Customized item description in line",
            "quantity": 2.0,
            "discountPercent": 5
        },
        {
            "sequence": "20000",  # 2nd line
            "lineType": "Item",
            "itemId": item_2_id,
            "quantity": 1.0
        },
        {
            "sequence": "30000",  # 3rd line comments
            "lineType": "Comment",
            "description": "This is Comments line"
        },
        {
            "sequence": "40000",  # 4th line g/l account
            "lineType": "Account",
            "accountId": account_id,  # mandatory account id
            "quantity": 1.0,
            "unitPrice": 100
        }
    ]
}

url_so = "http://bs17:7048/BC/api/v1.0/salesOrders"  # NAV page 5495
so = Connect(url_so, (user, psw), {"Accept-Language": "en-us"})  # create sales order header object
so.filter_text = f"externalDocumentNumber eq '{ext_doc_no}'"
response_list = so.read()  # looking for Sales Order with known external doc no

if len(response_list) > 0:  # order exists and we take order id
    so_number = response_list[0].get("number")  # get order No. just for fun - it is not used in further actions
    so_id = response_list[0].get("id")  # SO id we need later for lines edit
else:  # no order with specified external document No. exists
    response_list = so.insert(new_order)  # create new order with specified external doc no
    if (len(response_list) > 0) and so.except_error is None:
        print("Sales order is created", response_list)  # [201, 'Created'] if everything is OK
    else:
        raise Exception(so.except_error)

    so.filter_text = f"externalDocumentNumber eq '{ext_doc_no}'"
    response_list = so.read()  # looking for Sales Order with known external doc no
    if len(response_list) > 0:
        so_number = response_list[0].get("number")  # get just created order No. - later will use it to find invoice
        so_id = response_list[0].get("id")  # SO id we need later for lines edit
print("SO No", so_number)

# created order lines management
# we need sales order document_id to add it to endpoint url for record editing
if len(so_id) > 0:  # if doc id exists then we go to read lines of this doc
    url_sol = f"http://bs17:7048/BC/api/v1.0/salesOrders({so_id})/salesOrderLines"
else:
    raise Exception('Critical error - Can not find document')

sol = Connect(url_sol, (user, psw), {"Accept-Language": "en-us"})  # new connection to lines
response_list = sol.read()  # read all lines just for fun as we need only few lines for editing
if (len(response_list) > 0) and sol.except_error is None:
    print(f"SO has {len(response_list)} lines")  # number of lines in the document
else:
    raise Exception(sol.except_error)

# add new line in order
line_no = 35000  # line No or sequence
line2_no = 37500  # line No or sequence
line_insert = {
    "sequence": line_no,  # after 3rd line
    "lineType": "Item",
    "itemId": item_2_id,
    "quantity": 3.0
}
response_list = sol.insert(line_insert)  # insert line
if (len(response_list) > 0) and sol.except_error is None:
    print("Added line 35000: Item - 1996-S", response_list)  # [201, 'Created'] if everything is OK
else:
    raise Exception(sol.except_error)

# add one more line and later delete it
line_insert = {
    "sequence": line2_no,  # after 3rd line
    "lineType": "Item",
    "itemId": item_1_id,
    "quantity": 1.0
}
response_list = sol.insert(line_insert)  # insert fake line
if (len(response_list) > 0) and sol.except_error is None:
    print("Added line 37500: Item - '2000-S'", response_list)  # [201, 'Created'] if everything is OK
else:
    raise Exception(sol.except_error)

# count lines
sol.url = f"http://bs17:7048/BC/api/v1.0/salesOrders({so_id})/salesOrderLines"
response_list = sol.read()  # read all lines just for fun
if (len(response_list) > 0) and sol.except_error is None:
    print(f"SO has {len(response_list)} lines after added 2")  # number of lines in the document
else:
    raise Exception(sol.except_error)

#  for line editing we need to have line id, find it by search line with line no 30000
line_no = 30000
sol.filter_text = f"sequence eq {line_no}"  # add filter ?$filter=sequence eq 30000

response_list = sol.read()  # get line from document; line No is 30000
if (len(response_list) > 0) and sol.except_error is None:
    line_id = response_list[0].get('id')  # get line id
    print(f"Line id is {line_id}")
    print("description before update is", response_list[0].get("description"))
else:
    raise Exception(sol.except_error)

# modify exiting line: it is line no 30000
line_update = {"description": "This is updated Comments line"}  # new info to update line
sol.url = f"http://bs17:7048/BC/api/v1.0/salesOrderLines('{line_id}')"  # adding line_id to url
sol.filter_text = ''
#  for beta api document key was document id and sequence
# sol.url = f"http://bs17:7048/BC/api/v1.0/salesOrderLines({so_id},{line_no})"
response_list = sol.modify(line_update)  # update line in parameters new info dic
if (len(response_list) > 0) and sol.except_error is None:
    print("Modified line 30000 description now is 'This is updated Comments line'", response_list)
else:
    raise Exception(sol.except_error)

# delete line
line_no = 37500  # line No (sequence in response json)
# in API beta order line url includes document id and line no (line primary key)
# sol.url = f"http://bs17:7048/BC/api/v1.0/salesOrderLines({so_id},{line_no})"
##
# in API v1.0 we need to find sales line id and identify it by id
# we looking for line with sequence 37500

sol.url = f"http://bs17:7048/BC/api/v1.0/salesOrders({so_id})/salesOrderLines"
sol.filter_text = f"sequence eq {line_no}"  # add filter ?$filter=sequence eq 37500

response_list = sol.read()  # get line with filtered sequence 37500
if (len(response_list) > 0) and sol.except_error is None:
    line_id = response_list[0].get('id')
    print(f"Line 3750 id is  {line_id}")
else:
    raise Exception(sol.except_error)

sol.url = f"http://bs17:7048/BC/api/v1.0/salesOrderLines('{line_id}')"  # adding line_id to URL
sol.filter_text = ''  # remove any filters
response_list = sol.delete()  # update line in parameters new info dic
if (len(response_list) > 0) and sol.except_error is None:
    print("Deleted fake line 37500", response_list)
else:
    raise Exception(sol.except_error)

# count lines
sol.url = f"http://bs17:7048/BC/api/v1.0/salesOrders({so_id})/salesOrderLines"
response_list = sol.read()  # read all lines just for fun
print(f"SO has {len(response_list)} lines after deleted one")  # number of lines in the document

# execute action - order ship and invoice
# http://bs17:7048/BC/api/v1.0/salesOrders({so_id})/Microsoft.NAV.shipAndInvoice
if len(so_id) > 0:  # if doc id not blank (we found it earlier)then we can ship and invoice it
    so.url = f"http://bs17:7048/BC/api/v1.0/salesOrders({so_id})/Microsoft.NAV.shipAndInvoice"  # create URL
else:
    raise Exception('Critical error - Can not find document')

response_list = so.exe()  # execute sales order action "ship and invoice"
if (len(response_list) > 0) and so.except_error is None:
    print("Sales order is shipped and invoiced; response is ", response_list)
else:
    raise Exception(so.except_error)

# find just created invoice by "orderNumber"= so_number
url_salesInvoices = "http://bs17:7048/BC/api/v1.0/salesInvoices"
si = Connect(url_salesInvoices, (user, psw), {"Accept-Language": "en-us"})
so_number = '1001'
si.filter_text = f"orderNumber eq '{so_number}'"

response_list = si.read()

if (len(response_list) > 0) and si.except_error is None:
    si_number = response_list[0].get('number')
    si_totalAmount = response_list[0].get('totalAmountIncludingTax')
    si_remainingAmount = response_list[0].get('remainingAmount')
    print(f'Sales Invoice {si_number} is created \n Total Amount {si_totalAmount} \n '
          f'Remaining Amount {si_remainingAmount}')
else:
    raise Exception(si.except_error)

# Response from execution sample is
# Read customers Cronus Cardoxy Procurement
# Sales order Customer No IC1030
# Sales order is created [201, 'Created']
# SO No 1004
# SO has 4 lines
# Added line 35000: Item - 1996-S [201, 'Created']
# Added line 37500: Item - '2000-S' [201, 'Created']
# SO has 6 lines after added 2
# Line id is 2043b1e7-811e-eb11-b334-ef426b246304-30000
# description before update is This is Comments line
# Modified line 30000 description now is 'This is updated Comments line' [200, 'OK']
# Line 3750 id is  2043b1e7-811e-eb11-b334-ef426b246304-37500
# Deleted fake line 37500 [204, 'No Content']
# SO has 5 lines after deleted one
# Sales order is shipped and invoiced; response is  [204, 'No Content']
# Sales Invoice 103032 is created
#  Total Amount 3531.3
#  Remaining Amount 3531.3
