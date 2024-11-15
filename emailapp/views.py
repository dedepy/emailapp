from django.shortcuts import render
from django.http import JsonResponse
from .services import EmailImporter
import psycopg2
import threading
import pandas as pd
from django.shortcuts import redirect

conn = psycopg2.connect(database="",
                        user="",
                        password="",
                        host="",
                        port="")
cursor = conn.cursor()
def import_emails(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        provider = request.POST.get("provider")

        importer = EmailImporter(provider, username, password)
        importer.connect()
        importer.fetch_messages()
        importer.mail.logout()
    return render(request, "import_form.html")



import_progress = 0


def start_import(request):
    if request.method == "POST":
        global import_progress
        import_progress = 0

        username = request.POST.get("username")
        password = request.POST.get("password")
        provider = request.POST.get("provider")

        # Запускаем импорт в отдельном потоке
        def import_task():
            global import_progress
            importer = EmailImporter(provider, username, password)
            importer.connect()

            # Получаем все сообщения с прогрессом
            messages = importer.mail.select("inbox")[1][0].split()
            total = len(messages)
            for i, msg_id in enumerate(messages):
                importer.fetch_messages(msg_id)
                import_progress = (i + 1) * 100 // total  # Обновляем прогресс
            importer.mail.logout()

        threading.Thread(target=import_task).start()
        cursor.execute('SELECT * FROM emailapp_email;')
        rows = cursor.fetchall()

        table_data = []
        for row in rows:
            table_data.append({
                'id': row[0],
                'subject': row[1],
                'sender': row[2],
                'received_date': row[3],
                'sent_date': row[4],
                'body': row[5],
                'attachments': row[6]
            })

        context = {
            'table_data': table_data  # Передаем данные таблицы в шаблон
        }
        render(request, 'df.html', context)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request method"})


def get_import_progress(request):
    global import_progress
    return JsonResponse({"progress": import_progress})

