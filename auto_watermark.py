import os
import time
import shutil
import subprocess
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
import threading

ffmpeg_path = 'C:\\Program Files\\ffmpeg-master-latest-win64-gpl\\bin'
os.environ['PATH'] += os.pathsep + ffmpeg_path

image_extensions = ['.jpg', '.jpeg', '.png']
video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
root = Tk()
root.title('Auto Watermark PP')

# Configuração da grade
for i in range(8):
    root.grid_rowconfigure(i, weight=1)
for j in range(3):
    root.grid_columnconfigure(j, weight=1)

# Variáveis globais
global image_path, render_path, video_queue
image_path = ''
render_path = ''
video_queue = []  # Lista para armazenar os vídeos a serem renderizados

# Interface do usuário
label_file_explorer = Label(root, text="Projeto Auto Watermark - v1 Desktop", width=50, height=2, fg="blue")

def browse_image_file():
    global image_path
    data = filedialog.askopenfilename(
        initialdir=os.path.expanduser('~'),
        title="Selecione o arquivo de imagem",
        filetypes=(("Arquivos de imagem", image_extensions),)
    )
    image_path = os.path.abspath(data)

def destination_folder():
    global render_path
    data = filedialog.askdirectory()
    render_path = os.path.abspath(data)

def add_video_to_queue():
    global video_queue
    if len(video_queue) < 10:
        data = filedialog.askopenfilename(
            initialdir=os.path.expanduser('~'),
            title="Selecione o arquivo de vídeo",
            filetypes=(("Arquivos de vídeo", video_extensions),)
        )
        if data:
            video_queue.append(os.path.abspath(data))
            update_video_listbox()
    else:
        messagebox.showwarning("Limite de vídeos", "Você pode adicionar até 10 vídeos.")

def update_video_listbox():
    video_listbox.delete(0, END)
    for video in video_queue:
        video_listbox.insert(END, video)

def check_ffmpeg():
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        print("FFmpeg encontrado em:", ffmpeg_path)
        return ffmpeg_path
    else:
        print("FFmpeg não encontrado. Certifique-se de que o FFmpeg está instalado e no PATH.")
        exit(1)

def render_videos_thread():
    global image_path, render_path
    ffmpeg_path = check_ffmpeg()

    for video_path in video_queue:
        video_name = os.path.basename(video_path)
        output_video_name = f"{os.path.splitext(video_name)[0]}_watermarked.mp4"
        resolution = resolution_var.get()
        width, height = map(int, resolution.split('x'))
        render_path_full = os.path.join(render_path, output_video_name)

        command = [
            ffmpeg_path,
            '-hwaccel', 'cuda',
            '-i', video_path,
            '-i', image_path,
            '-filter_complex', f'[0:v]scale={width}:{height}[scaled];[scaled][1:v]overlay=W-w-10:H-h-10',
            '-c:v', 'h264_nvenc', 
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast',
            render_path_full
        ]

        try:
            print(f"Aplicando marca d'água em {video_name}...")
            progress.start()
            subprocess.run(command, check=True)
            print(f"Marca d'água aplicada com sucesso em {video_name}!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao aplicar a marca d'água em {video_name}: {e}")
        except FileNotFoundError as e:
            print(f"Arquivo não encontrado: {e}")
        finally:
            progress.stop()

def render_videos():
    if not video_queue:
        messagebox.showwarning("Fila vazia", "Adicione vídeos à fila antes de renderizar.")
        return
    thread = threading.Thread(target=render_videos_thread)
    thread.start()

# Criação de botões e widgets
button_image_explore = Button(root, text="Buscar marca d'água", command=browse_image_file) 
button_destination_folder = Button(root, text="Destino da renderização", command=destination_folder) 
render_title_label = Label(root, text='Título da renderização:')
render_title = Text(root, height=1, width=10)

resolution_var = StringVar()
resolution_var.set('1280x720') 

radio_button_1 = Radiobutton(root, text='1280x720 (HD)', value='1280x720', variable=resolution_var)
radio_button_2 = Radiobutton(root, text='1920x1080 (Full HD)', value='1920x1080', variable=resolution_var)
radio_button_3 = Radiobutton(root, text='3840x2160 (4K)', value='3840x2160', variable=resolution_var)

progress = Progressbar(root, orient=HORIZONTAL, length=300, mode='indeterminate')

# Layout da interface
label_file_explorer.grid(column=0, row=0, columnspan=3, pady=10)
button_image_explore.grid(column=0, row=1, padx=5, pady=5, sticky="ew")
button_destination_folder.grid(column=1, row=1, padx=5, pady=5, sticky="ew")

render_title_label.grid(column=0, row=2, padx=5, pady=5, sticky="e")
render_title.grid(column=1, row=2, padx=5, pady=5, columnspan=2, sticky="ew")

radio_button_1.grid(column=0, row=3, padx=5, pady=5, sticky="w")
radio_button_2.grid(column=1, row=3, padx=5, pady=5, sticky="w")
radio_button_3.grid(column=2, row=3, padx=5, pady=5, sticky="w")

button_add_video = Button(root, text="Adicionar Vídeo à Fila", command=add_video_to_queue)
button_add_video.grid(column=0, row=4, padx=5, pady=5, sticky="ew")

video_listbox = Listbox(root, width=50, height=10)
video_listbox.grid(column=0, row=5, columnspan=3, padx=10, pady=10)

button_render_videos = Button(root, text="Renderizar Vídeos", command=render_videos)
button_render_videos.grid(column=0, row=6, columnspan=3, padx=5, pady=10, sticky="ew")

button_exit = Button(root, text="Sair", command=exit) 
button_exit.grid(column=0, row=7, columnspan=3, padx=5, pady=5, sticky="ew")

progress.grid(column=0, row=8, columnspan=3, padx=10, pady=10)

root.mainloop()