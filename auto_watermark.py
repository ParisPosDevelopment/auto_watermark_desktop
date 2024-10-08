import os
import time
import shutil
import re
import subprocess
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar, Combobox
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from tqdm import tqdm
import threading

ffmpeg_path = 'C:\\Program Files\\ffmpeg-master-latest-win64-gpl\\bin'
os.environ['PATH'] += os.pathsep + ffmpeg_path

image_extensions = ['.jpg', '.jpeg', '.png']
video_extensions = ['.mp4','.avi', '.mkv', '.mov', '.mxf']
root = Tk()
root.title('Auto Watermark PP')

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)
root.grid_rowconfigure(6, weight=1)
root.grid_rowconfigure(7, weight=1)
root.grid_rowconfigure(8, weight=1)
root.grid_rowconfigure(9, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

global image_path, video_path, render_path

label_file_explorer = Label(root, 
							text = "Projeto Auto Warermark - v1 Desktop",
							width = 50, height = 2, 
							fg = "blue")

def browse_image_file():
	global image_path
	data = filedialog.askopenfilename(
										initialdir = os.path.expanduser('~'),
										title = "Selecione o arquivo de imagem",
										filetypes = (
											("Arquivos de imagem", image_extensions),
										))
	image_path =  os.path.abspath(data)

def browse_video_file():
	global video_path
	data = filedialog.askopenfilename(
										initialdir = os.path.expanduser('~'),
										title = "Selecione o arquivo de video",
										filetypes = (
											("Arquivos de vídeo", video_extensions),
										))
	video_path =  os.path.abspath(data)
 
def destination_folder():
	global render_path
	data = filedialog.askdirectory()
	render_path =  os.path.abspath(data)

button_image_explore = Button(root, 
						text = "Buscar marca d'água",
						command = browse_image_file) 

button_video_explore = Button(root, 
						text = "Buscar vídeo",
						command = browse_video_file) 

button_destination_folder = Button(root, 
						text = "Destino da renderização",
						command = destination_folder) 

render_title_label = Label(root, text='Título da renderização:')
render_title = Text(root, height=1, width=10)

resolution_var = StringVar()
resolution_var.set('1280x720') 
framerate_var = StringVar()
framerate_var.set('23.976')
formato_var = StringVar()
formato_var.set('.mov')
codec_var = StringVar()
codec_var.set('proxy')
bitrate_var = StringVar()
bitrate_var.set('16000')

resolution_combo = Combobox(root, textvariable=resolution_var, values=['1280x720', '1920x1080', '3840x2160'])
resolution_combo.grid(column=0, row=3, padx=5, pady=5, sticky="w")
resolution_combo.current(0)

framerate_combo = Combobox(root, textvariable=framerate_var, values=['23.976', '24', '30'])
framerate_combo.grid(column=0, row=4, padx=5, pady=5, sticky="w")
framerate_combo.current(0)

formato_combo = Combobox(root, textvariable=formato_var, values=['.mov', '.mp4'])
formato_combo.grid(column=0, row=5, padx=5, pady=5, sticky="w")
formato_combo.current(0)

codec_combo = Combobox(root, textvariable=codec_var, values=['proxy', 'h264'])
codec_combo.grid(column=0, row=6, padx=5, pady=5, sticky="w")
codec_combo.current(0)

progress = Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate')

def check_ffmpeg():
	ffmpeg_path = shutil.which('ffmpeg')
	if ffmpeg_path:
		print("FFmpeg encontrado em:", ffmpeg_path)
		return ffmpeg_path
	else:
		print("FFmpeg não encontrado. Certifique-se de que o FFmpeg está instalado e no PATH.")
		exit(1)

bitrate_entry = Entry(root, textvariable=bitrate_var, width=10)

def update_bitrate_entry(*args):
    if codec_var.get() == 'h264':
        bitrate_entry.grid(column=2, row=6, padx=5, pady=5, sticky="w")
    else:
        bitrate_entry.grid_remove()

# Conecte a função ao evento de mudança do combobox de formato
codec_var.trace('w', update_bitrate_entry)

def apply_watermark_thread():
    global image_path, video_path, render_path, ffmpeg_path
    codec = codec_var.get()
    formato = formato_var.get()
    video_name = str(render_title.get('1.0', 'end')).strip() + formato
    resolution = resolution_var.get()
    framerate = framerate_var.get()
    width, height = map(int, resolution.split('x'))
    render_path = os.path.join(render_path, video_name)
    ffmpeg_path = check_ffmpeg()
    bitrate = bitrate_var.get() if codec == 'h264' else '14000'

    # Initialize command base
    command = [
        ffmpeg_path,
        '-hwaccel', 'cuda',
        '-i', video_path,
        '-i', image_path,
        '-filter_complex', f'[0:v]scale={width}:{height}[scaled];[scaled][1:v]overlay=W-w-10:H-h-10',
        '-r', framerate,
    ]
    
    # Add codec-specific options
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

    # Add render path
    command.append(render_path)

    try:
        print("Aplicando marca d'água...")
        progress.start()
        # Open subprocess and capture output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Read and monitor output
        for line in process.stderr:
            if "frame=" in line:
                # Extract frame count from output
                frame_info = re.search(r"frame=\s*(\d+)", line)
                if frame_info:
                    frame_count = int(frame_info.group(1))
                    # Update progress (example: assuming 1000 frames)
                    progress['value'] = (frame_count / frame_count) * 100
                    root.update_idletasks()
        
        process.wait()  # Wait for the process to complete
        print("Marca d'água aplicada com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao aplicar a marca d'água: {e}")
    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")
    finally:
        progress.stop()
        
def apply_watermark():
	thread = threading.Thread(target=apply_watermark_thread)
	thread.start()	
 
button_apply_watermark = Button(root, 
						text = "Aplicar",
						command = apply_watermark) 

progress.grid(column=0, row=6, columnspan=3, padx=10, pady=10)

button_exit = Button(root, 
					text = "Sair",
					command = exit) 

label_file_explorer.grid(column=0, row=0, columnspan=3, pady=10)

button_image_explore.grid(column=0, row=1, padx=5, pady=5, sticky="ew")
button_video_explore.grid(column=1, row=1, padx=5, pady=5, sticky="ew")
button_destination_folder.grid(column=2, row=1, padx=5, pady=5, sticky="ew")

render_title_label.grid(column=0, row=2, padx=5, pady=5, sticky="e")
render_title.grid(column=1, row=2, padx=5, pady=5, columnspan=2, sticky="ew")

button_apply_watermark.grid(column=0, row=7, columnspan=3, padx=5, pady=10, sticky="ew")

button_exit.grid(column=0, row=9, columnspan=3, padx=5, pady=5, sticky="ew")

progress.grid(column=0, row=8, columnspan=3, padx=10, pady=10)

root.mainloop()