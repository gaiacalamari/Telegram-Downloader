import os
import html
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel, PeerChat, PeerUser

# Inserisci qui i tuoi dati API
api_id = 'INSERIRE ID API'
api_hash = 'HASH API'

# Numero di telefono della persona investigata
phone_number = '+39....'

# Creiamo una cartella principale per salvare tutto
output_dir = 'telegram_backup'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Funzione per formattare i messaggi in HTML
def save_messages_as_html(dialog_title, messages):
    dialog_dir = os.path.join(output_dir, dialog_title)
    if not os.path.exists(dialog_dir):
        os.makedirs(dialog_dir)
    
    html_file = os.path.join(dialog_dir, 'messages.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write('<html><body>')
        for message in reversed(messages):  # Invertiamo l'ordine dei messaggi
            if message.message:
                sender = message.sender_id if message.sender_id else "Unknown"
                timestamp = message.date.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f'<p><strong>{sender} [{timestamp}]:</strong> {html.escape(message.message)}</p>')
        f.write('</body></html>')

# Funzione per scaricare gli allegati
def download_attachments(dialog_title, messages):
    dialog_dir = os.path.join(output_dir, dialog_title)
    for message in messages:
        if message.media:
            file_path = client.download_media(message.media, dialog_dir)
            print(f'Downloaded file to {file_path}')

# Collegati al client Telegram
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    try:
        await client.start(phone=phone_number)
    except errors.SessionPasswordNeededError:
        password = input('Enter the 2-step verification password: ')
        await client.sign_in(password=password)
    
    # Recupera tutte le chat
    dialogs = await client.get_dialogs()

    for dialog in dialogs:
        dialog_title = dialog.name if dialog.name else "Unknown"
        print(f'Starting backup for chat: {dialog_title}')
        
        # Recupera la cronologia della chat
        messages = []
        offset_id = 0
        limit = 100
        while True:
            history = await client(GetHistoryRequest(
                peer=dialog.entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
            messages.extend(history.messages)
            offset_id = history.messages[-1].id

        # Salva i messaggi come HTML
        save_messages_as_html(dialog_title, messages)

        # Scarica gli allegati
        download_attachments(dialog_title, messages)

    await client.disconnect()
    print("Backup completato!")

with client:
    client.loop.run_until_complete(main())
