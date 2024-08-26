import os
import subprocess
from tkinter import *
from tkinter import filedialog
import shutil
ffmpeg_path = 'C:\\Program Files\\ffmpeg-master-latest-win64-gpl\\bin'
os.environ['PATH'] += os.pathsep + ffmpeg_path

# Extensões suportadas para vídeo e imagem
image_extensions = ['.jpg', '.jpeg', '.png']
video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
window = Tk()
window.title('Auto Watermark PP')
window.geometry("400x200")
window.config(background="white")

global image_path, video_path, render_path

# Label de descrição
label_file_explorer = Label(window,
                            text="Projeto Auto Watermark - v1 Desktop",
                            width=50, height=2,
                            fg="blue")

def browse_image_file():
    global image_path
    data = filedialog.askopenfilename(
        initialdir=os.path.expanduser('~'),
        title="Selecione o arquivo de imagem",
        filetypes=(
            ("Arquivos de imagem", image_extensions),
        ))
    image_path = os.path.abspath(data)

def browse_video_file():
    global video_path
    data = filedialog.askopenfilename(
        initialdir=os.path.expanduser('~'),
        title="Selecione o arquivo de vídeo",
        filetypes=(
            ("Arquivos de vídeo", video_extensions),
        ))
    video_path = os.path.abspath(data)

def destination_folder():
    global render_path
    data = filedialog.askdirectory()
    render_path = os.path.abspath(data)

# Botões de seleção de arquivos e pasta
button_image_explore = Button(window,
                              text="Buscar marca d'água",
                              command=browse_image_file)

button_video_explore = Button(window,
                              text="Buscar vídeo",
                              command=browse_video_file)

button_destination_folder = Button(window,
                                    text="Pasta de destino da renderização",
                                    command=destination_folder)

def check_ffmpeg():
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    else:
        print("FFmpeg não encontrado. Certifique-se de que o FFmpeg está instalado e no PATH.")
        exit(1)

def apply_watermark():
    global image_path, video_path, render_path

    if not all([image_path, video_path, render_path]):
        print("Todos os campos devem ser preenchidos!")
        return

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    render_file = os.path.join(render_path, f"{video_name}_rendered.mp4")

    ffmpeg_path = check_ffmpeg()

    # Comando ffmpeg para adicionar a marca d'água com aceleração por GPU
    command = [
        ffmpeg_path,
        '-hwaccel', 'cuda',
        '-i', video_path,
        '-i', image_path,
        '-filter_complex', '[0:v][1:v]overlay=W-w-10:H-h-10',
        '-c:v', 'h264_nvenc',  # Codec NVENC para aceleração por GPU
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        render_file
    ]

    try:
        print("Aplicando marca d'água...")
        subprocess.run(command, check=True)
        print("Marca d'água aplicada com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao aplicar a marca d'água: {e}")
    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")

# Botão para aplicar a marca d'água e sair
button_apply_watermark = Button(window,
                                text="Aplicar marca d'água",
                                command=apply_watermark)

button_exit = Button(window,
                     text="Sair",
                     command=window.quit)

# Adiciona widgets ao layout
label_file_explorer.grid(column=1, row=1)
button_image_explore.grid(column=1, row=2)
button_video_explore.grid(column=1, row=3)
button_destination_folder.grid(column=1, row=4)
button_apply_watermark.grid(column=1, row=5)
button_exit.grid(column=1, row=6)

window.mainloop()