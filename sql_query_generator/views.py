from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from sql_query_generator.utils import get_few_shot_db_chain

import json
from django.http import JsonResponse
from django.db import connection

def list_tables(request):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        AND name NOT LIKE 'django_%'
        AND name NOT LIKE 'auth_%'
        AND name NOT LIKE 'admin_%'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'tables': tables})

def sample_data(request, table_name):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return JsonResponse({'columns': columns, 'rows': rows})


@csrf_exempt
def query_database(request):
    if request.method == 'POST':
        try:
            chain = get_few_shot_db_chain()
            data = json.loads(request.body)
            question = data.get('question', '')
            print(f"Question received: {question}")
            if not question:
                return JsonResponse({'error': 'Question is required'}, status=400)

            try: 
                result = chain.invoke(question)
            except Exception as e:
                print(f"Error is: {e}")
            print(f"Result: {result}")

            if 'error' in result:
                raise Exception(result['error'])

            return JsonResponse({'answer': result})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

