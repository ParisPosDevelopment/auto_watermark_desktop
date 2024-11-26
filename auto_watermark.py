import os
import re
import shutil
import subprocess
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Combobox
import threading
import json

ffmpeg_path = 'C:\\Program Files\\ffmpeg-master-latest-win64-gpl\\bin'
os.environ['PATH'] += os.pathsep + ffmpeg_path

image_extensions = ['.jpg', '.jpeg', '.png']
video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.mxf']
root = Tk()
root.title('Auto Watermark PP')

# Configuração da grade
for i in range(8):
    root.grid_rowconfigure(i, weight=1)
for j in range(3):
    root.grid_columnconfigure(j, weight=1)

# Variáveis globais
global image_path, render_path, video_queue, process
process = None
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
        filetypes=[("Arquivos de imagem", image_extensions)])
    image_path = os.path.abspath(data)
    save_paths()
    update_selected_paths()

def browse_video_file():
    global video_path
    data = filedialog.askopenfilename(
        initialdir=os.path.expanduser('~'),
        title="Selecione o arquivo de vídeo",
        filetypes=[("Arquivos de vídeo", video_extensions)])
    video_path = os.path.abspath(data)
    save_paths()
    update_selected_paths()

def destination_folder():
    global render_path
    data = filedialog.askdirectory()
    render_path = os.path.abspath(data)
    save_paths()
    update_selected_paths()

def save_paths():
    global image_path, video_path, render_path
    paths = {
        'image_path': image_path,
        'video_path': video_path,
        'render_path': render_path
    }
    with open('saved_paths.json', 'w') as f:
        json.dump(paths, f)

def load_paths():
    global image_path, video_path, render_path
    if os.path.exists('saved_paths.json'):
        with open('saved_paths.json', 'r') as f:
            paths = json.load(f)
            image_path = paths.get('image_path', '')
            video_path = paths.get('video_path', '')
            render_path = paths.get('render_path', '')
    else:
        image_path = ''
        video_path = ''
        render_path = ''        

def update_selected_paths():
    global image_path, video_path, render_path
    selected_paths = f"Imagem: {image_path} \nVídeo: {video_path}\nDestino: {render_path}"
    selected_paths_label.config(text=selected_paths)

selected_paths_label = Label(root, text="Paths Selecionados:")

render_title_label = Label(root, text='Título da renderização:')
render_title = Text(root, height=1, width=10)

resolution_var = StringVar()
resolution_var.set('1920x1080')
framerate_var = StringVar()
framerate_var.set('23.976')
formato_var = StringVar()
formato_var.set('.mov')
codec_var = StringVar()
codec_var.set('proxy')
bitrate_var = StringVar()
bitrate_combo = Combobox(root, textvariable=bitrate_var, values=['6000k', '9000k', '12000k', '15000k'], width=10)
bitrate_combo.current(0)

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

        subprocess.run(command, check=True)

def render_videos():
    if not video_queue:
        messagebox.showwarning("Fila vazia", "Adicione vídeos à fila antes de renderizar.")
        return
    thread = threading.Thread(target=render_videos_thread)
    thread.start()

def update_bitrate_combo(*args):
    if codec_var.get() == 'h264':
        bitrate_combo.grid(column=3, row=6, padx=5, pady=5, sticky="w")
    else:
        bitrate_combo.grid_remove()

codec_var.trace('w', update_bitrate_combo)

bitrate_combo.current(0)

def get_video_frame_count(video_path):
    command = [
        'ffmpeg',
        '-i', video_path,
        '-map', '0:v:0',  # Pega apenas a primeira faixa de vídeo
        '-c', 'copy',
        '-f', 'null',  # Usa 'null' para não gerar saída
        '/dev/null'  # Este caminho não é usado
    ]
    
    process = subprocess.Popen(command, stderr=subprocess.PIPE, universal_newlines=True)
    for line in process.stderr:
        if 'frame=' in line:
            frame_info = re.search(r"frame=\s*(\d+)", line)
            if frame_info:
                return int(frame_info.group(1))
    return 0

def apply_watermark_thread():
    global image_path, video_path, render_path, ffmpeg_path, process
    codec = codec_var.get()
    formato = formato_var.get()
    video_name = str(render_title.get('1.0', 'end')).strip() + formato
    resolution = resolution_var.get()
    framerate = framerate_var.get()
    width, height = map(int, resolution.split('x'))
    render_path = os.path.join(render_path, video_name)
    ffmpeg_path = check_ffmpeg()
    bitrate = bitrate_var.get() if codec == 'h264' else '12000'

    total_frames = get_video_frame_count(video_path)
    if total_frames == 0:
        messagebox.showerror("Erro", "Não foi possível determinar o número total de frames.")
        return

    command = [
        ffmpeg_path,
        '-hwaccel', 'cuda',
        '-i', video_path,
        '-i', image_path,
        '-filter_complex', f'[0:v]scale={width}:{height}[scaled];[scaled][1:v]overlay=W-w-10:H-h-10',
        '-r', framerate,
    ]
    
    if codec == 'h264':
        command.extend([
            '-c:v', 'h264_nvenc',
            '-pix_fmt', 'yuv420p',
            '-preset', 'fast',
            '-b:v', bitrate,
        ])
    elif codec == 'proxy':
        command.extend([
            '-c:v', 'prores_ks',
            '-profile:v', '0',
            '-pix_fmt', 'yuva444p10le',
        ])
    else:
        print(f"Codec não suportado: {codec}")
        return

    command.append(render_path)

    try:
        print("Aplicando marca d'água...")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        for line in process.stderr:
            if "frame=" in line:
                frame_info = re.search(r"frame=\s*(\d+)", line)
                if frame_info:
                    frame_count = int(frame_info.group(1))
                    progress['value'] = frame_count
                    percentage = (frame_count / total_frames) * 100
                    percentage_label.config(text=f"{percentage:.2f}%")
                    root.update_idletasks()

        process.wait()  # Aguarda o processo finalizar
        progress.stop()
        print("Marca d'água aplicada com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao aplicar a marca d'água: {e}")
    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")

def apply_watermark():
    thread = threading.Thread(target=apply_watermark_thread)
    thread.start()

# Layout
button_image_explore = Button(root, text="Buscar marca d'água", command=browse_image_file)
button_video_explore = Button(root, text="Buscar vídeo", command=browse_video_file)
button_destination_folder = Button(root, text="Destino da renderização", command=destination_folder)

button_video_explore.grid(column=0, row=2, padx=5, pady=5, sticky="ew")
button_add_video = Button(root, text="Adicionar Vídeo à Fila", command=add_video_to_queue)
button_add_video.grid(column=0, row=3, padx=5, pady=5, sticky="ew")

resolution_combo = Combobox(root, textvariable=resolution_var, values=['1920x1080', '1280x720', '3840x2160'])
resolution_combo.grid(column=0, row=4, padx=5, pady=5, sticky="w")
resolution_combo.current(0)

framerate_combo = Combobox(root, textvariable=framerate_var, values=['23.976', '24', '30'])
framerate_combo.grid(column=1, row=4, padx=5, pady=5, sticky="w")
framerate_combo.current(0)

format_combo = Combobox(root, textvariable=formato_var, values=['.mov', '.mp4'])
format_combo.grid(column=0, row=5, padx=5, pady=5, sticky="w")
format_combo.current(0)

codec_combo = Combobox(root, textvariable=codec_var, values=['proxy', 'h264'])
codec_combo.grid(column=1, row=5, padx=5, pady=5, sticky="w")
codec_combo.current(0)

label_file_explorer.grid(column=0, row=0, columnspan=3, pady=10)
button_image_explore.grid(column=0, row=1, padx=5, pady=5, sticky="ew")
button_destination_folder.grid(column=1, row=1, padx=5, pady=5, sticky="ew")

render_title_label.grid(column=0, row=6, padx=5, pady=5, sticky="e")
render_title.grid(column=1, row=6, padx=5, pady=5, columnspan=2, sticky="ew")

selected_paths_label.grid(column=0, row=7, columnspan=3, pady=10)

video_listbox = Listbox(root, width=50, height=10)
video_listbox.grid(column=0, row=8, columnspan=3, padx=10, pady=10)

button_render_videos = Button(root, text="Renderizar Vídeos", command=render_videos)
button_render_videos.grid(column=0, row=9, columnspan=3, padx=5, pady=10, sticky="ew")

button_apply_watermark = Button(root, text="Aplicar", command=apply_watermark)
button_apply_watermark.grid(column=0, row=10, columnspan=3, padx=5, pady=10, sticky="ew")

button_exit = Button(root, text="Sair", command=root.quit)
button_exit.grid(column=0, row=11, columnspan=3, padx=5, pady=5, sticky="ew")

# Barra de progresso
progress = Progressbar(root, orient=HORIZONTAL, length=300, mode='indeterminate')
progress.grid(column=0, row=12, columnspan=2, padx=7, pady=5)

percentage_label = Label(root, text="0%")
percentage_label.grid(column=2, row=12, padx=5, pady=5)

# Carregar os caminhos salvos
load_paths()
update_selected_paths()

root.mainloop()