import pypandoc
from django.utils.text import slugify


def create_related_objects(listname, formdata, relatedclass, namefield):
    """Function to create related objects, if they are in form data
    return updated formdata object for further processing

    listname: str, Name of the field in the form
    formdata: dict, Data object from the form
    relatedclass: class, Class to create the new objects in
    namefield: object, field of relatedclass to use as the name of the new object
    """
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


# function to convert .docx-documents to html-strings
# makes use of pypandoc, which in turn requires pandoc
def convert_docx_html(dirpath, docname):
    if not dirpath.endswith('/'):
        dirpath = dirpath + '/'

    docpath = dirpath + docname

    # Wrap this in if-statement or try-except-block to check for file-ending
    dochtml = pypandoc.convert_file()
    return dochtml


def transcriptiones_slugify(string, model_class, slug_field):
    if len(string) > 50:
        string = string[:49]
    new_slug = slugify(string)

    inc_value = 1
    while model_class.objects.filter(**{slug_field: new_slug}).count() != 0:
        new_slug = new_slug[:40] + f"-{inc_value}"
        inc_value += 1
        if inc_value >= 10:
            return None

    return new_slug
