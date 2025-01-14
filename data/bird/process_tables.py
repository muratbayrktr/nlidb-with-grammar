import json

with open("./dev_tables.json", "r") as input_file:
    input_json = json.load(input_file)

def transform_data(data):
    result = {}
    for entry in data:
        db_id = entry["db_id"]
        table_names = entry["table_names_original"]
        column_names = entry["column_names_original"]

        result[db_id] = {}

        for table_index, table_name in enumerate(table_names):
            result[db_id][table_name] = []

        for column in column_names:
            table_index, column_name = column
            if table_index != -1:  
                table_name = table_names[table_index] 
                result[db_id][table_name].append(column_name)

    return result

transformed_data = transform_data(input_json)

with open("processed_tables.json", "w") as output_file:
    json.dump(transformed_data, output_file, indent=4)

print("Processed JSON saved to processed_tables.json")
