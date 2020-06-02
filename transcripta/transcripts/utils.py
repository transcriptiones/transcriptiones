
# Function to create related objects, if they are in formdata
# return updated formdata object for further processing
# listname: str, Name of the field in the form
# formdata: dict, Data object from the form
# relatedclass: class, Class to create the new objects in
# namefield: object, field of relatedclass to use as the name of the new object

def create_related_objects(listname, formdata, relatedclass, namefield):
    if listname in formdata:
        objs = list()
        newobjs = list()
        for obj in formdata.getlist(listname):
            try: 
                objs.append(int(obj))
            except ValueError:
                newobjs.append(obj)
        
        #create new author object for each element of the list.
        #append their pks to the list of authors from the form data
        for obj in newobjs:
            newobj = relatedclass(
                **{namefield: obj}
                )
            newobj.save()
            objs.append(newobj.pk)
        
        return formdata.setlist(listname, objs)