# Dynamics 365 Business Central API Connector

This connector simplifies http connection from Python
to [Microsoft Dynamics 365 Business Central API](https://docs.microsoft.com/en-us/dynamics-nav/api-reference/v1.0/)
providing 4 methods: insert, read, modify, delete (CRUD)

General information about developing app for Dynamics 365 Business Central API can be read 
[here](https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-develop-connect-apps).

Connection endpoint rules are described [here](https://docs.microsoft.com/en-us/dynamics-nav/endpoints-apis-for-dynamics).

Filters rules for API endpoint are described [here](https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-connect-apps-filtering) 

Connector uses python *request* module
##Connector Flow
1. Create connector *object = connect(url,url, auth, headers)*
    where:
    * **url** is connection endpoint (mandatory, but can be modified later)
    * **auth** is authorization information (optional but can't be modified later). for example for basic use tuple *(user, psw)*
    * **headers** is http header used in http calls. For example *{"Accept-Language": "en-us"}* 
2. Read data from database by execute *object.read(filter)*. 
    * filter is text according [API rules](https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-connect-apps-filtering). Filter can be set
    by execute *object.filter_text = new_filter*. Filter can be not used if record Id is used for example url to specific sales order is
    http://navbs:7048/BC/api/beta/salesOrders(document_Id) 
    * URL can be modified before read by execute *object.url = new_url*. In some cases must be specific url used. 
    For example read sales order lines need to be document_id included in url like: http://navbs:7048/BC/api/beta/salesOrders(document_id)/salesOrderLines
    * response is list of dictionaries of records.
    * if response is blank then maybe filter has no records but check *object.except_error* value
        * it could be connection error message (for example: wrong url, time out etc.)
        * it could be tuple of errors (for example: error from API execution) 
3. Insert (create) new record in database by execute *object.insert(json)*
    * json must to include all fields required for primary key creation. However if API page creates record 
    by using for example Number Series (Sales orders header) or autoincrement field then primary key fields values
    are not required for these fields.
    * URL can be modified before call by execute *object.url = new_url*. In some cases url must be specific for this operation. 
    For example: if need to create Sales Order Line when sales order already created then url must to include document_id like
    http://navbs:7048/BC/api/beta/salesOrders(document_id)/salesOrderLines   
    * response is API response to action. If record created then response is tuple (201, Created). 
    if response is blank then check *object.except_error* value
4. Modify (update) new record in database by execute *object.modify(json)*
    * json must to include all fields need to be modified.
    * URL can be modified before call by execute *object.url = new_url*. In some cases url must be specific for this operation. 
    For example: if need to modify sales order line (subpage of sales order header) then url must to include document_id and line number like
    http://navbs:7048/BC/api/beta/salesOrderLines({so_id},{line_no})"   
    * response is API response to action. If record created then response is tuple (200, OK). 
    if response is blank then check *object.except_error* value
5. Delete record need to execute *object.delete()*
    * url must to include document_id for "normal record" like customer, item etc. like http://navbs:7048/BC/api/beta/salesOrders(document_id)
     if record has relation to upper table like sales line then url must to include document_id and line_no like:
     http://navbs:7048/BC/api/beta/salesOrderLines(document_id,line_no)
    * response is API response to action. If record deleted then response is tuple (204, No Content). 
    if response is blank then check *object.except_error* value           

API structure can be analysed by execute $metadata url like http://navbs:7048/BC/api/beta/$metadata


This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.