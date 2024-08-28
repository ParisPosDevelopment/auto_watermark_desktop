import os
import time
import shutil
import re
import subprocess
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from tqdm import tqdm
import threading

ffmpeg_path = 'C:\\Program Files\\ffmpeg-master-latest-win64-gpl\\bin'
os.environ['PATH'] += os.pathsep + ffmpeg_path

image_extensions = ['.jpg', '.jpeg', '.png']
video_extensions = ['.mp4','.avi', '.mkv', '.mov']
root = Tk()
root.title('Auto Watermark PP')

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)
root.grid_rowconfigure(6, weight=1)
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

radio_button_1 = Radiobutton(root, text='1280x720 (HD)', value='1280x720', variable=resolution_var)
radio_button_2 = Radiobutton(root, text='1920x1080 (Full HD)', value='1920x1080', variable=resolution_var)
radio_button_3 = Radiobutton(root, text='3840x2160 (4K)', value='3840x2160', variable=resolution_var)

progress = Progressbar(root, orient=HORIZONTAL, length=300, mode='indeterminate')

def check_ffmpeg():
	ffmpeg_path = shutil.which('ffmpeg')
	if ffmpeg_path:
		print("FFmpeg encontrado em:", ffmpeg_path)
		return ffmpeg_path
	else:
		print("FFmpeg não encontrado. Certifique-se de que o FFmpeg está instalado e no PATH.")
		exit(1)

def apply_watermark_thread():
	global image_path, video_path, render_path, ffmpeg_path
	video_name = str(render_title.get('1.0','end')).strip() + ".mp4"
	resolution = resolution_var.get()
	width, height = map(int, resolution.split('x'))
	render_path = os.path.join(render_path, video_name)
	ffmpeg_path = check_ffmpeg()
	command = [
				ffmpeg_path,
				'-hwaccel', 'cuda',
				'-i', video_path,
				'-i', image_path,
				'-filter_complex', f'[0:v]scale={width}:{height}[scaled];[scaled][1:v]overlay=W-w-10:H-h-10',
				'-c:v', 'h264_nvenc', 
				'-pix_fmt', 'yuv420p',
				'-preset', 'fast',
				render_path
		]

	try:
		print("Aplicando marca d'água...")
		progress.start()
		subprocess.run(command, check=True)
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

radio_button_1.grid(column=0, row=3, padx=5, pady=5, sticky="w")
radio_button_2.grid(column=1, row=3, padx=5, pady=5, sticky="w")
radio_button_3.grid(column=2, row=3, padx=5, pady=5, sticky="w")

button_apply_watermark.grid(column=0, row=4, columnspan=3, padx=5, pady=10, sticky="ew")

button_exit.grid(column=0, row=5, columnspan=3, padx=5, pady=5, sticky="ew")

progress.grid(column=0, row=7, columnspan=3, padx=10, pady=10)

root.mainloop()