few_shots = [
    {'Question': "what are the column names of item table?",
     'SQLQuery' : "PRAGMA table_info(item);",
     'SQLResult': "Result of the SQL query",
     'Answer' : "Name and Description"
    },
    {'Question': "what is the description of Orange?",
     'SQLQuery' : "SELECT Description FROM item WHERE name='Orange'",
     'SQLResult': "Result of the SQL query",
     'Answer' : "An orange, also called sweet orange when it is desired to distinguish it from the bitter orange (Citrus × aurantium), is the fruit of a tree in the family Rutaceae. Botanically, this is the hybrid Citrus × sinensis, between the pomelo (Citrus maxima) and the mandarin orange (Citrus reticulata)."
    }
]
