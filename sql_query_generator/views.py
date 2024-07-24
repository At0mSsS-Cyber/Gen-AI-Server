from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from sql_query_generator.utils import get_few_shot_db_chain

import json

@csrf_exempt
def query_database(request):
    if request.method == 'POST':
        try:
            chain = get_few_shot_db_chain()
            data = json.loads(request.body)
            question = data.get('question', '')
            print(question)
            result = chain.invoke(question)
            return JsonResponse({'answer': result})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

