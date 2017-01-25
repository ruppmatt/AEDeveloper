import json
# Combine a base dictionary, d, with an additional dictionary j
# This function handles the case when information from outside of
# a HTTP request needs to get merged with another dictionary
def combine_data(d, j):
    for k,v in j.items():
        d[k]=v
    return d


# The MySQL connector needs the data in a particular format in order to insert
# it into the database.  It is a two part process: first create a template
# string that will be passed as the first parameter of cursor.execute.
# The string contains placeholders for the actual data.  In our case, these
# place holders are named in a Python-2 format-like manner.
# The dictionary's values to substitute the place-holding parameters is passed
# to the cursor.execute method as the second argument, where substitions
# are actually made.  (This method generates just the template string.)
# For example
# INSERT INTO mydb (field1, field2) VALUES (%(field1)s, %(field2)s)
# where field1 and field2 are keys to the dictionary provided by data
# The values will get inserted later by cursor.execute(template_string, dict)
def generate_insertion(table, data):
    #We need to play around to get the MySQL statement correct
    #when we're dealing with a dictionary worth of data
    ncol = len(data)
    cols = ', '.join(data.keys())  #List of our columns in order
    val_placeholder = ', '.join(map(lambda x: '%('+x+')s ', data.keys())) #Create our placeholders]
    insert_cmd =\
        "INSERT INTO {table} ({columns}) VALUES ({values})".format(
        columns=cols, values=val_placeholder, table=table)
    #print(Fore.MAGENTA + insert_cmd + Style.RESET_ALL)
    return insert_cmd


# A helper function to get particular fields in a table
# This will not properly sanitize, so use internally only!
def generate_get(table, fields, suffix=''):
    f = ', '.join(fields)
    cmd = 'SELECT {fields} FROM {table} {suffix}'.format(fields=f, table=table, suffix=suffix)
    #print(Fore.MAGENTA + cmd + Style.RESET_ALL)
    return cmd


# A helper function to make the return line for responses a little easier
# to look at
def generate_response(json_dict, code, header_dict={'ContentType':'application/json'}):
    response = json.dumps(json_dict), code, header_dict
    #print(Fore.CYAN + ', '.join(map(lambda x: str(x), response)) + Style.RESET_ALL)
    return response
