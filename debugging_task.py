def print_values_of(dictionary, keys):
    
    for key in keys:
        print(dictionary[key])  

simpson_catch_phrases = {"lisa": "BAAAAAART!",
                         "bart": "Eat My Shorts!",
                         "marge": "Mmm~mmmmm",
                         "homer": "d'oh!",  # Corrected quotation mark
                         "maggie": "(Pacifier Suck)"
                         }

print_values_of(simpson_catch_phrases, ['lisa', 'bart', 'homer']) 